"""Pydantic integration bridge for matrx-orm.

This module provides utilities to generate Pydantic v2 input-validation schemas
from ORM model field definitions, and to build typed output schemas from a
model's ``to_dict()`` shape.

Design principles
-----------------
- Pydantic is an **optional** dependency.  Every public function in this module
  raises ``ImportError`` with a helpful message if Pydantic is not installed.
- The ORM's core classes (``Model``, ``BaseManager``, field types) do **not**
  import this module at the top level.  Integration is opt-in: ``BaseManager``
  checks for Pydantic lazily when ``validate_input=True`` (the default).
- No ORM internals are duplicated here.  The bridge reads ``model._fields`` and
  calls ``field.python_type()`` / ``field.has_default()`` — the same extension
  points used by the rest of the system.

Public API
----------
- ``build_input_schema(model_cls, *, partial=False)`` — Pydantic model for
  create/update input validation.  ``partial=True`` makes every field optional
  (used for partial updates).
- ``build_output_schema(model_cls)`` — Pydantic model that mirrors the columns
  returned by ``model.to_dict()``.  Useful for API response typing and JSON
  schema generation.
- ``validate_input(model_cls, data, *, partial=False)`` — convenience wrapper
  that validates ``data`` and returns a cleaned ``dict`` ready for the ORM write
  pipeline.  Raises ``pydantic.ValidationError`` on failure.
- ``model_json_schema(model_cls, *, mode="input")`` — returns the JSON Schema
  dict for a model (useful for FastAPI / OpenAPI integration).

Caching
-------
Generated schemas are cached per (model_cls, partial) pair so that repeated
calls to ``create_item`` / ``update_item`` do not rebuild them on every request.
"""

from __future__ import annotations

import functools
from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from matrx_orm.core.base import Model
    from pydantic import BaseModel as PydanticBaseModel


def _require_pydantic() -> Any:
    """Import and return the pydantic module, raising a helpful error if absent."""
    try:
        import pydantic  # noqa: PLC0415
        return pydantic
    except ImportError:
        raise ImportError(
            "matrx-orm Pydantic integration requires pydantic v2. "
            "Install it with:  pip install pydantic"
        ) from None


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _field_annotation(field: Any, *, partial: bool) -> tuple[Any, Any]:
    """Return a (annotation, default) tuple suitable for ``create_model``.

    Rules
    -----
    - Primary-key fields are always optional (the DB or ORM supplies them).
    - Nullable fields are always optional.
    - Fields with a default are optional (default is carried over).
    - Everything else is required unless ``partial=True``.
    - ``ForeignKey`` fields are excluded from the schema (they carry internal
      IDs and are validated by the DB's referential integrity, not by Pydantic).
    """
    from typing import Optional  # noqa: PLC0415
    from pydantic import Field as PydanticField  # noqa: PLC0415
    from matrx_orm.core.fields import ForeignKey  # noqa: PLC0415

    if isinstance(field, ForeignKey):
        # FK columns accept str | None; they're optional (may be null).
        if field.null:
            return (Optional[str], None)
        return (Optional[str], PydanticField(default=None))

    py_type = field.python_type()

    # Wrap nullable types in Optional.
    if field.null or field.nullable:
        annotation = Optional[py_type]
    else:
        annotation = py_type

    # Determine default.
    if field.primary_key:
        # PK is server-generated; always optional on input.
        return (Optional[str], None)

    if partial:
        # For partial updates every field is optional with None sentinel.
        return (Optional[py_type], None)

    if field.has_default() or field.null or field.nullable:
        default_val = field.get_default()
        # Callables (e.g. uuid4) have already been resolved by get_default();
        # use None as the schema default so Pydantic doesn't call it again.
        return (annotation, default_val)

    # Required field.
    return (annotation, ...)


@functools.lru_cache(maxsize=256)
def _cached_input_schema(model_cls: type, partial: bool) -> "type[PydanticBaseModel]":
    """Build and cache a Pydantic input schema for *model_cls*.

    The cache key is (model_cls, partial).  Generated schemas are never
    invalidated during a process lifetime; model field definitions are fixed
    at class-creation time.
    """
    pydantic = _require_pydantic()
    from matrx_orm.core.fields import ForeignKey  # noqa: PLC0415

    field_definitions: dict[str, Any] = {}
    for name, field in model_cls._fields.items():
        # Skip internal ORM fields that callers should never supply directly.
        if getattr(field, "is_version_field", False):
            continue
        annotation, default = _field_annotation(field, partial=partial)
        field_definitions[name] = (annotation, default)

    schema_name = f"{model_cls.__name__}{'Partial' if partial else ''}InputSchema"
    return pydantic.create_model(
        schema_name,
        __config__=pydantic.ConfigDict(  # type: ignore[call-arg]
            extra="forbid",       # catch typos / unknown fields immediately
            populate_by_name=True,
            arbitrary_types_allowed=True,  # for Decimal, timedelta, etc.
        ),
        **field_definitions,
    )


@functools.lru_cache(maxsize=256)
def _cached_output_schema(model_cls: type) -> "type[PydanticBaseModel]":
    """Build and cache a Pydantic output schema for *model_cls*.

    All fields are optional in the output schema because ``to_dict()`` may omit
    ``None`` values and computed/relation fields vary per instance.
    """
    pydantic = _require_pydantic()
    from typing import Optional  # noqa: PLC0415

    field_definitions: dict[str, Any] = {}
    for name, field in model_cls._fields.items():
        py_type = field.python_type()
        field_definitions[name] = (Optional[py_type], None)

    schema_name = f"{model_cls.__name__}OutputSchema"
    return pydantic.create_model(
        schema_name,
        __config__=pydantic.ConfigDict(  # type: ignore[call-arg]
            extra="allow",           # allow computed/relation fields from to_dict()
            populate_by_name=True,
            arbitrary_types_allowed=True,
        ),
        **field_definitions,
    )


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def build_input_schema(model_cls: type, *, partial: bool = False) -> "type[PydanticBaseModel]":
    """Return a Pydantic ``BaseModel`` subclass for validating create/update input.

    Parameters
    ----------
    model_cls:
        An ORM ``Model`` subclass (e.g. ``Order``).
    partial:
        When ``True``, every field is made optional.  Pass this for partial
        update operations where only changed fields are supplied.

    Returns
    -------
    A Pydantic model class.  Instantiate it with the incoming data dict to
    validate; call ``.model_dump(exclude_none=True)`` to get a cleaned dict
    ready for the ORM write pipeline.

    Example
    -------
    ::

        schema = build_input_schema(Order)
        validated = schema(**request_data)
        order = await Order.create(**validated.model_dump(exclude_none=True))
    """
    _require_pydantic()
    return _cached_input_schema(model_cls, partial)


def build_output_schema(model_cls: type) -> "type[PydanticBaseModel]":
    """Return a Pydantic ``BaseModel`` subclass that mirrors ``model.to_dict()``.

    Useful for FastAPI response models, JSON Schema generation, and typed output
    validation in tests.

    Example
    -------
    ::

        OrderOut = build_output_schema(Order)
        # FastAPI usage:
        @app.get("/orders/{id}", response_model=OrderOut)
        async def get_order(id: str):
            order = await order_manager.load_by_id(id)
            return order.to_dict()
    """
    _require_pydantic()
    return _cached_output_schema(model_cls)


def validate_input(
    model_cls: type,
    data: dict[str, Any],
    *,
    partial: bool = False,
) -> dict[str, Any]:
    """Validate *data* against the model's input schema and return a cleaned dict.

    Parameters
    ----------
    model_cls:
        An ORM ``Model`` subclass.
    data:
        Raw input dict (e.g. from an API request body).
    partial:
        When ``True``, all fields are treated as optional (for PATCH-style
        partial updates).

    Returns
    -------
    A validated, type-coerced ``dict`` with ``None`` values stripped.  This
    dict is safe to pass directly to ``Model.create(**data)`` or
    ``manager.update_item(id, **data)``.

    Raises
    ------
    pydantic.ValidationError
        If validation fails.  The error contains field-level detail that can be
        serialised directly to a JSON API error response.
    ImportError
        If Pydantic is not installed.
    """
    schema_cls = build_input_schema(model_cls, partial=partial)
    validated = schema_cls(**data)
    return validated.model_dump(exclude_none=True)


def model_json_schema(model_cls: type, *, mode: str = "input") -> dict[str, Any]:
    """Return the JSON Schema dict for *model_cls*.

    Parameters
    ----------
    model_cls:
        An ORM ``Model`` subclass.
    mode:
        ``"input"`` (default) for the create/update schema, ``"output"`` for
        the ``to_dict()`` shape.

    Returns
    -------
    A JSON Schema ``dict`` compatible with OpenAPI 3.1.

    Example
    -------
    ::

        schema = model_json_schema(Order)
        # {"title": "OrderInputSchema", "type": "object", "properties": {...}}
    """
    _require_pydantic()
    if mode == "output":
        return _cached_output_schema(model_cls).model_json_schema()
    return _cached_input_schema(model_cls, False).model_json_schema()
