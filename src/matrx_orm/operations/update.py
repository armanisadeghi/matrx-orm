from __future__ import annotations

from typing import Any, Iterable, TYPE_CHECKING

from matrx_utils import vcprint
from matrx_orm.state import StateManager

from ..core.expressions import F
from ..query.builder import QueryBuilder

if TYPE_CHECKING:
    from matrx_orm.core.base import Model

debug = False


async def update(model_cls: type[Model], filters: dict[str, Any], **kwargs: Any) -> dict[str, Any]:
    return await QueryBuilder(model_cls).filter(**filters).update(**kwargs)


async def bulk_update(model_cls: type[Model], objects: list[Model], fields: list[str]) -> int:
    """
    Enhanced bulk_update that works within the current ORM limitations.
    Uses controlled batch processing for individual per-row updates.
    """
    if not objects or not fields:
        return 0

    invalid_fields = [k for k in fields if k not in model_cls._fields]
    if invalid_fields:
        vcprint(model_cls._fields, "Model Fields", color="yellow")
        raise ValueError(f"Invalid fields for {model_cls.__name__}: {invalid_fields}")

    valid_objects = [
        obj for obj in objects if hasattr(obj, "id") and obj.id is not None
    ]
    if not valid_objects:
        return 0

    vcprint(f"Processing {len(valid_objects)} objects for bulk update...", color="blue")

    rows_affected = 0
    failed_updates: list[dict[str, Any]] = []

    for i, obj in enumerate(valid_objects):
        try:
            update_data: dict[str, Any] = {}
            for field_name in fields:
                if field_name in model_cls._fields and hasattr(obj, field_name):
                    field = model_cls._fields[field_name]
                    value = getattr(obj, field_name)
                    if value is not None:
                        update_data[field_name] = field.get_db_prep_value(value)

            if update_data:
                result = (
                    await QueryBuilder(model_cls).filter(id=obj.id).update(**update_data)
                )
                if result.get("rows_affected", 0) > 0:
                    rows_affected += 1

                    await StateManager.cache(model_cls, obj)

            if (i + 1) % 10 == 0:
                vcprint(
                    f"Processed {i + 1}/{len(valid_objects)} updates...", color="cyan"
                )

        except Exception as e:
            vcprint(f"Failed to update object {obj.id}: {e}", color="red")
            failed_updates.append({"object": obj, "error": str(e)})
            continue

    if failed_updates:
        vcprint(
            f"Bulk update completed with {len(failed_updates)} failures", color="yellow"
        )
        for failure in failed_updates[:3]:
            vcprint(
                f"  Failed: {failure['object'].id} - {failure['error']}", color="red"
            )
        if len(failed_updates) > 3:
            vcprint(f"  ... and {len(failed_updates) - 3} more failures", color="red")
    else:
        vcprint("Bulk update completed successfully", color="green")

    return rows_affected


async def update_or_create(
    model_cls: type[Model], defaults: dict[str, Any] | None = None, **kwargs: Any
) -> tuple[Model, bool]:
    """Fixed to use proper Model methods instead of non-existent model.objects"""
    defaults = defaults or {}
    try:
        instance = await model_cls.get(**kwargs)
        for key, value in defaults.items():
            setattr(instance, key, value)
        await instance.save()
        return instance, False
    except model_cls.DoesNotExist:
        params = {**kwargs, **defaults}
        instance = await model_cls.create(**params)
        return instance, True


async def increment(model_cls: type[Model], filters: dict[str, Any], **kwargs: Any) -> dict[str, Any]:
    updates: dict[str, Any] = {}
    for field, amount in kwargs.items():
        updates[field] = F(field) + amount
    return await update(model_cls, filters, **updates)


async def decrement(model_cls: type[Model], filters: dict[str, Any], **kwargs: Any) -> dict[str, Any]:
    updates: dict[str, Any] = {}
    for field, amount in kwargs.items():
        updates[field] = F(field) - amount
    return await update(model_cls, filters, **updates)


async def update_instance(instance: Model, fields: Iterable[str] | None = None) -> Model:
    model_cls = instance.__class__
    pk_list = model_cls._meta.primary_keys
    if not pk_list:
        raise ValueError(f"Cannot update {model_cls.__name__} with no primary key.")
    pk_name = pk_list[0]
    pk_value = getattr(instance, pk_name, None)
    if pk_value is None:
        raise ValueError(f"Cannot update {model_cls.__name__}, {pk_name} is None")

    update_data: dict[str, Any] = {}
    field_names: Iterable[str] = (
        fields
        if fields is not None
        else [f for f in model_cls._fields if f != pk_name]
    )
    for field_name in field_names:
        if field_name == pk_name:
            continue
        if field_name not in model_cls._fields:
            continue
        field = model_cls._fields[field_name]
        value = getattr(instance, field_name, None)
        if value is not None:
            update_data[field_name] = field.get_db_prep_value(value)
        elif field.nullable:
            # Explicitly include nullable fields set to None so they're nulled in the DB
            update_data[field_name] = None

    filters = {pk_name: pk_value}

    if debug:
        vcprint(
            f"Updating instance with filters: {filters}", verbose=debug, color="cyan"
        )
        vcprint(f"Update data: {update_data}", verbose=debug, color="cyan")

    result = await update(model_cls, filters, **update_data)

    if result["rows_affected"] == 0:
        raise ValueError(
            f"No rows were updated for {model_cls.__name__} with {pk_name}={pk_value}"
        )

    if result["updated_rows"]:
        for key, value in result["updated_rows"][0].items():
            setattr(instance, key, value)

    return instance
