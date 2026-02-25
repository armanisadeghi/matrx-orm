"""
matrx_orm.core.model_view
~~~~~~~~~~~~~~~~~~~~~~~~~

ModelView — a declarative, zero-duplication projection layer for Model instances.

Replace BaseDTO with ModelView. A view is not a separate object that wraps the
model. It is a recipe: declare which relations to prefetch, which fields to
exclude, which FK columns to replace with their full related objects, and which
async computed fields to materialise. When applied, all results are stored flat
on the model instance and are invisible to the write path.

Backward compatibility: BaseDTO and dto_class on BaseManager continue to work
unchanged. ModelView is additive — migrate view by view over time.

Usage
-----

    class OrderView(ModelView):
        # Relations to prefetch concurrently on load.
        # Accepts FK field names, IFK field names, and M2M field names.
        prefetch: list[str] = ["customer_id", "line_items", "tags"]

        # Model fields to omit from to_dict() output.
        exclude: list[str] = ["internal_notes", "payment_processor_raw"]

        # Replace the FK column value with the full related object.
        # Key: FK field name on the model (e.g. "customer_id")
        # Value: name to use in the output (e.g. "customer")
        inline_fk: dict[str, str] = {"customer_id": "customer"}

        # Async computed fields: any async method whose name does NOT start
        # with an underscore is treated as a computed field.  The method
        # receives the model instance and should return a serialisable value.
        async def display_name(self, model: Any) -> str:
            customer = model.get_related("customer_id")
            if customer:
                return f"{customer.first_name} {customer.last_name}"
            return "Unknown"

        async def total_formatted(self, model: Any) -> str:
            return f"${model.total:.2f}"


    # Attach to a manager:
    class OrderBase(BaseManager[Order]):
        view_class = OrderView

    # OR apply directly to a model instance:
    await OrderView.apply(order_instance)

After apply() the instance carries:
  - All prefetched relations accessible via get_related()
  - Computed field values accessible as plain attributes
  - inline_fk replacements accessible under the new name
  - to_dict() returns the full flat application shape
"""

from __future__ import annotations

import asyncio
import inspect
import warnings
from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from matrx_orm.core.base import Model


class ModelViewMeta(type):
    """
    Metaclass that collects all async computed-field methods (those that don't
    start with '_') and stores them in _computed_methods at class creation time.
    This avoids re-scanning on every apply() call.
    """

    def __new__(
        mcs, name: str, bases: tuple[type, ...], attrs: dict[str, Any]
    ) -> ModelViewMeta:
        computed: dict[str, Any] = {}

        # Inherit computed methods from base classes first so subclasses can
        # override them without losing the rest.
        for base in reversed(bases):
            base_computed = getattr(base, "_computed_methods", {})
            computed.update(base_computed)

        for attr_name, value in attrs.items():
            # Skip dunder, private, and the class-level config attributes.
            if attr_name.startswith("_"):
                continue
            if attr_name in ("prefetch", "exclude", "inline_fk"):
                continue
            if inspect.iscoroutinefunction(value):
                computed[attr_name] = value

        attrs["_computed_methods"] = computed
        return super().__new__(mcs, name, bases, attrs)


class ModelView(metaclass=ModelViewMeta):
    """
    Base class for all model views.

    Class-level configuration
    -------------------------
    prefetch   : list[str]        — relation names to fetch before computing fields
    exclude    : list[str]        — model field names to suppress in to_dict()
    inline_fk  : dict[str, str]   — {fk_field: output_name} replaces the FK id
                                    value with the full related object in output

    Async methods (no leading underscore) are computed fields.  They receive
    (self, model) and their return value is stored on the model as a view field.
    """

    prefetch: list[str] = []
    exclude: list[str] = []
    inline_fk: dict[str, str] = {}

    # Populated by ModelViewMeta at class creation time.
    _computed_methods: dict[str, Any] = {}

    @classmethod
    async def apply(cls, model: "Model") -> "Model":
        """
        Materialise this view onto *model* in-place.

        Steps (all concurrent where possible):
          1. Prefetch all declared relations concurrently.
          2. Run all computed-field coroutines concurrently.
          3. Apply inline_fk substitutions.
          4. Register exclude / inline_fk metadata on the model so to_dict()
             can honour them without re-reading the view class.

        Returns the same model instance for convenience (chainable).
        """
        # ------------------------------------------------------------------ #
        # Step 1 — prefetch relations                                         #
        # ------------------------------------------------------------------ #
        prefetch = cls.prefetch
        if prefetch:
            await cls._prefetch_relations(model, prefetch)

        # ------------------------------------------------------------------ #
        # Step 2 — run computed fields concurrently                           #
        # ------------------------------------------------------------------ #
        computed = cls._computed_methods
        if computed:
            instance = cls()
            coros = {
                field_name: method(instance, model)
                for field_name, method in computed.items()
            }
            results = await asyncio.gather(*coros.values(), return_exceptions=True)
            for field_name, result in zip(coros.keys(), results):
                if isinstance(result, BaseException):
                    # Log but never raise — a bad computed field must not
                    # abort the entire load.
                    _warn_computed(cls.__name__, field_name, result)
                    model._view_data[field_name] = None
                else:
                    model._view_data[field_name] = result

        # ------------------------------------------------------------------ #
        # Step 3 — inline FK substitutions                                   #
        # ------------------------------------------------------------------ #
        for fk_field, output_name in cls.inline_fk.items():
            related = model.get_related(fk_field)
            if related is not None:
                model._view_data[output_name] = related
                # Mark the original FK field as inlined so to_dict() can
                # replace it with the output name.
                model._view_inlined_fks[fk_field] = output_name

        # ------------------------------------------------------------------ #
        # Step 4 — register exclude set on the instance                       #
        # ------------------------------------------------------------------ #
        if cls.exclude:
            model._view_excluded.update(cls.exclude)

        # Stamp the view class so introspection tools can see what was applied.
        model._applied_view = cls

        return model

    # ---------------------------------------------------------------------- #
    # Internal helpers                                                        #
    # ---------------------------------------------------------------------- #

    @classmethod
    async def _prefetch_relations(cls, model: "Model", relation_names: list[str]) -> None:
        """
        Fetch the listed relation names concurrently, routing each to the
        correct fetch method (FK / IFK / M2M) based on the model's metadata.
        Failures are logged and swallowed so one bad relation does not abort
        the whole load.
        """
        async def _safe_fetch(name: str) -> None:
            try:
                await model.fetch_one_relation(name)
            except Exception as exc:
                _warn_prefetch(cls.__name__, name, exc)

        await asyncio.gather(*(_safe_fetch(name) for name in relation_names))


# --------------------------------------------------------------------------- #
# Warning helpers — centralised so they're easy to find and silence           #
# --------------------------------------------------------------------------- #

def _warn_computed(view_name: str, field_name: str, exc: BaseException) -> None:
    warnings.warn(
        f"[ModelView:{view_name}] Computed field '{field_name}' raised "
        f"{type(exc).__name__}: {exc}. Stored as None.",
        RuntimeWarning,
        stacklevel=4,
    )


def _warn_prefetch(view_name: str, relation_name: str, exc: BaseException) -> None:
    warnings.warn(
        f"[ModelView:{view_name}] Prefetch of relation '{relation_name}' failed: "
        f"{type(exc).__name__}: {exc}. Skipped.",
        RuntimeWarning,
        stacklevel=4,
    )
