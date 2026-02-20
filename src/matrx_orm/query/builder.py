from __future__ import annotations

import asyncio
from typing import Any, Generic, TypeVar, TYPE_CHECKING

from matrx_utils import vcprint
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
    filters: list[dict[str, Any]]
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

    def _set_database(self, model_cls: type[ModelT]) -> str:
        if hasattr(model_cls, '_database') and model_cls._database:
            self.database = model_cls._database
            return self.database
        
        raise ValueError(f"Database not found for model {model_cls.__name__}")


    def filter(self, **kwargs: Any) -> QueryBuilder[ModelT]:
        """Applies SQL filters before execution."""
        if kwargs:
            self.filters.append(kwargs)
        return self

    def exclude(self, **kwargs: Any) -> QueryBuilder[ModelT]:
        """Applies SQL exclusion filters before execution."""
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
        for key, value in kwargs.items():
            self.aggregations.append({"name": key, "function": value})
        return self

    def _build_query(self) -> dict[str, Any]:
        """Constructs the SQL query before execution."""
        query: dict[str, Any] = {
            "model": self.model,
            "table": self.model._meta.qualified_table_name,
            "filters": self._merge_filters_excludes(),
            "order_by": self.order_by_fields,
            "limit": self.limit_val,
            "offset": self.offset_val,
            "select": self.select_fields or ["*"],
            "prefetch": self.prefetch_fields,
            "database": self.database,
        }
        return query

    def _merge_filters_excludes(self) -> dict[str, Any]:
        """Merges filters and excludes for proper SQL conditions."""
        combined: dict[str, Any] = {}
        for f in self.filters:
            combined.update(f)
        for e in self.excludes:
            for k, v in e.items():
                combined[f"exclude__{k}"] = v
        return combined

    def _get_executor(self) -> QueryExecutor:
        """Returns the QueryExecutor to execute the query."""
        return QueryExecutor(self._build_query())

    async def all(self) -> list[ModelT]:
        """Fetches all records matching the applied filters."""
        try:
            executor = self._get_executor()
            results = await executor.all()
            await StateManager.cache_bulk(self.model, results)
            if debug:
                vcprint(
                    f"[BUILDER: QUERY_BUILDER] all method]  Cached {len(results)} records for {self.model.__name__}",
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
        """
        Retrieves exactly one object matching the criteria.
        """
        filters = self._merge_filters_excludes()
        try:
            executor = self._get_executor()
            results = await executor.all()

            if not results:
                raise DoesNotExist(model=self.model, filters=filters)

            if len(results) > 1:
                raise MultipleObjectsReturned(
                    model=self.model,
                    count=len(results),
                    filters=filters,
                )

            return results[0]
        except ORMException as e:
            e.enrich(model=self.model, operation="get", filters=filters)
            raise

    async def get_or_none(self) -> ModelT | None:
        """
        Execute the query and return None if no results found
        instead of raising DoesNotExist
        """
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
        """Check if matching records exist."""
        try:
            return await self._get_executor().exists()
        except ORMException as e:
            e.enrich(model=self.model, operation="exists", filters=self._merge_filters_excludes())
            raise

    async def values(self, *fields: str) -> list[dict[str, Any]]:
        if fields:
            self.select_fields = list(fields)
        exec_ = self._get_executor()
        return await exec_.values()

    async def values_list(self, *fields: str, flat: bool = False) -> list[tuple[Any, ...]] | list[Any]:
        if fields:
            self.select_fields = list(fields)
        exec_ = self._get_executor()
        return await exec_.values_list(flat=flat)

    def values_sync(self, *fields: str) -> list[dict[str, Any]]:
        """Synchronous wrapper for values()."""
        try:
            asyncio.get_running_loop()
            raise RuntimeError("QueryBuilder.values_sync() called in async context. Use await .values() instead.")
        except RuntimeError as e:
            if "no running event loop" not in str(e):
                raise
        return asyncio.run(self.values(*fields))

    def values_list_sync(self, *fields: str, flat: bool = False) -> list[tuple[Any, ...]] | list[Any]:
        """Synchronous wrapper for values_list()."""
        try:
            asyncio.get_running_loop()
            raise RuntimeError("QueryBuilder.values_list_sync() called in async context. Use await .values_list() instead.")
        except RuntimeError as e:
            if "no running event loop" not in str(e):
                raise
        return asyncio.run(self.values_list(*fields, flat=flat))

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
