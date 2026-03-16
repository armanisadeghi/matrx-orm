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

Adapter decoupling
------------------
The ``TransactionContext`` no longer imports asyncpg directly.  Instead it
obtains its connection through ``AdapterRegistry.get(database).get_connection()``,
which returns a raw asyncpg pool connection for the default adapter but can
return any connection object for custom adapters, as long as that object
supports ``.execute(sql)`` and ``.fetch(sql, *args)``.

The ``_active_connection`` ContextVar is typed as ``Any`` so the rest of the
ORM can hold a reference to the active connection without depending on asyncpg.
``AsyncDatabaseManager.execute_query`` reads ``get_active_connection()`` and
reuses the connection when present — this behaviour is unchanged.
"""
from __future__ import annotations

import os
import uuid
from contextvars import ContextVar, Token
from typing import Any

from matrx_orm.exceptions import DatabaseError

# ContextVar holding the active connection (if any) for the current task tree.
_active_connection: ContextVar[Any | None] = ContextVar(
    "_active_connection", default=None
)
# ContextVar tracking savepoint depth (0 = top-level transaction)
_savepoint_depth: ContextVar[int] = ContextVar("_savepoint_depth", default=0)


def get_active_connection() -> Any | None:
    """Return the connection bound to the current transaction context, or None."""
    return _active_connection.get()


class TransactionContext:
    """Async context manager returned by ``transaction()``.

    On first entry (no active connection): acquires a connection via the
    adapter's ``get_connection()`` context manager, executes ``BEGIN``,
    and stores the connection in the ContextVar.

    On nested entry (active connection exists): creates a SAVEPOINT instead.
    """

    def __init__(self, database: str) -> None:
        self.database = database
        self._conn_token: Token[Any | None] | None = None
        self._depth_token: Token[int] | None = None
        self._is_savepoint: bool = False
        self._savepoint_name: str = ""
        self._raw_conn: Any | None = None
        self._adapter_cm: Any | None = None  # the async context manager from get_connection()

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
            from matrx_orm.adapters import AdapterRegistry
            adapter = AdapterRegistry.get(self.database)
            self._adapter_cm = adapter.get_connection()
            conn = await self._adapter_cm.__aenter__()
            self._raw_conn = conn
            try:
                await conn.execute("BEGIN")
            except Exception as e:
                await self._adapter_cm.__aexit__(type(e), e, e.__traceback__)
                self._raw_conn = None
                self._adapter_cm = None
                raise DatabaseError(
                    message=f"Failed to begin transaction: {e}",
                    details={"database": self.database},
                ) from e
            self._conn_token = _active_connection.set(conn)
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
            if self._depth_token is not None:
                _savepoint_depth.reset(self._depth_token)
            if exc_type is None:
                if conn is not None:
                    await conn.execute(f"RELEASE SAVEPOINT {self._savepoint_name}")
            else:
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

            conn_to_use = self._raw_conn
            if conn_to_use is None:
                return False

            try:
                if exc_type is None:
                    await conn_to_use.execute("COMMIT")
                else:
                    await conn_to_use.execute("ROLLBACK")
            finally:
                if self._adapter_cm is not None:
                    await self._adapter_cm.__aexit__(exc_type, exc_val, exc_tb)
                    self._adapter_cm = None
                    self._raw_conn = None

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
        from matrx_orm.core.config import get_all_database_project_names
        names = get_all_database_project_names()
        if names:
            return names[0]
    except Exception:
        pass
    return os.environ.get("MATRX_DEFAULT_DATABASE", "default")
