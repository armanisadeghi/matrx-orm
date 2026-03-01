"""
matrx_orm.core.types
~~~~~~~~~~~~~~~~~~~~

Typed containers for ORM relation results and common structured return values.

These dataclasses replace the untyped ``dict[str, Any]`` patterns that previously
obscured the shape of data returned by relation-fetching methods on both the
Model and BaseManager layers.

All containers are ``frozen`` (immutable after creation) and use ``slots`` for
minimal memory overhead.  Generic type parameters allow downstream code to
carry concrete model types through the type system.

Usage example::

    result: AllRelatedResults = await order.fetch_all_related()
    customer = result.foreign_keys.get("customer_id")   # Model | None
    line_items = result.inverse_foreign_keys.get("line_items")  # list[Model] | None
    tags = result.many_to_many.get("tags")               # list[Model]
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Generic, TypeVar, TYPE_CHECKING

if TYPE_CHECKING:
    from matrx_orm.core.base import Model

ModelT = TypeVar("ModelT", bound="Model")


@dataclass(frozen=True, slots=True)
class ForeignKeyResults(Generic[ModelT]):
    """Results from ``Model.fetch_fks()`` — one entry per FK on the model.

    Keys are FK field names (e.g. ``"customer_id"``).
    Values are the fetched related model instance, or ``None`` if the FK
    value was null or the fetch failed.
    """

    data: dict[str, ModelT | None]

    def get(self, key: str, default: ModelT | None = None) -> ModelT | None:
        return self.data.get(key, default)

    def __len__(self) -> int:
        return len(self.data)

    def __bool__(self) -> bool:
        return bool(self.data)

    def __contains__(self, key: str) -> bool:
        return key in self.data

    def __iter__(self):
        return iter(self.data)

    def keys(self):
        return self.data.keys()

    def values(self):
        return self.data.values()

    def items(self):
        return self.data.items()

    def to_dict(self) -> dict[str, dict[str, Any] | None]:
        """Serialise each FK model instance via its own ``to_dict()``.

        ``None`` values (null FK or failed fetch) are preserved as-is.
        """
        return {k: v.to_dict() if v is not None else None for k, v in self.data.items()}


@dataclass(frozen=True, slots=True)
class InverseForeignKeyResults(Generic[ModelT]):
    """Results from ``Model.fetch_ifks()`` — one entry per IFK on the model.

    Keys are IFK relation names (e.g. ``"line_items"``).
    Values are lists of related model instances, or ``None`` if the fetch failed.
    An empty list means the fetch succeeded but found no related rows.
    """

    data: dict[str, list[ModelT] | None]

    def get(self, key: str, default: list[ModelT] | None = None) -> list[ModelT] | None:
        return self.data.get(key, default)

    def __len__(self) -> int:
        return len(self.data)

    def __bool__(self) -> bool:
        return bool(self.data)

    def __contains__(self, key: str) -> bool:
        return key in self.data

    def __iter__(self):
        return iter(self.data)

    def keys(self):
        return self.data.keys()

    def values(self):
        return self.data.values()

    def items(self):
        return self.data.items()

    def to_dict(self) -> dict[str, list[dict[str, Any]] | None]:
        """Serialise each IFK model list element-wise via ``to_dict()``.

        ``None`` (failed fetch) is preserved; an empty list (successful but no
        rows) serialises to ``[]``.
        """
        return {
            k: [m.to_dict() for m in v] if v is not None else None
            for k, v in self.data.items()
        }


@dataclass(frozen=True, slots=True)
class ManyToManyResults(Generic[ModelT]):
    """Results from ``Model.fetch_m2ms()`` — one entry per M2M on the model.

    Keys are M2M relation names (e.g. ``"tags"``).
    Values are lists of related model instances.  An empty list means the
    fetch succeeded but the junction table had no matching rows.
    """

    data: dict[str, list[ModelT]]

    def get(self, key: str, default: list[ModelT] | None = None) -> list[ModelT] | None:
        return self.data.get(key, default)

    def __len__(self) -> int:
        return len(self.data)

    def __bool__(self) -> bool:
        return bool(self.data)

    def __contains__(self, key: str) -> bool:
        return key in self.data

    def __iter__(self):
        return iter(self.data)

    def keys(self):
        return self.data.keys()

    def values(self):
        return self.data.values()

    def items(self):
        return self.data.items()

    def to_dict(self) -> dict[str, list[dict[str, Any]]]:
        """Serialise each M2M model list element-wise via ``to_dict()``.

        Values are always lists (never ``None``); an empty list serialises to ``[]``.
        """
        return {k: [m.to_dict() for m in v] for k, v in self.data.items()}


@dataclass(frozen=True, slots=True)
class AllRelatedResults(Generic[ModelT]):
    """Typed container for ``Model.fetch_all_related()``.

    Replaces the old ``dict[str, dict[str, Any]]`` return with three
    named, properly typed attributes::

        result = await order.fetch_all_related()

        result.foreign_keys          # ForeignKeyResults
        result.inverse_foreign_keys  # InverseForeignKeyResults
        result.many_to_many          # ManyToManyResults

        # Attribute access on each:
        result.foreign_keys.get("customer_id")
        result.inverse_foreign_keys.get("line_items")
        result.many_to_many.get("tags")
    """

    foreign_keys: ForeignKeyResults[ModelT]
    inverse_foreign_keys: InverseForeignKeyResults[ModelT]
    many_to_many: ManyToManyResults[ModelT]

    @staticmethod
    def empty() -> AllRelatedResults:
        """Return an ``AllRelatedResults`` with no data in any category."""
        return AllRelatedResults[ModelT](
            foreign_keys=ForeignKeyResults[ModelT](data={}),
            inverse_foreign_keys=InverseForeignKeyResults[ModelT](data={}),
            many_to_many=ManyToManyResults[ModelT](data={}),
        )

    def to_dict(self) -> dict[str, dict[str, Any]]:
        """Serialise to the legacy dict shape for JSON / API boundaries."""
        return {
            "foreign_keys": self.foreign_keys.to_dict(),
            "inverse_foreign_keys": self.inverse_foreign_keys.to_dict(),
            "many_to_many": self.many_to_many.to_dict(),
        }


AggregateResult = dict[str, int | float | None]
"""Return type for ``QueryBuilder.aggregate()`` and ``QueryExecutor.aggregate()``.

Keys are the aggregation aliases supplied by the caller (e.g. ``total``,
``avg_price``).  Values are always numeric (``int`` or ``float``) or
``NULL`` (``None``).
"""


@dataclass(frozen=True, slots=True)
class UpdateResult:
    """Typed container for ``Model.update_where()`` and ``QueryBuilder.update()``.

    Replaces the old ``{"rows_affected": int, "updated_rows": list[dict]}``
    untyped dict with named attributes::

        result = await MyModel.update_where({"status": "draft"}, status="archived")
        result.rows_affected   # int
        result.updated_rows    # list[dict[str, Any]]
    """

    rows_affected: int
    updated_rows: list[dict[str, Any]]

    def to_dict(self) -> dict[str, Any]:
        """Serialise to the legacy dict shape for JSON / API boundaries."""
        return {
            "rows_affected": self.rows_affected,
            "updated_rows": self.updated_rows,
        }
