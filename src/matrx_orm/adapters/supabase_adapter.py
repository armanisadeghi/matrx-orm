"""Supabase adapter — asyncpg pool-backed adapter for Supabase-managed databases.

Supabase exposes a direct PostgreSQL connection endpoint alongside the PostgREST
HTTP API.  The ORM uses the **direct connection** (asyncpg over TCP) so that all
query features — raw SQL, aggregations, CTEs, pgvector, transactions, migrations —
work exactly as they do with plain PostgreSQL.

The PostgREST API (and the ``SupabaseManager`` in ``client/supabase_manager.py``)
remains available for client-side, RLS-gated access patterns where you want the
Supabase JWT auth layer enforced by the database rather than application code.

Connection string resolution
----------------------------
The adapter builds the connection string from the project's
``DatabaseProjectConfig`` fields, preferring ``supabase_service_key`` as the
password when present (required for server-side operations).  If
``supabase_service_key`` is empty it falls back to the standard ``password``
field, which lets users point the config at Supabase's pooler with a role
password instead.

The Supabase session pooler endpoint is ``aws-0-<region>.pooler.supabase.com:5432``.
The transaction pooler is the same host on port ``6543``.  Pass
``pool_mode="transaction"`` in the config when using the transaction pooler.

Usage
-----
Register the adapter explicitly::

    from matrx_orm.adapters import AdapterRegistry
    from matrx_orm.adapters.supabase_adapter import SupabaseAdapter

    AdapterRegistry.register("my_project", SupabaseAdapter("my_project"))

Or just set ``adapter_type = "supabase"`` in the ``DatabaseProjectConfig`` and
``AdapterRegistry.get()`` will auto-create it::

    config = DatabaseProjectConfig(
        name="my_project",
        adapter_type="supabase",
        supabase_url="https://abc123.supabase.co",
        supabase_service_key="eyJ...",
        host="aws-0-us-east-1.pooler.supabase.com",
        port="5432",
        database_name="postgres",
        user="postgres.abc123",
        password="",           # left empty — supabase_service_key is used
        alias="my_project",
    )
"""
from __future__ import annotations

from contextlib import asynccontextmanager
from typing import Any, AsyncIterator

from matrx_orm.adapters.base_adapter import BaseAdapter


class SupabaseAdapter(BaseAdapter):
    """asyncpg pool-backed adapter for Supabase direct PostgreSQL connections.

    Functionally equivalent to ``AsyncPostgreSQLAdapter`` — both delegate to
    ``AsyncDatabaseManager``.  The distinction is that this class reads
    ``supabase_service_key`` as the password override and logs a Supabase-
    specific message during connection setup, making it easier to audit which
    projects are using Supabase vs plain PostgreSQL.

    Parameters
    ----------
    config_name:
        The database project name registered in ``DatabaseRegistry``.
    """

    def __init__(self, config_name: str) -> None:
        self._config_name = config_name
        self._patch_config_if_needed()

    def _patch_config_if_needed(self) -> None:
        """If supabase_service_key is set but password is empty, copy it over.

        ``AsyncDatabaseManager`` reads the config dict key ``"password"`` when
        creating the pool.  When callers supply ``supabase_service_key`` instead
        of ``password``, we transparently copy it so the pool creation works.
        """
        try:
            from matrx_orm.core.config import registry as _db_registry
            config = _db_registry._configs.get(self._config_name)
            if config is None:
                return
            if config.supabase_service_key and not config.password:
                object.__setattr__(config, "password", config.supabase_service_key)
        except Exception:
            pass

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
        """Yield a raw asyncpg pool connection for transaction use."""
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
        """Close the connection pool for this Supabase project."""
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
        return f"SupabaseAdapter(config_name={self._config_name!r})"
