"""Secure local API server for desktop application integration.

Provides a localhost-only HTTP + WebSocket server that exposes ORM operations
to desktop frontends (Electron, Tauri, etc.) with token-based authentication.

Install the optional dependency group::

    pip install matrx-orm[api]

Quick start::

    from matrx_orm.api import APIServer, APIConfig

    server = APIServer(config=APIConfig(secret="my-secret"))
    server.register_manager("users", user_manager)
    await server.start()
"""

from matrx_orm.api.config import APIConfig
from matrx_orm.api.protocol import (
    RPCRequest,
    RPCResponse,
    RPCError,
    ErrorCode,
)
from matrx_orm.api.auth import TokenAuth
from matrx_orm.api.server import APIServer

__all__ = [
    "APIConfig",
    "APIServer",
    "TokenAuth",
    "RPCRequest",
    "RPCResponse",
    "RPCError",
    "ErrorCode",
]
