"""Request handlers that dispatch RPC methods to BaseManager operations.

Each registered manager is exposed under a namespace (e.g. ``"users"``).
The method ``"users.load_item"`` maps to ``user_manager.load_item(**params)``.

Only explicitly allow-listed manager methods are callable to prevent
arbitrary code execution.
"""

from __future__ import annotations

import asyncio
from typing import Any

from matrx_orm.api.protocol import ErrorCode, RPCRequest, RPCResponse


# Methods on BaseManager that are safe to expose over the API.
# Each entry maps from the public method name to the internal method name.
ALLOWED_METHODS: dict[str, str] = {
    # Single-item CRUD
    "load_item": "load_item",
    "load_item_or_none": "load_item_or_none",
    "load_by_id": "load_by_id",
    "create_item": "create_item",
    "update_item": "update_item",
    "delete_item": "delete_item",
    "exists": "exists",
    # Dict variants
    "get_item_dict": "get_item_dict",
    "create_item_get_dict": "create_item_get_dict",
    "update_item_get_dict": "update_item_get_dict",
    # Bulk reads
    "load_items": "load_items",
    "load_items_by_ids": "load_items_by_ids",
    "count": "count",
    # Bulk writes
    "create_items": "create_items",
    "update_where": "update_where",
    "delete_where": "delete_where",
    "upsert_item": "upsert_item",
    "upsert_items": "upsert_items",
    # Relationships
    "get_item_with_fk": "get_item_with_fk",
    "get_item_with_ifk": "get_item_with_ifk",
    "get_item_with_m2m": "get_item_with_m2m",
    "get_item_with_all_related": "get_item_with_all_related",
    "get_items_with_related": "get_items_with_related",
    # M2M mutations
    "add_m2m": "add_m2m",
    "remove_m2m": "remove_m2m",
    "set_m2m": "set_m2m",
    "clear_m2m": "clear_m2m",
    # Get or create
    "get_or_create": "get_or_create",
    # First / last
    "load_first_item": "load_first_item",
    "load_last_item": "load_last_item",
}


class RequestHandler:
    """Dispatches RPC requests to registered BaseManager instances.

    Usage::

        handler = RequestHandler()
        handler.register("users", user_manager)
        handler.register("posts", post_manager)

        response = await handler.handle(rpc_request)
    """

    def __init__(self) -> None:
        self._managers: dict[str, Any] = {}
        self._custom_methods: dict[str, Any] = {}

    def register(self, namespace: str, manager: Any) -> None:
        """Register a BaseManager under a namespace.

        Parameters
        ----------
        namespace : str
            The prefix for RPC methods (e.g. ``"users"`` enables
            ``"users.load_item"``, ``"users.create_item"``, etc.).
        manager : BaseManager
            The manager instance to dispatch to.
        """
        self._managers[namespace] = manager

    def register_method(self, name: str, handler: Any) -> None:
        """Register a custom async callable as an RPC method.

        Parameters
        ----------
        name : str
            Full method name (e.g. ``"system.health"``).
        handler : callable
            An async function that accepts ``**params`` and returns a result.
        """
        self._custom_methods[name] = handler

    def list_methods(self) -> list[str]:
        """Return all available RPC method names."""
        methods: list[str] = []
        for ns in sorted(self._managers):
            for method_name in sorted(ALLOWED_METHODS):
                methods.append(f"{ns}.{method_name}")
        methods.extend(sorted(self._custom_methods))
        return methods

    async def handle(self, request: RPCRequest) -> RPCResponse:
        """Dispatch a single RPC request and return the response."""
        # Check custom methods first
        if request.method in self._custom_methods:
            return await self._call_custom(request)

        # Parse namespace.method
        parts = request.method.split(".", 1)
        if len(parts) != 2:
            return RPCResponse.fail(
                ErrorCode.METHOD_NOT_FOUND,
                f"Invalid method format: '{request.method}'. "
                "Expected 'namespace.method' (e.g. 'users.load_item').",
                request.id,
            )

        namespace, method_name = parts

        if namespace not in self._managers:
            return RPCResponse.fail(
                ErrorCode.METHOD_NOT_FOUND,
                f"Unknown namespace: '{namespace}'. "
                f"Available: {list(self._managers.keys())}",
                request.id,
            )

        if method_name not in ALLOWED_METHODS:
            return RPCResponse.fail(
                ErrorCode.METHOD_NOT_FOUND,
                f"Method '{method_name}' is not allowed. "
                f"Available methods: {list(ALLOWED_METHODS.keys())}",
                request.id,
            )

        manager = self._managers[namespace]
        internal_method = ALLOWED_METHODS[method_name]
        fn = getattr(manager, internal_method, None)

        if fn is None:
            return RPCResponse.fail(
                ErrorCode.METHOD_NOT_FOUND,
                f"Manager for '{namespace}' does not implement '{internal_method}'.",
                request.id,
            )

        return await self._call_manager(fn, request)

    async def _call_manager(self, fn: Any, request: RPCRequest) -> RPCResponse:
        """Call a manager method with error translation."""
        try:
            result = await fn(**request.params)
            return RPCResponse.success(
                _serialize_result(result),
                request.id,
            )
        except Exception as exc:
            return _exception_to_response(exc, request.id)

    async def _call_custom(self, request: RPCRequest) -> RPCResponse:
        """Call a custom registered method."""
        fn = self._custom_methods[request.method]
        try:
            result = await fn(**request.params)
            return RPCResponse.success(
                _serialize_result(result),
                request.id,
            )
        except Exception as exc:
            return _exception_to_response(exc, request.id)

    async def handle_batch(self, requests: list[RPCRequest]) -> list[RPCResponse]:
        """Handle multiple RPC requests concurrently."""
        return await asyncio.gather(
            *(self.handle(req) for req in requests)
        )


def _serialize_result(result: Any) -> Any:
    """Convert ORM results to JSON-safe types."""
    if result is None:
        return None

    if isinstance(result, (str, int, float, bool)):
        return result

    if isinstance(result, list):
        return [_serialize_result(item) for item in result]

    if isinstance(result, tuple):
        return [_serialize_result(item) for item in result]

    if isinstance(result, dict):
        return {k: _serialize_result(v) for k, v in result.items()}

    # Model instances
    if hasattr(result, "to_dict"):
        return result.to_dict()

    return result


def _exception_to_response(
    exc: Exception, request_id: str | int | None
) -> RPCResponse:
    """Map ORM exceptions to appropriate RPC error responses."""
    from matrx_orm.exceptions import (
        DoesNotExist,
        ValidationError,
        IntegrityError,
        ConnectionError,
        QueryError,
        ORMException,
    )
    from matrx_orm.extended.app_error_handler import AppError

    if isinstance(exc, DoesNotExist):
        return RPCResponse.fail(
            ErrorCode.NOT_FOUND,
            str(exc.message),
            request_id,
            data={"model": exc.model},
        )

    if isinstance(exc, ValidationError):
        return RPCResponse.fail(
            ErrorCode.VALIDATION_ERROR,
            str(exc.message),
            request_id,
            data={"model": exc.model},
        )

    if isinstance(exc, IntegrityError):
        return RPCResponse.fail(
            ErrorCode.INTEGRITY_ERROR,
            str(exc.message),
            request_id,
            data={"model": exc.model},
        )

    if isinstance(exc, ConnectionError):
        return RPCResponse.fail(
            ErrorCode.CONNECTION_ERROR,
            "Database connection error",
            request_id,
        )

    if isinstance(exc, QueryError):
        return RPCResponse.fail(
            ErrorCode.QUERY_ERROR,
            str(exc.message),
            request_id,
        )

    if isinstance(exc, AppError):
        return RPCResponse.fail(
            ErrorCode.INTERNAL_ERROR,
            exc.client_visible or "An internal error occurred",
            request_id,
        )

    if isinstance(exc, ORMException):
        return RPCResponse.fail(
            ErrorCode.INTERNAL_ERROR,
            str(exc.message),
            request_id,
        )

    if isinstance(exc, TypeError):
        return RPCResponse.fail(
            ErrorCode.INVALID_PARAMS,
            f"Invalid parameters: {exc}",
            request_id,
        )

    # Unknown errors — don't leak internals
    return RPCResponse.fail(
        ErrorCode.INTERNAL_ERROR,
        "An unexpected error occurred",
        request_id,
    )
