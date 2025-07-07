from matrx_orm.state import StateManager

from ..core.fields import Field
from ..query.builder import QueryBuilder
from ..query.executor import QueryExecutor


async def create(model, **kwargs):
    instance = model(**kwargs)
    return await save(instance)


async def save(instance):
    data = {}
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

    # Convert DB values back to Python objects
    for key, value in result.items():
        field = instance.__class__._fields.get(key)
        if field and isinstance(field, Field):
            value = field.to_python(value)
        setattr(instance, key, value)

    return instance


async def bulk_create(model, objects_data):
    """
    Enhanced bulk_create that follows the same data processing pipeline as individual operations.
    Now properly handles the fact that bulk_insert() returns model instances, not raw dicts.
    """
    if not objects_data:
        return []

    # Create instances and process data exactly like save() does
    instances = []
    data_list = []

    for obj_data in objects_data:
        instance = model(**obj_data)
        instances.append(instance)

        # Process data exactly like save() does
        data = {}
        for field_name, field in model._fields.items():
            if isinstance(field, Field):
                value = getattr(instance, field_name)
                if value is None and field.default is not None:
                    value = field.get_default()
                if value is not None:
                    data[field_name] = field.get_db_prep_value(value)
        data_list.append(data)

    # Build query exactly like save() does
    from ..query.executor import QueryExecutor

    query = {
        "table": model._table_name,
        "data": data_list,
    }

    executor = QueryExecutor(query)

    # bulk_insert() returns model instances, not raw dicts like insert()
    created_instances = await executor.bulk_insert(query)

    # Cache all created instances like individual operations do
    for instance in created_instances:
        await StateManager.cache(model, instance)

    return created_instances


async def get_or_create(model, defaults=None, **kwargs):
    """Fixed to use proper Model methods instead of non-existent model.objects"""
    defaults = defaults or {}
    try:
        instance = await model.get(**kwargs)
        return instance, False
    except model.DoesNotExist:
        params = {**kwargs, **defaults}
        instance = await create(model, **params)
        return instance, True


async def update_or_create(model, defaults=None, **kwargs):
    """Fixed to use proper Model methods instead of non-existent model.objects"""
    defaults = defaults or {}
    try:
        instance = await model.get(**kwargs)
        for key, value in defaults.items():
            setattr(instance, key, value)
        await save(instance)
        return instance, False
    except model.DoesNotExist:
        params = {**kwargs, **defaults}
        instance = await create(model, **params)
        return instance, True


async def create_instance(model_class, **kwargs):
    """
    This matches the reference in Model.save() for creating a brand new record.
    Uses the existing 'create' function to do the heavy lifting.
    """
    return await create(model_class, **kwargs)
