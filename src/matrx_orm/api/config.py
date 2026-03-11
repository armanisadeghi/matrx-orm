"""Configuration for the desktop API server."""

from __future__ import annotations

import secrets
from dataclasses import dataclass, field


@dataclass
class APIConfig:
    """Configuration for the local API server.

    Parameters
    ----------
    host : str
        Bind address. Defaults to ``"127.0.0.1"`` (localhost only).
        **Never** set this to ``"0.0.0.0"`` in production — the API is
        designed for local desktop communication only.
    port : int
        TCP port to listen on.
    secret : str
        Shared secret used to sign and verify authentication tokens.
        If not provided, a secure random secret is generated at startup
        and printed to stdout so the client process can read it.
    token_ttl : int
        Token time-to-live in seconds. Default 24 hours.
    max_payload_bytes : int
        Maximum request body size. Default 10 MB.
    cors_origins : list[str]
        Allowed CORS origins. Defaults to common local dev origins.
    enable_websocket : bool
        Whether to expose the ``/ws`` WebSocket endpoint for streaming
        and subscription-style communication.
    log_requests : bool
        Log every incoming request at INFO level.
    """

    host: str = "127.0.0.1"
    port: int = 8745
    secret: str = ""
    token_ttl: int = 86400
    max_payload_bytes: int = 10 * 1024 * 1024
    cors_origins: list[str] = field(
        default_factory=lambda: [
            "http://localhost:3000",
            "http://localhost:5173",
            "http://127.0.0.1:3000",
            "http://127.0.0.1:5173",
            "tauri://localhost",
        ]
    )
    enable_websocket: bool = True
    log_requests: bool = True

    def __post_init__(self) -> None:
        if not self.secret:
            self.secret = secrets.token_urlsafe(32)
            self._auto_generated_secret = True
        else:
            self._auto_generated_secret = False

        if self.host not in ("127.0.0.1", "localhost", "::1"):
            import warnings

            warnings.warn(
                f"APIConfig.host is set to '{self.host}'. The matrx-orm API server "
                "is designed for localhost-only desktop communication. Binding to a "
                "non-local address exposes your database to the network.",
                stacklevel=2,
            )
