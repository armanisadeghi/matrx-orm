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
    data: dict[str, Any] = {}
    for field_name, field in instance.__class__._fields.items():
        if isinstance(field, Field):
            value = getattr(instance, field_name)
            if value is None and field.default is not None:
                value = field.get_default()
            if value is not None:
                data[field_name] = field.get_db_prep_value(value)

    query = QueryBuilder(instance.__class__)._build_query()
    query["data"] = data

    executor = QueryExecutor(query)
    result = await executor.insert(query)

    for key, value in result.items():
        field = instance.__class__._fields.get(key)
        if field and isinstance(field, Field):
            value = field.to_python(value)
        setattr(instance, key, value)

    return instance


async def bulk_create(model_cls: type[Model], objects_data: list[dict[str, Any]]) -> list[Model]:
    """
    Enhanced bulk_create that follows the same data processing pipeline as individual operations.
    Now properly handles the fact that bulk_insert() returns model instances, not raw dicts.
    """
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

    from ..query.executor import QueryExecutor

    query: dict[str, Any] = {
        "table": model_cls._meta.qualified_table_name,
        "data": data_list,
    }

    executor = QueryExecutor(query)

    created_instances = await executor.bulk_insert(query)

    for instance in created_instances:
        await StateManager.cache(model_cls, instance)

    return created_instances


async def get_or_create(model_cls: type[Model], defaults: dict[str, Any] | None = None, **kwargs: Any) -> tuple[Model, bool]:
    """Fixed to use proper Model methods instead of non-existent model.objects"""
    defaults = defaults or {}
    try:
        instance = await model_cls.get(**kwargs)
        return instance, False
    except model_cls.DoesNotExist:
        params = {**kwargs, **defaults}
        instance = await create(model_cls, **params)
        return instance, True


async def update_or_create(model_cls: type[Model], defaults: dict[str, Any] | None = None, **kwargs: Any) -> tuple[Model, bool]:
    """Fixed to use proper Model methods instead of non-existent model.objects"""
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


async def create_instance(model_cls: type[Model], **kwargs: Any) -> Model:
    """
    This matches the reference in Model.save() for creating a brand new record.
    Uses the existing 'create' function to do the heavy lifting.
    """
    return await create(model_cls, **kwargs)
