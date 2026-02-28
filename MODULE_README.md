# `` — Module Overview

> This document is partially auto-generated. Sections tagged `<!-- AUTO:id -->` are refreshed by the generator.
> Everything else is yours to edit freely and will never be overwritten.

<!-- AUTO:meta -->
## About This Document

This file is **partially auto-generated**. Sections wrapped in `<!-- AUTO:id -->` tags
are overwritten each time the generator runs. Everything else is yours to edit freely.

| Field | Value |
|-------|-------|
| Module | `` |
| Last generated | 2026-02-28 13:58 |
| Output file | `MODULE_README.md` |
| Signature mode | `signatures` |


**Child READMEs detected** (signatures collapsed — see links for detail):

| README | |
|--------|---|
| [`src/MODULE_README.md`](src/MODULE_README.md) | last generated 2026-02-28 13:57 |
| [`tests/MODULE_README.md`](tests/MODULE_README.md) | last generated 2026-02-28 13:57 |
**To refresh auto-sections:**
```bash
python utils/code_context/generate_module_readme.py  --mode signatures
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

> Auto-generated. 108 files across 23 directories.

```
./
├── .arman/
│   ├── pending/
│   │   ├── versioning/
├── .python-version
├── MODULE_README.md
├── database/
│   ├── orm/
│   │   ├── extended/
│   │   │   ├── managers/
│   │   │   │   ├── ai_model_base.py
├── examples/
├── extended_jan5_backup.py
├── main.py
├── release.sh
├── scripts/
│   ├── publish.sh
├── src/
│   ├── MODULE_README.md
│   ├── matrx_orm/
│   │   ├── __init__.py
│   │   ├── adapters/
│   │   │   ├── __init__.py
│   │   │   ├── base_adapter.py
│   │   │   ├── postgresql.py
│   │   ├── client/
│   │   │   ├── __init__.py
│   │   │   ├── postgres_connection.py
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── async_db_manager.py
│   │   │   ├── base.py
│   │   │   ├── config.py
│   │   │   ├── expressions.py
│   │   │   ├── extended.py
│   │   │   ├── fields.py
│   │   │   ├── model_view.py
│   │   │   ├── paginator.py
│   │   │   ├── registry.py
│   │   │   ├── relations.py
│   │   │   ├── signals.py
│   │   │   ├── transaction.py
│   │   │   ├── types.py
│   │   ├── error_handling.py
│   │   ├── exceptions.py
│   │   ├── extended/
│   │   │   ├── __init__.py
│   │   │   ├── app_error_handler.py
│   │   ├── middleware/
│   │   │   ├── __init__.py
│   │   │   ├── base.py
│   │   ├── operations/
│   │   │   ├── __init__.py
│   │   │   ├── create.py
│   │   │   ├── delete.py
│   │   │   ├── read.py
│   │   │   ├── update.py
│   │   ├── py.typed
│   │   ├── python_sql/
│   │   │   ├── __init__.py
│   │   │   ├── db_objects.py
│   │   │   ├── table_detailed_relationships.py
│   │   │   ├── table_typescript_relationship.py
│   │   ├── query/
│   │   │   ├── __init__.py
│   │   │   ├── builder.py
│   │   │   ├── executor.py
│   │   ├── schema_builder/
│   │   │   ├── __init__.py
│   │   │   ├── code_handler.py
│   │   │   ├── columns.py
│   │   │   ├── common.py
│   │   │   ├── generator.py
│   │   │   ├── helpers/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── base_generators.py
│   │   │   │   ├── entity_generators.py
│   │   │   │   ├── git_checker.py
│   │   │   ├── relationships.py
│   │   │   ├── runner.py
│   │   │   ├── schema.py
│   │   │   ├── schema_manager.py
│   │   │   ├── tables.py
│   │   │   ├── views.py
│   │   ├── sql_executor/
│   │   │   ├── __init__.py
│   │   │   ├── executor.py
│   │   │   ├── queries.py
│   │   │   ├── registry.py
│   │   │   ├── types.py
│   │   │   ├── utils.py
│   │   ├── state.py
│   │   ├── utils/
│   │   │   ├── __init__.py
│   │   │   ├── sql_utils.py
│   │   │   ├── type_converters.py
├── tests/
│   ├── MODULE_README.md
│   ├── __init__.py
│   ├── conftest.py
│   ├── level1/
│   │   ├── __init__.py
│   │   ├── test_config.py
│   │   ├── test_ddl_generator.py
│   │   ├── test_exceptions.py
│   │   ├── test_fields.py
│   │   ├── test_migration_diff_types.py
│   │   ├── test_migration_loader.py
│   │   ├── test_model_instance.py
│   │   ├── test_model_meta.py
│   │   ├── test_query_builder.py
│   │   ├── test_query_executor_sql.py
│   │   ├── test_registry.py
│   │   ├── test_relations.py
│   │   ├── test_state_cache.py
│   ├── level2/
│   │   ├── __init__.py
│   │   ├── conftest.py
│   │   ├── test_bulk_ops.py
│   │   ├── test_cache_integration.py
│   │   ├── test_crud.py
│   │   ├── test_foreign_keys.py
│   │   ├── test_m2m.py
│   │   ├── test_manager.py
│   │   ├── test_migrations_live.py
│   │   ├── test_query_execution.py
│   │   ├── test_schema_diff.py
│   ├── sample_project/
│   │   ├── __init__.py
│   │   ├── generate.py
│   │   ├── generated/
│   │   │   ├── .gitkeep
│   │   │   ├── primary/
│   │   ├── test_schema_generation.py
│   ├── schema/
│   │   ├── entity_tests.py
│   │   ├── test_base_generation.py
│   │   ├── test_generate_schema.py
│   ├── test_model_cls_refactor.py
# excluded: 21 .md, 2 .example, 2 (no ext), 1 .toml, 1 .lock, 1 .yaml
```
<!-- /AUTO:tree -->

<!-- AUTO:signatures -->
## API Signatures

> Auto-generated via `output_mode="{mode}"`. ~5-10% token cost vs full source.
> For full source, open the individual files directly.
> Submodules with their own `MODULE_README.md` are collapsed to a single stub line.

```
---
Filepath: extended_jan5_backup.py  [python]

  ModelT = TypeVar('ModelT')
  class BaseDTO:
      async def from_model(cls, model)
      async def _initialize_dto(self, model)
      def _get_error_context(self)
      def _report_error(self, message: str, error_type: str = 'GenericError', client_visible: str = None)
      def __getattr__(self, name)
      async def fetch_fk(self, field_name)
      async def fetch_ifk(self, field_name)
      async def fetch_one_relation(self, field_name)
      async def filter_fk(self, field_name, **kwargs)
      async def filter_ifk(self, field_name, **kwargs)
      def _serialize_value(self, value: Any, visited: Set[int]) -> Any
      def to_dict(self, visited: Set[int] = None) -> dict
      def print_keys(self)
      def __repr__(self) -> str
  class BaseManager(Generic[ModelT]):
      def __init__(self, model: Type[ModelT], dto_class = None, fetch_on_init_limit: int = 0, FETCH_ON_INIT_WITH_WARNINGS_OFF: Optional[str] = None)
      def _initialize_manager(self)
      def _get_error_context(self) -> dict
      def _report_error(self, message: str, error_type: str = 'GenericError', client_visible: str = None)
      async def _initialize_dto_runtime(self, dto, item)
      async def _initialize_item_runtime(self, item: Optional[ModelT]) -> Optional[ModelT]
      async def initialize(self)
      def initialize_sync(self)
      def add_computed_field(self, field)
      def add_relation_field(self, field)
      async def _process_item(self, item: Optional[ModelT]) -> Optional[ModelT]
      async def _get_item_or_raise(self, use_cache = True, **kwargs) -> ModelT
      async def _get_item_or_none(self, use_cache = True, **kwargs) -> Optional[ModelT]
      async def _get_item_with_retry(self, use_cache = True, **kwargs) -> ModelT
      async def _get_items(self, order_by: str = None, **kwargs) -> List[ModelT]
      async def _get_first_item(self, order_by: str = None, **kwargs) -> Optional[ModelT]
      async def _get_last_item(self, order_by: str = None, **kwargs) -> Optional[ModelT]
      async def _create_item(self, **data) -> ModelT
      async def _create_items(self, items_data: list, batch_size: int = 1000, ignore_conflicts: bool = False) -> List[ModelT]
      async def _update_item(self, item: ModelT, **updates) -> ModelT
      async def _delete_item(self, item)
      async def _delete_items(self, item)
      def _add_to_active(self, item_id)
      def _remove_from_active(self, item_id)
      async def _fetch_related(self, item, relation_name)
      async def _fetch_all_related(self, item)
      async def load_item(self, use_cache = True, **kwargs) -> ModelT
      async def load_item_or_none(self, use_cache = True, **kwargs) -> Optional[ModelT]
      async def load_item_with_retry(self, use_cache = True, **kwargs) -> ModelT
      async def load_items(self, **kwargs) -> List[ModelT]
      async def load_by_id(self, item_id) -> ModelT
      async def load_by_id_with_retry(self, item_id) -> ModelT
      async def load_items_by_ids(self, item_ids) -> List[ModelT]
      async def add_active_by_id(self, item_id)
      async def add_active_by_ids(self, item_ids)
      async def remove_active_by_id(self, item_id)
      async def remove_active_by_ids(self, item_ids)
      async def remove_all_active(self)
      async def get_active_items(self) -> List[ModelT]
      async def create_item(self, **data) -> ModelT
      async def create_items(self, items_data, batch_size = 1000, ignore_conflicts = False) -> List[ModelT]
      async def update_item(self, item_id, **updates) -> ModelT
      async def update_items(self, objects, fields, batch_size = 1000)
      async def delete_item(self, item_id)
      async def delete_items(self, objects, batch_size = 1000)
      async def exists(self, item_id)
      async def get_or_create(self, defaults = None, **kwargs)
      def _item_to_dict(self, item)
      def _print_item_keys(self, item)
      async def get_item_dict(self, item_id)
      async def get_items_dict(self, **kwargs)
      async def get_active_items_dict(self)
      async def create_item_get_dict(self, **data)
      async def update_item_get_dict(self, item_id, **updates)
      async def get_item_with_related(self, item_id, relation_name)
      async def get_item_with_related_with_retry(self, item_id, relation_name)
      async def get_items_with_related(self, relation_name)
      async def get_item_with_all_related(self, item_id)
      async def get_items_with_all_related(self)
      async def get_items_with_related_list(self, relation_names)
      async def get_item_through_fk(self, item_id, first_relation, second_relation)
      async def get_items_with_related_dict(self, relation_name)
      async def get_items_with_all_related_dict(self)
      async def create_item_get_object(self, **data)
      async def add_active_by_id_or_not(self, item_id = None)
      async def add_active_by_item_or_not(self, item = None)
      async def add_active_by_ids_or_not(self, item_ids = None)
      async def add_active_by_items_or_not(self, items = None)
      async def get_active_item(self, item_id)
      async def get_active_item_dict(self, item_id)
      async def load_item_get_dict(self, use_cache = True, **kwargs)
      async def load_items_by_ids_get_dict(self, item_ids)
      async def filter_items(self, **kwargs) -> List[ModelT]
      async def filter_items_by_ids(self, item_ids) -> List[ModelT]
      async def filter_items_get_dict(self, **kwargs)
      async def get_active_item_with_fk(self, item_id, related_model)
      async def get_active_items_with_fks(self)
      async def get_active_item_with_ifk(self, related_model)
      async def get_active_items_with_ifks(self)
      async def get_active_items_with_ifks_dict(self)
      async def get_active_item_with_all_related(self)
      async def get_active_items_with_all_related(self)
      async def get_active_items_with_all_related_dict(self)
      async def get_active_item_with_one_relation(self, relation_name)
      async def get_active_items_with_one_relation(self, relation_name)
      async def get_active_item_with_one_relation_dict(self, relation_name)
      async def get_active_item_with_related_models_list(self, related_models_list)
      async def get_active_items_with_related_models_list(self, related_models_list)
      async def get_active_item_with_related_models_list_dict(self, related_models_list)
      async def get_active_item_with_through_fk(self, item_id, first_relationship, second_relationship)
      async def get_active_item_through_ifk(self, item_id, first_relationship, second_relationship)
      def active_item_ids(self)
      def get_all_attributes(self)
      def get_item_attributes(self, item)
      def _auto_fetch_on_init_sync(self)
      async def _auto_fetch_on_init_async(self)
      def _trigger_fetch_warnings(self, count: int, items: list, warning_limit_threshold: int)
      def _trigger_limit_reached_warning(self, count: int, items: list)
      def _validation_error(self, class_name, data, field, message)
      def load_item_sync(self, use_cache = True, **kwargs) -> ModelT
      def load_item_or_none_sync(self, use_cache = True, **kwargs) -> Optional[ModelT]
      def load_items_sync(self, **kwargs) -> List[ModelT]
      def load_by_id_sync(self, item_id) -> ModelT
      def filter_items_sync(self, **kwargs) -> List[ModelT]
      def create_item_sync(self, **data) -> ModelT
      def update_item_sync(self, item_id, **updates) -> ModelT
      def delete_item_sync(self, item_id)
      def get_or_create_sync(self, defaults = None, **kwargs)
      def exists_sync(self, item_id)
      def get_active_items_sync(self) -> List[ModelT]
      def get_item_dict_sync(self, item_id)
      def get_items_dict_sync(self, **kwargs)



---
Filepath: .python-version  [unknown ()]

  # signature extraction not supported for this language



---
Filepath: release.sh  [unknown (.sh)]

  # signature extraction not supported for this language



---
Filepath: main.py  [python]




---
Submodule: tests/  [35 files — full detail in tests/MODULE_README.md]

---
Filepath: scripts/publish.sh  [unknown (.sh)]

  # signature extraction not supported for this language



---
Submodule: src/  [64 files — full detail in src/MODULE_README.md]

---
Filepath: database/orm/extended/managers/ai_model_base.py  [python]

  class ai_modelView(ModelView):
  class ai_modelDTO(BaseDTO):
      async def _initialize_dto(self, model)
      async def _process_core_data(self, model)
      async def _process_metadata(self, model)
      async def _initial_validation(self, model)
      async def _final_validation(self)
      async def get_validated_dict(self)
  class ai_modelBase(BaseManager[ai_model]):
      def __init__(self, dto_class: type[Any] | None = None, view_class: type[Any] | None = None)
      def _initialize_manager(self)
      async def _initialize_runtime_data(self, item: ai_model) -> None
      async def create_ai_models(self, **data)
      async def delete_ai_models(self, id)
      async def get_ai_models_with_all_related(self, id)
      async def load_ai_models_by_id(self, id)
      async def load_ai_models(self, use_cache = True, **kwargs)
      async def update_ai_models(self, id, **updates)
      async def load_ai_model(self, **kwargs)
      async def filter_ai_model(self, **kwargs)
      async def get_or_create(self, defaults = None, **kwargs)
      async def get_active_ai_model_with_name(self)
      async def get_active_ai_models_with_name(self)
      async def get_active_ai_models_with_through_name(self, id, second_relationship)
      async def get_active_ai_model_with_common_name(self)
      async def get_active_ai_models_with_common_name(self)
      async def get_active_ai_models_with_through_common_name(self, id, second_relationship)
      async def get_active_ai_model_with_provider(self)
      async def get_active_ai_models_with_provider(self)
      async def get_active_ai_models_with_through_provider(self, id, second_relationship)
      async def get_active_ai_model_with_model_class(self)
      async def get_active_ai_models_with_model_class(self)
      async def get_active_ai_models_with_through_model_class(self, id, second_relationship)
      async def get_active_ai_model_with_model_provider(self)
      async def get_active_ai_models_with_model_provider(self)
      async def get_active_ai_models_with_through_model_provider(self, id, second_relationship)
      async def add_active_ai_models_by_id_or_not(self, id = None)
      async def add_active_ai_models_by_ids_or_not(self, ids = None)
      async def add_active_ai_models_by_item_or_not(self, ai_models = None)
      async def add_active_ai_models_by_items_or_not(self, ai_model = None)
      async def create_ai_models_get_dict(self, **data)
      async def filter_ai_model_get_dict(self, **kwargs)
      async def get_active_ai_models_dict(self, id)
      async def get_active_ai_model_dict(self)
      async def get_active_ai_model_with_all_related_dict(self)
      async def get_active_ai_model_with_ifks_dict(self)
      async def get_ai_models_dict(self, id)
      async def get_ai_model_dict(self, **kwargs)
      async def get_ai_model_with_all_related_dict(self)
      async def load_ai_models_get_dict(self, use_cache = True, **kwargs)
      async def load_ai_model_by_ids_get_dict(self, ids)
      async def update_ai_models_get_dict(self, id, **updates)
      async def load_ai_model_by_ids(self, ids)
      def add_computed_field(self, field)
      def add_relation_field(self, field)
      def active_ai_models_ids(self)
  class ai_modelManager(ai_modelBase):
      def __new__(cls, *args, **kwargs)
      def __init__(self)
      async def _initialize_runtime_data(self, item: ai_model) -> None
```
<!-- /AUTO:signatures -->

<!-- AUTO:call_graph -->
## Call Graph

> Auto-generated. All Python files
> Covered submodules shown as stubs — see child READMEs for full detail: `src`, `tests`
> Excluded from call graph: `tests`.
> Shows which functions call which. `async` prefix = caller is an async function.
> Method calls shown as `receiver.method()`. Private methods (`_`) excluded by default.

### Call graph: extended_jan5_backup

```
Global Scope → extended_jan5_backup.TypeVar('ModelT') (line 13)
  async extended_jan5_backup.from_model → extended_jan5_backup.cls() (line 27)
  extended_jan5_backup._report_error → extended_jan5_backup.AppError() (line 49)
  async extended_jan5_backup.fetch_fk → ...fetch_fk(field_name) (line 67)
  async extended_jan5_backup.fetch_fk → ...set_relationship(field_name, result) (line 68)
  async extended_jan5_backup.fetch_ifk → ...fetch_ifk(field_name) (line 75)
  async extended_jan5_backup.fetch_ifk → ...set_relationship(field_name, result) (line 76)
  async extended_jan5_backup.fetch_one_relation → ...fetch_one_relation(field_name) (line 83)
  async extended_jan5_backup.fetch_one_relation → ...set_relationship(field_name, result) (line 84)
  async extended_jan5_backup.filter_fk → ...filter_fk(field_name) (line 91)
  async extended_jan5_backup.filter_fk → ...set_relationship(field_name, result) (line 92)
  async extended_jan5_backup.filter_ifk → ...filter_ifk(field_name) (line 99)
  async extended_jan5_backup.filter_ifk → ...set_relationship(field_name, result) (line 100)
  extended_jan5_backup._serialize_value → extended_jan5_backup.id(value) (line 107)
  extended_jan5_backup._serialize_value → visited.add(id(value)) (line 109)
  extended_jan5_backup._serialize_value → extended_jan5_backup.id(value) (line 109)
  extended_jan5_backup._serialize_value → visited.copy() (line 121)
  extended_jan5_backup._serialize_value → visited.copy() (line 125)
  extended_jan5_backup._serialize_value → value.items() (line 125)
  extended_jan5_backup._serialize_value → value.to_dict() (line 129)
  extended_jan5_backup._serialize_value → visited.copy() (line 129)
  extended_jan5_backup._serialize_value → extended_jan5_backup.callable(value.to_dict) (line 131)
  extended_jan5_backup._serialize_value → value.to_dict() (line 132)
  extended_jan5_backup.to_dict → extended_jan5_backup.id(self) (line 140)
  extended_jan5_backup.to_dict → visited.add(id(self)) (line 142)
  extended_jan5_backup.to_dict → extended_jan5_backup.id(self) (line 142)
  extended_jan5_backup.to_dict → visited.copy() (line 149)
  extended_jan5_backup.print_keys → ...keys() (line 155)
  extended_jan5_backup.__repr__ → self.to_dict() (line 163)
  extended_jan5_backup._initialize_manager → asyncio.get_running_loop() (line 192)
  extended_jan5_backup._initialize_manager → asyncio.create_task(self._auto_fetch_on_init_async()) (line 194)
  extended_jan5_backup._report_error → extended_jan5_backup.AppError() (line 210)
  async extended_jan5_backup._initialize_item_runtime → extended_jan5_backup.RuntimeContainer() (line 225)
  async extended_jan5_backup._initialize_item_runtime → ...from_model(item) (line 227)
  extended_jan5_backup.add_computed_field → ...add(field) (line 262)
  extended_jan5_backup.add_relation_field → ...add(field) (line 265)
  async extended_jan5_backup._get_item_or_raise → ...get() (line 277)
  async extended_jan5_backup._get_item_or_raise → extended_jan5_backup.AppError() (line 279)
  async extended_jan5_backup._get_item_or_none → ...get_or_none() (line 289)
  async extended_jan5_backup._get_item_with_retry → ...get_or_none() (line 297)
  async extended_jan5_backup._get_items → order_by(order_by) (line 311)
  async extended_jan5_backup._get_items → ...filter() (line 311)
  async extended_jan5_backup._get_items → ...filter() (line 313)
  async extended_jan5_backup._get_first_item → first() (line 320)
  async extended_jan5_backup._get_first_item → order_by(order_by) (line 320)
  async extended_jan5_backup._get_first_item → ...filter() (line 320)
  async extended_jan5_backup._get_first_item → first() (line 322)
  async extended_jan5_backup._get_first_item → ...filter() (line 322)
  async extended_jan5_backup._get_last_item → last() (line 328)
  async extended_jan5_backup._get_last_item → order_by(order_by) (line 328)
  async extended_jan5_backup._get_last_item → ...filter() (line 328)
  async extended_jan5_backup._create_item → ...create() (line 334)
  async extended_jan5_backup._create_items → ...bulk_create(items_data) (line 351)
  async extended_jan5_backup._create_items → initialized_items.append(item) (line 358)
  async extended_jan5_backup._update_item → extended_jan5_backup.AppError() (line 374)
  async extended_jan5_backup._update_item → item.update() (line 379)
  async extended_jan5_backup._delete_item → extended_jan5_backup.AppError() (line 386)
  async extended_jan5_backup._delete_item → item.delete() (line 391)
  extended_jan5_backup._add_to_active → ...add(item_id) (line 400)
  extended_jan5_backup._remove_from_active → ...discard(item_id) (line 405)
  async extended_jan5_backup._fetch_related → extended_jan5_backup.AppError() (line 411)
  async extended_jan5_backup._fetch_related → item.fetch_one_relation(relation_name) (line 416)
  async extended_jan5_backup._fetch_all_related → extended_jan5_backup.AppError() (line 430)
  async extended_jan5_backup._fetch_all_related → item.fetch_all_related() (line 435)
  async extended_jan5_backup.load_items → ...update([item.id for item in items if item]) (line 456)
  async extended_jan5_backup.load_by_id → self.load_item() (line 461)
  async extended_jan5_backup.load_by_id_with_retry → self.load_item_with_retry() (line 465)
  async extended_jan5_backup.load_items_by_ids → self.load_items() (line 471)
  async extended_jan5_backup.add_active_by_id → self.load_by_id(item_id) (line 476)
  async extended_jan5_backup.add_active_by_ids → self.load_items_by_ids(item_ids) (line 483)
  async extended_jan5_backup.remove_all_active → ...clear() (line 496)
  async extended_jan5_backup.get_active_items → asyncio.gather(*(self._get_item_or_raise(id=item_id) for item_id in self._active_items)) (line 501)
  async extended_jan5_backup.update_items → ...bulk_update(objects, fields) (line 551)
  async extended_jan5_backup.update_items → initialized_items.append(initialized_item) (line 557)
  async extended_jan5_backup.delete_items → ...bulk_delete(objects) (line 616)
  extended_jan5_backup._item_to_dict → ...to_dict() (line 669)
  extended_jan5_backup._item_to_dict → item.to_dict() (line 670)
  extended_jan5_backup._print_item_keys → ...keys() (line 679)
  extended_jan5_backup._print_item_keys → item.to_dict() (line 686)
  extended_jan5_backup._print_item_keys → item_dict.keys() (line 687)
  extended_jan5_backup._print_item_keys → ...print_keys() (line 696)
  async extended_jan5_backup.get_item_dict → self.load_by_id(item_id) (line 702)
  async extended_jan5_backup.get_items_dict → self.load_items() (line 707)
  async extended_jan5_backup.get_active_items_dict → self.get_active_items() (line 712)
  async extended_jan5_backup.create_item_get_dict → self.create_item() (line 717)
  async extended_jan5_backup.update_item_get_dict → self.update_item(item_id) (line 722)
  async extended_jan5_backup.get_item_with_related → self.load_by_id(item_id) (line 727)
  async extended_jan5_backup.get_item_with_related_with_retry → self.load_by_id_with_retry(item_id) (line 749)
  async extended_jan5_backup.get_items_with_related → self.load_items() (line 771)
  async extended_jan5_backup.get_items_with_related → asyncio.gather(*(self._fetch_related(item, relation_name) for item in items if item)) (line 772)
  async extended_jan5_backup.get_item_with_all_related → self.load_by_id(item_id) (line 779)
  async extended_jan5_backup.get_items_with_all_related → self.get_active_items() (line 787)
  async extended_jan5_backup.get_items_with_all_related → asyncio.gather(*(self._fetch_all_related(item) for item in items if item)) (line 788)
  async extended_jan5_backup.get_items_with_related_list → self.get_active_items() (line 794)
  async extended_jan5_backup.get_items_with_related_list → asyncio.gather(*(self._fetch_related(item, name) for name in relation_names)) (line 797)
  async extended_jan5_backup.get_item_through_fk → self.load_by_id(item_id) (line 804)
  async extended_jan5_backup.get_items_with_related_dict → self.get_items_with_related(relation_name) (line 815)
  async extended_jan5_backup.get_items_with_all_related_dict → self.get_items_with_all_related() (line 820)
  async extended_jan5_backup.add_active_by_ids_or_not → items.append(await self._process_item(item)) (line 852)
  async extended_jan5_backup.add_active_by_items_or_not → processed_items.append(await self._process_item(item)) (line 862)
  async extended_jan5_backup.get_active_item_dict → self.get_active_item(item_id) (line 874)
  async extended_jan5_backup.get_active_item_dict → item.to_dict() (line 875)
  async extended_jan5_backup.load_item_get_dict → self.load_item() (line 879)
  async extended_jan5_backup.load_item_get_dict → item.to_dict() (line 880)
  async extended_jan5_backup.load_items_by_ids_get_dict → self.load_items_by_ids(item_ids) (line 885)
  async extended_jan5_backup.load_items_by_ids_get_dict → item.to_dict() (line 886)
  async extended_jan5_backup.filter_items → ...filter() (line 891)
  async extended_jan5_backup.filter_items_by_ids → ...filter() (line 896)
  async extended_jan5_backup.filter_items_get_dict → self.filter_items() (line 901)
  async extended_jan5_backup.filter_items_get_dict → item.to_dict() (line 902)
  async extended_jan5_backup.get_active_items_with_fks → self.get_active_items() (line 914)
  async extended_jan5_backup.get_active_item_with_ifk → self.add_active_item() (line 923)
  async extended_jan5_backup.get_active_item_with_ifk → item.fetch_ifk(related_model) (line 925)
  async extended_jan5_backup.get_active_items_with_ifks → self.get_active_items() (line 931)
  async extended_jan5_backup.get_active_items_with_ifks → item.fetch_ifks() (line 934)
  async extended_jan5_backup.get_active_items_with_ifks_dict → item.to_dict() (line 940)
  async extended_jan5_backup.get_active_items_with_ifks_dict → self.get_active_items_with_ifks() (line 940)
  async extended_jan5_backup.get_active_item_with_all_related → self.add_active_item() (line 945)
  async extended_jan5_backup.get_active_item_with_all_related → item.fetch_all_related() (line 947)
  async extended_jan5_backup.get_active_items_with_all_related → self.get_active_items() (line 952)
  async extended_jan5_backup.get_active_items_with_all_related → item.fetch_all_related() (line 955)
  async extended_jan5_backup.get_active_items_with_all_related_dict → item.to_dict() (line 961)
  async extended_jan5_backup.get_active_items_with_all_related_dict → self.get_active_items_with_all_related() (line 962)
  async extended_jan5_backup.get_active_item_with_one_relation → self.get_active_items() (line 969)
  async extended_jan5_backup.get_active_item_with_one_relation → item.fetch_one_relation(relation_name) (line 972)
  async extended_jan5_backup.get_active_items_with_one_relation → self.get_active_items() (line 978)
  async extended_jan5_backup.get_active_items_with_one_relation → item.fetch_one_relation(relation_name) (line 981)
  async extended_jan5_backup.get_active_item_with_one_relation_dict → item.to_dict() (line 987)
  async extended_jan5_backup.get_active_item_with_one_relation_dict → self.get_active_item_with_one_relation(relation_name) (line 988)
  async extended_jan5_backup.get_active_item_with_related_models_list → self.get_active_items() (line 995)
  async extended_jan5_backup.get_active_item_with_related_models_list → item.fetch_one_relation(related_model) (line 998)
  async extended_jan5_backup.get_active_items_with_related_models_list → self.get_active_items() (line 1004)
  async extended_jan5_backup.get_active_items_with_related_models_list → item.fetch_one_relation(related_model) (line 1007)
  async extended_jan5_backup.get_active_item_with_related_models_list_dict → item.to_dict() (line 1013)
  async extended_jan5_backup.get_active_item_with_related_models_list_dict → self.get_active_item_with_related_models_list(related_models_list) (line 1014)
  async extended_jan5_backup.get_active_item_with_through_fk → self.get_active_item_with_fk(item_id, first_relationship) (line 1024)
  async extended_jan5_backup.get_active_item_with_through_fk → fk_instance.fetch_fk(second_relationship) (line 1028)
  async extended_jan5_backup.get_active_item_through_ifk → self.get_active_item_with_ifk(item_id, first_relationship) (line 1040)
  async extended_jan5_backup.get_active_item_through_ifk → ifk_instance.fetch_ifk(second_relationship) (line 1044)
  extended_jan5_backup.active_item_ids → ...copy() (line 1054)
  extended_jan5_backup.get_all_attributes → attributes.update({k: v for k, v in self.__dict__.items() if not callable(v)}) (line 1060)
  extended_jan5_backup.get_all_attributes → ...items() (line 1061)
  extended_jan5_backup.get_all_attributes → extended_jan5_backup.callable(v) (line 1061)
  extended_jan5_backup.get_all_attributes → attr.startswith('__') (line 1064)
  extended_jan5_backup.get_all_attributes → extended_jan5_backup.callable(value) (line 1066)
  extended_jan5_backup.get_item_attributes → copy() (line 1074)
  extended_jan5_backup.get_item_attributes → attr.startswith('__') (line 1079)
  extended_jan5_backup._auto_fetch_on_init_sync → asyncio.run(self._auto_fetch_on_init_async()) (line 1096)
  async extended_jan5_backup._auto_fetch_on_init_async → time.perf_counter() (line 1104)
  async extended_jan5_backup._auto_fetch_on_init_async → limit(self.fetch_on_init_limit) (line 1107)
  async extended_jan5_backup._auto_fetch_on_init_async → ...filter() (line 1107)
  async extended_jan5_backup._auto_fetch_on_init_async → time.perf_counter() (line 1114)
  async extended_jan5_backup._auto_fetch_on_init_async → ...startswith(suppression_prefix) (line 1138)
  async extended_jan5_backup._auto_fetch_on_init_async → ...update(initialized_items) (line 1164)
  extended_jan5_backup._trigger_fetch_warnings → center(80, '=') (line 1190)
  extended_jan5_backup._trigger_fetch_warnings → center(80) (line 1191)
  extended_jan5_backup._trigger_fetch_warnings → center(80) (line 1194)
  extended_jan5_backup._trigger_fetch_warnings → center(80) (line 1195)
  extended_jan5_backup._trigger_fetch_warnings → center(80) (line 1196)
  extended_jan5_backup._trigger_fetch_warnings → center(80) (line 1200)
  extended_jan5_backup._trigger_fetch_warnings → join(warning_lines) (line 1202)
  extended_jan5_backup._trigger_fetch_warnings → center(80) (line 1208)
  extended_jan5_backup._trigger_fetch_warnings → center(80) (line 1209)
  extended_jan5_backup._trigger_fetch_warnings → center(80) (line 1212)
  extended_jan5_backup._trigger_fetch_warnings → center(80) (line 1213)
  extended_jan5_backup._trigger_fetch_warnings → center(80) (line 1216)
  extended_jan5_backup._trigger_fetch_warnings → center(80) (line 1217)
  extended_jan5_backup._trigger_fetch_warnings → center(80) (line 1221)
  extended_jan5_backup._trigger_fetch_warnings → join(scary_warning) (line 1223)
  extended_jan5_backup._trigger_limit_reached_warning → center(80) (line 1230)
  extended_jan5_backup._trigger_limit_reached_warning → center(80) (line 1233)
  extended_jan5_backup._trigger_limit_reached_warning → center(80) (line 1236)
  extended_jan5_backup._trigger_limit_reached_warning → center(80) (line 1237)
  extended_jan5_backup._trigger_limit_reached_warning → center(80) (line 1238)
  extended_jan5_backup._trigger_limit_reached_warning → center(80) (line 1242)
  extended_jan5_backup._trigger_limit_reached_warning → join(warning_lines) (line 1244)
  extended_jan5_backup.load_item_sync → asyncio.get_running_loop() (line 1263)
  extended_jan5_backup.load_item_sync → asyncio.run(self.load_item(use_cache=use_cache, **kwargs)) (line 1268)
  extended_jan5_backup.load_item_sync → self.load_item() (line 1268)
  extended_jan5_backup.load_item_or_none_sync → asyncio.get_running_loop() (line 1273)
  extended_jan5_backup.load_item_or_none_sync → asyncio.run(self.load_item_or_none(use_cache=use_cache, **kwargs)) (line 1278)
  extended_jan5_backup.load_item_or_none_sync → self.load_item_or_none() (line 1278)
  extended_jan5_backup.load_items_sync → asyncio.get_running_loop() (line 1283)
  extended_jan5_backup.load_items_sync → asyncio.run(self.load_items(**kwargs)) (line 1288)
  extended_jan5_backup.load_items_sync → self.load_items() (line 1288)
  extended_jan5_backup.load_by_id_sync → asyncio.get_running_loop() (line 1293)
  extended_jan5_backup.load_by_id_sync → asyncio.run(self.load_by_id(item_id)) (line 1298)
  extended_jan5_backup.load_by_id_sync → self.load_by_id(item_id) (line 1298)
  extended_jan5_backup.filter_items_sync → asyncio.get_running_loop() (line 1303)
  extended_jan5_backup.filter_items_sync → asyncio.run(self.filter_items(**kwargs)) (line 1308)
  extended_jan5_backup.filter_items_sync → self.filter_items() (line 1308)
  extended_jan5_backup.create_item_sync → asyncio.get_running_loop() (line 1313)
  extended_jan5_backup.create_item_sync → asyncio.run(self.create_item(**data)) (line 1318)
  extended_jan5_backup.create_item_sync → self.create_item() (line 1318)
  extended_jan5_backup.update_item_sync → asyncio.get_running_loop() (line 1323)
  extended_jan5_backup.update_item_sync → asyncio.run(self.update_item(item_id, **updates)) (line 1328)
  extended_jan5_backup.update_item_sync → self.update_item(item_id) (line 1328)
  extended_jan5_backup.delete_item_sync → asyncio.get_running_loop() (line 1333)
  extended_jan5_backup.delete_item_sync → asyncio.run(self.delete_item(item_id)) (line 1338)
  extended_jan5_backup.delete_item_sync → self.delete_item(item_id) (line 1338)
  extended_jan5_backup.get_or_create_sync → asyncio.get_running_loop() (line 1343)
  extended_jan5_backup.get_or_create_sync → asyncio.run(self.get_or_create(defaults=defaults, **kwargs)) (line 1348)
  extended_jan5_backup.get_or_create_sync → self.get_or_create() (line 1348)
  extended_jan5_backup.exists_sync → asyncio.get_running_loop() (line 1353)
  extended_jan5_backup.exists_sync → asyncio.run(self.exists(item_id)) (line 1358)
  extended_jan5_backup.exists_sync → self.exists(item_id) (line 1358)
  extended_jan5_backup.get_active_items_sync → asyncio.get_running_loop() (line 1363)
  extended_jan5_backup.get_active_items_sync → asyncio.run(self.get_active_items()) (line 1368)
  extended_jan5_backup.get_active_items_sync → self.get_active_items() (line 1368)
  extended_jan5_backup.get_item_dict_sync → asyncio.get_running_loop() (line 1373)
  extended_jan5_backup.get_item_dict_sync → asyncio.run(self.get_item_dict(item_id)) (line 1378)
  extended_jan5_backup.get_item_dict_sync → self.get_item_dict(item_id) (line 1378)
  extended_jan5_backup.get_items_dict_sync → asyncio.get_running_loop() (line 1383)
  extended_jan5_backup.get_items_dict_sync → asyncio.run(self.get_items_dict(**kwargs)) (line 1388)
  extended_jan5_backup.get_items_dict_sync → self.get_items_dict() (line 1388)
```

### Call graph: src.matrx_orm.state

> Full detail in [`src/MODULE_README.md`](src/MODULE_README.md)

```
`src.matrx_orm.state.__init__ → src.matrx_orm.state.ConfigurationError() (line 36)` → ... → `state.count() (line 470)`
```

### Call graph: src.matrx_orm.exceptions

> Full detail in [`src/MODULE_README.md`](src/MODULE_README.md)

```
`src.matrx_orm.exceptions._capture_caller_frames → _tb.extract_stack() (line 24)` → ... → `join(lines) (line 932)`
```

### Call graph: src.matrx_orm.error_handling

> Full detail in [`src/MODULE_README.md`](src/MODULE_README.md)

```
`async src.matrx_orm.error_handling.handle_orm_operation → src.matrx_orm.error_handling.CacheError() (line 27)`
```

### Call graph: src.matrx_orm.extended.app_error_handler

> Full detail in [`src/MODULE_README.md`](src/MODULE_README.md)

```
`Global Scope → src.matrx_orm.extended.app_error_handler.TypeVar('_F') (line 9)` → ... → `src.matrx_orm.extended.app_error_handler.wraps(func) (line 104)`
```

### Call graph: src.matrx_orm.utils.sql_utils

> Full detail in [`src/MODULE_README.md`](src/MODULE_README.md)

```
`src.matrx_orm.utils.sql_utils.clean_default_value → re.sub('::[\\w\\s]+', '', default_value) (line 16)` → ... → `re.sub(':(\\w+)', replace_named_param, sql) (line 56)`
```

### Call graph: src.matrx_orm.utils.type_converters

> Full detail in [`src/MODULE_README.md`](src/MODULE_README.md)

```
`src.matrx_orm.utils.type_converters.to_python → datetime.fromisoformat(value) (line 23)` → ... → `TypeConverter.get_db_prep_value(value, model._fields[field_name].field_type) (line 100)`
```

### Call graph: src.matrx_orm.adapters.postgresql

> Full detail in [`src/MODULE_README.md`](src/MODULE_README.md)

```
`src.matrx_orm.adapters.postgresql.__init__ → src.matrx_orm.adapters.postgresql.get_database_config() (line 10)` → ... → `join(filters) (line 170)`
```

### Call graph: src.matrx_orm.adapters.base_adapter

> Full detail in [`src/MODULE_README.md`](src/MODULE_README.md)

```
`async src.matrx_orm.adapters.base_adapter.__aexit__ → self.close() (line 69)`
```

### Call graph: src.matrx_orm.python_sql.table_typescript_relationship

> Full detail in [`src/MODULE_README.md`](src/MODULE_README.md)

```
`src.matrx_orm.python_sql.table_typescript_relationship.transform_relationships_for_typescript → items() (line 34)` → ... → `src.matrx_orm.python_sql.table_typescript_relationship.analyze_relationships(relationships) (line 150)`
```

### Call graph: src.matrx_orm.python_sql.table_detailed_relationships

> Full detail in [`src/MODULE_README.md`](src/MODULE_README.md)

```
`src.matrx_orm.python_sql.table_detailed_relationships.get_table_relationships → src.matrx_orm.python_sql.table_detailed_relationships.execute_sql_query(query, (schema, schema), database_project) (line 118)` → ... → `src.matrx_orm.python_sql.table_detailed_relationships.analyze_many_to_many_relationships(all_relationships_list) (line 489)`
```

### Call graph: src.matrx_orm.python_sql.db_objects

> Full detail in [`src/MODULE_README.md`](src/MODULE_README.md)

```
`src.matrx_orm.python_sql.db_objects.get_full_db_objects → src.matrx_orm.python_sql.db_objects.execute_sql_query(query, (schema,), database_project) (line 172)` → ... → `src.matrx_orm.python_sql.db_objects.get_db_objects() (line 389)`
```

### Call graph: src.matrx_orm.query.executor

> Full detail in [`src/MODULE_README.md`](src/MODULE_README.md)

```
`Global Scope → src.matrx_orm.query.executor.object() (line 21)` → ... → `self.model() (line 877)`
```

### Call graph: src.matrx_orm.query.builder

> Full detail in [`src/MODULE_README.md`](src/MODULE_README.md)

```
`Global Scope → src.matrx_orm.query.builder.TypeVar('ModelT') (line 22)` → ... → `self.offset(start) (line 512)`
```

### Call graph: src.matrx_orm.client.postgres_connection

> Full detail in [`src/MODULE_README.md`](src/MODULE_README.md)

```
`src.matrx_orm.client.postgres_connection.init_connection_details → src.matrx_orm.client.postgres_connection.get_database_config() (line 20)` → ... → `putconn(conn) (line 170)`
```

### Call graph: src.matrx_orm.middleware.base

> Full detail in [`src/MODULE_README.md`](src/MODULE_README.md)

```
`src.matrx_orm.middleware.base.add_middleware → ...append(middleware) (line 22)` → ... → `middleware_manager.process_query(query) (line 248)`
```

### Call graph: src.matrx_orm.sql_executor.utils

> Full detail in [`src/MODULE_README.md`](src/MODULE_README.md)

```
`src.matrx_orm.sql_executor.utils.list_available_queries → src.matrx_orm.sql_executor.utils.get_registry() (line 5)` → ... → `join(docs) (line 61)`
```

### Call graph: src.matrx_orm.sql_executor.executor

> Full detail in [`src/MODULE_README.md`](src/MODULE_README.md)

```
`src.matrx_orm.sql_executor.executor.validate_params → src.matrx_orm.sql_executor.executor.get_registry() (line 17)` → ... → `src.matrx_orm.sql_executor.executor.db_execute_batch_query(query_data['query'], validated_params, batch_size, query_data['database']) (line 159)`
```

### Call graph: src.matrx_orm.sql_executor.registry

> Full detail in [`src/MODULE_README.md`](src/MODULE_README.md)

```
`src.matrx_orm.sql_executor.registry.get → ...get(name) (line 18)` → ... → `_global_registry.register(name, query) (line 52)`
```

### Call graph: src.matrx_orm.schema_builder.code_handler

> Full detail in [`src/MODULE_README.md`](src/MODULE_README.md)

```
`src.matrx_orm.schema_builder.code_handler._is_allowed → lower() (line 27)` → ... → `write_to_json(path, data) (line 50)`
```

### Call graph: src.matrx_orm.schema_builder.columns

> Full detail in [`src/MODULE_README.md`](src/MODULE_README.md)

```
`src.matrx_orm.schema_builder.columns.__init__ → self.initit_level_1() (line 79)` → ... → `...replace('vector(', '') (line 1324)`
```

### Call graph: src.matrx_orm.schema_builder.schema

> Full detail in [`src/MODULE_README.md`](src/MODULE_README.md)

```
`src.matrx_orm.schema_builder.schema.format_ts_object → re.sub('"(\\w+)"\\s*:', '\\1:', ts_object_str) (line 20)` → ... → `...items() (line 893)`
```

### Call graph: src.matrx_orm.schema_builder.common

> Full detail in [`src/MODULE_README.md`](src/MODULE_README.md)

```
`Global Scope → dotenv.load_dotenv() (line 7)` → ... → `os.getenv('MATRX_VERBOSE', '') (line 50)`
```

### Call graph: src.matrx_orm.schema_builder.runner

> Full detail in [`src/MODULE_README.md`](src/MODULE_README.md)

```
`src.matrx_orm.schema_builder.runner._close_pools → connection_pools.items() (line 29)` → ... → `src.matrx_orm.schema_builder.runner._close_pools() (line 252)`
```

### Call graph: src.matrx_orm.schema_builder.views

> Full detail in [`src/MODULE_README.md`](src/MODULE_README.md)

```
`src.matrx_orm.schema_builder.views.__init__ → ...to_snake_case(self.name) (line 36)` → ... → `self.generate_unique_name_lookups() (line 50)`
```

### Call graph: src.matrx_orm.schema_builder.relationships

> Full detail in [`src/MODULE_README.md`](src/MODULE_README.md)

```
`src.matrx_orm.schema_builder.relationships.__init__ → ...to_camel_case(self.column) (line 21)` → ... → `...to_camel_case(source_table.name) (line 29)`
```

### Call graph: src.matrx_orm.schema_builder.tables

> Full detail in [`src/MODULE_README.md`](src/MODULE_README.md)

```
`src.matrx_orm.schema_builder.tables.__init__ → ...to_snake_case(self.name) (line 91)` → ... → `...items() (line 1224)`
```

### Call graph: src.matrx_orm.schema_builder.generator

> Full detail in [`src/MODULE_README.md`](src/MODULE_README.md)

```
`src.matrx_orm.schema_builder.generator.get_schema_structure → schema_manager.get_table(table_name) (line 9)` → ... → `join(lines) (line 159)`
```

### Call graph: src.matrx_orm.schema_builder.schema_manager

> Full detail in [`src/MODULE_README.md`](src/MODULE_README.md)

```
`src.matrx_orm.schema_builder.schema_manager.__init__ → src.matrx_orm.schema_builder.schema_manager.get_database_config(database_project) (line 33)` → ... → `...save_frontend_junction_analysis_json(frontend_junction_analysis) (line 724)`
```

### Call graph: src.matrx_orm.schema_builder.helpers.entity_generators

> Full detail in [`src/MODULE_README.md`](src/MODULE_README.md)

```
`src.matrx_orm.schema_builder.helpers.entity_generators.generate_typescript_entity → overrides.get('schemaType', 'null') (line 19)` → ... → `src.matrx_orm.schema_builder.helpers.entity_generators.generate_all_entity_main_hooks(entity_names) (line 303)`
```

### Call graph: src.matrx_orm.schema_builder.helpers.git_checker

> Full detail in [`src/MODULE_README.md`](src/MODULE_README.md)

```
`src.matrx_orm.schema_builder.helpers.git_checker.check_git_status → os.getenv('ADMIN_PYTHON_ROOT', '') (line 17)` → ... → `sys.exit(1) (line 114)`
```

### Call graph: src.matrx_orm.schema_builder.helpers.base_generators

> Full detail in [`src/MODULE_README.md`](src/MODULE_README.md)

```
`src.matrx_orm.schema_builder.helpers.base_generators.generate_legacy_dto_manager_class → warnings.warn('generate_legacy_dto_manager_class() is deprecated. Use generate_base_manager_class() which scaffolds a ModelView.', DeprecationWarning) (line 189)` → ... → `src.matrx_orm.schema_builder.helpers.base_generators.plt(file_path, 'Manager class saved') (line 648)`
```

### Call graph: src.matrx_orm.core.config

> Full detail in [`src/MODULE_README.md`](src/MODULE_README.md)

```
`Global Scope → src.matrx_orm.core.config.field() (line 26)` → ... → `...join(ADMIN_TS_ROOT, 'constants/') (line 496)`
```

### Call graph: src.matrx_orm.core.signals

> Full detail in [`src/MODULE_README.md`](src/MODULE_README.md)

```
`src.matrx_orm.core.signals.connect → ...append(receiver) (line 54)` → ... → `src.matrx_orm.core.signals.Signal('post_delete') (line 99)`
```

### Call graph: src.matrx_orm.core.fields

> Full detail in [`src/MODULE_README.md`](src/MODULE_README.md)

```
`Global Scope → src.matrx_orm.core.fields.TypeVar('_JT') (line 15)` → ... → `validate(value) (line 1255)`
```

### Call graph: src.matrx_orm.core.base

> Full detail in [`src/MODULE_README.md`](src/MODULE_README.md)

```
`src.matrx_orm.core.base._to_snake_case → lower() (line 43)` → ... → `src.matrx_orm.core.base.QueryBuilder(cls) (line 1392)`
```

### Call graph: src.matrx_orm.core.extended

> Full detail in [`src/MODULE_README.md`](src/MODULE_README.md)

```
`Global Scope → src.matrx_orm.core.extended.TypeVar('ModelT') (line 16)` → ... → `self.delete_where() (line 1861)`
```

### Call graph: src.matrx_orm.core.async_db_manager

> Full detail in [`src/MODULE_README.md`](src/MODULE_README.md)

```
`async src.matrx_orm.core.async_db_manager._init_vector_codec → conn.set_type_codec('vector') (line 39)` → ... → `src.matrx_orm.core.async_db_manager.cause_error() (line 352)`
```

### Call graph: src.matrx_orm.core.model_view

> Full detail in [`src/MODULE_README.md`](src/MODULE_README.md)

```
`src.matrx_orm.core.model_view.__new__ → computed.update(base_computed) (line 86)` → ... → `warnings.warn(f"[ModelView:{view_name}] Prefetch of relation '{relation_name}' failed: {type(exc).__name__}: {exc}. Skipped.", RuntimeWarning) (line 221)`
```

### Call graph: src.matrx_orm.core.registry

> Full detail in [`src/MODULE_README.md`](src/MODULE_README.md)

```
`src.matrx_orm.core.registry.register_all → cls.register(model) (line 25)` → ... → `model_registry.get_model(model_name) (line 46)`
```

### Call graph: src.matrx_orm.core.paginator

> Full detail in [`src/MODULE_README.md`](src/MODULE_README.md)

```
`Global Scope → src.matrx_orm.core.paginator.TypeVar('ModelT') (line 34)` → ... → `self.page(self._current_page) (line 190)`
```

### Call graph: src.matrx_orm.core.expressions

> Full detail in [`src/MODULE_README.md`](src/MODULE_README.md)

```
`src.matrx_orm.core.expressions.__add__ → src.matrx_orm.core.expressions.Expression(self.field_name, '+', other) (line 19)` → ... → `params.append(literal) (line 760)`
```

### Call graph: src.matrx_orm.core.types

> Full detail in [`src/MODULE_README.md`](src/MODULE_README.md)

```
`Global Scope → src.matrx_orm.core.types.TypeVar('ModelT') (line 31)` → ... → `src.matrx_orm.core.types.dataclass() (line 192)`
```

### Call graph: src.matrx_orm.core.transaction

> Full detail in [`src/MODULE_README.md`](src/MODULE_README.md)

```
`Global Scope → src.matrx_orm.core.transaction.ContextVar('_active_connection') (line 35)` → ... → `...get('MATRX_DEFAULT_DATABASE', 'default') (line 159)`
```

### Call graph: src.matrx_orm.core.relations

> Full detail in [`src/MODULE_README.md`](src/MODULE_README.md)

```
`src.matrx_orm.core.relations._related_model → src.matrx_orm.core.relations.get_model_by_name(self.to_model) (line 29)` → ... → `target.lower() (line 478)`
```

### Call graph: src.matrx_orm.operations.delete

> Full detail in [`src/MODULE_README.md`](src/MODULE_README.md)

```
`async src.matrx_orm.operations.delete.delete → delete() (line 17)` → ... → `post_delete.send(model_cls) (line 70)`
```

### Call graph: src.matrx_orm.operations.read

> Full detail in [`src/MODULE_README.md`](src/MODULE_README.md)

```
`async src.matrx_orm.operations.read.get → get() (line 5)` → ... → `src.matrx_orm.operations.read.QueryBuilder(model_cls) (line 51)`
```

### Call graph: src.matrx_orm.operations.create

> Full detail in [`src/MODULE_README.md`](src/MODULE_README.md)

```
`async src.matrx_orm.operations.create.create → src.matrx_orm.operations.create.model_cls() (line 16)` → ... → `src.matrx_orm.operations.create.create(model_cls) (line 188)`
```

### Call graph: src.matrx_orm.operations.update

> Full detail in [`src/MODULE_README.md`](src/MODULE_README.md)

```
`async src.matrx_orm.operations.update.update → update() (line 20)` → ... → `post_save.send(model_cls) (line 197)`
```

### Call graph: database.orm.extended.managers.ai_model_base

```
async database.orm.extended.managers.ai_model_base.get_validated_dict → self.to_dict() (line 86)
  async database.orm.extended.managers.ai_model_base.create_ai_models → self.create_item() (line 115)
  async database.orm.extended.managers.ai_model_base.delete_ai_models → self.delete_item(id) (line 118)
  async database.orm.extended.managers.ai_model_base.get_ai_models_with_all_related → self.get_item_with_all_related(id) (line 121)
  async database.orm.extended.managers.ai_model_base.load_ai_models_by_id → self.load_by_id(id) (line 124)
  async database.orm.extended.managers.ai_model_base.load_ai_models → self.load_item(use_cache) (line 127)
  async database.orm.extended.managers.ai_model_base.update_ai_models → self.update_item(id) (line 130)
  async database.orm.extended.managers.ai_model_base.load_ai_model → self.load_items() (line 133)
  async database.orm.extended.managers.ai_model_base.filter_ai_model → self.filter_items() (line 136)
  async database.orm.extended.managers.ai_model_base.get_or_create → self.get_or_create(defaults) (line 139)
  async database.orm.extended.managers.ai_model_base.get_active_ai_model_with_name → self.get_active_items_with_one_relation('name') (line 142)
  async database.orm.extended.managers.ai_model_base.get_active_ai_models_with_name → self.get_active_item_with_one_relation('name') (line 145)
  async database.orm.extended.managers.ai_model_base.get_active_ai_models_with_through_name → self.get_active_item_with_through_fk(id, 'name', second_relationship) (line 148)
  async database.orm.extended.managers.ai_model_base.get_active_ai_model_with_common_name → self.get_active_items_with_one_relation('common_name') (line 151)
  async database.orm.extended.managers.ai_model_base.get_active_ai_models_with_common_name → self.get_active_item_with_one_relation('common_name') (line 154)
  async database.orm.extended.managers.ai_model_base.get_active_ai_models_with_through_common_name → self.get_active_item_with_through_fk(id, 'common_name', second_relationship) (line 157)
  async database.orm.extended.managers.ai_model_base.get_active_ai_model_with_provider → self.get_active_items_with_one_relation('provider') (line 160)
  async database.orm.extended.managers.ai_model_base.get_active_ai_models_with_provider → self.get_active_item_with_one_relation('provider') (line 163)
  async database.orm.extended.managers.ai_model_base.get_active_ai_models_with_through_provider → self.get_active_item_with_through_fk(id, 'provider', second_relationship) (line 166)
  async database.orm.extended.managers.ai_model_base.get_active_ai_model_with_model_class → self.get_active_items_with_one_relation('model_class') (line 169)
  async database.orm.extended.managers.ai_model_base.get_active_ai_models_with_model_class → self.get_active_item_with_one_relation('model_class') (line 172)
  async database.orm.extended.managers.ai_model_base.get_active_ai_models_with_through_model_class → self.get_active_item_with_through_fk(id, 'model_class', second_relationship) (line 175)
  async database.orm.extended.managers.ai_model_base.get_active_ai_model_with_model_provider → self.get_active_items_with_one_relation('model_provider') (line 178)
  async database.orm.extended.managers.ai_model_base.get_active_ai_models_with_model_provider → self.get_active_item_with_one_relation('model_provider') (line 181)
  async database.orm.extended.managers.ai_model_base.get_active_ai_models_with_through_model_provider → self.get_active_item_with_through_fk(id, 'model_provider', second_relationship) (line 184)
  async database.orm.extended.managers.ai_model_base.add_active_ai_models_by_id_or_not → self.add_active_by_id_or_not(id) (line 187)
  async database.orm.extended.managers.ai_model_base.add_active_ai_models_by_ids_or_not → self.add_active_by_ids_or_not(ids) (line 190)
  async database.orm.extended.managers.ai_model_base.add_active_ai_models_by_item_or_not → self.add_active_by_item_or_not(ai_models) (line 193)
  async database.orm.extended.managers.ai_model_base.add_active_ai_models_by_items_or_not → self.add_active_by_items_or_not(ai_model) (line 196)
  async database.orm.extended.managers.ai_model_base.create_ai_models_get_dict → self.create_item_get_dict() (line 199)
  async database.orm.extended.managers.ai_model_base.filter_ai_model_get_dict → self.filter_items_get_dict() (line 202)
  async database.orm.extended.managers.ai_model_base.get_active_ai_models_dict → self.get_active_item_dict(id) (line 205)
  async database.orm.extended.managers.ai_model_base.get_active_ai_model_dict → self.get_active_items_dict() (line 208)
  async database.orm.extended.managers.ai_model_base.get_active_ai_model_with_all_related_dict → self.get_active_items_with_all_related_dict() (line 211)
  async database.orm.extended.managers.ai_model_base.get_active_ai_model_with_ifks_dict → self.get_active_items_with_ifks_dict() (line 214)
  async database.orm.extended.managers.ai_model_base.get_ai_models_dict → self.get_item_dict(id) (line 217)
  async database.orm.extended.managers.ai_model_base.get_ai_model_dict → self.get_items_dict() (line 220)
  async database.orm.extended.managers.ai_model_base.get_ai_model_with_all_related_dict → self.get_items_with_all_related_dict() (line 223)
  async database.orm.extended.managers.ai_model_base.load_ai_models_get_dict → self.load_item_get_dict(use_cache) (line 226)
  async database.orm.extended.managers.ai_model_base.load_ai_model_by_ids_get_dict → self.load_items_by_ids_get_dict(ids) (line 229)
  async database.orm.extended.managers.ai_model_base.update_ai_models_get_dict → self.update_item_get_dict(id) (line 232)
  async database.orm.extended.managers.ai_model_base.load_ai_model_by_ids → self.load_items_by_ids(ids) (line 235)
  database.orm.extended.managers.ai_model_base.add_computed_field → self.add_computed_field(field) (line 238)
  database.orm.extended.managers.ai_model_base.add_relation_field → self.add_relation_field(field) (line 241)
  Global Scope → database.orm.extended.managers.ai_model_base.ai_modelManager() (line 263)
```
<!-- /AUTO:call_graph -->

<!-- AUTO:dependencies -->
## Dependencies

**External packages:** AiModel, CoreFoundation, IPython, OpenSSL, PIL, PyQt6, PySide6, TestMac, _manylinux, _typeshed, annotationlib, async_timeout, asyncpg, backports, basedpyright, brotli, brotlicffi, certifi, chardet, charset_normalizer, click, compression, cryptography, database_registry, defusedxml, dns, dotenv, dummy_threading, git, gitdb, gitdb_speedups, gyp, h2, idna, importlib_metadata, inflect, js, lldb, matrx_orm, matrx_utils, more_itertools, nodejs_wheel, numpy, olefile, packaging, pkg_resources, psycopg, psycopg2, psycopg_binary, psycopg_c, psycopg_pool, pyodide, pytest, requests, sha, shapely, simplejson, smmap, socks, typeguard, typeshed, typing_extensions, urllib3, uvloop, yaml
**Internal modules:** src.matrx_utils, tests.level2
<!-- /AUTO:dependencies -->

<!-- AUTO:config -->
## Generation Config

> Auto-managed. Contains the exact parameters used to generate this README.
> Used by parent modules to auto-refresh this file when it is stale.
> Do not edit manually — changes will be overwritten on the next run.

```json
{
  "subdirectory": "",
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
