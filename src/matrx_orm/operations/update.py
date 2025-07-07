from matrx_utils import vcprint
from matrx_orm.state import StateManager

from ..core.expressions import F
from ..query.builder import QueryBuilder

debug = False


async def update(model, filters, **kwargs):
    return await QueryBuilder(model).filter(**filters).update(**kwargs)


async def bulk_update(model, objects, fields):
    """
    Enhanced bulk_update that works within the current ORM limitations.
    Uses controlled batch processing since the ORM doesn't support __in operators yet.
    """
    if not objects or not fields:
        return 0

    # Validate fields like individual operations do
    invalid_fields = [k for k in fields if k not in model._fields]
    if invalid_fields:
        vcprint(model._fields, "Model Fields", color="yellow")
        raise ValueError(f"Invalid fields for {model.__name__}: {invalid_fields}")

    # Extract objects with valid IDs
    valid_objects = [
        obj for obj in objects if hasattr(obj, "id") and obj.id is not None
    ]
    if not valid_objects:
        return 0

    vcprint(f"Processing {len(valid_objects)} objects for bulk update...", color="blue")

    # Since the ORM doesn't support __in operator yet, we'll use individual updates
    # but process them efficiently with error handling and progress tracking
    rows_affected = 0
    failed_updates = []

    for i, obj in enumerate(valid_objects):
        try:
            # Prepare update data with proper field processing
            update_data = {}
            for field_name in fields:
                if field_name in model._fields and hasattr(obj, field_name):
                    field = model._fields[field_name]
                    value = getattr(obj, field_name)
                    if value is not None:
                        update_data[field_name] = field.get_db_prep_value(value)

            if update_data:
                # Use individual update through QueryBuilder (proven method)
                result = (
                    await QueryBuilder(model).filter(id=obj.id).update(**update_data)
                )
                if result.get("rows_affected", 0) > 0:
                    rows_affected += 1

                    # Update cache like individual operations do
                    await StateManager.cache(model, obj)

            # Progress indicator for large batches
            if (i + 1) % 10 == 0:
                vcprint(
                    f"Processed {i + 1}/{len(valid_objects)} updates...", color="cyan"
                )

        except Exception as e:
            vcprint(f"Failed to update object {obj.id}: {e}", color="red")
            failed_updates.append({"object": obj, "error": str(e)})
            continue

    # Report results
    if failed_updates:
        vcprint(
            f"Bulk update completed with {len(failed_updates)} failures", color="yellow"
        )
        for failure in failed_updates[:3]:  # Show first 3 failures
            vcprint(
                f"  Failed: {failure['object'].id} - {failure['error']}", color="red"
            )
        if len(failed_updates) > 3:
            vcprint(f"  ... and {len(failed_updates) - 3} more failures", color="red")
    else:
        vcprint("Bulk update completed successfully", color="green")

    return rows_affected


async def update_or_create(model, defaults=None, **kwargs):
    """Fixed to use proper Model methods instead of non-existent model.objects"""
    defaults = defaults or {}
    try:
        instance = await model.get(**kwargs)
        for key, value in defaults.items():
            setattr(instance, key, value)
        await instance.save()
        return instance, False
    except model.DoesNotExist:
        params = {**kwargs, **defaults}
        instance = await model.create(**params)
        return instance, True


async def increment(model, filters, **kwargs):
    updates = {}
    for field, amount in kwargs.items():
        updates[field] = F(field) + amount
    return await update(model, filters, **updates)


async def decrement(model, filters, **kwargs):
    updates = {}
    for field, amount in kwargs.items():
        updates[field] = F(field) - amount
    return await update(model, filters, **updates)


async def update_instance(instance, fields=None):
    model_class = instance.__class__
    pk_list = model_class._meta.primary_keys
    if not pk_list:
        raise ValueError(f"Cannot update {model_class.__name__} with no primary key.")
    pk_name = pk_list[0]
    pk_value = getattr(instance, pk_name, None)
    if pk_value is None:
        raise ValueError(f"Cannot update {model_class.__name__}, {pk_name} is None")

    update_data = {}
    # If fields is specified, only update those; otherwise, update all non-None fields
    field_names = (
        fields
        if fields is not None
        else [f for f in model_class._fields if f != pk_name]
    )
    for field_name in field_names:
        if field_name == pk_name:
            continue
        value = getattr(instance, field_name, None)
        if value is not None:  # Only include non-None values
            field = model_class._fields[field_name]
            update_data[field_name] = field.get_db_prep_value(value)

    filters = {pk_name: pk_value}

    if debug:
        vcprint(
            f"Updating instance with filters: {filters}", verbose=debug, color="cyan"
        )
        vcprint(f"Update data: {update_data}", verbose=debug, color="cyan")

    result = await update(model_class, filters, **update_data)

    if result["rows_affected"] == 0:
        raise ValueError(
            f"No rows were updated for {model_class.__name__} with {pk_name}={pk_value}"
        )

    if result["updated_rows"]:
        for key, value in result["updated_rows"][0].items():
            setattr(instance, key, value)

    return instance
