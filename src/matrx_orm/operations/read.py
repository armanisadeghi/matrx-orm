from ..query.builder import QueryBuilder


async def get(model_cls, *args, **kwargs):
    return await QueryBuilder(model_cls).filter(*args, **kwargs).get()


async def filter(model_cls, *args, **kwargs):
    return QueryBuilder(model_cls).filter(*args, **kwargs)


async def exclude(model_cls, *args, **kwargs):
    return QueryBuilder(model_cls).exclude(*args, **kwargs)


async def all(model_cls):
    return QueryBuilder(model_cls)


async def count(model_cls, *args, **kwargs):
    return await QueryBuilder(model_cls).filter(*args, **kwargs).count()


async def exists(model_cls, *args, **kwargs):
    return await QueryBuilder(model_cls).filter(*args, **kwargs).exists()


async def first(model_cls, *args, **kwargs):
    return await QueryBuilder(model_cls).filter(*args, **kwargs).first()


async def last(model_cls, *args, **kwargs):
    return await QueryBuilder(model_cls).filter(*args, **kwargs).last()


async def values(model_cls, *fields, **kwargs):
    return await QueryBuilder(model_cls).filter(**kwargs).values(*fields)


async def values_list(model_cls, *fields, flat=False, **kwargs):
    return await QueryBuilder(model_cls).filter(**kwargs).values_list(*fields, flat=flat)


async def in_bulk(model_cls, id_list, field="id"):
    objects = await QueryBuilder(model_cls).filter(**{f"{field}__in": id_list}).all()
    # Turn that list into a dict
    return {getattr(obj, field): obj for obj in objects}


async def iterator(model_cls, chunk_size=2000, **kwargs):
    qb = QueryBuilder(model_cls).filter(**kwargs)
    start, end = 0, chunk_size
    while True:
        chunk = await qb[start:end].all()
        if not chunk:
            break
        for item in chunk:
            yield item
        start, end = end, end + chunk_size
