# `src.matrx_orm` — Module Overview

> This document is partially auto-generated. Sections tagged `<!-- AUTO:id -->` are refreshed by the generator.
> Everything else is yours to edit freely and will never be overwritten.

<!-- AUTO:meta -->
## About This Document

This file is **partially auto-generated**. Sections wrapped in `<!-- AUTO:id -->` tags
are overwritten each time the generator runs. Everything else is yours to edit freely.

| Field | Value |
|-------|-------|
| Module | `src/matrx_orm` |
| Last generated | 2026-02-28 13:59 |
| Output file | `src/matrx_orm/MODULE_README.md` |
| Signature mode | `signatures` |


**Child READMEs detected** (signatures collapsed — see links for detail):

| README | |
|--------|---|
| [`src/matrx_orm/adapters/MODULE_README.md`](src/matrx_orm/adapters/MODULE_README.md) | last generated 2026-02-28 13:59 |
| [`src/matrx_orm/core/MODULE_README.md`](src/matrx_orm/core/MODULE_README.md) | last generated 2026-02-28 13:57 |
| [`src/matrx_orm/migrations/MODULE_README.md`](src/matrx_orm/migrations/MODULE_README.md) | last generated 2026-02-28 13:57 |
| [`src/matrx_orm/operations/MODULE_README.md`](src/matrx_orm/operations/MODULE_README.md) | last generated 2026-02-28 13:57 |
| [`src/matrx_orm/python_sql/MODULE_README.md`](src/matrx_orm/python_sql/MODULE_README.md) | last generated 2026-02-28 13:59 |
| [`src/matrx_orm/query/MODULE_README.md`](src/matrx_orm/query/MODULE_README.md) | last generated 2026-02-28 13:59 |
| [`src/matrx_orm/schema_builder/MODULE_README.md`](src/matrx_orm/schema_builder/MODULE_README.md) | last generated 2026-02-28 13:57 |
| [`src/matrx_orm/sql_executor/MODULE_README.md`](src/matrx_orm/sql_executor/MODULE_README.md) | last generated 2026-02-28 13:57 |
**To refresh auto-sections:**
```bash
python utils/code_context/generate_module_readme.py src/matrx_orm --mode signatures
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

> Auto-generated. 73 files across 14 directories.

```
src/matrx_orm/
├── MODULE_README.md
├── __init__.py
├── adapters/
│   ├── MODULE_README.md
│   ├── __init__.py
│   ├── base_adapter.py
│   ├── postgresql.py
├── client/
│   ├── __init__.py
│   ├── postgres_connection.py
├── core/
│   ├── MODULE_README.md
│   ├── __init__.py
│   ├── async_db_manager.py
│   ├── base.py
│   ├── config.py
│   ├── expressions.py
│   ├── extended.py
│   ├── fields.py
│   ├── model_view.py
│   ├── paginator.py
│   ├── registry.py
│   ├── relations.py
│   ├── signals.py
│   ├── transaction.py
│   ├── types.py
├── error_handling.py
├── exceptions.py
├── extended/
│   ├── __init__.py
│   ├── app_error_handler.py
├── middleware/
│   ├── __init__.py
│   ├── base.py
├── migrations/
│   ├── MODULE_README.md
├── operations/
│   ├── MODULE_README.md
│   ├── __init__.py
│   ├── create.py
│   ├── delete.py
│   ├── read.py
│   ├── update.py
├── py.typed
├── python_sql/
│   ├── MODULE_README.md
│   ├── __init__.py
│   ├── db_objects.py
│   ├── table_detailed_relationships.py
│   ├── table_typescript_relationship.py
├── query/
│   ├── MODULE_README.md
│   ├── __init__.py
│   ├── builder.py
│   ├── executor.py
├── schema_builder/
│   ├── MODULE_README.md
│   ├── __init__.py
│   ├── code_handler.py
│   ├── columns.py
│   ├── common.py
│   ├── generator.py
│   ├── helpers/
│   │   ├── __init__.py
│   │   ├── base_generators.py
│   │   ├── entity_generators.py
│   │   ├── git_checker.py
│   ├── relationships.py
│   ├── runner.py
│   ├── schema.py
│   ├── schema_manager.py
│   ├── tables.py
│   ├── views.py
├── sql_executor/
│   ├── MODULE_README.md
│   ├── __init__.py
│   ├── executor.py
│   ├── queries.py
│   ├── registry.py
│   ├── types.py
│   ├── utils.py
├── state.py
├── utils/
│   ├── __init__.py
│   ├── sql_utils.py
│   ├── type_converters.py
# excluded: 11 .md
```
<!-- /AUTO:tree -->

<!-- AUTO:signatures -->
## API Signatures

> Auto-generated via `output_mode="{mode}"`. ~5-10% token cost vs full source.
> For full source, open the individual files directly.
> Submodules with their own `MODULE_README.md` are collapsed to a single stub line.

```
---
Filepath: src/matrx_orm/__init__.py  [python]




---
Filepath: src/matrx_orm/state.py  [python]

  class CachePolicy(Enum):
  class ModelState:
      def __init__(self, model_class)
      def _get_cache_key(self, **kwargs)
      def _get_record_cache_key(self, record)
      async def get(self, **kwargs)
      def _find_in_cache(self, **kwargs)
      def _is_stale(self, record)
      async def cache(self, record)
      async def remove(self, record)
      async def _ensure_subscription(self, record)
      async def _setup_subscription(self, record)
      def update_from_subscription(self, data)
      def get_all_cached(self)
      def count(self)
      def clear_cache(self)
  class StateManager:
      def register_model(cls, model_class)
      async def get(cls, model_class, **kwargs)
      async def get_or_none(cls, model_class, **kwargs)
      async def get_all(cls, model_class, **kwargs)
      async def cache(cls, model_class, record)
      async def cache_bulk(cls, model_class, records)
      async def remove(cls, model_class, record)
      async def remove_bulk(cls, model_class, records)
      async def update(cls, model_class, record)
      async def clear_cache(cls, model_class)
      async def count(cls, model_class)



---
Filepath: src/matrx_orm/exceptions.py  [python]

  class ORMException(Exception):
      def __init__(self, message: str | None = None, model: type | str | None = None, details: Mapping[str, object] | None = None, class_name: str | None = None, method_name: str | None = None)
      def _format_caller_section(self) -> str | None
      def enrich(self, model: type | str | None = None, operation: str | None = None, args: object = None, **extra: object) -> 'ORMException'
      def _str(self, key: str, default: str = '') -> str
      def _sanitize_details(details: Mapping[str, object]) -> dict[str, object]
      def message(self)
      def format_message(self)
      def __str__(self)
  class ValidationError(ORMException):
      def __init__(self, message = None, model = None, field = None, value = None, reason = None, details = None)
      def format_message(self)
  class QueryError(ORMException):
      def format_message(self)
  class DoesNotExist(QueryError):
      def __init__(self, model: type | str | None = None, filters: dict[str, object] | None = None, class_name: str | None = None, method_name: str | None = None)
      def format_message(self)
  class MultipleObjectsReturned(QueryError):
      def __init__(self, model: type | str | None = None, count: int | None = None, filters: dict[str, object] | None = None)
      def format_message(self)
  class DatabaseError(ORMException):
  class ConnectionError(DatabaseError):
      def __init__(self, model = None, db_url = None, original_error = None)
      def format_message(self)
  class IntegrityError(DatabaseError):
      def __init__(self, model = None, constraint = None, original_error = None)
      def format_message(self)
  class TransactionError(DatabaseError):
      def __init__(self, model = None, operation = None, original_error = None)
  class ConfigurationError(ORMException):
      def __init__(self, model = None, config_key = None, reason = None)
      def format_message(self)
  class CacheError(ORMException):
      def __init__(self, model = None, operation = None, details = None, original_error = None)
      def format_message(self)
  class StateError(ORMException):
      def __init__(self, model = None, operation = None, reason = None, details = None, original_error = None)
      def format_message(self)
  class RelationshipError(ORMException):
      def __init__(self, model = None, related_model = None, field = None, reason = None)
  class AdapterError(ORMException):
      def __init__(self, model = None, adapter_name = None, original_error = None)
  class FieldError(ORMException):
      def __init__(self, model = None, field = None, value = None, reason = None)
  class MigrationError(ORMException):
      def __init__(self, model = None, migration = None, original_error = None)
      def format_message(self)
  class ParameterError(ORMException):
      def __init__(self, model = None, query = None, args = None, reason = None, class_name = None, method_name = None)
      def format_message(self)
  class UnknownDatabaseError(ORMException):
      def __init__(self, model = None, operation = None, query = None, args = None, traceback = None, original_error = None)
      def format_message(self)
  class OptimisticLockError(ORMException):
      def __init__(self, model = None, pk = None, expected_version: int | None = None, message: str | None = None) -> None
  def _capture_caller_frames() -> list[str]



---
Filepath: src/matrx_orm/py.typed  [unknown (.typed)]

  # signature extraction not supported for this language



---
Filepath: src/matrx_orm/error_handling.py  [python]

  async def handle_orm_operation(operation_name, model = None, **context)



---
Filepath: src/matrx_orm/extended/__init__.py  [python]




---
Filepath: src/matrx_orm/extended/app_error_handler.py  [python]

  DEFAULT_CLIENT_MESSAGE = 'Oops. Something went wrong. Please reload the page and try again.'
  class _HasErrorContext(Protocol):
      def _get_error_context(self) -> Mapping[str, object]
  class _HasModel(Protocol):
  class AppError(Exception):
      def __init__(self, message: str, error_type: str = 'GenericError', client_visible: str | None = None, context: Mapping[str, object] | None = None)
  def handle_errors(func: _F) -> _F
  def _handle_exception(e: Exception, cls_or_self: object, func_name: str) -> None
  async def async_wrapper(cls_or_self: object, *args: object, **kwargs: object) -> object
  def sync_wrapper(cls_or_self: object, *args: object, **kwargs: object) -> object



---
Filepath: src/matrx_orm/utils/__init__.py  [python]




---
Filepath: src/matrx_orm/utils/sql_utils.py  [python]

  def clean_default_value(default_value, data_type)
  def save_to_json(data, dir_override = None, filename_override = None, save_to_local_data = False)
  def sql_param_to_psycopg2(sql, params)
  def replace_named_param(match)



---
Filepath: src/matrx_orm/utils/type_converters.py  [python]

  class TypeConverter:
      def to_python(cls, value, field_type)
      def get_db_prep_value(cls, value, field_type)
  class CustomTypeConverter(TypeConverter):
      def register_converter(cls, python_type, to_db_func, to_python_func)
      def to_python(cls, value, field_type)
      def get_db_prep_value(cls, value, field_type)
  def convert_query_results(results, model)
  def prepare_query_params(params, model)



---
Submodule: src/matrx_orm/adapters/  [3 files — full detail in src/matrx_orm/adapters/MODULE_README.md]

---
Submodule: src/matrx_orm/python_sql/  [4 files — full detail in src/matrx_orm/python_sql/MODULE_README.md]

---
Submodule: src/matrx_orm/query/  [3 files — full detail in src/matrx_orm/query/MODULE_README.md]

---
Filepath: src/matrx_orm/client/__init__.py  [python]




---
Filepath: src/matrx_orm/client/postgres_connection.py  [python]

  def init_connection_details(config_name)
  def get_postgres_connection(database_project = 'this_will_cause_error_specify_the_database')
  def execute_sql_query(query, params = None, database_project = 'this_will_cause_error_specify_the_database')
  def execute_sql_file(filename, params = None, database_project = 'this_will_cause_error_specify_the_database')
  def execute_transaction_query(query, params = None, database_project = 'this_will_cause_error_specify_the_database')
  def execute_batch_query(query: str, batch_params: list[dict[str, Any]], batch_size: int = 50, database_project: str = '')



---
Filepath: src/matrx_orm/middleware/__init__.py  [python]




---
Filepath: src/matrx_orm/middleware/base.py  [python]

  class BaseMiddleware(ABC):
      async def process_query(self, query: Dict[str, Any]) -> Dict[str, Any]
      async def process_result(self, result: Any) -> Any
  class MiddlewareManager:
      def __init__(self)
      def add_middleware(self, middleware: BaseMiddleware)
      async def process_query(self, query: Dict[str, Any]) -> Dict[str, Any]
      async def process_result(self, result: Any) -> Any
  class QueryLoggingMiddleware(BaseMiddleware):
      async def process_query(self, query: Dict[str, Any]) -> Dict[str, Any]
      async def process_result(self, result: Any) -> Any
  class CachingMiddleware(BaseMiddleware):
      def __init__(self)
      async def process_query(self, query: Dict[str, Any]) -> Dict[str, Any]
      async def process_result(self, result: Any) -> Any
  class SoftDeleteMiddleware(BaseMiddleware):
      async def process_query(self, query: Dict[str, Any]) -> Dict[str, Any]
      async def process_result(self, result: Any) -> Any
  class TenantIsolationMiddleware(BaseMiddleware):
      def __init__(self, get_current_tenant_id: Callable[[], str])
      async def process_query(self, query: Dict[str, Any]) -> Dict[str, Any]
      async def process_result(self, result: Any) -> Any
  class EncryptionMiddleware(BaseMiddleware):
      def __init__(self, encrypt_func: Callable[[Any], Any], decrypt_func: Callable[[Any], Any], sensitive_fields: List[str])
      async def process_query(self, query: Dict[str, Any]) -> Dict[str, Any]
      async def process_result(self, result: Any) -> Any
  class ValidationMiddleware(BaseMiddleware):
      def __init__(self, validation_rules: Dict[str, Callable[[Any], bool]])
      async def process_query(self, query: Dict[str, Any]) -> Dict[str, Any]
      async def process_result(self, result: Any) -> Any
  class PerformanceMonitoringMiddleware(BaseMiddleware):
      def __init__(self)
      async def process_query(self, query: Dict[str, Any]) -> Dict[str, Any]
      async def process_result(self, result: Any) -> Any
  class AuditingMiddleware(BaseMiddleware):
      async def process_query(self, query: Dict[str, Any]) -> Dict[str, Any]
      async def process_result(self, result: Any) -> Any
      def log_operation(self, query)
  class SchemaEvolutionMiddleware(BaseMiddleware):
      def __init__(self, schema_version: str)
      async def process_query(self, query: Dict[str, Any]) -> Dict[str, Any]
      async def process_result(self, result: Any) -> Any
  class DataTransformationMiddleware(BaseMiddleware):
      def __init__(self, transformations: Dict[str, Callable[[Any], Any]])
      async def process_query(self, query: Dict[str, Any]) -> Dict[str, Any]
      async def process_result(self, result: Any) -> Any
  class AccessControlMiddleware(BaseMiddleware):
      def __init__(self, get_user_permissions: Callable[[], List[str]])
      async def process_query(self, query: Dict[str, Any]) -> Dict[str, Any]
      async def process_result(self, result: Any) -> Any
  class QueryOptimizationMiddleware(BaseMiddleware):
      async def process_query(self, query: Dict[str, Any]) -> Dict[str, Any]
      async def process_result(self, result: Any) -> Any
  class DistributedTracingMiddleware(BaseMiddleware):
      def __init__(self, tracer)
      async def process_query(self, query: Dict[str, Any]) -> Dict[str, Any]
      async def process_result(self, result: Any) -> Any



---
Submodule: src/matrx_orm/sql_executor/  [6 files — full detail in src/matrx_orm/sql_executor/MODULE_README.md]

---
Submodule: src/matrx_orm/schema_builder/  [15 files — full detail in src/matrx_orm/schema_builder/MODULE_README.md]

---
Submodule: src/matrx_orm/core/  [14 files — full detail in src/matrx_orm/core/MODULE_README.md]

---
Submodule: src/matrx_orm/operations/  [5 files — full detail in src/matrx_orm/operations/MODULE_README.md]

```
<!-- /AUTO:signatures -->

<!-- AUTO:dependencies -->
## Dependencies

**External packages:** asyncpg, dotenv, git, matrx_orm, matrx_utils, psycopg, psycopg_pool, typing_extensions, yaml
<!-- /AUTO:dependencies -->

<!-- AUTO:config -->
## Generation Config

> Auto-managed. Contains the exact parameters used to generate this README.
> Used by parent modules to auto-refresh this file when it is stale.
> Do not edit manually — changes will be overwritten on the next run.

```json
{
  "subdirectory": "src/matrx_orm",
  "mode": "signatures",
  "scope": null,
  "project_noise": null,
  "include_call_graph": true,
  "entry_points": null,
  "call_graph_exclude": [
    "tests"
  ]
}
```
<!-- /AUTO:config -->

<!-- AUTO:call_graph -->
## Call Graph

> Auto-generated. All Python files
> Covered submodules shown as stubs — see child READMEs for full detail: `adapters`, `core`, `migrations`, `operations`, `python_sql`, `query`, `schema_builder`, `sql_executor`
> Excluded from call graph: `tests`.
> Shows which functions call which. `async` prefix = caller is an async function.
> Method calls shown as `receiver.method()`. Private methods (`_`) excluded by default.

### Call graph: src.matrx_orm.state

```
src.matrx_orm.state.__init__ → src.matrx_orm.state.ConfigurationError() (line 36)
  src.matrx_orm.state._get_cache_key → join((str(kwargs[pk]) for pk in primary_keys)) (line 46)
  src.matrx_orm.state._get_cache_key → src.matrx_orm.state.CacheError() (line 49)
  src.matrx_orm.state._get_record_cache_key → join((str(getattr(record, pk)) for pk in record._meta.primary_keys)) (line 57)
  async src.matrx_orm.state.get → src.matrx_orm.state.ValidationError() (line 74)
  async src.matrx_orm.state.get → asyncio.Lock() (line 86)
  async src.matrx_orm.state.get → src.matrx_orm.state.CacheError() (line 88)
  async src.matrx_orm.state.get → src.matrx_orm.state.CacheError() (line 109)
  async src.matrx_orm.state.get → src.matrx_orm.state.CacheError() (line 130)
  async src.matrx_orm.state.get → src.matrx_orm.state.CacheError() (line 144)
  async src.matrx_orm.state.get → src.matrx_orm.state.CacheError() (line 150)
  src.matrx_orm.state._find_in_cache → ...values() (line 158)
  src.matrx_orm.state._find_in_cache → kwargs.items() (line 159)
  src.matrx_orm.state._is_stale → ...get(cache_key) (line 165)
  src.matrx_orm.state._is_stale → total_seconds() (line 170)
  src.matrx_orm.state._is_stale → datetime.now() (line 170)
  src.matrx_orm.state._is_stale → datetime.now() (line 172)
  src.matrx_orm.state._is_stale → src.matrx_orm.state.timedelta() (line 176)
  src.matrx_orm.state._is_stale → src.matrx_orm.state.timedelta() (line 178)
  src.matrx_orm.state._is_stale → src.matrx_orm.state.timedelta() (line 180)
  async src.matrx_orm.state.cache → src.matrx_orm.state.ValidationError() (line 187)
  async src.matrx_orm.state.cache → src.matrx_orm.state.ValidationError() (line 193)
  async src.matrx_orm.state.cache → datetime.now() (line 199)
  async src.matrx_orm.state.cache → src.matrx_orm.state.CacheError() (line 209)
  async src.matrx_orm.state.remove → ...pop(cache_key, None) (line 218)
  async src.matrx_orm.state.remove → ...pop(cache_key, None) (line 219)
  async src.matrx_orm.state._ensure_subscription → ...add(cache_key) (line 225)
  src.matrx_orm.state.update_from_subscription → ...from_db_result(data) (line 231)
  src.matrx_orm.state.update_from_subscription → datetime.now() (line 234)
  src.matrx_orm.state.get_all_cached → ...values() (line 238)
  src.matrx_orm.state.clear_cache → ...clear() (line 246)
  src.matrx_orm.state.clear_cache → ...clear() (line 247)
  src.matrx_orm.state.clear_cache → ...clear() (line 248)
  src.matrx_orm.state.register_model → model_class.get_database_name() (line 258)
  src.matrx_orm.state.register_model → src.matrx_orm.state.ModelState(model_class) (line 259)
  src.matrx_orm.state.register_model → src.matrx_orm.state.ConfigurationError() (line 261)
  async src.matrx_orm.state.get → model_class.get_database_name() (line 271)
  async src.matrx_orm.state.get → src.matrx_orm.state.StateError() (line 273)
  async src.matrx_orm.state.get → state.get() (line 282)
  async src.matrx_orm.state.get → model_class.get() (line 287)
  async src.matrx_orm.state.get → src.matrx_orm.state.CacheError() (line 293)
  async src.matrx_orm.state.get → cls.cache(model_class, record) (line 302)
  async src.matrx_orm.state.get → src.matrx_orm.state.StateError() (line 308)
  async src.matrx_orm.state.get_or_none → model_class.get_database_name() (line 322)
  async src.matrx_orm.state.get_or_none → src.matrx_orm.state.StateError() (line 324)
  async src.matrx_orm.state.get_or_none → state.get() (line 334)
  async src.matrx_orm.state.get_or_none → model_class.get() (line 342)
  async src.matrx_orm.state.get_or_none → cls.cache(model_class, record) (line 345)
  async src.matrx_orm.state.get_all → model_class.get_database_name() (line 370)
  async src.matrx_orm.state.get_all → state.get_all_cached() (line 376)
  async src.matrx_orm.state.get_all → kwargs.items() (line 377)
  async src.matrx_orm.state.get_all → model_class.filter() (line 388)
  async src.matrx_orm.state.get_all → cls.cache_bulk(model_class, records) (line 392)
  async src.matrx_orm.state.cache → model_class.get_database_name() (line 399)
  async src.matrx_orm.state.cache → state.cache(record) (line 401)
  async src.matrx_orm.state.cache_bulk → model_class.get_database_name() (line 410)
  async src.matrx_orm.state.cache_bulk → src.matrx_orm.state.StateError() (line 413)
  async src.matrx_orm.state.cache_bulk → state.get() (line 421)
  async src.matrx_orm.state.cache_bulk → state.cache(record) (line 422)
  async src.matrx_orm.state.cache_bulk → src.matrx_orm.state.StateError() (line 429)
  async src.matrx_orm.state.remove → model_class.get_database_name() (line 439)
  async src.matrx_orm.state.remove → state.remove(record) (line 441)
  async src.matrx_orm.state.remove_bulk → model_class.get_database_name() (line 446)
  async src.matrx_orm.state.remove_bulk → state.remove(record) (line 449)
  async src.matrx_orm.state.update → model_class.get_database_name() (line 454)
  async src.matrx_orm.state.update → state.cache(record) (line 456)
  async src.matrx_orm.state.clear_cache → model_class.get_database_name() (line 461)
  async src.matrx_orm.state.clear_cache → state.clear_cache() (line 463)
  async src.matrx_orm.state.count → model_class.get_database_name() (line 468)
  async src.matrx_orm.state.count → state.count() (line 470)
```

### Call graph: src.matrx_orm.exceptions

```
src.matrx_orm.exceptions._capture_caller_frames → _tb.extract_stack() (line 24)
  src.matrx_orm.exceptions._capture_caller_frames → frames.append(f'  File "{fi.filename}", line {fi.lineno}, in {fi.name}') (line 27)
  src.matrx_orm.exceptions._capture_caller_frames → frames.reverse() (line 30)
  src.matrx_orm.exceptions.__init__ → src.matrx_orm.exceptions._capture_caller_frames() (line 56)
  src.matrx_orm.exceptions.__init__ → self.format_message() (line 57)
  src.matrx_orm.exceptions._format_caller_section → lines.extend(self._caller_frames) (line 64)
  src.matrx_orm.exceptions._format_caller_section → join(lines) (line 65)
  src.matrx_orm.exceptions.enrich → extra.items() (line 89)
  src.matrx_orm.exceptions.enrich → self.format_message() (line 93)
  src.matrx_orm.exceptions._str → ...get(key, default) (line 98)
  src.matrx_orm.exceptions._sanitize_details → details.items() (line 107)
  src.matrx_orm.exceptions.format_message → error_msg.append(f'[ERROR in {self.model}: {self.class_name}.{self.method_name}()]\n') (line 126)
  src.matrx_orm.exceptions.format_message → error_msg.append(f'[ERROR in {self.model}]\n') (line 130)
  src.matrx_orm.exceptions.format_message → error_msg.append(f'Message: {self.message}') (line 132)
  src.matrx_orm.exceptions.format_message → error_msg.append('\nContext:') (line 135)
  src.matrx_orm.exceptions.format_message → ...items() (line 136)
  src.matrx_orm.exceptions.format_message → error_msg.append(f'  {key}: {str_val}') (line 142)
  src.matrx_orm.exceptions.format_message → error_msg.append('\n' + '=' * 80 + '\n') (line 144)
  src.matrx_orm.exceptions.format_message → join(error_msg) (line 146)
  src.matrx_orm.exceptions.__str__ → self.format_message() (line 149)
  src.matrx_orm.exceptions.__str__ → msg.rfind(sep) (line 156)
  src.matrx_orm.exceptions.__init__ → merged_details.update(details) (line 188)
  src.matrx_orm.exceptions.format_message → ...get('value') (line 194)
  src.matrx_orm.exceptions.format_message → lines.append('Matrx ORM  |  ValidationError') (line 196)
  src.matrx_orm.exceptions.format_message → lines.append('') (line 197)
  src.matrx_orm.exceptions.format_message → lines.append(self.message) (line 198)
  src.matrx_orm.exceptions.format_message → lines.append(f'  Reason:  {reason}') (line 200)
  src.matrx_orm.exceptions.format_message → lines.append(f'  Field:   {field}') (line 202)
  src.matrx_orm.exceptions.format_message → lines.append(f'  Value:   {value}') (line 204)
  src.matrx_orm.exceptions.format_message → lines.append('') (line 205)
  src.matrx_orm.exceptions.format_message → lines.append('Hint:') (line 206)
  src.matrx_orm.exceptions.format_message → reason.lower() (line 208)
  src.matrx_orm.exceptions.format_message → lines.append('  - You called update() or save() without passing any fields to change.') (line 209)
  src.matrx_orm.exceptions.format_message → lines.append("  - Ensure you are passing at least one keyword argument, e.g. update(status='active').") (line 212)
  src.matrx_orm.exceptions.format_message → reason.lower() (line 215)
  src.matrx_orm.exceptions.format_message → lines.append('  - One or more field names you passed do not exist on this model.') (line 216)
  src.matrx_orm.exceptions.format_message → lines.append('  - Check the model definition for the exact field names (case-sensitive).') (line 219)
  src.matrx_orm.exceptions.format_message → lines.append('  - Fields marked is_native=False (computed/virtual) cannot be updated directly.') (line 222)
  src.matrx_orm.exceptions.format_message → reason.lower() (line 225)
  src.matrx_orm.exceptions.format_message → lines.append('  - You called get() or a cache lookup without any filter arguments.') (line 226)
  src.matrx_orm.exceptions.format_message → lines.append("  - Pass at least one field to match on, e.g. get(id='...').") (line 229)
  src.matrx_orm.exceptions.format_message → reason.lower() (line 230)
  src.matrx_orm.exceptions.format_message → lines.append('  - You called create() or insert() with an empty data dict.') (line 231)
  src.matrx_orm.exceptions.format_message → lines.append('  - Ensure the object has at least the required fields set before saving.') (line 232)
  src.matrx_orm.exceptions.format_message → reason.lower() (line 235)
  src.matrx_orm.exceptions.format_message → lines.append('  - The record returned from the database was None and cannot be cached.') (line 236)
  src.matrx_orm.exceptions.format_message → lines.append('  - Check that your query actually returns a record before caching it.') (line 239)
  src.matrx_orm.exceptions.format_message → lines.append('  - Verify the field name exists on the model and the value is the correct type.') (line 243)
  src.matrx_orm.exceptions.format_message → lines.append('  - Check that required fields are populated before calling save() or create().') (line 246)
  src.matrx_orm.exceptions.format_message → lines.append('-' * 80 + '\n') (line 249)
  src.matrx_orm.exceptions.format_message → join(lines) (line 250)
  src.matrx_orm.exceptions.format_message → ...get('error', '') (line 258)
  src.matrx_orm.exceptions.format_message → ...get('query', '') (line 259)
  src.matrx_orm.exceptions.format_message → ...get('operation', '') (line 260)
  src.matrx_orm.exceptions.format_message → ...get('missing_keys', []) (line 261)
  src.matrx_orm.exceptions.format_message → lines.append('Matrx ORM  |  QueryError') (line 263)
  src.matrx_orm.exceptions.format_message → lines.append('') (line 264)
  src.matrx_orm.exceptions.format_message → lines.append(self.message) (line 265)
  src.matrx_orm.exceptions.format_message → lines.append(f'  Operation: {operation}') (line 267)
  src.matrx_orm.exceptions.format_message → lines.append(f'  Missing:   {missing_keys}') (line 269)
  src.matrx_orm.exceptions.format_message → lines.append(f'  Detail:    {error}') (line 271)
  src.matrx_orm.exceptions.format_message → lines.append(f'  Query:     {short_query}') (line 275)
  src.matrx_orm.exceptions.format_message → lines.append('') (line 276)
  src.matrx_orm.exceptions.format_message → lines.append('Hint:') (line 277)
  src.matrx_orm.exceptions.format_message → lines.append('  - QueryExecutor requires a properly constructed query dict.') (line 279)
  src.matrx_orm.exceptions.format_message → lines.append('  - Do not instantiate QueryExecutor directly. Use QueryBuilder,') (line 282)
  src.matrx_orm.exceptions.format_message → lines.append('    which calls QueryBuilder._build_query() to produce the correct dict.') (line 285)
  src.matrx_orm.exceptions.format_message → lower() (line 288)
  src.matrx_orm.exceptions.format_message → ...lower() (line 288)
  src.matrx_orm.exceptions.format_message → lines.append('  - The SQL generated by the ORM was rejected by PostgreSQL for invalid syntax.') (line 289)
  src.matrx_orm.exceptions.format_message → lines.append('  - This is likely an ORM bug. Please report the Query above.') (line 292)
  src.matrx_orm.exceptions.format_message → lines.append('  - An error occurred while executing a query that was not caught by a') (line 296)
  src.matrx_orm.exceptions.format_message → lines.append('    more specific exception handler.') (line 299)
  src.matrx_orm.exceptions.format_message → lines.append('  - Check the Detail and Query above for the root cause.') (line 300)
  src.matrx_orm.exceptions.format_message → lines.append('-' * 80 + '\n') (line 301)
  src.matrx_orm.exceptions.format_message → join(lines) (line 302)
  src.matrx_orm.exceptions.__init__ → join((f'{k}={v}' for k, v in resolved_filters.items())) (line 318)
  src.matrx_orm.exceptions.__init__ → resolved_filters.items() (line 318)
  src.matrx_orm.exceptions.format_message → lines.append('Matrx ORM  |  DoesNotExist') (line 331)
  src.matrx_orm.exceptions.format_message → lines.append('') (line 332)
  src.matrx_orm.exceptions.format_message → lines.append('NOTICE: Requested item not found') (line 333)
  src.matrx_orm.exceptions.format_message → lines.append('') (line 334)
  src.matrx_orm.exceptions.format_message → lines.append(self.message) (line 335)
  src.matrx_orm.exceptions.format_message → ...get('filters') (line 336)
  src.matrx_orm.exceptions.format_message → lines.append('') (line 338)
  src.matrx_orm.exceptions.format_message → lines.append('Search criteria:') (line 339)
  src.matrx_orm.exceptions.format_message → filters.items() (line 340)
  src.matrx_orm.exceptions.format_message → lines.append(f'  {k}: {v}') (line 341)
  src.matrx_orm.exceptions.format_message → lines.append('') (line 342)
  src.matrx_orm.exceptions.format_message → lines.append('Hint:') (line 343)
  src.matrx_orm.exceptions.format_message → lines.append('  - Use get() when the record is expected to exist — this error is intentional.') (line 344)
  src.matrx_orm.exceptions.format_message → lines.append('  - Use get_or_none() when a missing record is a valid, handled outcome.') (line 347)
  src.matrx_orm.exceptions.format_message → lines.append('  - Use filter(...).first() to get the first match or None without raising.') (line 350)
  src.matrx_orm.exceptions.format_message → lines.append('') (line 353)
  src.matrx_orm.exceptions.format_message → lines.append('This is not an ORM bug. The record does not exist in the database.') (line 354)
  src.matrx_orm.exceptions.format_message → lines.append('-' * 80 + '\n') (line 357)
  src.matrx_orm.exceptions.format_message → join(lines) (line 358)
  src.matrx_orm.exceptions.__init__ → join((f'{k}={v}' for k, v in resolved_filters.items())) (line 373)
  src.matrx_orm.exceptions.__init__ → resolved_filters.items() (line 373)
  src.matrx_orm.exceptions.format_message → ...get('count', '?') (line 378)
  src.matrx_orm.exceptions.format_message → ...get('filters') (line 379)
  src.matrx_orm.exceptions.format_message → lines.append('Matrx ORM  |  MultipleObjectsReturned') (line 381)
  src.matrx_orm.exceptions.format_message → lines.append('') (line 382)
  src.matrx_orm.exceptions.format_message → lines.append(f'ERROR: get() returned {count} records — exactly one was expected') (line 383)
  src.matrx_orm.exceptions.format_message → lines.append('') (line 386)
  src.matrx_orm.exceptions.format_message → lines.append(self.message) (line 387)
  src.matrx_orm.exceptions.format_message → lines.append('') (line 389)
  src.matrx_orm.exceptions.format_message → lines.append('Search criteria:') (line 390)
  src.matrx_orm.exceptions.format_message → filters.items() (line 391)
  src.matrx_orm.exceptions.format_message → lines.append(f'  {k}: {v}') (line 392)
  src.matrx_orm.exceptions.format_message → lines.append('') (line 393)
  src.matrx_orm.exceptions.format_message → lines.append('Hint:') (line 394)
  src.matrx_orm.exceptions.format_message → lines.append('  - Your filter criteria matched more than one row.') (line 395)
  src.matrx_orm.exceptions.format_message → lines.append('  - Use filter(...).all() if multiple results are valid.') (line 396)
  src.matrx_orm.exceptions.format_message → lines.append('  - Use filter(...).first() to silently take the first match.') (line 397)
  src.matrx_orm.exceptions.format_message → lines.append('  - Narrow your filter (e.g. add unique fields like id or email).') (line 398)
  src.matrx_orm.exceptions.format_message → lines.append('-' * 80 + '\n') (line 401)
  src.matrx_orm.exceptions.format_message → join(lines) (line 402)
  src.matrx_orm.exceptions.format_message → ...get('db_url', '') (line 421)
  src.matrx_orm.exceptions.format_message → ...get('original_error', '') (line 422)
  src.matrx_orm.exceptions.format_message → lines.append('Matrx ORM  |  ConnectionError') (line 424)
  src.matrx_orm.exceptions.format_message → lines.append('') (line 425)
  src.matrx_orm.exceptions.format_message → lines.append(self.message) (line 426)
  src.matrx_orm.exceptions.format_message → lines.append(f'  Target:   {db_url}') (line 428)
  src.matrx_orm.exceptions.format_message → lines.append(f'  DB error: {original}') (line 430)
  src.matrx_orm.exceptions.format_message → lines.append('') (line 431)
  src.matrx_orm.exceptions.format_message → lines.append('Hint:') (line 432)
  src.matrx_orm.exceptions.format_message → lines.append('  - asyncpg could not establish a connection to the database.') (line 433)
  src.matrx_orm.exceptions.format_message → lines.append('  - This is raised in two cases:') (line 434)
  src.matrx_orm.exceptions.format_message → lines.append('      1. Connection pool creation failed (wrong host/port/credentials).') (line 435)
  src.matrx_orm.exceptions.format_message → lines.append('      2. A live connection was lost mid-operation (ConnectionDoesNotExistError).') (line 438)
  src.matrx_orm.exceptions.format_message → lines.append('  - Verify the host, port, database_name, user, and password in your') (line 441)
  src.matrx_orm.exceptions.format_message → lines.append('    DatabaseProjectConfig registration.') (line 444)
  src.matrx_orm.exceptions.format_message → lines.append('  - Check that the database server is reachable from this environment.') (line 445)
  src.matrx_orm.exceptions.format_message → lines.append('  - SSL is required — ensure the database accepts SSL connections.') (line 448)
  src.matrx_orm.exceptions.format_message → lines.append('-' * 80 + '\n') (line 451)
  src.matrx_orm.exceptions.format_message → join(lines) (line 452)
  src.matrx_orm.exceptions.format_message → ...get('constraint', 'unknown') (line 465)
  src.matrx_orm.exceptions.format_message → ...get('original_error', '') (line 466)
  src.matrx_orm.exceptions.format_message → lines.append('Matrx ORM  |  IntegrityError') (line 468)
  src.matrx_orm.exceptions.format_message → lines.append('') (line 469)
  src.matrx_orm.exceptions.format_message → lines.append(self.message) (line 470)
  src.matrx_orm.exceptions.format_message → lines.append(f'  Constraint: {constraint}') (line 472)
  src.matrx_orm.exceptions.format_message → lines.append(f'  DB error:   {original}') (line 474)
  src.matrx_orm.exceptions.format_message → lines.append('') (line 475)
  src.matrx_orm.exceptions.format_message → lines.append('Hint:') (line 476)
  src.matrx_orm.exceptions.format_message → lines.append('  - A record with these values already exists in the database.') (line 478)
  src.matrx_orm.exceptions.format_message → lines.append('  - Use get_or_none() to check before inserting, or update the existing record.') (line 481)
  src.matrx_orm.exceptions.format_message → lines.append('  - If this is expected (e.g. race condition), wrap the call in a try/except IntegrityError.') (line 484)
  src.matrx_orm.exceptions.format_message → lines.append('  - The referenced record does not exist in the related table.') (line 488)
  src.matrx_orm.exceptions.format_message → lines.append('  - Ensure the parent record is created before the child.') (line 491)
  src.matrx_orm.exceptions.format_message → lines.append('  - Verify the foreign key ID is valid and the related model is saved.') (line 492)
  src.matrx_orm.exceptions.format_message → lines.append('  - The database rejected the write due to a constraint violation.') (line 496)
  src.matrx_orm.exceptions.format_message → lines.append('  - Check for unique constraints, foreign key references, or NOT NULL fields.') (line 499)
  src.matrx_orm.exceptions.format_message → lines.append('  - Review the DB error above for the specific constraint name.') (line 502)
  src.matrx_orm.exceptions.format_message → lines.append('-' * 80 + '\n') (line 505)
  src.matrx_orm.exceptions.format_message → join(lines) (line 506)
  src.matrx_orm.exceptions.format_message → ...get('config_key', '') (line 528)
  src.matrx_orm.exceptions.format_message → ...get('reason', '') (line 529)
  src.matrx_orm.exceptions.format_message → lines.append('Matrx ORM  |  ConfigurationError') (line 531)
  src.matrx_orm.exceptions.format_message → lines.append('') (line 532)
  src.matrx_orm.exceptions.format_message → lines.append(self.message) (line 533)
  src.matrx_orm.exceptions.format_message → lines.append(f'  Config key: {config_key}') (line 535)
  src.matrx_orm.exceptions.format_message → lines.append(f'  Reason:     {reason}') (line 537)
  src.matrx_orm.exceptions.format_message → lines.append('') (line 538)
  src.matrx_orm.exceptions.format_message → lines.append('Hint:') (line 539)
  src.matrx_orm.exceptions.format_message → lines.append('  - The model failed to initialize with the StateManager.') (line 541)
  src.matrx_orm.exceptions.format_message → lines.append('  - Ensure the model is registered via model_registry before making queries.') (line 542)
  src.matrx_orm.exceptions.format_message → lines.append('  - Check that the model class defines _meta, _database, and primary_keys.') (line 545)
  src.matrx_orm.exceptions.format_message → lines.append('  - A database configuration was referenced that has not been registered.') (line 549)
  src.matrx_orm.exceptions.format_message → lines.append('  - Call register_database(DatabaseProjectConfig(...)) at startup before') (line 552)
  src.matrx_orm.exceptions.format_message → lines.append('    any model queries run.') (line 555)
  src.matrx_orm.exceptions.format_message → lines.append('  - Verify the config_key matches exactly what was passed to register_database().') (line 556)
  src.matrx_orm.exceptions.format_message → lines.append('  - Check that all required env vars (host, port, user, password, database_name)') (line 559)
  src.matrx_orm.exceptions.format_message → lines.append('    are set and non-empty.') (line 562)
  src.matrx_orm.exceptions.format_message → lines.append('-' * 80 + '\n') (line 563)
  src.matrx_orm.exceptions.format_message → join(lines) (line 564)
  src.matrx_orm.exceptions.format_message → ...get('operation') (line 579)
  src.matrx_orm.exceptions.format_message → ...get('original_error', '') (line 580)
  src.matrx_orm.exceptions.format_message → lines.append('Matrx ORM  |  CacheError') (line 582)
  src.matrx_orm.exceptions.format_message → lines.append('') (line 583)
  src.matrx_orm.exceptions.format_message → lines.append(self.message) (line 584)
  src.matrx_orm.exceptions.format_message → lines.append(f'  Cause:     {original}') (line 586)
  src.matrx_orm.exceptions.format_message → lines.append('') (line 587)
  src.matrx_orm.exceptions.format_message → lines.append('Hint:') (line 588)
  src.matrx_orm.exceptions.format_message → lines.append('  - An error occurred inside the in-memory cache lookup.') (line 590)
  src.matrx_orm.exceptions.format_message → lines.append('  - This is typically caused by a model missing primary_keys in _meta,') (line 591)
  src.matrx_orm.exceptions.format_message → lines.append("    or a cached record that doesn't have the expected attributes.") (line 594)
  src.matrx_orm.exceptions.format_message → lines.append('  - asyncio.Lock() creation failed, which should not normally happen.') (line 598)
  src.matrx_orm.exceptions.format_message → lines.append('  - This may indicate an issue with the event loop state.') (line 601)
  src.matrx_orm.exceptions.format_message → lines.append('  - The cache miss triggered a database fetch, which then raised an') (line 603)
  src.matrx_orm.exceptions.format_message → lines.append('    unexpected error (not a DoesNotExist — that is handled separately).') (line 606)
  src.matrx_orm.exceptions.format_message → lines.append('  - Check the Cause above for the underlying database error.') (line 609)
  src.matrx_orm.exceptions.format_message → lines.append('  - An unexpected error occurred in the cache layer.') (line 611)
  src.matrx_orm.exceptions.format_message → lines.append('  - CacheErrors do not indicate a data loss problem — the cache is') (line 612)
  src.matrx_orm.exceptions.format_message → lines.append('    a read-through layer; the database is always the source of truth.') (line 615)
  src.matrx_orm.exceptions.format_message → lines.append('-' * 80 + '\n') (line 618)
  src.matrx_orm.exceptions.format_message → join(lines) (line 619)
  src.matrx_orm.exceptions.format_message → lines.append('Matrx ORM  |  StateError') (line 643)
  src.matrx_orm.exceptions.format_message → lines.append('') (line 644)
  src.matrx_orm.exceptions.format_message → lines.append(self.message) (line 645)
  src.matrx_orm.exceptions.format_message → lines.append(f'  Reason:   {reason}') (line 647)
  src.matrx_orm.exceptions.format_message → lines.append(f'  Cause:    {original}') (line 649)
  src.matrx_orm.exceptions.format_message → lines.append('') (line 650)
  src.matrx_orm.exceptions.format_message → lines.append('Hint:') (line 651)
  src.matrx_orm.exceptions.format_message → reason.lower() (line 652)
  src.matrx_orm.exceptions.format_message → lines.append('  - The model has not been registered with the StateManager.') (line 653)
  src.matrx_orm.exceptions.format_message → lines.append('  - This usually means the model file was not imported before queries ran.') (line 654)
  src.matrx_orm.exceptions.format_message → lines.append('  - Ensure all models are imported in your startup/init sequence so') (line 657)
  src.matrx_orm.exceptions.format_message → lines.append('    their metaclass registration runs before any query is attempted.') (line 660)
  src.matrx_orm.exceptions.format_message → reason.lower() (line 663)
  src.matrx_orm.exceptions.format_message → lines.append('  - The asyncpg connection pool encountered an interface error.') (line 664)
  src.matrx_orm.exceptions.format_message → lines.append('  - This can happen if you acquire a connection outside an async context,') (line 667)
  src.matrx_orm.exceptions.format_message → lines.append('    or if the pool was closed and not yet recreated.') (line 670)
  src.matrx_orm.exceptions.format_message → lines.append('  - The pool auto-recreates when the event loop changes (e.g. asyncio.run()).') (line 671)
  src.matrx_orm.exceptions.format_message → reason.lower() (line 674)
  src.matrx_orm.exceptions.format_message → lines.append('  - A connection pool failed to close cleanly during shutdown.') (line 675)
  src.matrx_orm.exceptions.format_message → lines.append('  - This is usually safe to ignore during process exit.') (line 678)
  src.matrx_orm.exceptions.format_message → lines.append('  - If it happens during tests, ensure each test cleans up with AsyncDatabaseManager.cleanup().') (line 679)
  src.matrx_orm.exceptions.format_message → lines.append('  - An unexpected error occurred in the ORM state/cache layer.') (line 683)
  src.matrx_orm.exceptions.format_message → lines.append('  - Check the Cause above for the underlying exception.') (line 686)
  src.matrx_orm.exceptions.format_message → lines.append('-' * 80 + '\n') (line 687)
  src.matrx_orm.exceptions.format_message → join(lines) (line 688)
  src.matrx_orm.exceptions.format_message → ...get('migration', '') (line 732)
  src.matrx_orm.exceptions.format_message → ...get('original_error', '') (line 733)
  src.matrx_orm.exceptions.format_message → lines.append('Matrx ORM  |  MigrationError') (line 735)
  src.matrx_orm.exceptions.format_message → lines.append('') (line 736)
  src.matrx_orm.exceptions.format_message → lines.append(self.message) (line 737)
  src.matrx_orm.exceptions.format_message → lines.append(f'  Migration: {migration}') (line 739)
  src.matrx_orm.exceptions.format_message → lines.append(f'  Detail:    {original}') (line 741)
  src.matrx_orm.exceptions.format_message → lines.append('') (line 743)
  src.matrx_orm.exceptions.format_message → lines.append('Hint:') (line 744)
  src.matrx_orm.exceptions.format_message → original.lower() (line 745)
  src.matrx_orm.exceptions.format_message → lines.append('  - A migration file was edited after it was already applied to the database.') (line 746)
  src.matrx_orm.exceptions.format_message → lines.append('  - NEVER edit applied migration files. The checksums are stored in the') (line 749)
  src.matrx_orm.exceptions.format_message → lines.append('    matrx_migrations table and will no longer match.') (line 752)
  src.matrx_orm.exceptions.format_message → lines.append('  - Create a new migration file to make further changes.') (line 753)
  src.matrx_orm.exceptions.format_message → lines.append("  - The migration file does not define an 'up' coroutine.") (line 755)
  src.matrx_orm.exceptions.format_message → lines.append('  - Every migration file must define:  async def up(db): ...') (line 756)
  src.matrx_orm.exceptions.format_message → lines.append('  - Optionally define:                 async def down(db): ...') (line 757)
  src.matrx_orm.exceptions.format_message → lines.append("  - You tried to roll back a migration that has no 'down' function.") (line 761)
  src.matrx_orm.exceptions.format_message → lines.append('  - Add  async def down(db): ...  to the migration file to enable rollback.') (line 764)
  src.matrx_orm.exceptions.format_message → lines.append('  - A migration recorded in the database no longer exists as a file.') (line 768)
  src.matrx_orm.exceptions.format_message → lines.append('  - Restore the deleted migration file before attempting rollback.') (line 771)
  src.matrx_orm.exceptions.format_message → original.lower() (line 774)
  src.matrx_orm.exceptions.format_message → lines.append('  - Two or more migrations declare each other as dependencies.') (line 775)
  src.matrx_orm.exceptions.format_message → lines.append("  - Review the 'dependencies' lists in those migration files and break the cycle.") (line 778)
  src.matrx_orm.exceptions.format_message → original.lower() (line 781)
  src.matrx_orm.exceptions.format_message → original.lower() (line 781)
  src.matrx_orm.exceptions.format_message → lines.append("  - A migration declares a dependency on a migration file that doesn't exist.") (line 782)
  src.matrx_orm.exceptions.format_message → lines.append("  - Check the 'dependencies' list in the failing migration file.") (line 785)
  src.matrx_orm.exceptions.format_message → lines.append('  - Ensure the dependency name exactly matches the filename stem (without .py).') (line 788)
  src.matrx_orm.exceptions.format_message → original.lower() (line 791)
  src.matrx_orm.exceptions.format_message → lines.append('  - Python could not import the migration file as a module.') (line 792)
  src.matrx_orm.exceptions.format_message → lines.append('  - Check for syntax errors or invalid imports in that migration file.') (line 793)
  src.matrx_orm.exceptions.format_message → lines.append('  - The migration SQL itself raised an error when executed against the database.') (line 797)
  src.matrx_orm.exceptions.format_message → lines.append('  - The database was not modified (each migration runs in a transaction).') (line 800)
  src.matrx_orm.exceptions.format_message → lines.append("  - Fix the SQL in the migration's 'up' function and re-run migrate.") (line 803)
  src.matrx_orm.exceptions.format_message → lines.append('-' * 80 + '\n') (line 806)
  src.matrx_orm.exceptions.format_message → join(lines) (line 807)
  src.matrx_orm.exceptions.format_message → ...get('reason', '') (line 838)
  src.matrx_orm.exceptions.format_message → ...get('query', '') (line 839)
  src.matrx_orm.exceptions.format_message → ...get('args', []) (line 840)
  src.matrx_orm.exceptions.format_message → lines.append('Matrx ORM  |  ParameterError') (line 842)
  src.matrx_orm.exceptions.format_message → lines.append('') (line 843)
  src.matrx_orm.exceptions.format_message → lines.append(self.message) (line 844)
  src.matrx_orm.exceptions.format_message → lines.append(f'  Reason: {reason}') (line 846)
  src.matrx_orm.exceptions.format_message → lines.append(f'  Query:  {short_query}') (line 849)
  src.matrx_orm.exceptions.format_message → lines.append(f'  Args:   {args}') (line 851)
  src.matrx_orm.exceptions.format_message → lines.append('') (line 852)
  src.matrx_orm.exceptions.format_message → lines.append('Hint:') (line 853)
  src.matrx_orm.exceptions.format_message → lines.append('  - asyncpg raised a DataError, meaning a bound parameter value is the wrong type') (line 854)
  src.matrx_orm.exceptions.format_message → lines.append("    or is out of range for the column's PostgreSQL type.") (line 857)
  src.matrx_orm.exceptions.format_message → lines.append('  - Common causes:') (line 858)
  src.matrx_orm.exceptions.format_message → lines.append('      - Passing a string where a UUID or integer is expected.') (line 859)
  src.matrx_orm.exceptions.format_message → lines.append('      - Passing None for a NOT NULL column.') (line 860)
  src.matrx_orm.exceptions.format_message → lines.append('      - Passing a Python list where a scalar is expected (use field__in=... instead).') (line 861)
  src.matrx_orm.exceptions.format_message → lines.append("  - Check the Args above and verify each value matches the column's type.") (line 864)
  src.matrx_orm.exceptions.format_message → lines.append('-' * 80 + '\n') (line 867)
  src.matrx_orm.exceptions.format_message → join(lines) (line 868)
  src.matrx_orm.exceptions.format_message → ...get('operation', '') (line 895)
  src.matrx_orm.exceptions.format_message → ...get('original_error', '') (line 896)
  src.matrx_orm.exceptions.format_message → ...get('query', '') (line 897)
  src.matrx_orm.exceptions.format_message → ...get('args', []) (line 898)
  src.matrx_orm.exceptions.format_message → lines.append('Matrx ORM  |  UnknownDatabaseError') (line 900)
  src.matrx_orm.exceptions.format_message → lines.append('') (line 901)
  src.matrx_orm.exceptions.format_message → lines.append(self.message) (line 902)
  src.matrx_orm.exceptions.format_message → lines.append(f'  Operation: {operation}') (line 904)
  src.matrx_orm.exceptions.format_message → lines.append(f'  DB error:  {original}') (line 906)
  src.matrx_orm.exceptions.format_message → lines.append(f'  Query:     {short_query}') (line 909)
  src.matrx_orm.exceptions.format_message → lines.append(f'  Args:      {args}') (line 911)
  src.matrx_orm.exceptions.format_message → lines.append('') (line 912)
  src.matrx_orm.exceptions.format_message → lines.append('Hint:') (line 913)
  src.matrx_orm.exceptions.format_message → lines.append('  - This is the catch-all for any asyncpg exception not handled by a more') (line 914)
  src.matrx_orm.exceptions.format_message → lines.append('    specific error class (not a syntax error, unique violation, data error,') (line 917)
  src.matrx_orm.exceptions.format_message → lines.append('    or connection failure).') (line 920)
  src.matrx_orm.exceptions.format_message → lines.append('  - The full Python traceback was captured at raise time — check your logs.') (line 921)
  src.matrx_orm.exceptions.format_message → lines.append('  - Common causes: permission denied, relation does not exist, column') (line 924)
  src.matrx_orm.exceptions.format_message → lines.append('    type mismatch, or a Postgres function raising an exception.') (line 927)
  src.matrx_orm.exceptions.format_message → lines.append('  - The Query and Args above are the exact SQL and parameters that failed.') (line 928)
  src.matrx_orm.exceptions.format_message → lines.append('-' * 80 + '\n') (line 931)
  src.matrx_orm.exceptions.format_message → join(lines) (line 932)
```

### Call graph: src.matrx_orm.error_handling

```
async src.matrx_orm.error_handling.handle_orm_operation → src.matrx_orm.error_handling.CacheError() (line 27)
```

### Call graph: src.matrx_orm.extended.app_error_handler

```
Global Scope → src.matrx_orm.extended.app_error_handler.TypeVar('_F') (line 9)
  src.matrx_orm.extended.app_error_handler.__init__ → traceback.format_exc() (line 36)
  src.matrx_orm.extended.app_error_handler.__init__ → traceback.format_exc() (line 36)
  src.matrx_orm.extended.app_error_handler._handle_exception → context.update(extra) (line 70)
  src.matrx_orm.extended.app_error_handler._handle_exception → src.matrx_orm.extended.app_error_handler.AppError() (line 87)
  src.matrx_orm.extended.app_error_handler.handle_errors → inspect.iscoroutinefunction(func) (line 94)
  async src.matrx_orm.extended.app_error_handler.async_wrapper → src.matrx_orm.extended.app_error_handler.func(cls_or_self, *args) (line 98)
  async src.matrx_orm.extended.app_error_handler.async_wrapper → src.matrx_orm.extended.app_error_handler._handle_exception(e, cls_or_self, func.__name__) (line 100)
  async src.matrx_orm.extended.app_error_handler.async_wrapper → src.matrx_orm.extended.app_error_handler.wraps(func) (line 95)
  src.matrx_orm.extended.app_error_handler.sync_wrapper → src.matrx_orm.extended.app_error_handler.func(cls_or_self, *args) (line 107)
  src.matrx_orm.extended.app_error_handler.sync_wrapper → src.matrx_orm.extended.app_error_handler._handle_exception(e, cls_or_self, func.__name__) (line 109)
  src.matrx_orm.extended.app_error_handler.sync_wrapper → src.matrx_orm.extended.app_error_handler.wraps(func) (line 104)
```

### Call graph: src.matrx_orm.utils.sql_utils

```
src.matrx_orm.utils.sql_utils.clean_default_value → re.sub('::[\\w\\s]+', '', default_value) (line 16)
  src.matrx_orm.utils.sql_utils.clean_default_value → cleaned_value.startswith("'") (line 18)
  src.matrx_orm.utils.sql_utils.clean_default_value → cleaned_value.endswith("'") (line 18)
  src.matrx_orm.utils.sql_utils.clean_default_value → cleaned_value.strip("'") (line 19)
  src.matrx_orm.utils.sql_utils.clean_default_value → cleaned_value.lower() (line 26)
  src.matrx_orm.utils.sql_utils.save_to_json → ...join(str(settings.BASE_DIR), 'code_generator/local_data/current_sql_data') (line 32)
  src.matrx_orm.utils.sql_utils.save_to_json → ...join(str(settings.TEMP_DIR), 'code_generator/sql_queries') (line 34)
  src.matrx_orm.utils.sql_utils.save_to_json → ...exists(directory) (line 36)
  src.matrx_orm.utils.sql_utils.save_to_json → os.makedirs(directory) (line 37)
  src.matrx_orm.utils.sql_utils.save_to_json → strftime('%Y%m%d_%H%M%S') (line 39)
  src.matrx_orm.utils.sql_utils.save_to_json → ...now() (line 39)
  src.matrx_orm.utils.sql_utils.save_to_json → ...join(directory, filename) (line 40)
  src.matrx_orm.utils.sql_utils.save_to_json → src.matrx_orm.utils.sql_utils.open(filepath, 'w') (line 42)
  src.matrx_orm.utils.sql_utils.save_to_json → json.dump(data, json_file) (line 43)
  src.matrx_orm.utils.sql_utils.save_to_json → src.matrx_orm.utils.sql_utils.print_link(filepath) (line 45)
  src.matrx_orm.utils.sql_utils.sql_param_to_psycopg2 → params.items() (line 50)
  src.matrx_orm.utils.sql_utils.replace_named_param → match.group(1) (line 53)
  src.matrx_orm.utils.sql_utils.sql_param_to_psycopg2 → re.sub(':(\\w+)', replace_named_param, sql) (line 56)
```

### Call graph: src.matrx_orm.utils.type_converters

```
src.matrx_orm.utils.type_converters.to_python → datetime.fromisoformat(value) (line 23)
  src.matrx_orm.utils.type_converters.to_python → date.fromisoformat(value) (line 25)
  src.matrx_orm.utils.type_converters.to_python → src.matrx_orm.utils.type_converters.UUID(value) (line 27)
  src.matrx_orm.utils.type_converters.to_python → json.loads(value) (line 29)
  src.matrx_orm.utils.type_converters.to_python → src.matrx_orm.utils.type_converters.Decimal(value) (line 31)
  src.matrx_orm.utils.type_converters.to_python → field_type.startswith('array') (line 32)
  src.matrx_orm.utils.type_converters.to_python → field_type.split(':') (line 33)
  src.matrx_orm.utils.type_converters.to_python → cls.to_python(item, item_type) (line 34)
  src.matrx_orm.utils.type_converters.get_db_prep_value → value.isoformat() (line 46)
  src.matrx_orm.utils.type_converters.get_db_prep_value → json.dumps(value) (line 50)
  src.matrx_orm.utils.type_converters.get_db_prep_value → field_type.startswith('array') (line 53)
  src.matrx_orm.utils.type_converters.get_db_prep_value → field_type.split(':') (line 54)
  src.matrx_orm.utils.type_converters.get_db_prep_value → cls.get_db_prep_value(item, item_type) (line 55)
  src.matrx_orm.utils.type_converters.to_python → to_python(value, field_type) (line 71)
  src.matrx_orm.utils.type_converters.get_db_prep_value → get_db_prep_value(value, field_type) (line 77)
  Global Scope → CustomTypeConverter.register_converter('ipaddress', lambda ip: str(ip), lambda ip_str: ipaddress.ip_address(ip_str)) (line 81)
  Global Scope → ipaddress.ip_address(ip_str) (line 81)
  src.matrx_orm.utils.type_converters.convert_query_results → ...items() (line 89)
  src.matrx_orm.utils.type_converters.convert_query_results → TypeConverter.to_python(row[field_name], field.field_type) (line 91)
  src.matrx_orm.utils.type_converters.convert_query_results → converted.append(converted_row) (line 92)
  src.matrx_orm.utils.type_converters.prepare_query_params → params.items() (line 98)
  src.matrx_orm.utils.type_converters.prepare_query_params → TypeConverter.get_db_prep_value(value, model._fields[field_name].field_type) (line 100)
```

### Call graph: src.matrx_orm.adapters.postgresql

> Full detail in [`src/matrx_orm/adapters/MODULE_README.md`](src/matrx_orm/adapters/MODULE_README.md)

```
`src.matrx_orm.adapters.postgresql.__init__ → src.matrx_orm.adapters.postgresql.get_database_config() (line 10)` → ... → `join(filters) (line 170)`
```

### Call graph: src.matrx_orm.adapters.base_adapter

> Full detail in [`src/matrx_orm/adapters/MODULE_README.md`](src/matrx_orm/adapters/MODULE_README.md)

```
`async src.matrx_orm.adapters.base_adapter.__aexit__ → self.close() (line 69)`
```

### Call graph: src.matrx_orm.python_sql.table_typescript_relationship

> Full detail in [`src/matrx_orm/python_sql/MODULE_README.md`](src/matrx_orm/python_sql/MODULE_README.md)

```
`src.matrx_orm.python_sql.table_typescript_relationship.transform_relationships_for_typescript → items() (line 34)` → ... → `src.matrx_orm.python_sql.table_typescript_relationship.analyze_relationships(relationships) (line 150)`
```

### Call graph: src.matrx_orm.python_sql.table_detailed_relationships

> Full detail in [`src/matrx_orm/python_sql/MODULE_README.md`](src/matrx_orm/python_sql/MODULE_README.md)

```
`src.matrx_orm.python_sql.table_detailed_relationships.get_table_relationships → src.matrx_orm.python_sql.table_detailed_relationships.execute_sql_query(query, (schema, schema), database_project) (line 118)` → ... → `src.matrx_orm.python_sql.table_detailed_relationships.analyze_many_to_many_relationships(all_relationships_list) (line 489)`
```

### Call graph: src.matrx_orm.python_sql.db_objects

> Full detail in [`src/matrx_orm/python_sql/MODULE_README.md`](src/matrx_orm/python_sql/MODULE_README.md)

```
`src.matrx_orm.python_sql.db_objects.get_full_db_objects → src.matrx_orm.python_sql.db_objects.execute_sql_query(query, (schema,), database_project) (line 172)` → ... → `src.matrx_orm.python_sql.db_objects.get_db_objects() (line 389)`
```

### Call graph: src.matrx_orm.query.executor

> Full detail in [`src/matrx_orm/query/MODULE_README.md`](src/matrx_orm/query/MODULE_README.md)

```
`Global Scope → src.matrx_orm.query.executor.object() (line 21)` → ... → `self.model() (line 877)`
```

### Call graph: src.matrx_orm.query.builder

> Full detail in [`src/matrx_orm/query/MODULE_README.md`](src/matrx_orm/query/MODULE_README.md)

```
`Global Scope → src.matrx_orm.query.builder.TypeVar('ModelT') (line 22)` → ... → `self.offset(start) (line 512)`
```

### Call graph: src.matrx_orm.client.postgres_connection

```
src.matrx_orm.client.postgres_connection.init_connection_details → src.matrx_orm.client.postgres_connection.get_database_config() (line 20)
  src.matrx_orm.client.postgres_connection.init_connection_details → config.get('host') (line 23)
  src.matrx_orm.client.postgres_connection.init_connection_details → config.get('port') (line 24)
  src.matrx_orm.client.postgres_connection.init_connection_details → config.get('protocol', 'postgresql') (line 25)
  src.matrx_orm.client.postgres_connection.init_connection_details → config.get('database_name') (line 26)
  src.matrx_orm.client.postgres_connection.init_connection_details → config.get('user') (line 27)
  src.matrx_orm.client.postgres_connection.init_connection_details → config.get('password') (line 28)
  src.matrx_orm.client.postgres_connection.init_connection_details → src.matrx_orm.client.postgres_connection.quote_plus(safe_user) (line 47)
  src.matrx_orm.client.postgres_connection.init_connection_details → src.matrx_orm.client.postgres_connection.quote_plus(safe_password) (line 47)
  src.matrx_orm.client.postgres_connection.init_connection_details → src.matrx_orm.client.postgres_connection.ConnectionPool(connection_string) (line 54)
  src.matrx_orm.client.postgres_connection.init_connection_details → open() (line 61)
  src.matrx_orm.client.postgres_connection.get_postgres_connection → src.matrx_orm.client.postgres_connection.init_connection_details(database_project) (line 67)
  src.matrx_orm.client.postgres_connection.get_postgres_connection → getconn() (line 68)
  src.matrx_orm.client.postgres_connection.execute_sql_query → src.matrx_orm.client.postgres_connection.get_postgres_connection(database_project) (line 76)
  src.matrx_orm.client.postgres_connection.execute_sql_query → conn.cursor() (line 78)
  src.matrx_orm.client.postgres_connection.execute_sql_query → src.matrx_orm.client.postgres_connection.sql_param_to_psycopg2(query, params) (line 80)
  src.matrx_orm.client.postgres_connection.execute_sql_query → cur.execute(query, params) (line 81)
  src.matrx_orm.client.postgres_connection.execute_sql_query → cur.fetchall() (line 82)
  src.matrx_orm.client.postgres_connection.execute_sql_query → conn.commit() (line 83)
  src.matrx_orm.client.postgres_connection.execute_sql_query → conn.rollback() (line 86)
  src.matrx_orm.client.postgres_connection.execute_sql_query → putconn(conn) (line 89)
  src.matrx_orm.client.postgres_connection.execute_sql_file → ...join(os.path.dirname(__file__), 'sql') (line 96)
  src.matrx_orm.client.postgres_connection.execute_sql_file → ...dirname(__file__) (line 96)
  src.matrx_orm.client.postgres_connection.execute_sql_file → src.matrx_orm.client.postgres_connection.open(os.path.join(sql_dir, filename), 'r') (line 97)
  src.matrx_orm.client.postgres_connection.execute_sql_file → ...join(sql_dir, filename) (line 97)
  src.matrx_orm.client.postgres_connection.execute_sql_file → sql_file.read() (line 98)
  src.matrx_orm.client.postgres_connection.execute_sql_file → src.matrx_orm.client.postgres_connection.sql_param_to_psycopg2(query, params) (line 101)
  src.matrx_orm.client.postgres_connection.execute_sql_file → src.matrx_orm.client.postgres_connection.execute_sql_query(query, params, database_project) (line 106)
  src.matrx_orm.client.postgres_connection.execute_transaction_query → src.matrx_orm.client.postgres_connection.get_postgres_connection(database_project) (line 114)
  src.matrx_orm.client.postgres_connection.execute_transaction_query → conn.cursor() (line 116)
  src.matrx_orm.client.postgres_connection.execute_transaction_query → src.matrx_orm.client.postgres_connection.sql_param_to_psycopg2(query, params) (line 118)
  src.matrx_orm.client.postgres_connection.execute_transaction_query → cur.execute(query, params) (line 119)
  src.matrx_orm.client.postgres_connection.execute_transaction_query → conn.commit() (line 120)
  src.matrx_orm.client.postgres_connection.execute_transaction_query → cur.fetchall() (line 124)
  src.matrx_orm.client.postgres_connection.execute_transaction_query → putconn(conn) (line 128)
  src.matrx_orm.client.postgres_connection.execute_batch_query → src.matrx_orm.client.postgres_connection.get_postgres_connection(database_project) (line 136)
  src.matrx_orm.client.postgres_connection.execute_batch_query → row_params.items() (line 150)
  src.matrx_orm.client.postgres_connection.execute_batch_query → json.dumps(value) (line 153)
  src.matrx_orm.client.postgres_connection.execute_batch_query → conn.cursor() (line 158)
  src.matrx_orm.client.postgres_connection.execute_batch_query → src.matrx_orm.client.postgres_connection.sql_param_to_psycopg2(query, processed_params) (line 160)
  src.matrx_orm.client.postgres_connection.execute_batch_query → cur.execute(query_with_names, params) (line 161)
  src.matrx_orm.client.postgres_connection.execute_batch_query → conn.commit() (line 162)
  src.matrx_orm.client.postgres_connection.execute_batch_query → cur.fetchall() (line 164)
  src.matrx_orm.client.postgres_connection.execute_batch_query → all_results.extend(result) (line 166)
  src.matrx_orm.client.postgres_connection.execute_batch_query → putconn(conn) (line 170)
```

### Call graph: src.matrx_orm.middleware.base

```
src.matrx_orm.middleware.base.add_middleware → ...append(middleware) (line 22)
  async src.matrx_orm.middleware.base.process_query → middleware.process_query(query) (line 26)
  async src.matrx_orm.middleware.base.process_result → middleware.process_result(result) (line 31)
  async src.matrx_orm.middleware.base.process_query → self.get_current_tenant_id() (line 81)
  async src.matrx_orm.middleware.base.process_query → self.encrypt_func(query['values'][field]) (line 106)
  async src.matrx_orm.middleware.base.process_result → self.decrypt_func(result[field]) (line 113)
  async src.matrx_orm.middleware.base.process_result → self.decrypt_func(item[field]) (line 118)
  async src.matrx_orm.middleware.base.process_query → ...items() (line 128)
  async src.matrx_orm.middleware.base.process_query → src.matrx_orm.middleware.base.rule(query['values'][field]) (line 130)
  async src.matrx_orm.middleware.base.process_query → time.time() (line 145)
  async src.matrx_orm.middleware.base.process_result → time.time() (line 151)
  async src.matrx_orm.middleware.base.process_query → query.get('operation') (line 159)
  async src.matrx_orm.middleware.base.process_query → self.log_operation(query) (line 160)
  async src.matrx_orm.middleware.base.process_query → ...items() (line 190)
  async src.matrx_orm.middleware.base.process_query → src.matrx_orm.middleware.base.transform(query['values'][field]) (line 192)
  async src.matrx_orm.middleware.base.process_query → self.get_user_permissions() (line 205)
  async src.matrx_orm.middleware.base.process_query → ...start_span('database_query') (line 229)
  async src.matrx_orm.middleware.base.process_query → span.set_tag('query', str(query)) (line 230)
  Global Scope → src.matrx_orm.middleware.base.MiddlewareManager() (line 239)
  Global Scope → middleware_manager.add_middleware(QueryLoggingMiddleware()) (line 240)
  Global Scope → src.matrx_orm.middleware.base.QueryLoggingMiddleware() (line 240)
  Global Scope → middleware_manager.add_middleware(CachingMiddleware()) (line 241)
  Global Scope → src.matrx_orm.middleware.base.CachingMiddleware() (line 241)
  Global Scope → middleware_manager.add_middleware(SoftDeleteMiddleware()) (line 242)
  Global Scope → src.matrx_orm.middleware.base.SoftDeleteMiddleware() (line 242)
  Global Scope → middleware_manager.process_query(query) (line 248)
```

### Call graph: src.matrx_orm.sql_executor.utils

> Full detail in [`src/matrx_orm/sql_executor/MODULE_README.md`](src/matrx_orm/sql_executor/MODULE_README.md)

```
`src.matrx_orm.sql_executor.utils.list_available_queries → src.matrx_orm.sql_executor.utils.get_registry() (line 5)` → ... → `join(docs) (line 61)`
```

### Call graph: src.matrx_orm.sql_executor.executor

> Full detail in [`src/matrx_orm/sql_executor/MODULE_README.md`](src/matrx_orm/sql_executor/MODULE_README.md)

```
`src.matrx_orm.sql_executor.executor.validate_params → src.matrx_orm.sql_executor.executor.get_registry() (line 17)` → ... → `src.matrx_orm.sql_executor.executor.db_execute_batch_query(query_data['query'], validated_params, batch_size, query_data['database']) (line 159)`
```

### Call graph: src.matrx_orm.sql_executor.registry

> Full detail in [`src/matrx_orm/sql_executor/MODULE_README.md`](src/matrx_orm/sql_executor/MODULE_README.md)

```
`src.matrx_orm.sql_executor.registry.get → ...get(name) (line 18)` → ... → `_global_registry.register(name, query) (line 52)`
```

### Call graph: src.matrx_orm.schema_builder.code_handler

> Full detail in [`src/matrx_orm/schema_builder/MODULE_README.md`](src/matrx_orm/schema_builder/MODULE_README.md)

```
`src.matrx_orm.schema_builder.code_handler._is_allowed → lower() (line 27)` → ... → `write_to_json(path, data) (line 50)`
```

### Call graph: src.matrx_orm.schema_builder.columns

> Full detail in [`src/matrx_orm/schema_builder/MODULE_README.md`](src/matrx_orm/schema_builder/MODULE_README.md)

```
`src.matrx_orm.schema_builder.columns.__init__ → self.initit_level_1() (line 79)` → ... → `...replace('vector(', '') (line 1324)`
```

### Call graph: src.matrx_orm.schema_builder.schema

> Full detail in [`src/matrx_orm/schema_builder/MODULE_README.md`](src/matrx_orm/schema_builder/MODULE_README.md)

```
`src.matrx_orm.schema_builder.schema.format_ts_object → re.sub('"(\\w+)"\\s*:', '\\1:', ts_object_str) (line 20)` → ... → `...items() (line 893)`
```

### Call graph: src.matrx_orm.schema_builder.common

> Full detail in [`src/matrx_orm/schema_builder/MODULE_README.md`](src/matrx_orm/schema_builder/MODULE_README.md)

```
`Global Scope → dotenv.load_dotenv() (line 7)` → ... → `os.getenv('MATRX_VERBOSE', '') (line 50)`
```

### Call graph: src.matrx_orm.schema_builder.runner

> Full detail in [`src/matrx_orm/schema_builder/MODULE_README.md`](src/matrx_orm/schema_builder/MODULE_README.md)

```
`src.matrx_orm.schema_builder.runner._close_pools → connection_pools.items() (line 29)` → ... → `src.matrx_orm.schema_builder.runner._close_pools() (line 252)`
```

### Call graph: src.matrx_orm.schema_builder.views

> Full detail in [`src/matrx_orm/schema_builder/MODULE_README.md`](src/matrx_orm/schema_builder/MODULE_README.md)

```
`src.matrx_orm.schema_builder.views.__init__ → ...to_snake_case(self.name) (line 36)` → ... → `self.generate_unique_name_lookups() (line 50)`
```

### Call graph: src.matrx_orm.schema_builder.relationships

> Full detail in [`src/matrx_orm/schema_builder/MODULE_README.md`](src/matrx_orm/schema_builder/MODULE_README.md)

```
`src.matrx_orm.schema_builder.relationships.__init__ → ...to_camel_case(self.column) (line 21)` → ... → `...to_camel_case(source_table.name) (line 29)`
```

### Call graph: src.matrx_orm.schema_builder.tables

> Full detail in [`src/matrx_orm/schema_builder/MODULE_README.md`](src/matrx_orm/schema_builder/MODULE_README.md)

```
`src.matrx_orm.schema_builder.tables.__init__ → ...to_snake_case(self.name) (line 91)` → ... → `...items() (line 1224)`
```

### Call graph: src.matrx_orm.schema_builder.generator

> Full detail in [`src/matrx_orm/schema_builder/MODULE_README.md`](src/matrx_orm/schema_builder/MODULE_README.md)

```
`src.matrx_orm.schema_builder.generator.get_schema_structure → schema_manager.get_table(table_name) (line 9)` → ... → `join(lines) (line 159)`
```

### Call graph: src.matrx_orm.schema_builder.schema_manager

> Full detail in [`src/matrx_orm/schema_builder/MODULE_README.md`](src/matrx_orm/schema_builder/MODULE_README.md)

```
`src.matrx_orm.schema_builder.schema_manager.__init__ → src.matrx_orm.schema_builder.schema_manager.get_database_config(database_project) (line 33)` → ... → `...save_frontend_junction_analysis_json(frontend_junction_analysis) (line 724)`
```

### Call graph: src.matrx_orm.schema_builder.helpers.entity_generators

> Full detail in [`src/matrx_orm/schema_builder/MODULE_README.md`](src/matrx_orm/schema_builder/MODULE_README.md)

```
`src.matrx_orm.schema_builder.helpers.entity_generators.generate_typescript_entity → overrides.get('schemaType', 'null') (line 19)` → ... → `src.matrx_orm.schema_builder.helpers.entity_generators.generate_all_entity_main_hooks(entity_names) (line 303)`
```

### Call graph: src.matrx_orm.schema_builder.helpers.git_checker

> Full detail in [`src/matrx_orm/schema_builder/MODULE_README.md`](src/matrx_orm/schema_builder/MODULE_README.md)

```
`src.matrx_orm.schema_builder.helpers.git_checker.check_git_status → os.getenv('ADMIN_PYTHON_ROOT', '') (line 17)` → ... → `sys.exit(1) (line 114)`
```

### Call graph: src.matrx_orm.schema_builder.helpers.base_generators

> Full detail in [`src/matrx_orm/schema_builder/MODULE_README.md`](src/matrx_orm/schema_builder/MODULE_README.md)

```
`src.matrx_orm.schema_builder.helpers.base_generators.generate_legacy_dto_manager_class → warnings.warn('generate_legacy_dto_manager_class() is deprecated. Use generate_base_manager_class() which scaffolds a ModelView.', DeprecationWarning) (line 189)` → ... → `src.matrx_orm.schema_builder.helpers.base_generators.plt(file_path, 'Manager class saved') (line 648)`
```

### Call graph: src.matrx_orm.core.config

> Full detail in [`src/matrx_orm/core/MODULE_README.md`](src/matrx_orm/core/MODULE_README.md)

```
`Global Scope → src.matrx_orm.core.config.field() (line 26)` → ... → `...join(ADMIN_TS_ROOT, 'constants/') (line 496)`
```

### Call graph: src.matrx_orm.core.signals

> Full detail in [`src/matrx_orm/core/MODULE_README.md`](src/matrx_orm/core/MODULE_README.md)

```
`src.matrx_orm.core.signals.connect → ...append(receiver) (line 54)` → ... → `src.matrx_orm.core.signals.Signal('post_delete') (line 99)`
```

### Call graph: src.matrx_orm.core.fields

> Full detail in [`src/matrx_orm/core/MODULE_README.md`](src/matrx_orm/core/MODULE_README.md)

```
`Global Scope → src.matrx_orm.core.fields.TypeVar('_JT') (line 15)` → ... → `validate(value) (line 1255)`
```

### Call graph: src.matrx_orm.core.base

> Full detail in [`src/matrx_orm/core/MODULE_README.md`](src/matrx_orm/core/MODULE_README.md)

```
`src.matrx_orm.core.base._to_snake_case → lower() (line 43)` → ... → `src.matrx_orm.core.base.QueryBuilder(cls) (line 1392)`
```

### Call graph: src.matrx_orm.core.extended

> Full detail in [`src/matrx_orm/core/MODULE_README.md`](src/matrx_orm/core/MODULE_README.md)

```
`Global Scope → src.matrx_orm.core.extended.TypeVar('ModelT') (line 16)` → ... → `self.delete_where() (line 1861)`
```

### Call graph: src.matrx_orm.core.async_db_manager

> Full detail in [`src/matrx_orm/core/MODULE_README.md`](src/matrx_orm/core/MODULE_README.md)

```
`async src.matrx_orm.core.async_db_manager._init_vector_codec → conn.set_type_codec('vector') (line 39)` → ... → `src.matrx_orm.core.async_db_manager.cause_error() (line 352)`
```

### Call graph: src.matrx_orm.core.model_view

> Full detail in [`src/matrx_orm/core/MODULE_README.md`](src/matrx_orm/core/MODULE_README.md)

```
`src.matrx_orm.core.model_view.__new__ → computed.update(base_computed) (line 86)` → ... → `warnings.warn(f"[ModelView:{view_name}] Prefetch of relation '{relation_name}' failed: {type(exc).__name__}: {exc}. Skipped.", RuntimeWarning) (line 221)`
```

### Call graph: src.matrx_orm.core.registry

> Full detail in [`src/matrx_orm/core/MODULE_README.md`](src/matrx_orm/core/MODULE_README.md)

```
`src.matrx_orm.core.registry.register_all → cls.register(model) (line 25)` → ... → `model_registry.get_model(model_name) (line 46)`
```

### Call graph: src.matrx_orm.core.paginator

> Full detail in [`src/matrx_orm/core/MODULE_README.md`](src/matrx_orm/core/MODULE_README.md)

```
`Global Scope → src.matrx_orm.core.paginator.TypeVar('ModelT') (line 34)` → ... → `self.page(self._current_page) (line 190)`
```

### Call graph: src.matrx_orm.core.expressions

> Full detail in [`src/matrx_orm/core/MODULE_README.md`](src/matrx_orm/core/MODULE_README.md)

```
`src.matrx_orm.core.expressions.__add__ → src.matrx_orm.core.expressions.Expression(self.field_name, '+', other) (line 19)` → ... → `params.append(literal) (line 760)`
```

### Call graph: src.matrx_orm.core.types

> Full detail in [`src/matrx_orm/core/MODULE_README.md`](src/matrx_orm/core/MODULE_README.md)

```
`Global Scope → src.matrx_orm.core.types.TypeVar('ModelT') (line 31)` → ... → `src.matrx_orm.core.types.dataclass() (line 192)`
```

### Call graph: src.matrx_orm.core.transaction

> Full detail in [`src/matrx_orm/core/MODULE_README.md`](src/matrx_orm/core/MODULE_README.md)

```
`Global Scope → src.matrx_orm.core.transaction.ContextVar('_active_connection') (line 35)` → ... → `...get('MATRX_DEFAULT_DATABASE', 'default') (line 159)`
```

### Call graph: src.matrx_orm.core.relations

> Full detail in [`src/matrx_orm/core/MODULE_README.md`](src/matrx_orm/core/MODULE_README.md)

```
`src.matrx_orm.core.relations._related_model → src.matrx_orm.core.relations.get_model_by_name(self.to_model) (line 29)` → ... → `target.lower() (line 478)`
```

### Call graph: src.matrx_orm.operations.delete

> Full detail in [`src/matrx_orm/operations/MODULE_README.md`](src/matrx_orm/operations/MODULE_README.md)

```
`async src.matrx_orm.operations.delete.delete → delete() (line 17)` → ... → `post_delete.send(model_cls) (line 70)`
```

### Call graph: src.matrx_orm.operations.read

> Full detail in [`src/matrx_orm/operations/MODULE_README.md`](src/matrx_orm/operations/MODULE_README.md)

```
`async src.matrx_orm.operations.read.get → get() (line 5)` → ... → `src.matrx_orm.operations.read.QueryBuilder(model_cls) (line 51)`
```

### Call graph: src.matrx_orm.operations.create

> Full detail in [`src/matrx_orm/operations/MODULE_README.md`](src/matrx_orm/operations/MODULE_README.md)

```
`async src.matrx_orm.operations.create.create → src.matrx_orm.operations.create.model_cls() (line 16)` → ... → `src.matrx_orm.operations.create.create(model_cls) (line 188)`
```

### Call graph: src.matrx_orm.operations.update

> Full detail in [`src/matrx_orm/operations/MODULE_README.md`](src/matrx_orm/operations/MODULE_README.md)

```
`async src.matrx_orm.operations.update.update → update() (line 20)` → ... → `post_save.send(model_cls) (line 197)`
```
<!-- /AUTO:call_graph -->
