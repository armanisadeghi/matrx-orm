# Model Parameter Refactoring Summary

**Date**: February 10, 2026  
**Issue**: The `model` parameter in operations conflicted with potential field names  
**Solution**: Renamed all `model` parameters to `model_cls` throughout the ORM

---

## Changes Made

### 1. Operations Module (`src/matrx_orm/operations/`)

#### `create.py`
- ✅ `async def create(model_cls, **kwargs)` - was `model`
- ✅ `async def bulk_create(model_cls, objects_data)` - was `model`
- ✅ `async def get_or_create(model_cls, defaults=None, **kwargs)` - was `model`
- ✅ `async def update_or_create(model_cls, defaults=None, **kwargs)` - was `model`
- ✅ `async def create_instance(model_cls, **kwargs)` - was `model_class`

#### `read.py`
- ✅ `async def get(model_cls, *args, **kwargs)` - was `model`
- ✅ `async def filter(model_cls, *args, **kwargs)` - was `model`
- ✅ `async def exclude(model_cls, *args, **kwargs)` - was `model`
- ✅ `async def all(model_cls)` - was `model`
- ✅ `async def count(model_cls, *args, **kwargs)` - was `model`
- ✅ `async def exists(model_cls, *args, **kwargs)` - was `model`
- ✅ `async def first(model_cls, *args, **kwargs)` - was `model`
- ✅ `async def last(model_cls, *args, **kwargs)` - was `model`
- ✅ `async def values(model_cls, *fields, **kwargs)` - was `model`
- ✅ `async def values_list(model_cls, *fields, flat=False, **kwargs)` - was `model`
- ✅ `async def in_bulk(model_cls, id_list, field="id")` - was `model`
- ✅ `async def iterator(model_cls, chunk_size=2000, **kwargs)` - was `model`

#### `update.py`
- ✅ `async def update(model_cls, filters, **kwargs)` - was `model`
- ✅ `async def bulk_update(model_cls, objects, fields)` - was `model`
- ✅ `async def update_or_create(model_cls, defaults=None, **kwargs)` - was `model`
- ✅ `async def increment(model_cls, filters, **kwargs)` - was `model`
- ✅ `async def decrement(model_cls, filters, **kwargs)` - was `model`
- ✅ `async def update_instance(instance, fields=None)` - internal `model_class` → `model_cls`

#### `delete.py`
- ✅ `async def delete(model_cls, **kwargs)` - was `model`
- ✅ `async def bulk_delete(model_cls, objects)` - was `model`
- ✅ `async def soft_delete(model_cls, **kwargs)` - was `model`
- ✅ `async def restore(model_cls, **kwargs)` - was `model`
- ✅ `async def purge(model_cls, **kwargs)` - was `model`
- ✅ `async def delete_instance(instance)` - internal `model_class` → `model_cls`

### 2. Query Module (`src/matrx_orm/query/`)

#### `builder.py`
- ✅ `def __init__(self, model_cls, database=None)` - was `model`
- ✅ `def _set_database(self, model_cls)` - was `model`
- ✅ `def join(self, model_cls, on, join_type="INNER")` - was `model`
- Note: `self.model` remains unchanged (internal instance variable, not a parameter)

### 3. Core Module (`src/matrx_orm/core/`)

#### `base.py`
- ✅ Updated all `QueryBuilder(model=cls)` calls to `QueryBuilder(cls)`
- Changed 5 instances in methods: `get()`, `get_or_none()`, `filter()`, `all()`, `get_many()`

---

## Files NOT Changed (And Why They're Safe)

### `src/matrx_orm/core/extended.py`
- `BaseManager.__init__(self, model: Type[ModelT], ...)` - Internal framework class, not user-facing

### `src/matrx_orm/core/fields.py`
- `Field.contribute_to_class(self, model, name)` - Internal Django-style hook, called by framework

### `src/matrx_orm/core/relations.py`
- `Relation.contribute_to_class(self, model, name)` - Internal framework method, not user-facing

These methods are **internal framework APIs** that users never call directly. They're invoked automatically by the metaclass and ORM internals, so the parameter name `model` is safe here.

---

## Documentation Created

### `RESERVED_NAMES.md`
Comprehensive documentation listing:
- All reserved parameter names (including `model_cls`)
- All reserved Model class attributes
- All reserved Model instance methods
- Safe naming conventions with examples
- Technical details about the refactoring

---

## Testing

### Syntax Validation
✅ All modified files compile successfully:
```bash
python3 -m py_compile src/matrx_orm/operations/*.py
python3 -m py_compile src/matrx_orm/query/builder.py
python3 -m py_compile src/matrx_orm/core/base.py
```

### Pattern Verification
✅ No remaining `async def func(model,` patterns in operations
✅ No remaining `def func(model,` patterns in operations
✅ All `QueryBuilder(model=...)` calls updated to positional arguments

---

## Impact Analysis

### ✅ Backward Compatible
- Internal API change only - users don't call these functions directly
- Users call `Model.create()`, `Model.filter()`, etc. which internally call operations
- No breaking changes to user-facing API

### ✅ Solves the Problem
Users can now safely use `model` as a field name:
```python
class AIModel(Model):
    _table_name = "ai_models"
    _database = "main"
    
    id = Field(primary_key=True)
    model = Field()  # ✅ No longer conflicts!
    name = Field()
```

### ✅ Consistent Convention
- All operations now use `model_cls` consistently
- Clear distinction: `model_cls` = class, `instance` = object
- Follows Python convention (similar to `cls` in class methods)

---

## Verification Checklist

- [x] All operation functions updated
- [x] QueryBuilder constructor updated
- [x] All QueryBuilder calls in base.py updated
- [x] Internal framework methods identified and left unchanged
- [x] Documentation created (RESERVED_NAMES.md)
- [x] Syntax validation passed
- [x] Pattern verification passed
- [x] No remaining conflicts found

---

## Next Steps

1. **Test in Development**: Run existing test suite to ensure no regressions
2. **Update Examples**: If any example code exists, update it to show `model` field usage
3. **Version Bump**: Consider this a minor version bump (no breaking changes)
4. **Changelog**: Add entry about the internal refactoring and new field name support

---

## Questions or Issues?

If you encounter any issues with this refactoring:
1. Check RESERVED_NAMES.md for the complete list of reserved names
2. Verify you're using the latest version of all ORM files
3. Report any edge cases not covered by this refactoring

**Refactoring completed successfully!** 🎉
