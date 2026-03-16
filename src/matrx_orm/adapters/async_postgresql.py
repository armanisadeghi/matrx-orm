"""Pool-based asyncpg adapter for PostgreSQL (and Supabase direct connections).

This adapter wraps ``AsyncDatabaseManager`` — the existing singleton that owns
all asyncpg connection pools — scoping every call to a single ``config_name``.
It is the default adapter that ``AdapterRegistry`` instantiates when no
explicit adapter is registered for a given database project.

All the real work (pool creation, write-queue routing, exponential-backoff retry,
pgvector codec registration, event-loop lifecycle) stays in ``AsyncDatabaseManager``
so existing behaviour is 100% preserved. This class is a thin, config-scoped
delegation layer.
"""
from __future__ import annotations

from contextlib import asynccontextmanager
from typing import Any, AsyncIterator

from matrx_orm.adapters.base_adapter import BaseAdapter


class AsyncPostgreSQLAdapter(BaseAdapter):
    """asyncpg pool-backed adapter scoped to a single database project.

    Parameters
    ----------
    config_name:
        The database project name registered in ``DatabaseRegistry``.
    """

    def __init__(self, config_name: str) -> None:
        self._config_name = config_name

    # ------------------------------------------------------------------
    # Core execution
    # ------------------------------------------------------------------

    async def execute_query(
        self,
        sql: str,
        *args: Any,
        timeout: float = 10.0,
    ) -> list[dict[str, Any]]:
        from matrx_orm.core.async_db_manager import AsyncDatabaseManager
        return await AsyncDatabaseManager.execute_query(
            self._config_name, sql, *args, timeout=timeout
        )

    async def execute_write(
        self,
        sql: str,
        *args: Any,
        timeout: float = 10.0,
        max_retries: int = 2,
    ) -> list[dict[str, Any]]:
        from matrx_orm.core.async_db_manager import AsyncDatabaseManager
        return await AsyncDatabaseManager.execute_write(
            self._config_name, sql, *args, timeout=timeout, max_retries=max_retries
        )

    # ------------------------------------------------------------------
    # Connection management
    # ------------------------------------------------------------------

    @asynccontextmanager
    async def get_connection(self, timeout: float = 10.0) -> AsyncIterator[Any]:
        """Yield a raw asyncpg pool connection."""
        from matrx_orm.core.async_db_manager import AsyncDatabaseManager
        async with AsyncDatabaseManager.get_connection(self._config_name, timeout) as conn:
            yield conn

    def get_active_connection(self) -> Any | None:
        """Return the asyncpg connection bound to the current transaction, if any."""
        try:
            from matrx_orm.core.transaction import get_active_connection
            return get_active_connection()
        except ImportError:
            return None

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    async def close(self) -> None:
        """Close the connection pool for this config_name.

        After calling this, the pool will be recreated on the next request.
        """
        from matrx_orm.core.async_db_manager import AsyncDatabaseManager
        pool = AsyncDatabaseManager._pools.get(self._config_name)
        if pool is not None:
            try:
                await pool.close()
            except Exception:
                pass
            AsyncDatabaseManager._pools.pop(self._config_name, None)
            AsyncDatabaseManager._pool_loops.pop(self._config_name, None)
            AsyncDatabaseManager._locks.pop(self._config_name, None)

    # ------------------------------------------------------------------
    # Repr
    # ------------------------------------------------------------------

    def __repr__(self) -> str:
        return f"AsyncPostgreSQLAdapter(config_name={self._config_name!r})"
