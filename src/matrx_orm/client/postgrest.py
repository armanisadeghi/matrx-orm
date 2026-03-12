"""PostgREST query translator and HTTP client.

Translates ORM-style filter/order/limit/select operations into PostgREST
query parameters and executes them over HTTP. This is the core engine that
makes ``SupabaseManager`` work.

PostgREST filter syntax reference:
    eq, neq, gt, gte, lt, lte, like, ilike, in, is, not, or, and

This module does NOT use asyncpg or any direct database connection.
All data access goes through the Supabase REST API, which enforces RLS.
"""

from __future__ import annotations

import json
from typing import Any
from urllib.parse import quote

from matrx_orm.client.supabase_config import SupabaseClientConfig


# Maps ORM lookup operators to PostgREST operators
_ORM_TO_POSTGREST: dict[str, str] = {
    "eq": "eq",
    "ne": "neq",
    "gt": "gt",
    "gte": "gte",
    "lt": "lt",
    "lte": "lte",
    "in": "in",
    "contains": "like",
    "icontains": "ilike",
    "startswith": "like",
    "endswith": "like",
    "isnull": "is",
    # JSONB
    "json_contains": "cs",
    "json_contained_by": "cd",
}


class PostgRESTClient:
    """Low-level HTTP client for the Supabase PostgREST API.

    Handles authentication headers, request construction, error handling,
    and retries. Used internally by ``SupabaseManager``.
    """

    def __init__(self, config: SupabaseClientConfig) -> None:
        self._config = config

    def _headers(self, access_token: str, *, prefer: str = "") -> dict[str, str]:
        """Build request headers with auth token."""
        h = dict(self._config.default_headers)
        h["Authorization"] = f"Bearer {access_token}"
        if prefer:
            h["Prefer"] = prefer
        return h

    # ── CRUD Operations ────────────────────────────────────────────────

    async def select(
        self,
        table: str,
        access_token: str,
        *,
        columns: str = "*",
        filters: dict[str, Any] | None = None,
        order: list[str] | None = None,
        limit: int | None = None,
        offset: int | None = None,
        count: str | None = None,
        single: bool = False,
    ) -> list[dict[str, Any]] | dict[str, Any] | int:
        """Execute a SELECT query via PostgREST.

        Parameters
        ----------
        table : str
            Table name.
        access_token : str
            The user's JWT from Supabase Auth.
        columns : str
            Comma-separated column names, or ``"*"`` for all.
        filters : dict
            ORM-style filters (e.g. ``{"status": "active", "age__gte": 18}``).
        order : list[str]
            Order-by columns. Prefix with ``"-"`` for DESC.
        limit : int
            Maximum rows to return.
        offset : int
            Number of rows to skip.
        count : str
            If ``"exact"``, returns the count instead of rows.
        single : bool
            If True, expect exactly one row (PostgREST returns object, not array).

        Returns
        -------
        list[dict] | dict | int
            Query results.
        """
        import aiohttp

        url = f"{self._config.rest_url}/{table}"
        params = self._build_query_params(
            columns=columns,
            filters=filters,
            order=order,
            limit=limit,
            offset=offset,
        )

        prefer_parts: list[str] = []
        if count:
            prefer_parts.append(f"count={count}")
        if single:
            params["limit"] = "1"
            headers = self._headers(
                access_token,
                prefer=", ".join(prefer_parts) if prefer_parts else "",
            )
            headers["Accept"] = "application/vnd.pgrst.object+json"
        else:
            headers = self._headers(
                access_token,
                prefer=", ".join(prefer_parts) if prefer_parts else "",
            )

        data = await self._request("GET", url, headers=headers, params=params)

        if count == "exact" and isinstance(data, dict) and "_count" in data:
            return data["_count"]

        return data

    async def insert(
        self,
        table: str,
        access_token: str,
        data: dict[str, Any] | list[dict[str, Any]],
        *,
        on_conflict: str = "",
        upsert: bool = False,
        returning: str = "representation",
    ) -> dict[str, Any] | list[dict[str, Any]]:
        """INSERT one or more rows.

        Parameters
        ----------
        table : str
            Table name.
        access_token : str
            The user's JWT.
        data : dict | list[dict]
            Row data to insert.
        on_conflict : str
            Comma-separated conflict columns (for upsert).
        upsert : bool
            If True, use UPSERT (requires ``on_conflict``).
        returning : str
            ``"representation"`` to return the inserted row(s),
            ``"minimal"`` to return nothing.
        """
        url = f"{self._config.rest_url}/{table}"

        prefer_parts = [f"return={returning}"]
        if upsert:
            prefer_parts.append("resolution=merge-duplicates")

        headers = self._headers(access_token, prefer=", ".join(prefer_parts))

        params = {}
        if on_conflict:
            params["on_conflict"] = on_conflict

        result = await self._request(
            "POST", url, headers=headers, json_body=data, params=params
        )

        if isinstance(data, list):
            return result if isinstance(result, list) else [result]
        return result[0] if isinstance(result, list) and len(result) == 1 else result

    async def update(
        self,
        table: str,
        access_token: str,
        data: dict[str, Any],
        *,
        filters: dict[str, Any] | None = None,
        returning: str = "representation",
    ) -> list[dict[str, Any]]:
        """UPDATE rows matching filters.

        Parameters
        ----------
        table : str
            Table name.
        access_token : str
            The user's JWT.
        data : dict
            Column=value pairs to update.
        filters : dict
            ORM-style filters to identify which rows to update.
        returning : str
            ``"representation"`` or ``"minimal"``.
        """
        url = f"{self._config.rest_url}/{table}"
        params = self._build_query_params(filters=filters)
        headers = self._headers(
            access_token, prefer=f"return={returning}"
        )

        result = await self._request(
            "PATCH", url, headers=headers, json_body=data, params=params
        )
        return result if isinstance(result, list) else [result] if result else []

    async def delete(
        self,
        table: str,
        access_token: str,
        *,
        filters: dict[str, Any] | None = None,
        returning: str = "representation",
    ) -> list[dict[str, Any]]:
        """DELETE rows matching filters.

        Parameters
        ----------
        table : str
            Table name.
        access_token : str
            The user's JWT.
        filters : dict
            ORM-style filters. **Required** — PostgREST rejects unfiltered deletes.
        """
        if not filters:
            raise ValueError(
                "DELETE requires at least one filter to prevent accidental "
                "deletion of all rows. Use explicit filters."
            )

        url = f"{self._config.rest_url}/{table}"
        params = self._build_query_params(filters=filters)
        headers = self._headers(
            access_token, prefer=f"return={returning}"
        )

        result = await self._request(
            "DELETE", url, headers=headers, params=params
        )
        return result if isinstance(result, list) else [result] if result else []

    async def rpc(
        self,
        function_name: str,
        access_token: str,
        params: dict[str, Any] | None = None,
    ) -> Any:
        """Call a PostgreSQL function via PostgREST RPC.

        Parameters
        ----------
        function_name : str
            The function name (must be in the configured schema).
        access_token : str
            The user's JWT.
        params : dict
            Function arguments.
        """
        url = f"{self._config.rest_url}/rpc/{function_name}"
        headers = self._headers(access_token)
        return await self._request(
            "POST", url, headers=headers, json_body=params or {}
        )

    # ── Query parameter builder ────────────────────────────────────────

    def _build_query_params(
        self,
        *,
        columns: str = "*",
        filters: dict[str, Any] | None = None,
        order: list[str] | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> dict[str, str]:
        """Convert ORM-style query args to PostgREST query parameters."""
        params: dict[str, str] = {}

        if columns != "*":
            params["select"] = columns

        if filters:
            for key, value in filters.items():
                field_name, operator = self._parse_filter_key(key)
                pg_filter = self._build_postgrest_filter(
                    field_name, operator, value
                )
                if pg_filter:
                    col, op_val = pg_filter
                    params[col] = op_val

        if order:
            order_parts = []
            for term in order:
                if term.startswith("-"):
                    order_parts.append(f"{term[1:]}.desc")
                else:
                    order_parts.append(f"{term}.asc")
            params["order"] = ",".join(order_parts)

        if limit is not None:
            params["limit"] = str(limit)

        if offset is not None:
            params["offset"] = str(offset)

        return params

    @staticmethod
    def _parse_filter_key(key: str) -> tuple[str, str]:
        """Parse ``field__operator`` into ``(field, operator)``."""
        _OPERATORS = {
            "eq", "ne", "gt", "gte", "lt", "lte", "in",
            "contains", "icontains", "startswith", "endswith",
            "isnull", "json_contains", "json_contained_by",
            "json_has_key", "json_has_any", "json_has_all",
        }
        if "__" in key:
            parts = key.rsplit("__", 1)
            if parts[1] in _OPERATORS:
                return parts[0], parts[1]
        return key, "eq"

    @staticmethod
    def _build_postgrest_filter(
        field: str, operator: str, value: Any
    ) -> tuple[str, str] | None:
        """Convert a single filter to PostgREST format.

        Returns ``(column_name, "operator.value")`` or None if unsupported.
        """
        if operator == "eq":
            return field, f"eq.{_format_value(value)}"
        if operator == "ne":
            return field, f"neq.{_format_value(value)}"
        if operator == "gt":
            return field, f"gt.{_format_value(value)}"
        if operator == "gte":
            return field, f"gte.{_format_value(value)}"
        if operator == "lt":
            return field, f"lt.{_format_value(value)}"
        if operator == "lte":
            return field, f"lte.{_format_value(value)}"
        if operator == "in":
            items = ",".join(_format_value(v) for v in value)
            return field, f"in.({items})"
        if operator == "contains":
            return field, f"like.*{value}*"
        if operator == "icontains":
            return field, f"ilike.*{value}*"
        if operator == "startswith":
            return field, f"like.{value}*"
        if operator == "endswith":
            return field, f"like.*{value}"
        if operator == "isnull":
            return field, "is.null" if value else "not.is.null"
        if operator == "json_contains":
            return field, f"cs.{json.dumps(value)}"
        if operator == "json_contained_by":
            return field, f"cd.{json.dumps(value)}"
        if operator == "json_has_key":
            return field, f"cs.{json.dumps({value: None})}"
        return None


def _format_value(value: Any) -> str:
    """Format a Python value for PostgREST query parameters."""
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, str):
        return value
    return str(value)


class PostgRESTError(Exception):
    """Raised when a PostgREST request fails."""

    def __init__(
        self,
        message: str,
        status: int = 0,
        code: str = "",
        details: str = "",
        hint: str = "",
    ) -> None:
        self.message = message
        self.status = status
        self.code = code
        self.details = details
        self.hint = hint
        super().__init__(message)

    def __str__(self) -> str:
        parts = [self.message]
        if self.code:
            parts.append(f"Code: {self.code}")
        if self.details:
            parts.append(f"Details: {self.details}")
        if self.hint:
            parts.append(f"Hint: {self.hint}")
        return " | ".join(parts)


# ── HTTP request execution ─────────────────────────────────────────────

async def _make_request(
    method: str,
    url: str,
    *,
    headers: dict[str, str],
    params: dict[str, str] | None = None,
    json_body: Any = None,
    timeout: float = 30.0,
    max_retries: int = 3,
) -> Any:
    """Execute an HTTP request with retries on transient failures."""
    import asyncio
    import aiohttp

    last_error: Exception | None = None

    for attempt in range(max_retries):
        try:
            async with aiohttp.ClientSession() as session:
                kwargs: dict[str, Any] = {
                    "headers": headers,
                    "timeout": aiohttp.ClientTimeout(total=timeout),
                }
                if params:
                    kwargs["params"] = params
                if json_body is not None:
                    kwargs["json"] = json_body

                async with session.request(method, url, **kwargs) as resp:
                    text = await resp.text()

                    if resp.status >= 400:
                        error_data = {}
                        try:
                            error_data = json.loads(text)
                        except json.JSONDecodeError:
                            pass

                        error = PostgRESTError(
                            message=error_data.get("message", text),
                            status=resp.status,
                            code=error_data.get("code", ""),
                            details=error_data.get("details", ""),
                            hint=error_data.get("hint", ""),
                        )

                        # Don't retry client errors (4xx)
                        if 400 <= resp.status < 500:
                            raise error
                        # Retry server errors (5xx)
                        last_error = error
                    else:
                        if not text:
                            return []

                        # Check for count in content-range header
                        content_range = resp.headers.get("Content-Range", "")
                        if content_range and "/" in content_range:
                            try:
                                total = int(content_range.split("/")[1])
                                result = json.loads(text)
                                if isinstance(result, list):
                                    return {"_count": total, "_data": result}
                            except (ValueError, IndexError):
                                pass

                        return json.loads(text)

        except aiohttp.ClientError as exc:
            last_error = exc

        # Exponential backoff
        if attempt < max_retries - 1:
            await asyncio.sleep(2 ** attempt)

    raise last_error or PostgRESTError("Request failed after retries")


# Attach the request method to the client
PostgRESTClient._request = staticmethod(_make_request)  # type: ignore[attr-defined]
