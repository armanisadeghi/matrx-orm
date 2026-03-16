"""Abstract base class that every database adapter must implement.

All adapters are scoped to a single ``config_name`` (database project).
The interface mirrors ``AsyncDatabaseManager`` but removes the ``config_name``
argument from every method — the adapter already knows which database it
represents.

The optional ``execute_query_dict`` hook lets adapters that cannot run raw SQL
(e.g. a PostgREST adapter) intercept the pre-compiled query dict.
``QueryExecutor`` calls ``execute_query_dict`` first; if an adapter returns
``NotImplemented`` the executor falls through to the normal ``execute_query``
path with the compiled SQL.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from contextlib import asynccontextmanager
from typing import Any, AsyncIterator


class BaseAdapter(ABC):
    """Per-database-project adapter interface."""

    # ------------------------------------------------------------------
    # Core execution methods
    # ------------------------------------------------------------------

    @abstractmethod
    async def execute_query(
        self,
        sql: str,
        *args: Any,
        timeout: float = 10.0,
    ) -> list[dict[str, Any]]:
        """Execute a read (SELECT) query and return rows as dicts."""

    @abstractmethod
    async def execute_write(
        self,
        sql: str,
        *args: Any,
        timeout: float = 10.0,
        max_retries: int = 2,
    ) -> list[dict[str, Any]]:
        """Execute a write (INSERT/UPDATE/DELETE) query and return rows as dicts.

        Implementations should handle retries and write-queue routing as needed.
        """

    # ------------------------------------------------------------------
    # Connection management
    # ------------------------------------------------------------------

    @abstractmethod
    @asynccontextmanager
    async def get_connection(self, timeout: float = 10.0) -> AsyncIterator[Any]:
        """Async context manager that yields a raw connection for transaction use.

        The returned object must support ``.execute(sql)`` and ``.fetch(sql, *args)``
        so that ``TransactionContext`` can issue ``BEGIN``/``COMMIT``/``ROLLBACK``.
        """
        # Required to satisfy the abstract decorator; concrete subclasses must yield.
        raise NotImplementedError
        yield  # pragma: no cover — makes this an async generator stub

    @abstractmethod
    def get_active_connection(self) -> Any | None:
        """Return the connection bound to the current transaction context, or None.

        Used by ``execute_query`` to reuse the transaction connection when one
        is active in the current async task.
        """

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    @abstractmethod
    async def close(self) -> None:
        """Release all connections and clean up resources."""

    # ------------------------------------------------------------------
    # Optional hook for non-SQL adapters
    # ------------------------------------------------------------------

    async def execute_query_dict(
        self,
        query_dict: dict[str, Any],
    ) -> list[dict[str, Any]] | type[NotImplemented]:
        """Optional hook: receive the pre-compiled query dict instead of SQL.

        Adapters that cannot execute raw SQL (e.g. PostgREST) should override
        this method and translate the query dict to their native API calls.

        Return ``NotImplemented`` (the singleton, not ``NotImplementedError``)
        to signal that the caller should fall through to ``execute_query``.

        The default implementation always returns ``NotImplemented``.
        """
        return NotImplemented

    async def execute_write_dict(
        self,
        query_dict: dict[str, Any],
    ) -> list[dict[str, Any]] | type[NotImplemented]:
        """Optional write hook — same convention as ``execute_query_dict``."""
        return NotImplemented

    # ------------------------------------------------------------------
    # Context manager support
    # ------------------------------------------------------------------

    async def __aenter__(self) -> BaseAdapter:
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        await self.close()
