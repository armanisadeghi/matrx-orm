from __future__ import annotations

import asyncio
from typing import Any, Generic, TypeVar, TYPE_CHECKING

from matrx_utils import vcprint
from ..core.async_db_manager import run_sync
from ..query.executor import QueryExecutor
from ..exceptions import (
    DoesNotExist,
    MultipleObjectsReturned,
    ORMException,
    QueryError,
    ValidationError,
)
from ..state import StateManager

if TYPE_CHECKING:
    from ..core.base import Model

ModelT = TypeVar("ModelT", bound="Model")

debug = False


class QueryBuilder(Generic[ModelT]):
    model: type[ModelT]
    database: str
    filters: list[Any]          # dict[str,Any] or Q objects
    excludes: list[dict[str, Any]]
    order_by_fields: list[str | Any]
    limit_val: int | None
    offset_val: int | None
    select_fields: list[str]
    prefetch_fields: list[str]
    joins: list[dict[str, Any]]
    group_by_fields: list[str]
    having_filters: list[dict[str, Any]]
    aggregations: list[dict[str, Any]]
    distinct_fields: list[str] | None   # None = no DISTINCT; [] = DISTINCT; [f...] = DISTINCT ON
    for_update_opts: dict[str, Any] | None
    select_related_fields: list[str]

    def __init__(self, model_cls: type[ModelT], database: str | None = None) -> None:
        self.model = model_cls
        self.database = self._set_database(model_cls)
        self.filters = []
        self.excludes = []
        self.order_by_fields = []
        self.limit_val = None
        self.offset_val = None
        self.select_fields = []
        self.prefetch_fields = []
        self.joins = []
        self.group_by_fields = []
        self.having_filters = []
        self.aggregations = []
        self.distinct_fields = None
        self.for_update_opts = None
        self.select_related_fields = []

    def _set_database(self, model_cls: type[ModelT]) -> str:
        if hasattr(model_cls, "_database") and model_cls._database:
            self.database = model_cls._database
            return self.database
        raise ValueError(f"Database not found for model {model_cls.__name__}")

    # ------------------------------------------------------------------
    # Chainable builder methods
    # ------------------------------------------------------------------

    def filter(self, *args: Any, **kwargs: Any) -> QueryBuilder[ModelT]:
        """Apply filter conditions. Accepts Q objects and/or keyword filters.

        Examples::

            .filter(status="active")
            .filter(Q(status="active") | Q(role="admin"))
            .filter(Q(a=1), b=2)          # AND composition
        """
        from ..core.expressions import Q
        for arg in args:
            if isinstance(arg, Q):
                self.filters.append(arg)
            else:
                raise TypeError(f"Positional filter argument must be a Q object, got {type(arg)}")
        if kwargs:
            self.filters.append(kwargs)
        return self

    def exclude(self, **kwargs: Any) -> QueryBuilder[ModelT]:
        """Apply SQL exclusion filters."""
        if kwargs:
            self.excludes.append(kwargs)
        return self

    def order_by(self, *fields: str | Any) -> QueryBuilder[ModelT]:
        self.order_by_fields.extend(fields)
        return self

    def limit(self, value: int) -> QueryBuilder[ModelT]:
        self.limit_val = value
        return self

    def offset(self, value: int) -> QueryBuilder[ModelT]:
        self.offset_val = value
        return self

    def select(self, *fields: str) -> QueryBuilder[ModelT]:
        self.select_fields.extend(fields)
        return self

    def prefetch_related(self, *fields: str) -> QueryBuilder[ModelT]:
        self.prefetch_fields.extend(fields)
        return self

    def select_related(self, *fields: str) -> QueryBuilder[ModelT]:
        """Eager-load FK targets via JOIN in the same query (no N+1)."""
        self.select_related_fields.extend(fields)
        return self

    def join(self, model_cls: type[Any], on: str, join_type: str = "INNER") -> QueryBuilder[ModelT]:
        self.joins.append({"model": model_cls, "on": on, "type": join_type})
        return self

    def group_by(self, *fields: str) -> QueryBuilder[ModelT]:
        self.group_by_fields.extend(fields)
        return self

    def having(self, **kwargs: Any) -> QueryBuilder[ModelT]:
        self.having_filters.append(kwargs)
        return self

    def annotate(self, **kwargs: Any) -> QueryBuilder[ModelT]:
        """Add computed columns (aggregates or functions) to the SELECT.

        Usage::

            .annotate(total=Sum("amount"), name_lower=Lower("username"))
        """
        for key, value in kwargs.items():
            self.aggregations.append({"name": key, "function": value})
        return self

    def distinct(self, *fields: str) -> QueryBuilder[ModelT]:
        """Add DISTINCT or DISTINCT ON to the query.

        No args  → ``SELECT DISTINCT ...``
        With args → ``SELECT DISTINCT ON (f1, f2) ...`` (PostgreSQL-specific)
        """
        self.distinct_fields = list(fields)
        return self

    def select_for_update(
        self,
        nowait: bool = False,
        skip_locked: bool = False,
        of: list[str] | None = None,
    ) -> QueryBuilder[ModelT]:
        """Append ``FOR UPDATE [NOWAIT | SKIP LOCKED] [OF ...]`` to the query.

        Must be used inside a transaction.
        """
        self.for_update_opts = {"nowait": nowait, "skip_locked": skip_locked, "of": of or []}
        return self

    def using(self, database: str) -> QueryBuilder[ModelT]:
        """Override the database for this query."""
        self.database = database
        return self

    def reverse(self) -> QueryBuilder[ModelT]:
        """Reverse each ordering term."""
        reversed_fields = []
        for term in self.order_by_fields:
            if isinstance(term, str):
                reversed_fields.append(term[1:] if term.startswith("-") else f"-{term}")
            else:
                reversed_fields.append(term)
        self.order_by_fields = reversed_fields
        return self

    # ------------------------------------------------------------------
    # Internal query dict construction
    # ------------------------------------------------------------------

    def _build_query(self) -> dict[str, Any]:
        """Construct the query dict passed to QueryExecutor."""
        query: dict[str, Any] = {
            "model": self.model,
            "table": self.model._meta.qualified_table_name,
            "filters": self._collect_filters(),
            "order_by": self.order_by_fields,
            "limit": self.limit_val,
            "offset": self.offset_val,
            "select": self.select_fields or ["*"],
            "prefetch": self.prefetch_fields,
            "database": self.database,
            # New keys
            "group_by": self.group_by_fields,
            "having": self._merge_having(),
            "aggregations": self.aggregations,
            "distinct": self.distinct_fields,
            "for_update": self.for_update_opts,
            "select_related": self.select_related_fields,
        }
        return query

    def _collect_filters(self) -> list[Any]:
        """Return a list of filter items: each is a dict or a Q object."""
        from ..core.expressions import Q
        result: list[Any] = []
        for f in self.filters:
            result.append(f)
        for e in self.excludes:
            # Convert excludes to negated Q objects
            result.append(~Q(**e))
        return result

    def _merge_filters_excludes(self) -> dict[str, Any]:
        """Legacy helper used by enrichment/error paths — returns a flat dict snapshot."""
        combined: dict[str, Any] = {}
        for f in self.filters:
            if isinstance(f, dict):
                combined.update(f)
        for e in self.excludes:
            for k, v in e.items():
                combined[f"exclude__{k}"] = v
        return combined

    def _merge_having(self) -> dict[str, Any]:
        combined: dict[str, Any] = {}
        for h in self.having_filters:
            combined.update(h)
        return combined

    def _get_executor(self) -> QueryExecutor:
        return QueryExecutor(self._build_query())

    # ------------------------------------------------------------------
    # Terminal async methods
    # ------------------------------------------------------------------

    async def all(self) -> list[ModelT]:
        """Fetch all matching records."""
        try:
            executor = self._get_executor()
            results = await executor.all()
            await StateManager.cache_bulk(self.model, results)
            if debug:
                vcprint(
                    f"[BUILDER] all() cached {len(results)} records for {self.model.__name__}",
                    color="bright_gold",
                )
            return results
        except ORMException as e:
            e.enrich(model=self.model, operation="all", filters=self._merge_filters_excludes())
            raise
        except Exception as e:
            raise QueryError(model=self.model, details={"operation": "all", "error": str(e)})

    async def first(self) -> ModelT | None:
        """Get the first matching record."""
        try:
            return await self._get_executor().first()
        except ORMException as e:
            e.enrich(model=self.model, operation="first", filters=self._merge_filters_excludes())
            raise

    async def last(self) -> ModelT | None:
        """Order by primary key descending and fetch the first record."""
        pk_name = getattr(self.model._meta, "pk_name", "id")
        self.order_by(f"-{pk_name}")
        return await self.first()

    async def get(self) -> ModelT:
        """Retrieve exactly one matching record; raises if 0 or >1 found."""
        filters = self._merge_filters_excludes()
        try:
            executor = self._get_executor()
            results = await executor.all()
            if not results:
                raise DoesNotExist(model=self.model, filters=filters)
            if len(results) > 1:
                raise MultipleObjectsReturned(model=self.model, count=len(results), filters=filters)
            return results[0]
        except ORMException as e:
            e.enrich(model=self.model, operation="get", filters=filters)
            raise

    async def get_or_none(self) -> ModelT | None:
        """Return the matching record or None if not found."""
        try:
            return await self.get()
        except DoesNotExist:
            return None
        except Exception as e:
            vcprint(f"Error in QueryBuilder.get_or_none: {str(e)}", color="red")
            return None

    async def update(self, **kwargs: Any) -> dict[str, Any]:
        """Update matching records."""
        try:
            if not kwargs:
                raise ValidationError(model=self.model, reason="No update data provided")
            return await self._get_executor().update(**kwargs)
        except ValidationError:
            raise
        except ORMException as e:
            e.enrich(model=self.model, operation="update", filters=self._merge_filters_excludes())
            raise

    async def delete(self) -> int:
        """Delete matching records."""
        try:
            return await self._get_executor().delete()
        except ORMException as e:
            e.enrich(model=self.model, operation="delete", filters=self._merge_filters_excludes())
            raise

    async def count(self) -> int:
        """Count matching records."""
        try:
            return await self._get_executor().count()
        except ORMException as e:
            e.enrich(model=self.model, operation="count", filters=self._merge_filters_excludes())
            raise

    async def exists(self) -> bool:
        """Check whether any matching record exists."""
        try:
            return await self._get_executor().exists()
        except ORMException as e:
            e.enrich(model=self.model, operation="exists", filters=self._merge_filters_excludes())
            raise

    async def aggregate(self, **kwargs: Any) -> dict[str, Any]:
        """Run aggregation functions and return a single result dict.

        Usage::

            result = await Order.filter(status="paid").aggregate(
                total=Sum("amount"), avg=Avg("amount"), count=Count("id")
            )
        """
        if kwargs:
            for key, value in kwargs.items():
                self.aggregations.append({"name": key, "function": value})
        try:
            return await self._get_executor().aggregate()
        except ORMException as e:
            e.enrich(model=self.model, operation="aggregate", filters=self._merge_filters_excludes())
            raise

    async def values(self, *fields: str) -> list[dict[str, Any]]:
        if fields:
            self.select_fields = list(fields)
        return await self._get_executor().values()

    async def values_list(self, *fields: str, flat: bool = False) -> list[tuple[Any, ...]] | list[Any]:
        if fields:
            self.select_fields = list(fields)
        return await self._get_executor().values_list(flat=flat)

    # ------------------------------------------------------------------
    # Synchronous wrappers
    # ------------------------------------------------------------------

    def values_sync(self, *fields: str) -> list[dict[str, Any]]:
        """Synchronous wrapper for values()."""
        try:
            asyncio.get_running_loop()
            raise RuntimeError("QueryBuilder.values_sync() called in async context. Use await .values() instead.")
        except RuntimeError as e:
            if "no running event loop" not in str(e):
                raise
        return run_sync(self.values(*fields))

    def values_list_sync(self, *fields: str, flat: bool = False) -> list[tuple[Any, ...]] | list[Any]:
        """Synchronous wrapper for values_list()."""
        try:
            asyncio.get_running_loop()
            raise RuntimeError("QueryBuilder.values_list_sync() called in async context. Use await .values_list() instead.")
        except RuntimeError as e:
            if "no running event loop" not in str(e):
                raise
        return run_sync(self.values_list(*fields, flat=flat))

    # ------------------------------------------------------------------
    # Async iteration and slicing
    # ------------------------------------------------------------------

    async def __aiter__(self) -> Any:
        executor = self._get_executor()
        async for item in executor:
            yield item

    def __getitem__(self, k: slice) -> QueryBuilder[ModelT]:
        if isinstance(k, slice):
            start = k.start or 0
            stop = k.stop if k.stop is not None else 0
            if stop > 0:
                self.limit(stop - start)
            self.offset(start)
            return self
        raise TypeError("Index access not supported, use slicing")
