"""High-level ORM-like manager for client-side Supabase access.

Provides a familiar CRUD API (like BaseManager) but executes all queries
through the Supabase PostgREST API instead of direct asyncpg connections.
RLS policies enforce per-user data access automatically.

Usage::

    from matrx_orm.client import SupabaseClientConfig, SupabaseAuth, SupabaseManager

    config = SupabaseClientConfig(
        url="https://abc123.supabase.co",
        anon_key="eyJ...",
    )
    auth = SupabaseAuth(config)
    session = await auth.sign_in_with_password("user@example.com", "pass")

    # Create a manager for a table
    users = SupabaseManager("users", config=config, auth=auth)

    # CRUD — same patterns as BaseManager
    user = await users.create_item(username="alice", email="alice@example.com")
    all_users = await users.load_items(status="active")
    updated = await users.update_item(user["id"], username="bob")
    await users.delete_item(user["id"])
"""

from __future__ import annotations

from typing import Any

from matrx_orm.client.postgrest import PostgRESTClient, PostgRESTError
from matrx_orm.client.supabase_auth import SupabaseAuth, SupabaseAuthError
from matrx_orm.client.supabase_config import SupabaseClientConfig


class SupabaseManager:
    """Client-side table manager using Supabase PostgREST.

    Parameters
    ----------
    table : str
        The database table name.
    config : SupabaseClientConfig
        Supabase project configuration.
    auth : SupabaseAuth
        Auth client (must be signed in before making queries).
    pk : str
        Primary key column name. Default ``"id"``.
    columns : str
        Default columns to select. ``"*"`` for all.
    """

    def __init__(
        self,
        table: str,
        *,
        config: SupabaseClientConfig,
        auth: SupabaseAuth,
        pk: str = "id",
        columns: str = "*",
    ) -> None:
        self._table = table
        self._config = config
        self._auth = auth
        self._pk = pk
        self._columns = columns
        self._client = PostgRESTClient(config)

    async def _token(self) -> str:
        """Get a valid access token, refreshing if expired."""
        session = await self._auth.ensure_valid_session()
        return session.access_token

    # ── Single-item CRUD ───────────────────────────────────────────────

    async def load_item(self, item_id: Any = None, **filters: Any) -> dict[str, Any]:
        """Load a single item by ID or filters. Raises if not found."""
        if item_id is not None:
            filters[self._pk] = item_id

        result = await self._client.select(
            self._table,
            await self._token(),
            columns=self._columns,
            filters=filters,
            limit=2,
        )

        if isinstance(result, list):
            if len(result) == 0:
                raise PostgRESTError(
                    f"No {self._table} found matching: {filters}",
                    status=404,
                )
            if len(result) > 1:
                raise PostgRESTError(
                    f"Multiple {self._table} found ({len(result)}) when "
                    f"expecting one. Filters: {filters}",
                    status=409,
                )
            return result[0]
        return result

    async def load_item_or_none(
        self, item_id: Any = None, **filters: Any
    ) -> dict[str, Any] | None:
        """Load a single item, returning None if not found."""
        try:
            return await self.load_item(item_id, **filters)
        except PostgRESTError as exc:
            if exc.status == 404:
                return None
            raise

    async def create_item(self, **data: Any) -> dict[str, Any]:
        """Insert a single row and return it."""
        return await self._client.insert(
            self._table, await self._token(), data
        )

    async def update_item(
        self, item_id: Any, **updates: Any
    ) -> dict[str, Any]:
        """Update a single row by primary key and return it."""
        if not updates:
            raise ValueError("No update data provided")

        results = await self._client.update(
            self._table,
            await self._token(),
            updates,
            filters={self._pk: item_id},
        )
        if not results:
            raise PostgRESTError(
                f"No {self._table} found with {self._pk}={item_id}",
                status=404,
            )
        return results[0]

    async def delete_item(self, item_id: Any) -> bool:
        """Delete a single row by primary key."""
        results = await self._client.delete(
            self._table,
            await self._token(),
            filters={self._pk: item_id},
        )
        return len(results) > 0

    async def exists(self, item_id: Any = None, **filters: Any) -> bool:
        """Check if a row exists matching the given filters."""
        if item_id is not None:
            filters[self._pk] = item_id

        result = await self._client.select(
            self._table,
            await self._token(),
            columns=self._pk,
            filters=filters,
            limit=1,
        )
        return bool(result) if isinstance(result, list) else True

    # ── Multi-item reads ───────────────────────────────────────────────

    async def load_items(
        self,
        *,
        order: list[str] | None = None,
        limit: int | None = None,
        offset: int | None = None,
        **filters: Any,
    ) -> list[dict[str, Any]]:
        """Load multiple items matching filters."""
        result = await self._client.select(
            self._table,
            await self._token(),
            columns=self._columns,
            filters=filters if filters else None,
            order=order,
            limit=limit,
            offset=offset,
        )
        return result if isinstance(result, list) else [result]

    async def load_items_by_ids(
        self, ids: list[Any]
    ) -> list[dict[str, Any]]:
        """Load multiple items by their primary keys."""
        return await self.load_items(**{f"{self._pk}__in": ids})

    async def count(self, **filters: Any) -> int:
        """Count rows matching filters."""
        result = await self._client.select(
            self._table,
            await self._token(),
            columns=self._pk,
            filters=filters if filters else None,
            count="exact",
        )
        if isinstance(result, dict) and "_count" in result:
            return result["_count"]
        if isinstance(result, int):
            return result
        return len(result) if isinstance(result, list) else 0

    async def load_first_item(
        self, order: list[str] | None = None, **filters: Any
    ) -> dict[str, Any] | None:
        """Load the first item matching filters, or None."""
        results = await self.load_items(
            order=order, limit=1, **filters
        )
        return results[0] if results else None

    # ── Bulk writes ────────────────────────────────────────────────────

    async def create_items(
        self, items: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """Insert multiple rows."""
        result = await self._client.insert(
            self._table, await self._token(), items
        )
        return result if isinstance(result, list) else [result]

    async def update_where(
        self, updates: dict[str, Any], **filters: Any
    ) -> list[dict[str, Any]]:
        """Update all rows matching filters."""
        return await self._client.update(
            self._table,
            await self._token(),
            updates,
            filters=filters,
        )

    async def delete_where(self, **filters: Any) -> int:
        """Delete all rows matching filters. Returns count deleted."""
        results = await self._client.delete(
            self._table,
            await self._token(),
            filters=filters,
        )
        return len(results)

    async def upsert_item(
        self,
        data: dict[str, Any],
        conflict_fields: list[str] | None = None,
    ) -> dict[str, Any]:
        """Insert or update a row based on conflict columns."""
        on_conflict = ",".join(conflict_fields) if conflict_fields else self._pk
        result = await self._client.insert(
            self._table,
            await self._token(),
            data,
            on_conflict=on_conflict,
            upsert=True,
        )
        return result if isinstance(result, dict) else result[0]

    async def upsert_items(
        self,
        items: list[dict[str, Any]],
        conflict_fields: list[str] | None = None,
    ) -> list[dict[str, Any]]:
        """Insert or update multiple rows."""
        on_conflict = ",".join(conflict_fields) if conflict_fields else self._pk
        result = await self._client.insert(
            self._table,
            await self._token(),
            items,
            on_conflict=on_conflict,
            upsert=True,
        )
        return result if isinstance(result, list) else [result]

    async def get_or_create(
        self, defaults: dict[str, Any] | None = None, **lookup: Any
    ) -> tuple[dict[str, Any], bool]:
        """Get an existing row or create a new one.

        Returns
        -------
        tuple[dict, bool]
            The row and a boolean indicating if it was created.
        """
        existing = await self.load_item_or_none(**lookup)
        if existing:
            return existing, False

        data = dict(lookup)
        if defaults:
            data.update(defaults)
        created = await self.create_item(**data)
        return created, True

    # ── RPC (stored procedures) ────────────────────────────────────────

    async def rpc(
        self, function_name: str, **params: Any
    ) -> Any:
        """Call a PostgreSQL function via PostgREST RPC."""
        return await self._client.rpc(
            function_name,
            await self._token(),
            params=params,
        )

    # ── Relationships (select with foreign keys) ───────────────────────

    async def load_items_with_related(
        self,
        *related: str,
        order: list[str] | None = None,
        limit: int | None = None,
        **filters: Any,
    ) -> list[dict[str, Any]]:
        """Load items with related table data embedded.

        PostgREST supports foreign key joins via the ``select`` parameter::

            select=*,author:users(id,username,email)

        Parameters
        ----------
        *related : str
            Related table references in PostgREST format.
            Examples: ``"author:users(id,username)"`` or ``"tags(*)"``
        """
        parts = [self._columns]
        for rel in related:
            parts.append(rel)
        columns = ",".join(parts)

        result = await self._client.select(
            self._table,
            await self._token(),
            columns=columns,
            filters=filters if filters else None,
            order=order,
            limit=limit,
        )
        return result if isinstance(result, list) else [result]

    # ── Dict output ────────────────────────────────────────────────────

    async def get_item_dict(
        self, item_id: Any = None, **filters: Any
    ) -> dict[str, Any] | None:
        """Load a single item as a dict, or None."""
        return await self.load_item_or_none(item_id, **filters)

    async def get_items_dict(self, **filters: Any) -> list[dict[str, Any]]:
        """Load items as a list of dicts."""
        return await self.load_items(**filters)
