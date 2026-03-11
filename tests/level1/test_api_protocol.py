"""Unit tests for matrx_orm.api.protocol — RPC request/response serialization.

These tests run without a database connection (level1).
"""

from __future__ import annotations

import json
import uuid
from datetime import datetime, date, time, timedelta
from decimal import Decimal

import pytest

from matrx_orm.api.protocol import (
    ErrorCode,
    RPCRequest,
    RPCResponse,
    RPCError,
)


class TestRPCRequest:
    def test_from_json_minimal(self) -> None:
        req = RPCRequest.from_json('{"method": "users.load_items"}')
        assert req.method == "users.load_items"
        assert req.params == {}
        assert req.id is None

    def test_from_json_full(self) -> None:
        raw = json.dumps({
            "method": "users.create_item",
            "params": {"username": "alice", "age": 30},
            "id": 42,
        })
        req = RPCRequest.from_json(raw)
        assert req.method == "users.create_item"
        assert req.params == {"username": "alice", "age": 30}
        assert req.id == 42

    def test_from_json_bytes(self) -> None:
        raw = b'{"method": "test"}'
        req = RPCRequest.from_json(raw)
        assert req.method == "test"

    def test_from_json_invalid_json(self) -> None:
        with pytest.raises(ValueError, match="Invalid JSON"):
            RPCRequest.from_json("not json{")

    def test_from_json_not_object(self) -> None:
        with pytest.raises(ValueError, match="must be a JSON object"):
            RPCRequest.from_json('"just a string"')

    def test_from_json_missing_method(self) -> None:
        with pytest.raises(ValueError, match="must include a 'method'"):
            RPCRequest.from_json('{"params": {}}')

    def test_from_json_method_not_string(self) -> None:
        with pytest.raises(ValueError, match="must include a 'method'"):
            RPCRequest.from_json('{"method": 42}')

    def test_from_json_params_not_dict(self) -> None:
        with pytest.raises(ValueError, match="'params' must be a JSON object"):
            RPCRequest.from_json('{"method": "test", "params": [1, 2]}')

    def test_string_id(self) -> None:
        req = RPCRequest.from_json('{"method": "test", "id": "req-abc"}')
        assert req.id == "req-abc"


class TestRPCResponse:
    def test_success(self) -> None:
        resp = RPCResponse.success({"id": "123", "name": "alice"}, request_id=1)
        data = json.loads(resp.to_json())
        assert data["result"] == {"id": "123", "name": "alice"}
        assert data["id"] == 1
        assert "error" not in data or data.get("error") is None

    def test_fail(self) -> None:
        resp = RPCResponse.fail(
            ErrorCode.NOT_FOUND,
            "User not found",
            request_id=5,
            data={"model": "User"},
        )
        data = json.loads(resp.to_json())
        assert data["result"] is None
        assert data["error"]["code"] == 1001
        assert data["error"]["message"] == "User not found"
        assert data["error"]["data"] == {"model": "User"}
        assert data["id"] == 5

    def test_success_null_result(self) -> None:
        resp = RPCResponse.success(None, request_id=1)
        data = json.loads(resp.to_json())
        assert data["result"] is None

    def test_success_list_result(self) -> None:
        resp = RPCResponse.success([1, 2, 3], request_id=1)
        data = json.loads(resp.to_json())
        assert data["result"] == [1, 2, 3]

    def test_fail_no_data(self) -> None:
        resp = RPCResponse.fail(ErrorCode.INTERNAL_ERROR, "oops")
        data = json.loads(resp.to_json())
        assert data["error"]["code"] == -32603
        assert "data" not in data["error"]


class TestRPCError:
    def test_to_dict(self) -> None:
        err = RPCError(code=1001, message="Not found")
        assert err.to_dict() == {"code": 1001, "message": "Not found"}

    def test_to_dict_with_data(self) -> None:
        err = RPCError(code=1001, message="Not found", data={"model": "User"})
        d = err.to_dict()
        assert d["data"] == {"model": "User"}


class TestErrorCode:
    def test_values(self) -> None:
        assert ErrorCode.PARSE_ERROR == -32700
        assert ErrorCode.NOT_FOUND == 1001
        assert ErrorCode.AUTH_INVALID == 1005


class TestJSONSerialization:
    """Test that the custom JSON serializer handles ORM types."""

    def test_uuid(self) -> None:
        uid = uuid.UUID("12345678-1234-5678-1234-567812345678")
        resp = RPCResponse.success({"id": uid})
        data = json.loads(resp.to_json())
        assert data["result"]["id"] == "12345678-1234-5678-1234-567812345678"

    def test_datetime(self) -> None:
        dt = datetime(2025, 1, 15, 10, 30, 0)
        resp = RPCResponse.success({"created": dt})
        data = json.loads(resp.to_json())
        assert data["result"]["created"] == "2025-01-15T10:30:00"

    def test_date(self) -> None:
        d = date(2025, 1, 15)
        resp = RPCResponse.success({"date": d})
        data = json.loads(resp.to_json())
        assert data["result"]["date"] == "2025-01-15"

    def test_time(self) -> None:
        t = time(10, 30, 0)
        resp = RPCResponse.success({"time": t})
        data = json.loads(resp.to_json())
        assert data["result"]["time"] == "10:30:00"

    def test_timedelta(self) -> None:
        td = timedelta(hours=2, minutes=30)
        resp = RPCResponse.success({"duration": td})
        data = json.loads(resp.to_json())
        assert data["result"]["duration"] == 9000.0

    def test_decimal(self) -> None:
        resp = RPCResponse.success({"price": Decimal("19.99")})
        data = json.loads(resp.to_json())
        assert data["result"]["price"] == 19.99

    def test_bytes(self) -> None:
        resp = RPCResponse.success({"data": b"\xde\xad\xbe\xef"})
        data = json.loads(resp.to_json())
        assert data["result"]["data"] == "deadbeef"

    def test_set(self) -> None:
        resp = RPCResponse.success({"tags": {1, 2, 3}})
        data = json.loads(resp.to_json())
        assert sorted(data["result"]["tags"]) == [1, 2, 3]

    def test_to_dict_object(self) -> None:
        class FakeModel:
            def to_dict(self):
                return {"id": "123", "name": "test"}

        resp = RPCResponse.success(FakeModel())
        data = json.loads(resp.to_json())
        assert data["result"] == {"id": "123", "name": "test"}
