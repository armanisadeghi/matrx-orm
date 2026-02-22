from __future__ import annotations

from typing import Any, TYPE_CHECKING

from matrx_orm.state import StateManager

from ..core.fields import Field
from ..query.builder import QueryBuilder
from ..query.executor import QueryExecutor

if TYPE_CHECKING:
    from matrx_orm.core.base import Model


async def create(model_cls: type[Model], **kwargs: Any) -> Model:
    instance = model_cls(**kwargs)
    return await save(instance)


async def save(instance: Model) -> Model:
    from matrx_orm.core.signals import pre_create, post_create

    model_cls = instance.__class__
    await pre_create.send(model_cls, instance=instance)

    data: dict[str, Any] = {}
    for field_name, field in model_cls._fields.items():
        if isinstance(field, Field):
            value = getattr(instance, field_name)
            if value is None and field.default is not None:
                value = field.get_default()
            if value is not None:
                data[field_name] = field.get_db_prep_value(value)

    query = QueryBuilder(model_cls)._build_query()
    query["data"] = data

    executor = QueryExecutor(query)
    result = await executor.insert(query)

    for key, value in result.items():
        field = model_cls._fields.get(key)
        if field and isinstance(field, Field):
            value = field.to_python(value)
        setattr(instance, key, value)

    await post_create.send(model_cls, instance=instance, created=True)
    return instance


async def bulk_create(model_cls: type[Model], objects_data: list[dict[str, Any]]) -> list[Model]:
    """Bulk insert with field coercion. Returns hydrated model instances."""
    if not objects_data:
        return []

    instances: list[Model] = []
    data_list: list[dict[str, Any]] = []

    for obj_data in objects_data:
        instance = model_cls(**obj_data)
        instances.append(instance)

        data: dict[str, Any] = {}
        for field_name, field in model_cls._fields.items():
            if isinstance(field, Field):
                value = getattr(instance, field_name)
                if value is None and field.default is not None:
                    value = field.get_default()
                if value is not None:
                    data[field_name] = field.get_db_prep_value(value)
        data_list.append(data)

    query = QueryBuilder(model_cls)._build_query()
    query["data"] = data_list

    executor = QueryExecutor(query)
    created_instances = await executor.bulk_insert(query)

    for inst in created_instances:
        await StateManager.cache(model_cls, inst)

    return created_instances


async def get_or_create(
    model_cls: type[Model], defaults: dict[str, Any] | None = None, **kwargs: Any
) -> tuple[Model, bool]:
    defaults = defaults or {}
    try:
        instance = await model_cls.get(**kwargs)
        return instance, False
    except model_cls.DoesNotExist:
        params = {**kwargs, **defaults}
        instance = await create(model_cls, **params)
        return instance, True


async def update_or_create(
    model_cls: type[Model], defaults: dict[str, Any] | None = None, **kwargs: Any
) -> tuple[Model, bool]:
    defaults = defaults or {}
    try:
        instance = await model_cls.get(**kwargs)
        for key, value in defaults.items():
            setattr(instance, key, value)
        await save(instance)
        return instance, False
    except model_cls.DoesNotExist:
        params = {**kwargs, **defaults}
        instance = await create(model_cls, **params)
        return instance, True


async def upsert(
    model_cls: type[Model],
    data: dict[str, Any],
    conflict_fields: list[str],
    update_fields: list[str] | None = None,
) -> Model:
    """INSERT ... ON CONFLICT (conflict_fields) DO UPDATE SET ... RETURNING *"""
    instance = model_cls(**data)
    prepared: dict[str, Any] = {}
    for field_name, field in model_cls._fields.items():
        if isinstance(field, Field):
            value = getattr(instance, field_name)
            if value is None and field.default is not None:
                value = field.get_default()
            if value is not None:
                prepared[field_name] = field.get_db_prep_value(value)

    query = QueryBuilder(model_cls)._build_query()
    query["data"] = prepared
    query["conflict_fields"] = conflict_fields
    query["update_fields"] = update_fields

    executor = QueryExecutor(query)
    result = await executor.upsert(query)

    for key, value in result.items():
        field = model_cls._fields.get(key)
        if field and isinstance(field, Field):
            value = field.to_python(value)
        setattr(instance, key, value)

    await StateManager.cache(model_cls, instance)
    return instance


async def bulk_upsert(
    model_cls: type[Model],
    objects_data: list[dict[str, Any]],
    conflict_fields: list[str],
    update_fields: list[str] | None = None,
) -> list[Model]:
    """Bulk INSERT ... ON CONFLICT DO UPDATE for multiple rows."""
    if not objects_data:
        return []

    data_list: list[dict[str, Any]] = []
    for obj_data in objects_data:
        instance = model_cls(**obj_data)
        prepared: dict[str, Any] = {}
        for field_name, field in model_cls._fields.items():
            if isinstance(field, Field):
                value = getattr(instance, field_name)
                if value is None and field.default is not None:
                    value = field.get_default()
                if value is not None:
                    prepared[field_name] = field.get_db_prep_value(value)
        data_list.append(prepared)

    query = QueryBuilder(model_cls)._build_query()
    query["data"] = data_list
    query["conflict_fields"] = conflict_fields
    query["update_fields"] = update_fields

    executor = QueryExecutor(query)
    created_instances = await executor.bulk_upsert(query)

    for inst in created_instances:
        await StateManager.cache(model_cls, inst)

    return created_instances


async def create_instance(model_cls: type[Model], **kwargs: Any) -> Model:
    """Alias used by Model.save() for creating a brand new record."""
    return await create(model_cls, **kwargs)
