"""Async-friendly paginator for QueryBuilder querysets.

Usage::

    from matrx_orm import Paginator

    paginator = Paginator(User.filter(is_active=True).order_by("-created_at"), per_page=20)

    # Fetch a specific page
    page = await paginator.page(1)

    print(page.items)           # list[User] — the rows on this page
    print(page.number)          # 1
    print(page.total_count)     # total matching rows
    print(page.total_pages)     # ceil(total_count / per_page)
    print(page.has_next)        # True / False
    print(page.has_previous)    # True / False
    print(page.next_number)     # int or None
    print(page.previous_number) # int or None

    # Async iteration over all pages
    async for page in paginator:
        process(page.items)
"""
from __future__ import annotations

import math
from typing import Any, Generic, TypeVar, TYPE_CHECKING

if TYPE_CHECKING:
    from matrx_orm.query.builder import QueryBuilder
    from matrx_orm.core.base import Model

ModelT = TypeVar("ModelT", bound="Model")


class Page(Generic[ModelT]):
    """A single page of results."""

    def __init__(
        self,
        items: list[ModelT],
        number: int,
        per_page: int,
        total_count: int,
    ) -> None:
        self.items = items
        self.number = number
        self.per_page = per_page
        self.total_count = total_count

    @property
    def total_pages(self) -> int:
        if self.per_page <= 0:
            return 0
        return math.ceil(self.total_count / self.per_page)

    @property
    def has_next(self) -> bool:
        return self.number < self.total_pages

    @property
    def has_previous(self) -> bool:
        return self.number > 1

    @property
    def next_number(self) -> int | None:
        return self.number + 1 if self.has_next else None

    @property
    def previous_number(self) -> int | None:
        return self.number - 1 if self.has_previous else None

    @property
    def start_index(self) -> int:
        """1-based index of the first item on this page."""
        return (self.number - 1) * self.per_page + 1

    @property
    def end_index(self) -> int:
        """1-based index of the last item on this page."""
        return min(self.number * self.per_page, self.total_count)

    def __repr__(self) -> str:
        return (
            f"Page(number={self.number}, total_pages={self.total_pages}, "
            f"items={len(self.items)}, total_count={self.total_count})"
        )

    def __iter__(self):  # type: ignore[override]
        return iter(self.items)

    def __len__(self) -> int:
        return len(self.items)


class Paginator(Generic[ModelT]):
    """Paginate any QueryBuilder queryset.

    Args:
        queryset:  A QueryBuilder instance (not yet executed).
        per_page:  Number of rows per page (must be > 0).

    The paginator executes two queries per ``page()`` call:
    one ``COUNT(*)`` and one ``SELECT … LIMIT … OFFSET``.
    """

    def __init__(self, queryset: "QueryBuilder[ModelT]", per_page: int = 20) -> None:
        if per_page <= 0:
            raise ValueError("per_page must be a positive integer")
        self._queryset = queryset
        self.per_page = per_page
        self._total_count: int | None = None
        self._current_page: int = 1

    async def count(self) -> int:
        """Return (and cache) the total number of matching rows."""
        if self._total_count is None:
            self._total_count = await self._queryset.count()
        return self._total_count

    @property
    def total_pages(self) -> int | None:
        """Total page count — None until count() has been called."""
        if self._total_count is None:
            return None
        return math.ceil(self._total_count / self.per_page)

    async def page(self, number: int) -> "Page[ModelT]":
        """Fetch page *number* (1-based).

        Raises ``ValueError`` if *number* is out of range.
        """
        total = await self.count()
        total_pgs = math.ceil(total / self.per_page) if total > 0 else 1

        if number < 1:
            raise ValueError(f"Page number must be >= 1, got {number}")
        if number > total_pgs:
            raise ValueError(
                f"Page {number} does not exist — there are only {total_pgs} pages "
                f"({total} rows, {self.per_page} per page)"
            )

        offset = (number - 1) * self.per_page
        # Clone the queryset with limit/offset applied (does not mutate the original)
        from matrx_orm.query.builder import QueryBuilder
        paged_qs = self._clone_with_pagination(offset)
        items = await paged_qs.all()

        return Page(
            items=items,
            number=number,
            per_page=self.per_page,
            total_count=total,
        )

    def _clone_with_pagination(self, offset: int) -> "QueryBuilder[ModelT]":
        """Return a shallow clone of the queryset with LIMIT/OFFSET set."""
        import copy
        clone = copy.copy(self._queryset)
        # Don't mutate any mutable lists — copy them shallowly
        clone.filters = list(self._queryset.filters)
        clone.excludes = list(self._queryset.excludes)
        clone.order_by_fields = list(self._queryset.order_by_fields)
        clone.select_fields = list(self._queryset.select_fields)
        clone.aggregations = list(self._queryset.aggregations)
        clone.group_by_fields = list(self._queryset.group_by_fields)
        clone.having_filters = list(self._queryset.having_filters)
        clone.ctes = list(self._queryset.ctes)
        clone.select_related_fields = list(self._queryset.select_related_fields)
        clone.limit_val = self.per_page
        clone.offset_val = offset
        return clone

    # ------------------------------------------------------------------
    # Async iteration over all pages
    # ------------------------------------------------------------------

    def __aiter__(self) -> "Paginator[ModelT]":
        self._current_page = 1
        self._total_count = None  # reset so count is re-fetched on first iteration
        return self

    async def __anext__(self) -> "Page[ModelT]":
        total = await self.count()
        total_pgs = math.ceil(total / self.per_page) if total > 0 else 1
        if self._current_page > total_pgs:
            raise StopAsyncIteration
        page = await self.page(self._current_page)
        self._current_page += 1
        return page
