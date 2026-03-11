"""Unit tests for matrx_orm.api.handlers — Request dispatch and error mapping.

These tests run without a database connection (level1).
Uses mock managers to test the dispatch logic.
"""

from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock

import pytest

from matrx_orm.api.handlers import RequestHandler, ALLOWED_METHODS
from matrx_orm.api.protocol import ErrorCode, RPCRequest


class FakeManager:
    """Mock manager with common BaseManager methods."""

    def __init__(self) -> None:
        self.load_item = AsyncMock(return_value={"id": "abc", "name": "Alice"})
        self.load_items = AsyncMock(return_value=[{"id": "abc"}, {"id": "def"}])
        self.create_item = AsyncMock(return_value={"id": "new-id", "name": "Bob"})
        self.update_item = AsyncMock(return_value={"id": "abc", "name": "Updated"})
        self.delete_item = AsyncMock(return_value=True)
        self.count = AsyncMock(return_value=42)
        self.exists = AsyncMock(return_value=True)
        self.load_item_or_none = AsyncMock(return_value=None)


@pytest.fixture
def handler() -> RequestHandler:
    h = RequestHandler()
    h.register("users", FakeManager())
    return h


class TestMethodRegistration:
    def test_register_manager(self, handler: RequestHandler) -> None:
        assert "users" in handler._managers

    def test_list_methods(self, handler: RequestHandler) -> None:
        methods = handler.list_methods()
        assert "users.load_item" in methods
        assert "users.create_item" in methods
        assert "users.delete_item" in methods

    def test_register_custom_method(self, handler: RequestHandler) -> None:
        async def custom(**params: Any) -> str:
            return "hello"

        handler.register_method("system.hello", custom)
        methods = handler.list_methods()
        assert "system.hello" in methods


class TestMethodDispatch:
    @pytest.mark.asyncio
    async def test_load_item(self, handler: RequestHandler) -> None:
        req = RPCRequest(method="users.load_item", params={"id": "abc"}, id=1)
        resp = await handler.handle(req)
        assert resp.error is None
        assert resp.result == {"id": "abc", "name": "Alice"}
        assert resp.id == 1

    @pytest.mark.asyncio
    async def test_load_items(self, handler: RequestHandler) -> None:
        req = RPCRequest(method="users.load_items", params={}, id=2)
        resp = await handler.handle(req)
        assert resp.error is None
        assert len(resp.result) == 2

    @pytest.mark.asyncio
    async def test_create_item(self, handler: RequestHandler) -> None:
        req = RPCRequest(
            method="users.create_item",
            params={"name": "Bob"},
            id=3,
        )
        resp = await handler.handle(req)
        assert resp.error is None
        assert resp.result["name"] == "Bob"

    @pytest.mark.asyncio
    async def test_count(self, handler: RequestHandler) -> None:
        req = RPCRequest(method="users.count", params={}, id=4)
        resp = await handler.handle(req)
        assert resp.result == 42

    @pytest.mark.asyncio
    async def test_custom_method(self, handler: RequestHandler) -> None:
        async def greet(name: str = "world", **params: Any) -> str:
            return f"Hello, {name}!"

        handler.register_method("system.greet", greet)
        req = RPCRequest(method="system.greet", params={"name": "Alice"}, id=5)
        resp = await handler.handle(req)
        assert resp.result == "Hello, Alice!"


class TestErrorHandling:
    @pytest.mark.asyncio
    async def test_unknown_namespace(self, handler: RequestHandler) -> None:
        req = RPCRequest(method="orders.load_item", params={}, id=1)
        resp = await handler.handle(req)
        assert resp.error is not None
        assert resp.error.code == ErrorCode.METHOD_NOT_FOUND
        assert "orders" in resp.error.message

    @pytest.mark.asyncio
    async def test_unknown_method(self, handler: RequestHandler) -> None:
        req = RPCRequest(method="users.hack_database", params={}, id=1)
        resp = await handler.handle(req)
        assert resp.error is not None
        assert resp.error.code == ErrorCode.METHOD_NOT_FOUND
        assert "hack_database" in resp.error.message

    @pytest.mark.asyncio
    async def test_invalid_method_format(self, handler: RequestHandler) -> None:
        req = RPCRequest(method="justoneword", params={}, id=1)
        resp = await handler.handle(req)
        assert resp.error is not None
        assert resp.error.code == ErrorCode.METHOD_NOT_FOUND

    @pytest.mark.asyncio
    async def test_manager_raises_type_error(self, handler: RequestHandler) -> None:
        manager = handler._managers["users"]
        manager.load_item = AsyncMock(side_effect=TypeError("bad param"))

        req = RPCRequest(method="users.load_item", params={"wrong": True}, id=1)
        resp = await handler.handle(req)
        assert resp.error is not None
        assert resp.error.code == ErrorCode.INVALID_PARAMS

    @pytest.mark.asyncio
    async def test_manager_raises_unknown_error(self, handler: RequestHandler) -> None:
        manager = handler._managers["users"]
        manager.load_item = AsyncMock(side_effect=RuntimeError("unexpected"))

        req = RPCRequest(method="users.load_item", params={}, id=1)
        resp = await handler.handle(req)
        assert resp.error is not None
        assert resp.error.code == ErrorCode.INTERNAL_ERROR
        # Should NOT leak the internal error message
        assert "unexpected" not in resp.error.message


class TestBatchRequests:
    @pytest.mark.asyncio
    async def test_batch(self, handler: RequestHandler) -> None:
        requests = [
            RPCRequest(method="users.count", params={}, id=1),
            RPCRequest(method="users.load_items", params={}, id=2),
        ]
        responses = await handler.handle_batch(requests)
        assert len(responses) == 2
        assert responses[0].result == 42
        assert len(responses[1].result) == 2


class TestAllowedMethods:
    def test_no_dangerous_methods(self) -> None:
        """Ensure we don't expose methods that could be dangerous."""
        dangerous = {
            "raw_sql",
            "_execute",
            "__init__",
            "_process_item",
            "initialize",
            "_auto_fetch_on_init_async",
        }
        for method in ALLOWED_METHODS:
            assert method not in dangerous
            assert not method.startswith("_")
