from matrx_orm.state import StateManager

from ..query.builder import QueryBuilder
from .update import update


async def delete(model, **kwargs):
    return await QueryBuilder(model).filter(**kwargs).delete()


async def bulk_delete(model, objects):
    """
    Enhanced bulk_delete that follows the same patterns as individual operations.
    Now properly handles cache removal like individual delete operations do.
    """
    if not objects:
        return 0

    ids = [obj.id for obj in objects if hasattr(obj, "id") and obj.id is not None]
    if not ids:
        return 0

    # Perform bulk delete using the proven individual operation pattern
    rows_affected = await delete(model, id__in=ids)

    # Remove from cache like individual delete operations do
    if rows_affected > 0:
        for obj in objects:
            if hasattr(obj, "id") and obj.id in ids:
                await StateManager.remove(model, obj)

    return rows_affected


async def soft_delete(model, **kwargs):
    from datetime import datetime

    return await update(model, deleted_at=datetime.now(), **kwargs)


async def restore(model, **kwargs):
    return await update(model, deleted_at=None, **kwargs)


async def purge(model, **kwargs):
    return await delete(model, deleted_at__isnull=False, **kwargs)


async def delete_instance(instance):
    model_class = instance.__class__
    pk_list = model_class._meta.primary_keys
    if not pk_list:
        raise ValueError(f"Cannot delete {model_class.__name__} with no primary key.")
    pk_name = pk_list[0]
    pk_value = getattr(instance, pk_name, None)
    if pk_value is None:
        raise ValueError(f"Cannot delete {model_class.__name__}, {pk_name} is None")

    await delete(model_class, **{pk_name: pk_value})
