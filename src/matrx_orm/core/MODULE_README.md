# `src.matrx_orm.core` — Module Overview

> This document is partially auto-generated. Sections tagged `<!-- AUTO:id -->` are refreshed by the generator.
> Everything else is yours to edit freely and will never be overwritten.

<!-- AUTO:meta -->
## About This Document

This file is **partially auto-generated**. Sections wrapped in `<!-- AUTO:id -->` tags
are overwritten each time the generator runs. Everything else is yours to edit freely.

| Field | Value |
|-------|-------|
| Module | `src/matrx_orm/core` |
| Last generated | 2026-02-28 13:57 |
| Output file | `src/matrx_orm/core/MODULE_README.md` |
| Signature mode | `signatures` |

**To refresh auto-sections:**
```bash
python utils/code_context/generate_module_readme.py src/matrx_orm/core --mode signatures
```

**To add permanent notes:** Write anywhere outside the `<!-- AUTO:... -->` blocks.
<!-- /AUTO:meta -->

<!-- HUMAN-EDITABLE: This section is yours. Agents & Humans can edit this section freely — it will not be overwritten. -->

## Architecture

> **Fill this in.** Describe the execution flow and layer map for this module.
> See `utils/code_context/MODULE_README_SPEC.md` for the recommended format.
>
> Suggested structure:
>
> ### Layers
> | File | Role |
> |------|------|
> | `entry.py` | Public entry point — receives requests, returns results |
> | `engine.py` | Core dispatch logic |
> | `models.py` | Shared data types |
>
> ### Call Flow (happy path)
> ```
> entry_function() → engine.dispatch() → implementation()
> ```


<!-- AUTO:tree -->
## Directory Tree

> Auto-generated. 15 files across 1 directories.

```
src/matrx_orm/core/
├── MODULE_README.md
├── __init__.py
├── async_db_manager.py
├── base.py
├── config.py
├── expressions.py
├── extended.py
├── fields.py
├── model_view.py
├── paginator.py
├── registry.py
├── relations.py
├── signals.py
├── transaction.py
├── types.py
# excluded: 4 .md
```
<!-- /AUTO:tree -->

<!-- AUTO:signatures -->
## API Signatures

> Auto-generated via `output_mode="signatures"`. ~5-10% token cost vs full source.
> For full source, open the individual files directly.

```
---
Filepath: src/matrx_orm/core/config.py  [python]

  class DatabaseConfigError(Exception):
  class DatabaseProjectConfig:
  class DatabaseRegistry:
      def __new__(cls)
      def __init__(self) -> None
      def register(self, config: DatabaseProjectConfig) -> None
      def get_database_config(self, config_name: str) -> dict
      def get_config_dataclass(self, config_name: str) -> DatabaseProjectConfig
      def get_manager_config_by_project_name(self, config_name)
      def get_all_database_configs(self) -> dict[str, dict[str, Any]]
      def get_all_database_project_names(self) -> list[str]
      def get_all_database_projects(self) -> list[dict]
      def get_all_database_projects_redacted(self) -> list[dict[str, Any]]
      def get_database_alias(self, db_project)
  def get_manager_config(config_name: str) -> dict
  def register_database(config: DatabaseProjectConfig) -> None
  def register_database_from_env(name: str, env_prefix: str, alias: str = '', additional_schemas: list[str] | None = None, entity_overrides: dict[str, Any] | None = None, field_overrides: dict[str, Any] | None = None, manager_config_overrides: dict[str, Any] | None = None, env_var_overrides: dict[str, str] | None = None) -> bool
  def get_connection_string(config_name: str) -> str
  def get_schema_builder_overrides(db_project: str) -> dict[str, dict[str, Any]]
  def get_code_config(db_project: str) -> dict[str, Any]


---
Filepath: src/matrx_orm/core/__init__.py  [python]



---
Filepath: src/matrx_orm/core/signals.py  [python]

  class Signal:
      def __init__(self, name: str) -> None
      def connect(self, receiver: Callable[..., Any]) -> Callable[..., Any]
      def disconnect(self, receiver: Callable[..., Any]) -> None
      async def send(self, sender: Any, **kwargs: Any) -> list[tuple[Callable[..., Any], Any]]
      def __repr__(self) -> str


---
Filepath: src/matrx_orm/core/fields.py  [python]

  class Field:
      def __init__(self, db_type: str, is_native: bool = True, null: bool = True, nullable: bool | None = None, unique: bool = False, primary_key: bool = False, default: Any = None, index: bool = False, validators: list[Any] | None = None, **kwargs: Any)
      def contribute_to_class(self, model, name)
      def get_default(self)
      async def validate(self, value) -> None
      def to_python(self, value: Any) -> Any
      def from_db_value(self, value: Any) -> Any
      def get_db_prep_value(self, value: Any) -> Any
      def desc(self)
      def asc(self)
      def to_dict(self) -> dict
  class UUIDField(Field):
      def __init__(self, **kwargs)
      def get_default(self)
      def to_python(self, value)
      def from_db_value(self, value)
  class UUIDFieldREAL(Field):
      def __init__(self, **kwargs)
      def get_default(self)
      def to_python(self, value)
      def from_db_value(self, value)
      async def validate(self, value)
  class CharField(Field):
      def __init__(self, max_length: int = 255, **kwargs)
      def get_db_prep_value(self, value)
      async def validate(self, value: str | None) -> None
  class TextField(Field):
      def __init__(self, **kwargs)
      def get_db_prep_value(self, value)
      async def validate(self, value: str | None) -> None
  class IntegerField(Field):
      def __init__(self, **kwargs)
      def to_python(self, value)
      def get_db_prep_value(self, value)
      async def validate(self, value: int | None) -> None
  class FloatField(Field):
      def __init__(self, **kwargs)
      def get_db_prep_value(self, value)
      async def validate(self, value: float | int | None) -> None
  class BooleanField(Field):
      def __init__(self, **kwargs)
      async def validate(self, value: bool | None) -> None
      def to_python(self, value)
      def get_db_prep_value(self, value)
  class DateTimeField(Field):
      def __init__(self, auto_now: bool = False, auto_now_add: bool = False, **kwargs)
      def to_python(self, value)
      def get_db_prep_value(self, value)
  class TimeField(Field):
      def __init__(self, **kwargs)
      def to_python(self, value)
      def get_db_prep_value(self, value)
  class DateField(Field):
      def __init__(self, **kwargs)
      def to_python(self, value)
      def get_db_prep_value(self, value)
  class JSONField(Field, Generic[_JT]):
      def __init__(self, **kwargs)
      def to_python(self, value)
      def get_db_prep_value(self, value)
  class ArrayField(Field):
      def __init__(self, item_type: Field, **kwargs)
      async def validate(self, value: list[Any] | None) -> None
      def to_python(self, value: list[Any] | None) -> list[Any] | None
      def get_db_prep_value(self, value: list[Any] | None) -> list[Any] | None
  class EnumField(Field):
      def __init__(self, enum_class: type[PythonEnum] | None = None, choices: list[str] | None = None, max_length: int = 255, **kwargs: Any)
      def get_db_prep_value(self, value: str | PythonEnum | None) -> str | None
      def to_python(self, value: str | None) -> PythonEnum | str | None
      async def validate(self, value: str | PythonEnum | None) -> None
      def to_dict(self) -> dict
  class IPv4Field(Field):
      def __init__(self, **kwargs)
      async def validate(self, value: str) -> None
  class IPv6Field(Field):
      def __init__(self, **kwargs)
      async def validate(self, value: str) -> None
  class MacAddressField(Field):
      def __init__(self, **kwargs)
      async def validate(self, value: str) -> None
  class EmailField(CharField):
      def __init__(self, **kwargs)
      async def validate_email(value: str) -> None
  class DecimalField(Field):
      def __init__(self, max_digits: int | None = None, decimal_places: int = 2, **kwargs: Any)
      def to_python(self, value)
      def get_db_prep_value(self, value)
      async def validate(self, value: Decimal | int | float | str | None) -> None
  class BigIntegerField(Field):
      def __init__(self, **kwargs)
      def to_python(self, value)
      def get_db_prep_value(self, value)
      async def validate(self, value: int | None) -> None
  class SmallIntegerField(Field):
      def __init__(self, **kwargs)
      def to_python(self, value)
      def get_db_prep_value(self, value)
      async def validate(self, value: int | None) -> None
  class BinaryField(Field):
      def __init__(self, **kwargs)
      async def validate(self, value: bytes | bytearray | None) -> None
  class SlugField(CharField):
      def __init__(self, max_length: int = 200, **kwargs)
      async def validate(self, value: str | None) -> None
  class IPNetworkField(Field):
      def __init__(self, **kwargs)
      async def validate(self, value: str) -> None
  class MoneyField(DecimalField):
      def __init__(self, max_digits: int = 19, decimal_places: int = 2, **kwargs)
  class HStoreField(Field):
      def __init__(self, **kwargs)
      def to_python(self, value)
      def get_db_prep_value(self, value)
      async def validate(self, value: dict[str, str | None] | None) -> None
  class JSONBField(Field, Generic[_JT]):
      def __init__(self, **kwargs)
      def to_python(self, value)
      def get_db_prep_value(self, value)
  class FileField(CharField):
      def __init__(self, max_length: int = 100, **kwargs)
      async def validate(self, value: str | None) -> None
  class TimeDeltaField(Field):
      def __init__(self, **kwargs)
      def to_python(self, value)
      def get_db_prep_value(self, value)
      async def validate(self, value) -> None
  class UUIDArrayField(ArrayField):
      def __init__(self, **kwargs)
  class PointField(Field):
      def __init__(self, **kwargs)
      def to_python(self, value)
      def get_db_prep_value(self, value)
      async def validate(self, value)
  class RangeField(Field):
      def __init__(self, range_type: str, **kwargs)
      async def validate(self, value)
  class CITextField(CharField):
      def __init__(self, **kwargs)
  class PrimitiveArrayField(Field):
      def __init__(self, element_type: str, **kwargs)
      async def validate(self, value: list[Any] | None) -> None
  class JSONBArrayField(ArrayField):
      def __init__(self, **kwargs)
  class HStoreArrayField(ArrayField):
      def __init__(self, **kwargs)
  class TextArrayField(ArrayField):
      def __init__(self, **kwargs)
  class IntegerArrayField(ArrayField):
      def __init__(self, **kwargs)
  class BooleanArrayField(ArrayField):
      def __init__(self, **kwargs)
  class DecimalArrayField(ArrayField):
      def __init__(self, max_digits: int, decimal_places: int, **kwargs)
  class DateArrayField(ArrayField):
      def __init__(self, **kwargs)
  class IPv6ArrayField(ArrayField):
      def __init__(self, **kwargs)
  class IPNetworkArrayField(ArrayField):
      def __init__(self, **kwargs)
  class TimeArrayField(ArrayField):
      def __init__(self, **kwargs)
  class ImageField(FileField):
      def __init__(self, max_length: int = 100, **kwargs)
      async def validate(self, value: str | None) -> None
  class IPAddressField(Field):
      def __init__(self, **kwargs)
      async def validate(self, value: str) -> None
  class ForeignKey(Field):
      def __init__(self, to_model: str | type, to_column: str, related_name: str | None = None, on_delete: str = 'CASCADE', on_update: str = 'CASCADE', to_db: str | None = None, to_schema: str | None = None, **kwargs: Any)
      def to_python(self, value)
      def from_db_value(self, value)
      def get_db_prep_value(self, value)
      async def validate(self, value) -> None
  class CompositeField(Field):
      def __init__(self, fields, **kwargs)
      async def validate(self, value: tuple[Any, ...] | None) -> None
      def to_python(self, value) -> tuple | None
      def get_db_prep_value(self, value)
  class VersionField(Field):
      def __init__(self, **kwargs) -> None
      def to_python(self, value) -> int
      def get_db_prep_value(self, value)
  class VectorField(Field):
      def __init__(self, dimensions: int, dtype: str = 'float32', **kwargs) -> None
      def to_python(self, value) -> list[float] | None
      def get_db_prep_value(self, value) -> str | None
      async def validate(self, value) -> None
  def __get__(self, obj: None, objtype: type = ...) -> Field
  def __get__(self, obj: object, objtype: type = ...) -> Any
  def __get__(self, obj: object | None, objtype: type = ...) -> Any
  def __get__(self, obj: None, objtype: type = ...) -> UUIDField
  def __get__(self, obj: object, objtype: type = ...) -> str | None
  def __get__(self, obj: object | None, objtype: type = ...) -> str | UUIDField | None
  def __get__(self, obj: None, objtype: type = ...) -> CharField
  def __get__(self, obj: object, objtype: type = ...) -> str | None
  def __get__(self, obj: object | None, objtype: type = ...) -> str | CharField | None
  def __get__(self, obj: None, objtype: type = ...) -> TextField
  def __get__(self, obj: object, objtype: type = ...) -> str | None
  def __get__(self, obj: object | None, objtype: type = ...) -> str | TextField | None
  def __get__(self, obj: None, objtype: type = ...) -> IntegerField
  def __get__(self, obj: object, objtype: type = ...) -> int | None
  def __get__(self, obj: object | None, objtype: type = ...) -> int | IntegerField | None
  def __get__(self, obj: None, objtype: type = ...) -> FloatField
  def __get__(self, obj: object, objtype: type = ...) -> float | None
  def __get__(self, obj: object | None, objtype: type = ...) -> float | FloatField | None
  def __get__(self, obj: None, objtype: type = ...) -> BooleanField
  def __get__(self, obj: object, objtype: type = ...) -> bool | None
  def __get__(self, obj: object | None, objtype: type = ...) -> bool | BooleanField | None
  def __get__(self, obj: None, objtype: type = ...) -> DateTimeField
  def __get__(self, obj: object, objtype: type = ...) -> datetime | None
  def __get__(self, obj: object | None, objtype: type = ...) -> datetime | DateTimeField | None
  def __get__(self, obj: None, objtype: type = ...) -> TimeField
  def __get__(self, obj: object, objtype: type = ...) -> time | None
  def __get__(self, obj: object | None, objtype: type = ...) -> time | TimeField | None
  def __get__(self, obj: None, objtype: type = ...) -> DateField
  def __get__(self, obj: object, objtype: type = ...) -> date | None
  def __get__(self, obj: object | None, objtype: type = ...) -> date | DateField | None
  def __get__(self, obj: None, objtype: type = ...) -> 'JSONField[_JT]'
  def __get__(self, obj: object, objtype: type = ...) -> _JT | None
  def __get__(self, obj: object | None, objtype: type = ...) -> _JT | None | 'JSONField[_JT]'
  def __set__(self, obj: object, value: _JT | None) -> None
  def __get__(self, obj: None, objtype: type = ...) -> ArrayField
  def __get__(self, obj: object, objtype: type = ...) -> list[Any] | None
  def __get__(self, obj: object | None, objtype: type = ...) -> list[Any] | ArrayField | None
  def __get__(self, obj: None, objtype: type = ...) -> DecimalField
  def __get__(self, obj: object, objtype: type = ...) -> Decimal | None
  def __get__(self, obj: object | None, objtype: type = ...) -> Decimal | DecimalField | None
  def __get__(self, obj: None, objtype: type = ...) -> BigIntegerField
  def __get__(self, obj: object, objtype: type = ...) -> int | None
  def __get__(self, obj: object | None, objtype: type = ...) -> int | BigIntegerField | None
  def __get__(self, obj: None, objtype: type = ...) -> SmallIntegerField
  def __get__(self, obj: object, objtype: type = ...) -> int | None
  def __get__(self, obj: object | None, objtype: type = ...) -> int | SmallIntegerField | None
  def __get__(self, obj: None, objtype: type = ...) -> BinaryField
  def __get__(self, obj: object, objtype: type = ...) -> bytes | None
  def __get__(self, obj: object | None, objtype: type = ...) -> bytes | BinaryField | None
  def __get__(self, obj: None, objtype: type = ...) -> HStoreField
  def __get__(self, obj: object, objtype: type = ...) -> dict[str, str | None] | None
  def __get__(self, obj: object | None, objtype: type = ...) -> dict[str, str | None] | HStoreField | None
  def __get__(self, obj: None, objtype: type = ...) -> 'JSONBField[_JT]'
  def __get__(self, obj: object, objtype: type = ...) -> _JT | None
  def __get__(self, obj: object | None, objtype: type = ...) -> _JT | None | 'JSONBField[_JT]'
  def __set__(self, obj: object, value: _JT | None) -> None
  def __get__(self, obj: None, objtype: type = ...) -> TimeDeltaField
  def __get__(self, obj: object, objtype: type = ...) -> timedelta | None
  def __get__(self, obj: object | None, objtype: type = ...) -> timedelta | TimeDeltaField | None


---
Filepath: src/matrx_orm/core/base.py  [python]

  class RuntimeContainer:
      def __init__(self) -> None
      def __getattr__(self, name: str) -> Any
      def __setattr__(self, name: str, value: Any) -> None
      def set_relationship(self, name: str, value: Any) -> None
      def to_dict(self) -> dict[str, Any]
  class RuntimeMixin:
      def __init__(self, *args: Any, **kwargs: Any) -> None
      def _initialize_runtime(self) -> None
      def to_dict(self) -> dict[str, Any]
  class ModelOptions:
      def qualified_table_name(self) -> str
  class ModelMeta(type):
      def __new__(mcs, name: str, bases: tuple[type, ...], attrs: dict[str, Any]) -> ModelMeta
  class Model(RuntimeMixin):
      def __init__(self, **kwargs: Any) -> None
      def get_database_name(cls) -> str
      async def create(cls, **kwargs: Any) -> Model
      async def bulk_create(cls, objects_data: list[dict[str, Any]]) -> list[Model]
      async def bulk_update(cls, objects: Sequence[Model], fields: list[str]) -> int
      async def bulk_delete(cls, objects: Sequence[Model]) -> int
      async def upsert(cls, data: dict[str, Any], conflict_fields: list[str], update_fields: list[str] | None = None) -> Model
      async def bulk_upsert(cls, objects_data: list[dict[str, Any]], conflict_fields: list[str], update_fields: list[str] | None = None) -> list[Model]
      async def count(cls, **kwargs: Any) -> int
      def count_sync(cls, **kwargs: Any) -> int
      async def exists(cls, **kwargs: Any) -> bool
      def exists_sync(cls, **kwargs: Any) -> bool
      async def update_where(cls, filters: dict[str, Any], **updates: Any) -> UpdateResult
      async def delete_where(cls, **filters: Any) -> int
      async def get(cls, use_cache: bool = True, **kwargs: Any) -> Model
      def get_sync(cls, use_cache: bool = True, **kwargs: Any) -> Model
      async def get_or_none(cls, use_cache: bool = True, **kwargs: Any) -> Model | None
      def get_or_none_sync(cls, use_cache: bool = True, **kwargs: Any) -> Model | None
      def filter(cls, *args: Any, **kwargs: Any) -> QueryBuilder
      async def raw(cls, sql: str, *params: Any) -> list[Model]
      async def raw_sql(cls, sql: str, *params: Any) -> list[dict[str, Any]]
      def filter_sync(cls, **kwargs: Any) -> list[Model]
      async def all(cls) -> list[Self]
      def all_sync(cls) -> list[Self]
      async def save(self, **kwargs: Any) -> Self
      async def update(self, **kwargs: Any) -> Self
      async def update_fields(cls, instance_or_id: Model | Any, **kwargs: Any) -> Model | None
      async def delete(self) -> None
      def get_cache_key(self) -> str
      def table_name(self) -> Any
      def get_field(cls, field_name: str) -> Field | None
      def get_relation(cls, field_name: str) -> ForeignKeyReference | InverseForeignKeyReference
      def _serialize_value(self, value: Any) -> Any
      def to_dict(self) -> dict[str, Any]
      def to_flat_dict(self) -> dict[str, Any]
      def from_db_result(cls, data: dict[str, Any]) -> Model
      async def fetch_fk(self, field_name: str) -> Model | None
      def _check_double_s_typo(self, field_name: str, method_name: str) -> None
      async def fetch_ifk(self, field_name: str) -> list[Model]
      async def fetch_one_relation(self, field_name: str) -> Model | list[Model] | None
      async def fetch_fks(self) -> ForeignKeyResults[Model]
      async def fetch_ifks(self) -> InverseForeignKeyResults[Model]
      async def fetch_m2m(self, relation_name: str) -> list[Model]
      async def fetch_m2ms(self) -> ManyToManyResults[Model]
      async def add_m2m(self, relation_name: str, *target_ids: Any) -> int
      async def remove_m2m(self, relation_name: str, *target_ids: Any) -> int
      async def set_m2m(self, relation_name: str, target_ids: list[Any]) -> None
      async def clear_m2m(self, relation_name: str) -> int
      async def fetch_all_related(self) -> AllRelatedResults[Model]
      async def filter_fk(self, field_name: str, **kwargs: Any) -> list[Model]
      async def filter_ifk(self, field_name: str, **kwargs: Any) -> list[Model]
      async def filter_one_relation(self, field_name: str, **kwargs: Any) -> list[Model]
      def set_related(self, field_name: str, value: Any, is_inverse: bool = False, is_m2m: bool = False) -> None
      def get_related(self, field_name: str) -> Any
      def has_related(self, field_name: str) -> bool
      async def get_by_id(cls, id_value: Any, use_cache: bool = True) -> Model
      async def ensure_m2m_tables(cls) -> None
      async def get_many(cls, **kwargs: Any) -> list[Self]
  def _to_snake_case(name: str) -> str
  def formated_error(message: str, class_name: str | None = None, method_name: str | None = None, context: Any = None) -> None
  async def _safe_fetch_fk(field_name: str) -> tuple[str, Model | None]
  async def _safe_fetch_ifk(field_name: str) -> tuple[str, list[Model] | None]
  async def _safe_fetch_m2m(relation_name: str) -> tuple[str, list[Model]]


---
Filepath: src/matrx_orm/core/extended.py  [python]

  ModelT = TypeVar('ModelT', bound=Model)
  class BaseDTO:
      async def from_model(cls, model: Model) -> BaseDTO
      async def _initialize_dto(self, model: Model) -> None
      def _get_error_context(self) -> dict[str, str]
      def _report_error(self, message: str, error_type: str = 'GenericError', client_visible: str | None = None) -> AppError
      def __getattr__(self, name: str) -> Any
      async def fetch_fk(self, field_name: str) -> Model | None
      async def fetch_ifk(self, field_name: str) -> list[Model]
      async def fetch_one_relation(self, field_name: str) -> Model | list[Model] | None
      async def filter_fk(self, field_name: str, **kwargs: Any) -> list[Model]
      async def filter_ifk(self, field_name: str, **kwargs: Any) -> list[Model]
      def _serialize_value(self, value: Any, visited: set[int]) -> Any
      def to_dict(self, visited: set[int] | None = None) -> dict[str, Any]
      def print_keys(self) -> None
      def __repr__(self) -> str
  class BaseManager(Generic[ModelT]):
      def __init__(self, model: type[ModelT], dto_class: type[BaseDTO] | None = None, view_class: type | None = None, fetch_on_init_limit: int = 0, FETCH_ON_INIT_WITH_WARNINGS_OFF: str | None = None) -> None
      def _initialize_manager(self) -> None
      def _get_error_context(self) -> dict[str, str]
      def _report_error(self, message: str, error_type: str = 'GenericError', client_visible: str | None = None) -> AppError
      async def _initialize_dto_runtime(self, dto: BaseDTO, item: ModelT) -> None
      async def _initialize_runtime_data(self, item: ModelT) -> None
      async def _initialize_item_runtime(self, item: ModelT | None) -> ModelT | None
      async def initialize(self) -> BaseManager[ModelT]
      def initialize_sync(self) -> BaseManager[ModelT]
      def add_computed_field(self, field: str) -> None
      def add_relation_field(self, field: str) -> None
      async def _process_item(self, item: ModelT | None) -> ModelT | None
      async def _get_item_or_raise(self, use_cache: bool = True, **kwargs: Any) -> ModelT
      async def _get_item_or_none(self, use_cache: bool = True, **kwargs: Any) -> ModelT | None
      async def _get_item_with_retry(self, use_cache: bool = True, **kwargs: Any) -> ModelT
      async def _get_items(self, order_by: str | None = None, **kwargs: Any) -> list[ModelT]
      async def _get_first_item(self, order_by: str | None = None, **kwargs: Any) -> ModelT | None
      async def _get_last_item(self, order_by: str | None = None, **kwargs: Any) -> ModelT | None
      async def _create_item(self, **data: Any) -> ModelT
      async def _create_items(self, items_data: list[dict[str, Any]], batch_size: int = 1000, ignore_conflicts: bool = False) -> list[ModelT]
      async def _update_item(self, item: ModelT, **updates: Any) -> ModelT
      async def _delete_item(self, item: ModelT) -> bool
      async def _delete_items(self, item: ModelT) -> None
      def _add_to_active(self, item_id: Any) -> Any
      def _remove_from_active(self, item_id: Any) -> None
      async def _fetch_related(self, item: Model, relation_name: str) -> Model | list[Model] | None
      async def _fetch_all_related(self, item: ModelT) -> AllRelatedResults[Model]
      async def load_item(self, use_cache: bool = True, **kwargs: Any) -> ModelT
      async def load_item_or_none(self, use_cache: bool = True, **kwargs: Any) -> ModelT | None
      async def load_item_with_retry(self, use_cache: bool = True, **kwargs: Any) -> ModelT
      async def load_items(self, **kwargs: Any) -> list[ModelT]
      async def load_by_id(self, item_id: Any) -> ModelT
      async def load_by_id_with_retry(self, item_id: Any) -> ModelT
      async def load_items_by_ids(self, item_ids: list[Any]) -> list[ModelT]
      async def add_active_by_id(self, item_id: Any) -> ModelT
      async def add_active_by_ids(self, item_ids: list[Any]) -> list[ModelT]
      async def remove_active_by_id(self, item_id: Any) -> None
      async def remove_active_by_ids(self, item_ids: list[Any]) -> None
      async def remove_all_active(self) -> None
      async def get_active_items(self) -> list[ModelT]
      async def create_item(self, **data: Any) -> ModelT
      async def create_items(self, items_data: list[dict[str, Any]], batch_size: int = 1000, ignore_conflicts: bool = False) -> list[ModelT]
      async def update_item(self, item_id: Any, **updates: Any) -> ModelT
      async def update_items(self, objects: list[ModelT], fields: list[str], batch_size: int = 1000) -> int
      async def delete_item(self, item_id: Any) -> bool
      async def delete_items(self, objects: list[ModelT], batch_size: int = 1000) -> int
      async def exists(self, item_id: Any) -> bool
      async def get_or_create(self, defaults: dict[str, Any] | None = None, **kwargs: Any) -> ModelT | None
      async def upsert_item(self, data: dict[str, Any], conflict_fields: list[str], update_fields: list[str] | None = None) -> ModelT
      async def upsert_items(self, items_data: list[dict[str, Any]], conflict_fields: list[str], update_fields: list[str] | None = None) -> list[ModelT]
      async def count(self, **filters: Any) -> int
      async def update_where(self, filters: dict[str, Any], **updates: Any) -> UpdateResult
      async def delete_where(self, **filters: Any) -> int
      def _item_to_dict(self, item: ModelT | None) -> dict[str, Any] | None
      def _print_item_keys(self, item: ModelT | None) -> None
      async def get_item_dict(self, item_id: Any) -> dict[str, Any] | None
      async def get_items_dict(self, **kwargs: Any) -> list[dict[str, Any] | None]
      async def get_active_items_dict(self) -> list[dict[str, Any] | None]
      async def create_item_get_dict(self, **data: Any) -> dict[str, Any] | None
      async def update_item_get_dict(self, item_id: Any, **updates: Any) -> dict[str, Any] | None
      async def get_item_with_related(self, item_id: Any, relation_name: str, *, use_join: bool | None = None) -> tuple[ModelT, Model | list[Model] | None]
      async def get_item_with_related_with_retry(self, item_id: Any, relation_name: str) -> tuple[ModelT, Model | list[Model] | None]
      async def get_items_with_related(self, relation_name: str, *, use_join: bool | None = None) -> list[ModelT]
      async def get_item_with_all_related(self, item_id: Any) -> tuple[ModelT, AllRelatedResults[Model]]
      async def get_items_with_all_related(self) -> list[ModelT]
      async def get_item_with_m2m(self, item_id: Any, relation_name: str) -> tuple[ModelT, list[Model]]
      async def get_item_with_fk(self, item_id: Any, fk_name: str, *, use_join: bool = True) -> tuple[ModelT, Model | None]
      async def get_item_with_ifk(self, item_id: Any, ifk_name: str) -> tuple[ModelT, list[Model]]
      async def add_m2m(self, item_id: Any, relation_name: str, *target_ids: Any) -> int
      async def remove_m2m(self, item_id: Any, relation_name: str, *target_ids: Any) -> int
      async def set_m2m(self, item_id: Any, relation_name: str, target_ids: list[Any]) -> None
      async def clear_m2m(self, item_id: Any, relation_name: str) -> int
      async def get_items_with_related_list(self, relation_names: list[str]) -> list[ModelT]
      async def get_item_through_fk(self, item_id: Any, first_relation: str, second_relation: str) -> tuple[ModelT, Model | None, Model | None]
      async def get_items_with_related_dict(self, relation_name: str) -> list[dict[str, Any] | None]
      async def get_items_with_all_related_dict(self) -> list[dict[str, Any] | None]
      async def create_item_get_object(self, **data: Any) -> ModelT
      async def add_active_by_id_or_not(self, item_id: Any = None) -> ModelT | None
      async def add_active_by_item_or_not(self, item: ModelT | None = None) -> ModelT | None
      async def add_active_by_ids_or_not(self, item_ids: list[Any] | None = None) -> list[ModelT] | None
      async def add_active_by_items_or_not(self, items: list[ModelT] | None = None) -> list[ModelT] | None
      async def get_active_item(self, item_id: Any) -> ModelT | None
      async def get_active_item_dict(self, item_id: Any) -> dict[str, Any] | None
      async def load_item_get_dict(self, use_cache: bool = True, **kwargs: Any) -> dict[str, Any] | None
      async def load_items_by_ids_get_dict(self, item_ids: list[Any]) -> list[dict[str, Any]]
      async def filter_items(self, **kwargs: Any) -> list[ModelT]
      async def filter_items_by_ids(self, item_ids: list[Any]) -> list[ModelT]
      async def filter_items_get_dict(self, **kwargs: Any) -> list[dict[str, Any]]
      async def get_active_item_with_fk(self, item_id: Any, related_model: str) -> tuple[ModelT | None, Model | list[Model] | None]
      async def get_active_items_with_fks(self) -> list[ModelT]
      async def get_active_item_with_ifk(self, related_model: str) -> ModelT | None
      async def get_active_items_with_ifks(self) -> list[ModelT]
      async def get_active_items_with_ifks_dict(self) -> list[dict[str, Any]]
      async def get_active_item_with_all_related(self) -> ModelT | None
      async def get_active_items_with_all_related(self) -> list[ModelT]
      async def get_active_items_with_all_related_dict(self) -> list[dict[str, Any]]
      async def get_active_item_with_one_relation(self, relation_name: str) -> list[ModelT]
      async def get_active_items_with_one_relation(self, relation_name: str) -> list[ModelT]
      async def get_active_item_with_one_relation_dict(self, relation_name: str) -> list[dict[str, Any]]
      async def get_active_item_with_related_models_list(self, related_models_list: list[str]) -> list[ModelT]
      async def get_active_items_with_related_models_list(self, related_models_list: list[str]) -> list[ModelT]
      async def get_active_item_with_related_models_list_dict(self, related_models_list: list[str]) -> list[dict[str, Any]]
      async def get_active_item_with_through_fk(self, item_id: Any, first_relationship: str, second_relationship: str) -> tuple[ModelT, Model | None, Model | None]
      async def get_active_item_through_ifk(self, item_id: Any, first_relationship: str, second_relationship: str) -> tuple[ModelT, list[Model] | None, list[Model] | None]
      def active_item_ids(self) -> set[Any]
      def get_all_attributes(self) -> dict[str, Any]
      def get_item_attributes(self, item: ModelT | None) -> dict[str, Any]
      def _auto_fetch_on_init_sync(self) -> None
      async def _auto_fetch_on_init_async(self) -> None
      def _trigger_fetch_warnings(self, count: int, items: list[ModelT | None], warning_limit_threshold: int) -> None
      def _trigger_limit_reached_warning(self, count: int, items: list[ModelT | None]) -> None
      def _validation_error(self, class_name: str, data: Any, field: str, message: str) -> None
      def load_item_sync(self, use_cache: bool = True, **kwargs: Any) -> ModelT
      def load_item_or_none_sync(self, use_cache: bool = True, **kwargs: Any) -> ModelT | None
      def load_items_sync(self, **kwargs: Any) -> list[ModelT]
      def load_by_id_sync(self, item_id: Any) -> ModelT
      def filter_items_sync(self, **kwargs: Any) -> list[ModelT]
      def create_item_sync(self, **data: Any) -> ModelT
      def update_item_sync(self, item_id: Any, **updates: Any) -> ModelT
      def delete_item_sync(self, item_id: Any) -> bool
      def get_or_create_sync(self, defaults: dict[str, Any] | None = None, **kwargs: Any) -> ModelT | None
      def exists_sync(self, item_id: Any) -> bool
      def get_active_items_sync(self) -> list[ModelT]
      def get_item_dict_sync(self, item_id: Any) -> dict[str, Any] | None
      def get_items_dict_sync(self, **kwargs: Any) -> list[dict[str, Any] | None]
      def upsert_item_sync(self, data: dict[str, Any], conflict_fields: list[str], update_fields: list[str] | None = None) -> ModelT
      def count_sync(self, **filters: Any) -> int
      def update_where_sync(self, filters: dict[str, Any], **updates: Any) -> UpdateResult
      def delete_where_sync(self, **filters: Any) -> int


---
Filepath: src/matrx_orm/core/async_db_manager.py  [python]

  class AsyncDatabaseManager:
      def __new__(cls)
      async def get_pool(cls, config_name)
      async def get_connection(cls, config_name, timeout = 10.0)
      async def execute_query(cls, config_name: str, query: str, *args: Any, timeout: float = 10.0) -> list[dict[str, Any]]
      async def cleanup(cls)
  async def _init_vector_codec(conn: asyncpg.Connection) -> None
  def run_sync(coro)
  async def main()
  async def cause_error()
  async def _wrapped()


---
Filepath: src/matrx_orm/core/model_view.py  [python]

  class ModelViewMeta(type):
      def __new__(mcs, name: str, bases: tuple[type, ...], attrs: dict[str, Any]) -> ModelViewMeta
  class ModelView:
      async def apply(cls, model: 'Model') -> 'Model'
      async def _prefetch_relations(cls, model: 'Model', relation_names: list[str]) -> None
  def _warn_computed(view_name: str, field_name: str, exc: BaseException) -> None
  def _warn_prefetch(view_name: str, relation_name: str, exc: BaseException) -> None
  async def _safe_fetch(name: str) -> None


---
Filepath: src/matrx_orm/core/registry.py  [python]

  class ModelRegistry:
      def register(cls, model_class: type[Model]) -> None
      def register_all(cls, models: list[type[Model]]) -> None
      def get_model(cls, model_name: str) -> type[Model] | None
      def all_models(cls) -> dict[str, type[Model]]
      def clear(cls) -> None
  def get_model_by_name(model_name: str) -> type[Model]


---
Filepath: src/matrx_orm/core/paginator.py  [python]

  ModelT = TypeVar('ModelT', bound='Model')
  class Page(Generic[ModelT]):
      def __init__(self, items: list[ModelT], number: int, per_page: int, total_count: int) -> None
      def total_pages(self) -> int
      def has_next(self) -> bool
      def has_previous(self) -> bool
      def next_number(self) -> int | None
      def previous_number(self) -> int | None
      def start_index(self) -> int
      def end_index(self) -> int
      def __repr__(self) -> str
      def __iter__(self)
      def __len__(self) -> int
  class Paginator(Generic[ModelT]):
      def __init__(self, queryset: 'QueryBuilder[ModelT]', per_page: int = 20) -> None
      async def count(self) -> int
      def total_pages(self) -> int | None
      async def page(self, number: int) -> 'Page[ModelT]'
      def _clone_with_pagination(self, offset: int) -> 'QueryBuilder[ModelT]'
      def __aiter__(self) -> 'Paginator[ModelT]'
      async def __anext__(self) -> 'Page[ModelT]'


---
Filepath: src/matrx_orm/core/expressions.py  [python]

  class F:
      def __init__(self, field_name: str) -> None
      def __add__(self, other: Any) -> Expression
      def __radd__(self, other: Any) -> Expression
      def __sub__(self, other: Any) -> Expression
      def __mul__(self, other: Any) -> Expression
      def __truediv__(self, other: Any) -> Expression
      def __repr__(self) -> str
  class Expression:
      def __init__(self, field_name: str, operator: str, value: Any) -> None
      def as_sql(self, params: list[Any]) -> str
      def __repr__(self) -> str
  class Q:
      def __init__(self, *args: 'Q', **kwargs: Any) -> None
      def __and__(self, other: 'Q') -> 'Q'
      def __or__(self, other: 'Q') -> 'Q'
      def __invert__(self) -> 'Q'
      def is_leaf(self) -> bool
      def __repr__(self) -> str
  class OuterRef:
      def __init__(self, field_name: str) -> None
      def __repr__(self) -> str
  class Subquery:
      def __init__(self, queryset: Any) -> None
      def as_sql(self, outer_table: str, params: list[Any]) -> str
      def __repr__(self) -> str
  class Exists:
      def __init__(self, queryset: Any) -> None
      def as_sql(self, outer_table: str, params: list[Any]) -> str
      def __repr__(self) -> str
  class Func:
      def __init__(self, *args: Any, output_field: str | None = None) -> None
      def as_sql(self, params: list[Any]) -> str
      def __repr__(self) -> str
  class Coalesce(Func):
  class Lower(Func):
  class Upper(Func):
  class Length(Func):
  class Trim(Func):
  class Now(Func):
      def __init__(self) -> None
      def as_sql(self, params: list[Any]) -> str
  class Concat(Func):
  class Greatest(Func):
  class Least(Func):
  class Abs(Func):
  class Round(Func):
  class Cast(Func):
      def __init__(self, expr: Any, as_type: str) -> None
      def as_sql(self, params: list[Any]) -> str
  class Extract(Func):
      def __init__(self, part: str, field: str | F | Func) -> None
      def as_sql(self, params: list[Any]) -> str
  class DateTrunc(Func):
      def __init__(self, precision: str, field: str | F | Func) -> None
      def as_sql(self, params: list[Any]) -> str
  class Aggregate(Func):
      def __init__(self, field: str | F | Func | None = None, *, distinct: bool = False) -> None
      def as_sql(self, params: list[Any]) -> str
  class Sum(Aggregate):
  class Avg(Aggregate):
  class Min(Aggregate):
  class Max(Aggregate):
  class Count(Aggregate):
      def __init__(self, field: str | F | Func | None = None, *, distinct: bool = False) -> None
  class StdDev(Aggregate):
  class Variance(Aggregate):
  class Window:
      def __init__(self, expression: 'Func | Aggregate', *, partition_by: str | list[str] | None = None, order_by: str | list[str] | None = None, frame: str | None = None) -> None
      def as_sql(self, params: list[Any]) -> str
      def __repr__(self) -> str
  class RowNumber(Func):
      def __init__(self) -> None
      def as_sql(self, params: list[Any]) -> str
  class Rank(Func):
      def __init__(self) -> None
      def as_sql(self, params: list[Any]) -> str
  class DenseRank(Func):
      def __init__(self) -> None
      def as_sql(self, params: list[Any]) -> str
  class Lag(Func):
      def __init__(self, field: str | F | Func, offset: int = 1, default: Any = None) -> None
      def as_sql(self, params: list[Any]) -> str
  class Lead(Func):
      def __init__(self, field: str | F | Func, offset: int = 1, default: Any = None) -> None
      def as_sql(self, params: list[Any]) -> str
  class FirstValue(Func):
  class LastValue(Func):
  class NthValue(Func):
      def __init__(self, field: str | F | Func, n: int) -> None
      def as_sql(self, params: list[Any]) -> str
  class Ntile(Func):
      def __init__(self, n: int) -> None
      def as_sql(self, params: list[Any]) -> str
  class CumeDist(Func):
      def __init__(self) -> None
      def as_sql(self, params: list[Any]) -> str
  class PercentRank(Func):
      def __init__(self) -> None
      def as_sql(self, params: list[Any]) -> str
  class CTE:
      def __init__(self, name: str, query: 'str | Any', *, recursive: bool = False) -> None
      def as_sql(self, params: list[Any]) -> str
      def __repr__(self) -> str
  class VectorDistance:
      def __init__(self, column: str, vector: list[float], metric: str = 'cosine') -> None
      def as_sql(self, params: list[Any]) -> str
      def __repr__(self) -> str
  def _render_subquery(queryset: Any, outer_table: str, params: list[Any], exists: bool = False) -> str
  def _parse_lookup_simple(key: str) -> tuple[str, str]
  def _render_func_arg(arg: Any, params: list[Any]) -> str


---
Filepath: src/matrx_orm/core/types.py  [python]

  ModelT = TypeVar('ModelT', bound='Model')
  AggregateResult = dict[str, int | float | None]
  class ForeignKeyResults(Generic[ModelT]):
      def get(self, key: str, default: ModelT | None = None) -> ModelT | None
      def __len__(self) -> int
      def __bool__(self) -> bool
      def __contains__(self, key: str) -> bool
      def __iter__(self)
      def keys(self)
      def values(self)
      def items(self)
  class InverseForeignKeyResults(Generic[ModelT]):
      def get(self, key: str, default: list[ModelT] | None = None) -> list[ModelT] | None
      def __len__(self) -> int
      def __bool__(self) -> bool
      def __contains__(self, key: str) -> bool
      def __iter__(self)
      def keys(self)
      def values(self)
      def items(self)
  class ManyToManyResults(Generic[ModelT]):
      def get(self, key: str, default: list[ModelT] | None = None) -> list[ModelT] | None
      def __len__(self) -> int
      def __bool__(self) -> bool
      def __contains__(self, key: str) -> bool
      def __iter__(self)
      def keys(self)
      def values(self)
      def items(self)
  class AllRelatedResults(Generic[ModelT]):
      def empty() -> AllRelatedResults
      def to_dict(self) -> dict[str, dict[str, Any]]
  class UpdateResult:
      def to_dict(self) -> dict[str, Any]


---
Filepath: src/matrx_orm/core/transaction.py  [python]

  class TransactionContext:
      def __init__(self, database: str) -> None
      async def __aenter__(self) -> TransactionContext
      async def __aexit__(self, exc_type: type[BaseException] | None, exc_val: BaseException | None, exc_tb: Any) -> bool
  def get_active_connection() -> asyncpg.Connection | None
  def transaction(database: str | None = None) -> TransactionContext
  def _get_default_database() -> str


---
Filepath: src/matrx_orm/core/relations.py  [python]

  class ForeignKeyReference:
      def _related_model(self) -> type[Model]
      def model(self) -> type[Model]
      def field(self) -> str
      def field_name(self) -> str
      def related_model(self) -> type[Model]
      def related_column(self) -> str
      async def fetch_data(self, instance: Model, column_value: Any) -> Model | None
  class InverseForeignKeyReference:
      def _related_model(self) -> type[Model]
      def model(self) -> type[Model]
      def field(self) -> str
      def related_model(self) -> type[Model]
      async def fetch_data(self, instance: Model, referenced_value: Any = None) -> list[Model]
  class LazyRelation:
      def __init__(self, instance: Model, field: Any) -> None
      async def __call__(self) -> Any
  class RelationDescriptor:
      def __init__(self, field: Any) -> None
      def __get__(self, instance: Model | None, owner: type[Model]) -> Any
      def __set__(self, instance: Model, value: Any) -> None
  class RelationField(Field):
      def __init__(self, to_model: str | type[Any], **kwargs: Any) -> None
      def contribute_to_class(self, model: type[Model], name: str) -> None
      def resolve_model(self) -> type[Model]
      def get_field_type(self) -> str
  class ForeignKey(RelationField):
      def __init__(self, to_model: str | type[Any], **kwargs: Any) -> None
      def contribute_to_class(self, model: type[Model], name: str) -> None
      async def get_related_objects(self, instance: Model) -> Model | None
      async def handle_on_delete(self, instance: Model) -> None
      def get_db_prep_value(self, value: Any) -> Any
      def from_db_value(self, value: Any) -> Any
  class RelationLoader:
      def __init__(self, instance: Model, field: Any) -> None
      async def load(self) -> Any
  class OneToOneField(ForeignKey):
      def __init__(self, to_model: str | type[Any], **kwargs: Any) -> None
  class ManyToManyReference:
      def _resolved_model(self) -> type[Model]
      def resolved_model(self) -> type[Model]
      def qualified_junction_table(self) -> str
      async def _get_db_name(self, instance: Model) -> str
      def _enrich_context(self) -> dict[str, str]
      async def fetch_related(self, instance: Model) -> list[Model]
      async def add(self, instance: Model, *target_ids: Any) -> int
      async def remove(self, instance: Model, *target_ids: Any) -> int
      async def set(self, instance: Model, target_ids: list[Any]) -> None
      async def clear(self, instance: Model) -> int
  class ManyToManyField(RelationField):
      def __init__(self, to_model: str | type[Any], **kwargs: Any) -> None
      def get_junction_table_name(self, source_model_name: str) -> str
```
<!-- /AUTO:signatures -->

<!-- AUTO:dependencies -->
## Dependencies

**External packages:** asyncpg, matrx_orm, matrx_utils, typing_extensions
<!-- /AUTO:dependencies -->

<!-- AUTO:config -->
## Generation Config

> Auto-managed. Contains the exact parameters used to generate this README.
> Used by parent modules to auto-refresh this file when it is stale.
> Do not edit manually — changes will be overwritten on the next run.

```json
{
  "subdirectory": "src/matrx_orm/core",
  "mode": "signatures",
  "scope": null,
  "project_noise": null,
  "include_call_graph": false,
  "entry_points": null,
  "call_graph_exclude": [
    "tests"
  ]
}
```
<!-- /AUTO:config -->
