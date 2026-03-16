"""PostgREST client adapter — routes all ORM queries through Supabase PostgREST.

This adapter allows the full BaseManager / QueryBuilder / QueryExecutor stack
to work transparently against a Supabase project using only the publishable
anon key + the user's JWT.  No asyncpg connection is opened; every operation
goes through the Supabase REST API, which enforces Row-Level Security
automatically.

Typical setup (called by matrx_ai.initialize(client_mode=True, ...))::

    from matrx_orm.adapters import AdapterRegistry
    from matrx_orm.adapters.postgrest_client_adapter import PostgRESTClientAdapter
    from matrx_orm.client import SupabaseClientConfig, SupabaseAuth

    config = SupabaseClientConfig(url="https://abc.supabase.co", anon_key="eyJ...")
    auth   = SupabaseAuth(config)
    AdapterRegistry.register("supabase_automation_matrix",
                              PostgRESTClientAdapter(config, auth))

After that, every ``Model.filter().all()``, ``BaseManager.load_items()``,
``create_item()``, ``update_item()``, etc. routes through PostgREST.

Limitations
-----------
- Raw SQL (``Model.raw()``, ``Model.raw_sql()``) is **not supported** — PostgREST
  does not accept arbitrary SQL.  Those methods will raise ``NotImplementedError``
  when this adapter is active.  Use ``SupabaseManager.rpc()`` for stored
  procedures instead.
- M2M junction-table writes (``Model.ensure_m2m_tables()``) are also not
  supported in client mode — schema DDL cannot be issued via PostgREST.
- Transactions (``get_connection()`` context manager) are not supported.  Each
  PostgREST request is its own implicit transaction.
- ``select_related`` (SQL JOINs) fall back to PostgREST embedded resource
  notation when possible; complex JOINs will degrade gracefully to a
  non-joined result.
"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from typing import Any, AsyncIterator

from matrx_orm.adapters.base_adapter import BaseAdapter

logger = logging.getLogger("matrx_orm.adapters.postgrest_client")


class PostgRESTClientAdapter(BaseAdapter):
    """BaseAdapter implementation that speaks to Supabase via PostgREST HTTP.

    Two construction patterns are supported:

    **Pattern 1 — with SupabaseAuth (standalone client-side use)**::

        from matrx_orm.client import SupabaseClientConfig, SupabaseAuth
        from matrx_orm.adapters.postgrest_client_adapter import PostgRESTClientAdapter

        config = SupabaseClientConfig(url="https://abc.supabase.co", anon_key="eyJ...")
        auth   = SupabaseAuth(config)
        adapter = PostgRESTClientAdapter(config=config, auth=auth)

    **Pattern 2 — with a get_jwt callable (matrx_ai client mode)**::

        adapter = PostgRESTClientAdapter(
            url="https://abc.supabase.co",
            anon_key="eyJ...",
            get_jwt=lambda: current_token,   # sync OR async callable
        )

    Parameters
    ----------
    config:
        ``SupabaseClientConfig`` **or** ``None``.  When ``None``, ``url`` and
        ``anon_key`` must be provided and a minimal config is built internally.
    auth:
        ``SupabaseAuth`` instance, **or** ``None`` when ``get_jwt`` is provided.
    url:
        Supabase project URL.  Only used when ``config`` is ``None``.
    anon_key:
        Supabase publishable anon key.  Only used when ``config`` is ``None``.
    get_jwt:
        Sync or async callable (no arguments) that returns the current user's
        JWT string, or ``None`` / empty string when unauthenticated.  When
        provided, ``auth`` is ignored for token resolution.  Falls back to
        ``anon_key`` when the callable returns ``None`` or raises.
    """

    def __init__(
        self,
        config: Any = None,
        auth: Any = None,
        *,
        url: str = "",
        anon_key: str = "",
        get_jwt: Any = None,
    ) -> None:
        from matrx_orm.client.postgrest import PostgRESTClient
        from matrx_orm.client.supabase_config import SupabaseClientConfig

        if config is None:
            if not url or not anon_key:
                raise ValueError(
                    "Either a SupabaseClientConfig must be passed as 'config', "
                    "or 'url' and 'anon_key' must both be provided."
                )
            config = SupabaseClientConfig(url=url, anon_key=anon_key)

        self._config = config
        self._auth = auth
        self._get_jwt = get_jwt  # sync or async callable, or None
        self._client = PostgRESTClient(config)

    # ------------------------------------------------------------------
    # Token helper
    # ------------------------------------------------------------------

    async def _token(self) -> str:
        """Return a valid JWT.

        Resolution order:
        1. ``get_jwt`` callable if provided (sync or async).
        2. ``SupabaseAuth.ensure_valid_session()`` if auth provided.
        3. Anon key fallback (works for public / RLS-unrestricted tables).
        """
        import asyncio

        if self._get_jwt is not None:
            try:
                result = self._get_jwt()
                if asyncio.iscoroutine(result):
                    result = await result
                if result:
                    return result
            except Exception:
                pass

        if self._auth is not None:
            try:
                session = await self._auth.ensure_valid_session()
                if session and session.access_token:
                    return session.access_token
            except Exception:
                pass

        return self._config.anon_key

    # ------------------------------------------------------------------
    # execute_query_dict — primary SELECT hook for QueryExecutor
    # ------------------------------------------------------------------

    async def execute_query_dict(
        self,
        query_dict: dict[str, Any],
    ) -> list[dict[str, Any]] | type[NotImplemented]:
        """Translate a QueryBuilder query dict to a PostgREST SELECT call.

        This is called by ``QueryExecutor._execute()`` **before** the SQL path.
        Returning a list (even empty) signals that PostgREST handled the query
        and the executor should skip SQL entirely.
        """
        table: str = query_dict.get("table", "")
        if not table:
            return NotImplemented

        token = await self._token()
        filters = self._translate_filters(query_dict.get("filters", {}))
        order = self._translate_order(query_dict.get("order_by", []))
        limit: int | None = query_dict.get("limit")
        offset: int | None = query_dict.get("offset")
        select_cols: list[str] | None = query_dict.get("select")
        columns = ", ".join(select_cols) if select_cols else "*"

        logger.debug(
            "[PostgRESTClientAdapter] SELECT %s filters=%s limit=%s",
            table, filters, limit,
        )

        try:
            result = await self._client.select(
                table,
                token,
                columns=columns,
                filters=filters if filters else None,
                order=order if order else None,
                limit=limit,
                offset=offset,
            )
            if isinstance(result, list):
                return result
            # single-object response (shouldn't happen on list queries)
            return [result] if result else []
        except Exception as exc:
            logger.error(
                "[PostgRESTClientAdapter] SELECT failed for %s: %s", table, exc
            )
            raise

    # ------------------------------------------------------------------
    # execute_write_dict — write hook for QueryExecutor DML
    # ------------------------------------------------------------------

    async def execute_write_dict(
        self,
        query_dict: dict[str, Any],
    ) -> list[dict[str, Any]] | type[NotImplemented]:
        """Translate a write query dict to the appropriate PostgREST call.

        Called by ``QueryExecutor`` for INSERT / UPDATE / DELETE / UPSERT
        before it falls through to the SQL path.

        query_dict keys used:
        - ``operation``: "insert" | "update" | "delete" | "upsert" | "bulk_insert"
          | "bulk_upsert"
        - ``table``: table name
        - ``data``: dict (single row) or list of dicts (bulk)
        - ``filters``: ORM filter dict (for UPDATE / DELETE)
        - ``conflict_fields``: list[str] (for UPSERT)
        - ``update_fields``: list[str] (for UPSERT, optional)
        """
        operation: str = query_dict.get("operation", "")
        table: str = query_dict.get("table", "")
        if not table or not operation:
            return NotImplemented

        token = await self._token()
        filters = self._translate_filters(query_dict.get("filters", {}))
        data: dict | list = query_dict.get("data", {})

        logger.debug(
            "[PostgRESTClientAdapter] %s %s", operation.upper(), table
        )

        try:
            if operation == "insert":
                result = await self._client.insert(table, token, data)
                return [result] if isinstance(result, dict) else (result or [])

            if operation == "bulk_insert":
                result = await self._client.insert(table, token, data)
                return result if isinstance(result, list) else ([result] if result else [])

            if operation == "upsert":
                conflict_fields: list[str] = query_dict.get("conflict_fields", [])
                on_conflict = ",".join(conflict_fields) if conflict_fields else "id"
                result = await self._client.insert(
                    table, token, data,
                    on_conflict=on_conflict,
                    upsert=True,
                )
                return [result] if isinstance(result, dict) else (result or [])

            if operation == "bulk_upsert":
                conflict_fields = query_dict.get("conflict_fields", [])
                on_conflict = ",".join(conflict_fields) if conflict_fields else "id"
                result = await self._client.insert(
                    table, token, data,
                    on_conflict=on_conflict,
                    upsert=True,
                )
                return result if isinstance(result, list) else ([result] if result else [])

            if operation == "update":
                result = await self._client.update(
                    table, token, data,
                    filters=filters if filters else None,
                )
                return result if isinstance(result, list) else ([result] if result else [])

            if operation == "delete":
                if not filters:
                    raise ValueError(
                        "DELETE via PostgREST requires at least one filter. "
                        "Use explicit filter kwargs to identify which rows to delete."
                    )
                result = await self._client.delete(
                    table, token,
                    filters=filters,
                )
                return result if isinstance(result, list) else ([result] if result else [])

        except Exception as exc:
            logger.error(
                "[PostgRESTClientAdapter] %s failed for %s: %s",
                operation.upper(), table, exc,
            )
            raise

        return NotImplemented

    # ------------------------------------------------------------------
    # execute_query / execute_write — SQL fallbacks (not supported)
    # ------------------------------------------------------------------

    async def execute_query(
        self,
        sql: str,
        *args: Any,
        timeout: float = 10.0,
    ) -> list[dict[str, Any]]:
        """Raw SQL is not supported via PostgREST.

        This is called only when ``execute_query_dict`` returns ``NotImplemented``
        (which shouldn't happen for normal ORM queries).  If you reach this
        method, the query uses a feature that PostgREST cannot represent —
        complex CTEs, raw aggregations, pgvector similarity, etc.

        Consider using ``SupabaseManager.rpc()`` with a PostgreSQL function
        for these cases, or switch to a direct asyncpg adapter for server-side
        deployments.
        """
        raise NotImplementedError(
            "Raw SQL queries are not supported in PostgREST (client) mode.\n"
            "This query requires a direct database connection (asyncpg).\n"
            f"SQL attempted: {sql[:200]!r}"
        )

    async def execute_write(
        self,
        sql: str,
        *args: Any,
        timeout: float = 10.0,
        max_retries: int = 2,
    ) -> list[dict[str, Any]]:
        """Raw SQL writes are not supported via PostgREST."""
        raise NotImplementedError(
            "Raw SQL writes are not supported in PostgREST (client) mode.\n"
            "This write requires a direct database connection (asyncpg).\n"
            f"SQL attempted: {sql[:200]!r}"
        )

    # ------------------------------------------------------------------
    # Connection management — not supported in client mode
    # ------------------------------------------------------------------

    @asynccontextmanager
    async def get_connection(self, timeout: float = 10.0) -> AsyncIterator[Any]:
        """Transactions are not supported via PostgREST."""
        raise NotImplementedError(
            "Direct connections and transactions are not available in PostgREST "
            "(client) mode.  Each PostgREST request is its own implicit transaction."
        )
        yield  # pragma: no cover

    def get_active_connection(self) -> Any | None:
        """No persistent connection in PostgREST mode."""
        return None

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    async def close(self) -> None:
        """Nothing to close — PostgREST uses stateless HTTP."""
        pass

    # ------------------------------------------------------------------
    # Filter / order translation helpers
    # ------------------------------------------------------------------

    def _translate_filters(
        self, filters: dict[str, Any] | None
    ) -> dict[str, Any]:
        """Pass ORM filter dicts straight through.

        ``PostgRESTClient._build_query_params()`` already understands the ORM
        ``field__operator`` convention, so no translation is needed here.
        The executor hands us the same filter dict the query builder built.
        """
        if not filters:
            return {}
        cleaned: dict[str, Any] = {}
        for key, value in filters.items():
            # Skip None values — they mean "no filter"
            if value is not None:
                cleaned[key] = value
        return cleaned

    def _translate_order(self, order_by: list[str] | None) -> list[str] | None:
        """Pass order_by list straight through — same format as PostgRESTClient."""
        return order_by if order_by else None

    # ------------------------------------------------------------------
    # Repr
    # ------------------------------------------------------------------

    def __repr__(self) -> str:
        return (
            f"PostgRESTClientAdapter("
            f"url={getattr(self._config, 'url', '?')!r}, "
            f"auth={'get_jwt' if self._get_jwt else ('SupabaseAuth' if self._auth else 'anon_key')})"
        )
