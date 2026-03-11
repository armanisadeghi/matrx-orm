"""Async HTTP + WebSocket server for desktop app communication.

Uses ``aiohttp`` as the transport layer. Install with::

    pip install matrx-orm[api]

The server binds to localhost only and requires token authentication
on every request.
"""

from __future__ import annotations

import asyncio
import json
import logging
import sys
from typing import Any

from matrx_orm.api.auth import AuthError, TokenAuth
from matrx_orm.api.config import APIConfig
from matrx_orm.api.handlers import RequestHandler
from matrx_orm.api.protocol import ErrorCode, RPCRequest, RPCResponse

logger = logging.getLogger("matrx_orm.api")


class APIServer:
    """Local API server for desktop application integration.

    Usage::

        from matrx_orm.api import APIServer, APIConfig

        server = APIServer(config=APIConfig(secret="shared-secret"))
        server.register_manager("users", user_manager)
        server.register_manager("posts", post_manager)

        # Register custom methods
        async def health(**params):
            return {"status": "ok"}
        server.register_method("system.health", health)

        # Start (blocking)
        await server.start()

        # Or start in background
        await server.start_background()
        # ... later ...
        await server.stop()
    """

    def __init__(self, config: APIConfig | None = None) -> None:
        self._config = config or APIConfig()
        self._auth = TokenAuth(self._config.secret, self._config.token_ttl)
        self._handler = RequestHandler()
        self._app: Any = None
        self._runner: Any = None
        self._site: Any = None

    @property
    def config(self) -> APIConfig:
        return self._config

    @property
    def auth(self) -> TokenAuth:
        return self._auth

    def register_manager(self, namespace: str, manager: Any) -> None:
        """Register a BaseManager under a namespace for RPC dispatch."""
        self._handler.register(namespace, manager)
        logger.info("Registered manager: %s", namespace)

    def register_method(self, name: str, handler: Any) -> None:
        """Register a custom async callable as an RPC method."""
        self._handler.register_method(name, handler)

    def _build_app(self) -> Any:
        """Create the aiohttp Application with routes and middleware."""
        try:
            from aiohttp import web
        except ImportError:
            raise ImportError(
                "aiohttp is required for the API server. "
                "Install it with: pip install matrx-orm[api]"
            ) from None

        app = web.Application(
            client_max_size=self._config.max_payload_bytes,
        )

        # Routes
        app.router.add_post("/auth/token", self._handle_auth_token)
        app.router.add_post("/auth/revoke", self._handle_auth_revoke)
        app.router.add_post("/rpc", self._handle_rpc)
        app.router.add_get("/health", self._handle_health)
        app.router.add_get("/methods", self._handle_methods)

        if self._config.enable_websocket:
            app.router.add_get("/ws", self._handle_websocket)

        # CORS middleware
        app.middlewares.append(self._cors_middleware)

        return app

    # ── Middleware ──────────────────────────────────────────────────────────

    async def _cors_middleware(self, app: Any, handler: Any) -> Any:
        from aiohttp import web

        async def middleware_handler(request: web.Request) -> web.StreamResponse:
            # Handle preflight
            if request.method == "OPTIONS":
                response = web.Response(status=204)
            else:
                response = await handler(request)

            origin = request.headers.get("Origin", "")
            if origin in self._config.cors_origins:
                response.headers["Access-Control-Allow-Origin"] = origin
            response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
            response.headers["Access-Control-Allow-Headers"] = (
                "Content-Type, Authorization"
            )
            response.headers["Access-Control-Max-Age"] = "3600"
            return response

        return middleware_handler

    # ── Auth helpers ───────────────────────────────────────────────────────

    def _extract_token(self, request: Any) -> str | None:
        """Extract bearer token from Authorization header."""
        auth = request.headers.get("Authorization", "")
        if auth.startswith("Bearer "):
            return auth[7:]
        return None

    def _require_auth(self, request: Any) -> None:
        """Validate the bearer token or raise AuthError."""
        token = self._extract_token(request)
        if not token:
            raise AuthError("Authorization header with Bearer token is required")
        self._auth.validate_token(token)

    # ── Route handlers ─────────────────────────────────────────────────────

    async def _handle_auth_token(self, request: Any) -> Any:
        """``POST /auth/token`` — Exchange shared secret for a bearer token."""
        from aiohttp import web

        try:
            body = await request.json()
        except Exception:
            return web.json_response(
                RPCResponse.fail(
                    ErrorCode.PARSE_ERROR, "Invalid JSON body"
                ).to_json(),
                status=400,
                content_type="application/json",
            )

        secret = body.get("secret", "")
        if secret != self._config.secret:
            return web.json_response(
                {"error": "Invalid secret"},
                status=401,
            )

        client_id = body.get("client_id", "desktop")
        scopes = body.get("scopes")
        ttl = body.get("ttl")

        token = self._auth.issue_token(
            client_id=client_id,
            scopes=scopes,
            ttl=ttl,
        )

        return web.json_response({
            "token": token,
            "expires_in": ttl or self._config.token_ttl,
        })

    async def _handle_auth_revoke(self, request: Any) -> Any:
        """``POST /auth/revoke`` — Revoke a bearer token."""
        from aiohttp import web

        try:
            self._require_auth(request)
        except AuthError as exc:
            return web.json_response(
                {"error": exc.message}, status=401
            )

        try:
            body = await request.json()
            token_to_revoke = body.get("token", "")
            if token_to_revoke:
                self._auth.revoke_token(token_to_revoke)
        except Exception:
            pass

        return web.json_response({"revoked": True})

    async def _handle_health(self, request: Any) -> Any:
        """``GET /health`` — Health check (no auth required)."""
        from aiohttp import web

        return web.json_response({
            "status": "ok",
            "managers": list(self._handler._managers.keys()),
        })

    async def _handle_methods(self, request: Any) -> Any:
        """``GET /methods`` — List all available RPC methods."""
        from aiohttp import web

        try:
            self._require_auth(request)
        except AuthError as exc:
            return web.json_response(
                {"error": exc.message}, status=401
            )

        return web.json_response({
            "methods": self._handler.list_methods(),
        })

    async def _handle_rpc(self, request: Any) -> Any:
        """``POST /rpc`` — Execute an RPC method call."""
        from aiohttp import web

        # Auth check
        try:
            self._require_auth(request)
        except AuthError as exc:
            return web.json_response(
                RPCResponse.fail(
                    ErrorCode.AUTH_INVALID, exc.message
                ).to_json(),
                status=401,
                content_type="application/json",
            )

        # Parse body
        try:
            raw = await request.read()
        except Exception:
            return web.json_response(
                RPCResponse.fail(
                    ErrorCode.PARSE_ERROR, "Failed to read request body"
                ).to_json(),
                status=400,
                content_type="application/json",
            )

        # Single request or batch
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            return web.json_response(
                RPCResponse.fail(
                    ErrorCode.PARSE_ERROR, "Invalid JSON"
                ).to_json(),
                status=400,
                content_type="application/json",
            )

        # Batch request
        if isinstance(data, list):
            try:
                requests = [RPCRequest.from_json(json.dumps(item)) for item in data]
            except ValueError as exc:
                return web.json_response(
                    RPCResponse.fail(
                        ErrorCode.INVALID_REQUEST, str(exc)
                    ).to_json(),
                    status=400,
                    content_type="application/json",
                )
            responses = await self._handler.handle_batch(requests)
            body = "[" + ",".join(r.to_json() for r in responses) + "]"
            return web.Response(
                text=body,
                content_type="application/json",
            )

        # Single request
        try:
            rpc_request = RPCRequest.from_json(raw)
        except ValueError as exc:
            return web.json_response(
                RPCResponse.fail(
                    ErrorCode.INVALID_REQUEST, str(exc)
                ).to_json(),
                status=400,
                content_type="application/json",
            )

        if self._config.log_requests:
            logger.info("RPC: %s", rpc_request.method)

        response = await self._handler.handle(rpc_request)
        return web.Response(
            text=response.to_json(),
            content_type="application/json",
        )

    async def _handle_websocket(self, request: Any) -> Any:
        """``GET /ws`` — WebSocket endpoint for streaming RPC."""
        from aiohttp import web, WSMsgType

        ws = web.WebSocketResponse()
        await ws.prepare(request)

        # First message must be auth
        auth_msg = await ws.receive()
        if auth_msg.type != WSMsgType.TEXT:
            await ws.close(code=4001, message=b"Expected auth message")
            return ws

        try:
            auth_data = json.loads(auth_msg.data)
            token = auth_data.get("token", "")
            self._auth.validate_token(token)
        except (json.JSONDecodeError, AuthError) as exc:
            error_msg = exc.message if isinstance(exc, AuthError) else "Invalid JSON"
            await ws.send_json({"error": error_msg, "type": "auth_error"})
            await ws.close(code=4001, message=b"Authentication failed")
            return ws

        await ws.send_json({"type": "auth_ok"})
        logger.info("WebSocket client authenticated")

        # Message loop
        async for msg in ws:
            if msg.type == WSMsgType.TEXT:
                try:
                    rpc_request = RPCRequest.from_json(msg.data)
                except ValueError as exc:
                    await ws.send_str(
                        RPCResponse.fail(
                            ErrorCode.INVALID_REQUEST, str(exc)
                        ).to_json()
                    )
                    continue

                if self._config.log_requests:
                    logger.info("WS RPC: %s", rpc_request.method)

                response = await self._handler.handle(rpc_request)
                await ws.send_str(response.to_json())

            elif msg.type in (WSMsgType.ERROR, WSMsgType.CLOSE):
                break

        logger.info("WebSocket client disconnected")
        return ws

    # ── Lifecycle ──────────────────────────────────────────────────────────

    async def start(self) -> None:
        """Start the server (blocking). Use Ctrl+C to stop."""
        from aiohttp import web

        self._app = self._build_app()

        if self._config._auto_generated_secret:
            print(
                f"\n  MATRX API Server"
                f"\n  Listening: http://{self._config.host}:{self._config.port}"
                f"\n  Secret:    {self._config.secret}"
                f"\n  (Auto-generated. Pass this to your desktop app.)\n",
                file=sys.stderr,
            )
        else:
            print(
                f"\n  MATRX API Server"
                f"\n  Listening: http://{self._config.host}:{self._config.port}\n",
                file=sys.stderr,
            )

        runner = web.AppRunner(self._app)
        await runner.setup()
        site = web.TCPSite(runner, self._config.host, self._config.port)
        await site.start()

        # Block until interrupted
        try:
            await asyncio.Event().wait()
        except (KeyboardInterrupt, asyncio.CancelledError):
            pass
        finally:
            await runner.cleanup()

    async def start_background(self) -> None:
        """Start the server in the background. Call ``stop()`` to shut down."""
        from aiohttp import web

        self._app = self._build_app()
        self._runner = web.AppRunner(self._app)
        await self._runner.setup()
        self._site = web.TCPSite(
            self._runner, self._config.host, self._config.port
        )
        await self._site.start()

        if self._config._auto_generated_secret:
            logger.info(
                "API server started on http://%s:%s (secret: %s)",
                self._config.host,
                self._config.port,
                self._config.secret,
            )
        else:
            logger.info(
                "API server started on http://%s:%s",
                self._config.host,
                self._config.port,
            )

    async def stop(self) -> None:
        """Stop the background server."""
        if self._runner:
            await self._runner.cleanup()
            self._runner = None
            self._site = None
            logger.info("API server stopped")

    @property
    def url(self) -> str:
        """Base URL of the running server."""
        return f"http://{self._config.host}:{self._config.port}"
