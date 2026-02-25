# Matrx ORM Reserved Names

This document lists all reserved parameter and attribute names in the Matrx ORM that should **NOT** be used as field names in your models to avoid conflicts.
 
## Critical: Why This Matters

Using reserved names as field names in your models will cause errors because they conflict with internal ORM parameters and methods. For example, a field named `model` would conflict with the `model_cls` parameter used throughout the ORM's internal operations.

---

## Reserved Field Names

### ❌ DO NOT USE These Field Names

The following names are **forbidden** as field names in your models:

#### Internal ORM Parameters
- `model_cls` - Used internally to pass model classes to operations
- `instance` - Used for model instance operations
- `database` - Used for database connection management
- `query` - Used for query building
- `executor` - Used for query execution
- `filters` - Used for query filtering
- `kwargs` - Used for keyword arguments in operations

#### Model Class Attributes (Reserved by Base Model)
- `_meta` - Model metadata container
- `_fields` - Dictionary of model fields
- `_cache_policy` - Cache configuration
- `_cache_timeout` - Cache timeout setting
- `_realtime_updates` - Real-time update flag
- `_table_name` - Database table name
- `_database` - Database name
- `_indexes` - Index definitions
- `_unique_together` - Unique constraint definitions
- `_constraints` - Additional constraints
- `_inverse_foreign_keys` - Inverse foreign key relationships
- `_primary_keys` - Primary key field names
- `_dynamic_fields` - Dynamic relationship fields
- `_extra_data` - Extra data storage
- `_dynamic_data` - Dynamic relationship data

#### Model Instance Methods (Reserved by Base Model)
- `save` - Save instance to database
- `update` - Update instance fields
- `delete` - Delete instance from database
- `create` - Class method to create new instance
- `get` - Class method to retrieve instance
- `filter` - Class method to filter instances
- `all` - Class method to get all instances
- `bulk_create` - Class method for bulk creation
- `bulk_update` - Class method for bulk updates
- `bulk_delete` - Class method for bulk deletion
- `get_or_none` - Class method to get or return None
- `get_or_create` - Get existing or create new instance
- `update_or_create` - Update existing or create new instance
- `get_by_id` - Get instance by ID
- `get_many` - Get multiple instances
- `update_fields` - Update specific fields
- `to_dict` - Convert instance to dictionary
- `to_flat_dict` - Convert instance to flat dictionary
- `from_db_result` - Create instance from database result
- `get_cache_key` - Get cache key for instance
- `get_field` - Get field definition
- `get_relation` - Get relationship definition
- `get_related` - Get related data
- `set_related` - Set related data
- `has_related` - Check if related data is loaded
- `fetch_fk` - Fetch foreign key relationship
- `fetch_ifk` - Fetch inverse foreign key relationship
- `fetch_fks` - Fetch all foreign key relationships
- `fetch_ifks` - Fetch all inverse foreign key relationships
- `fetch_all_related` - Fetch all related data
- `fetch_one_relation` - Fetch one relationship
- `filter_fk` - Filter foreign key relationship
- `filter_ifk` - Filter inverse foreign key relationship
- `filter_one_relation` - Filter one relationship
- `get_database_name` - Get database name

#### Exception Classes (Reserved by Base Model)
- `DoesNotExist` - Exception for missing records
- `MultipleObjectsReturned` - Exception for multiple results
- `ValidationError` - Exception for validation errors

#### Runtime Container Attributes
- `runtime` - Runtime data container
- `dto` - Data transfer object (legacy — superseded by ModelView)

#### ModelView Instance Stores (set by ModelView.apply())
- `_view_data` - Flat dict of computed field values and inline FK objects
- `_view_excluded` - Set of model field names suppressed from to_dict() output
- `_view_inlined_fks` - Maps FK field name → output name for inlined FK objects
- `_applied_view` - The ModelView class last applied to this instance (or None)

---

## Safe Naming Conventions

### ✅ DO USE These Patterns

Instead of reserved names, use descriptive field names that clearly indicate their purpose:

#### Good Examples
```python
from matrx_orm import Model, Field

class User(Model):
    _table_name = "users"
    _database = "main"
    
    # Good field names - clear and not reserved
    user_id = Field(primary_key=True)
    user_name = Field()
    user_email = Field()
    user_model_preference = Field()  # Instead of 'model'
    user_database_name = Field()     # Instead of 'database'
    query_count = Field()             # Instead of 'query'
    filter_preferences = Field()      # Instead of 'filters'
```

#### Bad Examples (DO NOT DO THIS)
```python
# ❌ BAD - These will cause conflicts
class User(Model):
    model = Field()      # Conflicts with model_cls parameter
    database = Field()   # Conflicts with database parameter
    query = Field()      # Conflicts with query parameter
    filters = Field()    # Conflicts with filters parameter
    save = Field()       # Conflicts with save() method
    update = Field()     # Conflicts with update() method
```

---

## Technical Details

### Why `model_cls` Instead of `model`?

The ORM uses `model_cls` (model class) as the parameter name throughout all operations to avoid conflicts with potential field names. This naming convention:

1. **Prevents Field Name Conflicts**: Users can't accidentally create a field named `model_cls` (it's not a natural field name)
2. **Maintains Clarity**: The `_cls` suffix clearly indicates it's a class reference, not an instance
3. **Follows Python Conventions**: Similar to `cls` parameter in class methods

### Internal Usage Pattern

All ORM operations follow this pattern:

```python
# Operations receive model_cls parameter
async def create(model_cls, **kwargs):
    instance = model_cls(**kwargs)
    return await save(instance)

# QueryBuilder stores it as self.model internally
class QueryBuilder:
    def __init__(self, model_cls, database=None):
        self.model = model_cls  # Internal storage is fine
        # ...
```

---

## Checking for Conflicts

If you're unsure whether a field name is safe, follow these rules:

1. **Avoid any name starting with underscore** (`_`) - these are reserved for internal use
2. **Avoid any name matching a Model class method** - check the list above
3. **When in doubt, add a prefix** - e.g., `user_model` instead of `model`
4. **Use descriptive names** - `user_email` is better than `email` anyway

---

## Version History

- **v1.0.0** (2026-02-10): Initial documentation with `model` → `model_cls` refactoring
  - Renamed all `model` parameters to `model_cls` across operations
  - Updated QueryBuilder to use `model_cls` parameter
  - Maintained backward compatibility for internal `self.model` usage

---

## Questions or Issues?

If you encounter a naming conflict not listed here, please:

1. Check if the name is a Python built-in or keyword
2. Review your model's field names for conflicts
3. Consider using a more descriptive name with a prefix
4. Report the issue if you believe it's a bug in the ORM

---

**Last Updated**: February 25, 2026
