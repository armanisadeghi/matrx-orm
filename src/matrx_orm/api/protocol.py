"""JSON-RPC-inspired request/response protocol for the desktop API.

Every request is a JSON object with:
    - ``method``: The operation to perform (e.g. ``"users.load_item"``)
    - ``params``: A dict of keyword arguments for the method
    - ``id``: Optional client-generated request ID for correlation

Every response is a JSON object with:
    - ``result``: The return value (on success)
    - ``error``: An error object (on failure)
    - ``id``: Echoed from the request
"""

from __future__ import annotations

import enum
import json
from dataclasses import asdict, dataclass, field
from typing import Any


class ErrorCode(enum.IntEnum):
    """Standard error codes (JSON-RPC compatible range + custom range)."""

    PARSE_ERROR = -32700
    INVALID_REQUEST = -32600
    METHOD_NOT_FOUND = -32601
    INVALID_PARAMS = -32602
    INTERNAL_ERROR = -32603

    # Application-level errors (custom range)
    NOT_FOUND = 1001
    VALIDATION_ERROR = 1002
    INTEGRITY_ERROR = 1003
    AUTH_REQUIRED = 1004
    AUTH_INVALID = 1005
    PERMISSION_DENIED = 1006
    RATE_LIMITED = 1007
    CONNECTION_ERROR = 1008
    QUERY_ERROR = 1009


@dataclass
class RPCRequest:
    """Parsed incoming request."""

    method: str
    params: dict[str, Any] = field(default_factory=dict)
    id: str | int | None = None

    @classmethod
    def from_json(cls, raw: str | bytes) -> RPCRequest:
        """Parse a JSON string into an RPCRequest.

        Raises ValueError on malformed input.
        """
        try:
            data = json.loads(raw)
        except (json.JSONDecodeError, TypeError) as exc:
            raise ValueError(f"Invalid JSON: {exc}") from exc

        if not isinstance(data, dict):
            raise ValueError("Request must be a JSON object")

        method = data.get("method")
        if not method or not isinstance(method, str):
            raise ValueError("Request must include a 'method' string")

        params = data.get("params", {})
        if not isinstance(params, dict):
            raise ValueError("'params' must be a JSON object")

        return cls(
            method=method,
            params=params,
            id=data.get("id"),
        )


@dataclass
class RPCError:
    """Error payload for failed requests."""

    code: int
    message: str
    data: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {"code": self.code, "message": self.message}
        if self.data:
            d["data"] = self.data
        return d


@dataclass
class RPCResponse:
    """Response envelope."""

    result: Any = None
    error: RPCError | None = None
    id: str | int | None = None

    def to_json(self) -> str:
        d: dict[str, Any] = {"id": self.id}
        if self.error:
            d["error"] = self.error.to_dict()
            d["result"] = None
        else:
            d["result"] = self.result
        return json.dumps(d, default=_json_default)

    @classmethod
    def success(cls, result: Any, request_id: str | int | None = None) -> RPCResponse:
        return cls(result=result, id=request_id)

    @classmethod
    def fail(
        cls,
        code: ErrorCode | int,
        message: str,
        request_id: str | int | None = None,
        data: dict[str, Any] | None = None,
    ) -> RPCResponse:
        return cls(
            error=RPCError(code=int(code), message=message, data=data),
            id=request_id,
        )


def _json_default(obj: Any) -> Any:
    """JSON serializer for types not handled by the stdlib."""
    import datetime
    import uuid
    from decimal import Decimal

    if isinstance(obj, uuid.UUID):
        return str(obj)
    if isinstance(obj, (datetime.datetime, datetime.date)):
        return obj.isoformat()
    if isinstance(obj, datetime.time):
        return obj.isoformat()
    if isinstance(obj, datetime.timedelta):
        return obj.total_seconds()
    if isinstance(obj, Decimal):
        return float(obj)
    if isinstance(obj, bytes):
        return obj.hex()
    if isinstance(obj, set):
        return list(obj)
    if hasattr(obj, "to_dict"):
        return obj.to_dict()
    if hasattr(obj, "__dict__"):
        return {k: v for k, v in obj.__dict__.items() if not k.startswith("_")}
    raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")
