"""Thin wrapper around AsyncDatabaseManager passed as the `db` parameter to migration functions."""

from __future__ import annotations

from typing import Any

from matrx_orm.core.async_db_manager import AsyncDatabaseManager


class MigrationDB:
    """Database helper object injected into migration up()/down() functions.

    Wraps ``AsyncDatabaseManager.execute_query`` with the correct config name
    and provides convenience methods for common DDL / DML patterns.
    """

    def __init__(self, config_name: str) -> None:
        self._config_name = config_name

    async def execute(self, sql: str, *args: Any, timeout: float = 30.0) -> list[dict]:
        """Execute a single SQL statement and return rows (if any)."""
        rows = await AsyncDatabaseManager.execute_query(
            self._config_name, sql, *args, timeout=timeout
        )
        return [dict(r) for r in rows] if rows else []

    async def execute_many(self, statements: list[str], timeout: float = 30.0) -> None:
        """Execute multiple SQL statements sequentially."""
        for sql in statements:
            await self.execute(sql, timeout=timeout)

    async def fetch(self, sql: str, *args: Any, timeout: float = 30.0) -> list[dict]:
        """Alias for ``execute`` – reads feel more natural with ``fetch``."""
        return await self.execute(sql, *args, timeout=timeout)

    async def fetch_one(self, sql: str, *args: Any, timeout: float = 30.0) -> dict | None:
        """Execute SQL and return the first row, or None."""
        rows = await self.execute(sql, *args, timeout=timeout)
        return rows[0] if rows else None

    async def fetch_val(self, sql: str, *args: Any, timeout: float = 30.0) -> Any:
        """Execute SQL and return the first column of the first row."""
        row = await self.fetch_one(sql, *args, timeout=timeout)
        if row is None:
            return None
        return next(iter(row.values()))
