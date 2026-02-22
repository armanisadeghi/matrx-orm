"""ORM-level transaction context manager.

Usage::

    from matrx_orm import transaction

    async with transaction():
        user = await User.create(name="alice")
        await Profile.create(user_id=user.id, bio="hello")
        # auto-commits on exit, auto-rollbacks on exception

    # Nested transaction → savepoint
    async with transaction():
        await Order.create(...)
        async with transaction():          # creates a SAVEPOINT
            await AuditLog.create(...)     # rolled back independently if this block raises

Transactions are propagated via a ``contextvars.ContextVar`` so every
``execute_query`` call within the same async task (and its children)
automatically uses the same connection without any manual passing.
"""
from __future__ import annotations

import uuid
import asyncio
import asyncpg
from contextlib import asynccontextmanager
from contextvars import ContextVar, Token
from typing import Any, AsyncIterator

from matrx_orm.core.async_db_manager import AsyncDatabaseManager
from matrx_orm.exceptions import DatabaseError, ConnectionError as OrmConnectionError

# ContextVar holding the active connection (if any) for the current task tree.
_active_connection: ContextVar[asyncpg.Connection | None] = ContextVar(
    "_active_connection", default=None
)
# ContextVar tracking savepoint depth (0 = top-level transaction)
_savepoint_depth: ContextVar[int] = ContextVar("_savepoint_depth", default=0)


def get_active_connection() -> asyncpg.Connection | None:
    """Return the connection bound to the current transaction context, or None."""
    return _active_connection.get()


class TransactionContext:
    """Async context manager returned by ``transaction()``.

    On first entry (no active connection): acquires a connection, executes
    BEGIN, and stores the connection in the ContextVar.

    On nested entry (active connection exists): creates a SAVEPOINT instead.
    """

    def __init__(self, database: str) -> None:
        self.database = database
        self._conn_token: Token[asyncpg.Connection | None] | None = None
        self._depth_token: Token[int] | None = None
        self._is_savepoint: bool = False
        self._savepoint_name: str = ""
        self._pool_conn: asyncpg.Connection | None = None
        self._pool: asyncpg.Pool | None = None

    async def __aenter__(self) -> TransactionContext:
        existing = _active_connection.get()
        if existing is not None:
            # Nested → savepoint
            self._is_savepoint = True
            self._savepoint_name = f"sp_{uuid.uuid4().hex[:12]}"
            depth = _savepoint_depth.get()
            self._depth_token = _savepoint_depth.set(depth + 1)
            await existing.execute(f"SAVEPOINT {self._savepoint_name}")
        else:
            # Top-level → BEGIN
            self._is_savepoint = False
            pool = await AsyncDatabaseManager.get_pool(self.database)
            self._pool = pool
            self._pool_conn = await pool.acquire()
            try:
                await self._pool_conn.execute("BEGIN")
            except Exception as e:
                await pool.release(self._pool_conn)
                raise DatabaseError(
                    message=f"Failed to begin transaction: {e}",
                    details={"database": self.database},
                )
            self._conn_token = _active_connection.set(self._pool_conn)
            self._depth_token = _savepoint_depth.set(0)
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: Any,
    ) -> bool:
        conn = _active_connection.get()
        if self._is_savepoint:
            # Restore savepoint depth
            if self._depth_token is not None:
                _savepoint_depth.reset(self._depth_token)
            if exc_type is None:
                # Release the savepoint (make it permanent within the outer tx)
                if conn is not None:
                    await conn.execute(f"RELEASE SAVEPOINT {self._savepoint_name}")
            else:
                # Roll back to the savepoint only
                if conn is not None:
                    await conn.execute(f"ROLLBACK TO SAVEPOINT {self._savepoint_name}")
                    await conn.execute(f"RELEASE SAVEPOINT {self._savepoint_name}")
                return False  # re-raise the exception
        else:
            # Top-level: restore ContextVars before touching the connection
            if self._conn_token is not None:
                _active_connection.reset(self._conn_token)
            if self._depth_token is not None:
                _savepoint_depth.reset(self._depth_token)

            conn_to_use = self._pool_conn
            if conn_to_use is None:
                return False

            try:
                if exc_type is None:
                    await conn_to_use.execute("COMMIT")
                else:
                    await conn_to_use.execute("ROLLBACK")
            finally:
                if self._pool is not None:
                    await self._pool.release(conn_to_use)

            if exc_type is not None:
                return False  # re-raise

        return False  # never suppress exceptions


def transaction(database: str | None = None) -> TransactionContext:
    """Return a ``TransactionContext`` async context manager.

    ``database`` defaults to the first configured database when omitted.
    """
    if database is None:
        database = _get_default_database()
    return TransactionContext(database)


def _get_default_database() -> str:
    """Infer a default database name from env / config."""
    try:
        from matrx_orm.core.config import get_default_database_name
        return get_default_database_name()
    except (ImportError, Exception):
        pass
    import os
    return os.environ.get("MATRX_DEFAULT_DATABASE", "default")
