# `src` — Module Overview

> This document is partially auto-generated. Sections tagged `<!-- AUTO:id -->` are refreshed by the generator.
> Everything else is yours to edit freely and will never be overwritten.

<!-- AUTO:meta -->
## About This Document

This file is **partially auto-generated**. Sections wrapped in `<!-- AUTO:id -->` tags
are overwritten each time the generator runs. Everything else is yours to edit freely.

| Field | Value |
|-------|-------|
| Module | `src` |
| Last generated | 2026-02-28 13:57 |
| Output file | `src/MODULE_README.md` |
| Signature mode | `signatures` |


**Child READMEs detected** (signatures collapsed — see links for detail):

| README | |
|--------|---|
| [`src/matrx_orm/MODULE_README.md`](src/matrx_orm/MODULE_README.md) | last generated 2026-02-28 13:57 |
**To refresh auto-sections:**
```bash
python utils/code_context/generate_module_readme.py src --mode signatures
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

> Auto-generated. 66 files across 14 directories.

```
src/
├── MODULE_README.md
├── matrx_orm/
│   ├── MODULE_README.md
│   ├── __init__.py
│   ├── adapters/
│   │   ├── __init__.py
│   │   ├── base_adapter.py
│   │   ├── postgresql.py
│   ├── client/
│   │   ├── __init__.py
│   │   ├── postgres_connection.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── async_db_manager.py
│   │   ├── base.py
│   │   ├── config.py
│   │   ├── expressions.py
│   │   ├── extended.py
│   │   ├── fields.py
│   │   ├── model_view.py
│   │   ├── paginator.py
│   │   ├── registry.py
│   │   ├── relations.py
│   │   ├── signals.py
│   │   ├── transaction.py
│   │   ├── types.py
│   ├── error_handling.py
│   ├── exceptions.py
│   ├── extended/
│   │   ├── __init__.py
│   │   ├── app_error_handler.py
│   ├── middleware/
│   │   ├── __init__.py
│   │   ├── base.py
│   ├── operations/
│   │   ├── __init__.py
│   │   ├── create.py
│   │   ├── delete.py
│   │   ├── read.py
│   │   ├── update.py
│   ├── py.typed
│   ├── python_sql/
│   │   ├── __init__.py
│   │   ├── db_objects.py
│   │   ├── table_detailed_relationships.py
│   │   ├── table_typescript_relationship.py
│   ├── query/
│   │   ├── __init__.py
│   │   ├── builder.py
│   │   ├── executor.py
│   ├── schema_builder/
│   │   ├── __init__.py
│   │   ├── code_handler.py
│   │   ├── columns.py
│   │   ├── common.py
│   │   ├── generator.py
│   │   ├── helpers/
│   │   │   ├── __init__.py
│   │   │   ├── base_generators.py
│   │   │   ├── entity_generators.py
│   │   │   ├── git_checker.py
│   │   ├── relationships.py
│   │   ├── runner.py
│   │   ├── schema.py
│   │   ├── schema_manager.py
│   │   ├── tables.py
│   │   ├── views.py
│   ├── sql_executor/
│   │   ├── __init__.py
│   │   ├── executor.py
│   │   ├── queries.py
│   │   ├── registry.py
│   │   ├── types.py
│   │   ├── utils.py
│   ├── state.py
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── sql_utils.py
│   │   ├── type_converters.py
# excluded: 9 .md
```
<!-- /AUTO:tree -->

<!-- AUTO:signatures -->
## API Signatures

> Auto-generated via `output_mode="{mode}"`. ~5-10% token cost vs full source.
> For full source, open the individual files directly.
> Submodules with their own `MODULE_README.md` are collapsed to a single stub line.

```
---
Submodule: src/matrx_orm/  [64 files — full detail in src/matrx_orm/MODULE_README.md]

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
  "subdirectory": "src",
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

<!-- AUTO:call_graph -->
## Call Graph

> Auto-generated. All Python files
> Covered submodules shown as stubs — see child READMEs for full detail: `matrx_orm`
> Excluded from call graph: `tests`.
> Shows which functions call which. `async` prefix = caller is an async function.
> Method calls shown as `receiver.method()`. Private methods (`_`) excluded by default.

### Call graph: src.matrx_orm.state

> Full detail in [`src/matrx_orm/MODULE_README.md`](src/matrx_orm/MODULE_README.md)

```
`src.matrx_orm.state.__init__ → src.matrx_orm.state.ConfigurationError() (line 36)` → ... → `state.count() (line 470)`
```

### Call graph: src.matrx_orm.exceptions

> Full detail in [`src/matrx_orm/MODULE_README.md`](src/matrx_orm/MODULE_README.md)

```
`src.matrx_orm.exceptions._capture_caller_frames → _tb.extract_stack() (line 24)` → ... → `join(lines) (line 932)`
```

### Call graph: src.matrx_orm.error_handling

> Full detail in [`src/matrx_orm/MODULE_README.md`](src/matrx_orm/MODULE_README.md)

```
`async src.matrx_orm.error_handling.handle_orm_operation → src.matrx_orm.error_handling.CacheError() (line 27)`
```

### Call graph: src.matrx_orm.extended.app_error_handler

> Full detail in [`src/matrx_orm/MODULE_README.md`](src/matrx_orm/MODULE_README.md)

```
`Global Scope → src.matrx_orm.extended.app_error_handler.TypeVar('_F') (line 9)` → ... → `src.matrx_orm.extended.app_error_handler.wraps(func) (line 104)`
```

### Call graph: src.matrx_orm.utils.sql_utils

> Full detail in [`src/matrx_orm/MODULE_README.md`](src/matrx_orm/MODULE_README.md)

```
`src.matrx_orm.utils.sql_utils.clean_default_value → re.sub('::[\\w\\s]+', '', default_value) (line 16)` → ... → `re.sub(':(\\w+)', replace_named_param, sql) (line 56)`
```

### Call graph: src.matrx_orm.utils.type_converters

> Full detail in [`src/matrx_orm/MODULE_README.md`](src/matrx_orm/MODULE_README.md)

```
`src.matrx_orm.utils.type_converters.to_python → datetime.fromisoformat(value) (line 23)` → ... → `TypeConverter.get_db_prep_value(value, model._fields[field_name].field_type) (line 100)`
```

### Call graph: src.matrx_orm.adapters.postgresql

> Full detail in [`src/matrx_orm/MODULE_README.md`](src/matrx_orm/MODULE_README.md)

```
`src.matrx_orm.adapters.postgresql.__init__ → src.matrx_orm.adapters.postgresql.get_database_config() (line 10)` → ... → `join(filters) (line 170)`
```

### Call graph: src.matrx_orm.adapters.base_adapter

> Full detail in [`src/matrx_orm/MODULE_README.md`](src/matrx_orm/MODULE_README.md)

```
`async src.matrx_orm.adapters.base_adapter.__aexit__ → self.close() (line 69)`
```

### Call graph: src.matrx_orm.python_sql.table_typescript_relationship

> Full detail in [`src/matrx_orm/MODULE_README.md`](src/matrx_orm/MODULE_README.md)

```
`src.matrx_orm.python_sql.table_typescript_relationship.transform_relationships_for_typescript → items() (line 34)` → ... → `src.matrx_orm.python_sql.table_typescript_relationship.analyze_relationships(relationships) (line 150)`
```

### Call graph: src.matrx_orm.python_sql.table_detailed_relationships

> Full detail in [`src/matrx_orm/MODULE_README.md`](src/matrx_orm/MODULE_README.md)

```
`src.matrx_orm.python_sql.table_detailed_relationships.get_table_relationships → src.matrx_orm.python_sql.table_detailed_relationships.execute_sql_query(query, (schema, schema), database_project) (line 118)` → ... → `src.matrx_orm.python_sql.table_detailed_relationships.analyze_many_to_many_relationships(all_relationships_list) (line 489)`
```

### Call graph: src.matrx_orm.python_sql.db_objects

> Full detail in [`src/matrx_orm/MODULE_README.md`](src/matrx_orm/MODULE_README.md)

```
`src.matrx_orm.python_sql.db_objects.get_full_db_objects → src.matrx_orm.python_sql.db_objects.execute_sql_query(query, (schema,), database_project) (line 172)` → ... → `src.matrx_orm.python_sql.db_objects.get_db_objects() (line 389)`
```

### Call graph: src.matrx_orm.query.executor

> Full detail in [`src/matrx_orm/MODULE_README.md`](src/matrx_orm/MODULE_README.md)

```
`Global Scope → src.matrx_orm.query.executor.object() (line 21)` → ... → `self.model() (line 877)`
```

### Call graph: src.matrx_orm.query.builder

> Full detail in [`src/matrx_orm/MODULE_README.md`](src/matrx_orm/MODULE_README.md)

```
`Global Scope → src.matrx_orm.query.builder.TypeVar('ModelT') (line 22)` → ... → `self.offset(start) (line 512)`
```

### Call graph: src.matrx_orm.client.postgres_connection

> Full detail in [`src/matrx_orm/MODULE_README.md`](src/matrx_orm/MODULE_README.md)

```
`src.matrx_orm.client.postgres_connection.init_connection_details → src.matrx_orm.client.postgres_connection.get_database_config() (line 20)` → ... → `putconn(conn) (line 170)`
```

### Call graph: src.matrx_orm.middleware.base

> Full detail in [`src/matrx_orm/MODULE_README.md`](src/matrx_orm/MODULE_README.md)

```
`src.matrx_orm.middleware.base.add_middleware → ...append(middleware) (line 22)` → ... → `middleware_manager.process_query(query) (line 248)`
```

### Call graph: src.matrx_orm.sql_executor.utils

> Full detail in [`src/matrx_orm/MODULE_README.md`](src/matrx_orm/MODULE_README.md)

```
`src.matrx_orm.sql_executor.utils.list_available_queries → src.matrx_orm.sql_executor.utils.get_registry() (line 5)` → ... → `join(docs) (line 61)`
```

### Call graph: src.matrx_orm.sql_executor.executor

> Full detail in [`src/matrx_orm/MODULE_README.md`](src/matrx_orm/MODULE_README.md)

```
`src.matrx_orm.sql_executor.executor.validate_params → src.matrx_orm.sql_executor.executor.get_registry() (line 17)` → ... → `src.matrx_orm.sql_executor.executor.db_execute_batch_query(query_data['query'], validated_params, batch_size, query_data['database']) (line 159)`
```

### Call graph: src.matrx_orm.sql_executor.registry

> Full detail in [`src/matrx_orm/MODULE_README.md`](src/matrx_orm/MODULE_README.md)

```
`src.matrx_orm.sql_executor.registry.get → ...get(name) (line 18)` → ... → `_global_registry.register(name, query) (line 52)`
```

### Call graph: src.matrx_orm.schema_builder.code_handler

> Full detail in [`src/matrx_orm/MODULE_README.md`](src/matrx_orm/MODULE_README.md)

```
`src.matrx_orm.schema_builder.code_handler._is_allowed → lower() (line 27)` → ... → `write_to_json(path, data) (line 50)`
```

### Call graph: src.matrx_orm.schema_builder.columns

> Full detail in [`src/matrx_orm/MODULE_README.md`](src/matrx_orm/MODULE_README.md)

```
`src.matrx_orm.schema_builder.columns.__init__ → self.initit_level_1() (line 79)` → ... → `...replace('vector(', '') (line 1324)`
```

### Call graph: src.matrx_orm.schema_builder.schema

> Full detail in [`src/matrx_orm/MODULE_README.md`](src/matrx_orm/MODULE_README.md)

```
`src.matrx_orm.schema_builder.schema.format_ts_object → re.sub('"(\\w+)"\\s*:', '\\1:', ts_object_str) (line 20)` → ... → `...items() (line 893)`
```

### Call graph: src.matrx_orm.schema_builder.common

> Full detail in [`src/matrx_orm/MODULE_README.md`](src/matrx_orm/MODULE_README.md)

```
`Global Scope → dotenv.load_dotenv() (line 7)` → ... → `os.getenv('MATRX_VERBOSE', '') (line 50)`
```

### Call graph: src.matrx_orm.schema_builder.runner

> Full detail in [`src/matrx_orm/MODULE_README.md`](src/matrx_orm/MODULE_README.md)

```
`src.matrx_orm.schema_builder.runner._close_pools → connection_pools.items() (line 29)` → ... → `src.matrx_orm.schema_builder.runner._close_pools() (line 252)`
```

### Call graph: src.matrx_orm.schema_builder.views

> Full detail in [`src/matrx_orm/MODULE_README.md`](src/matrx_orm/MODULE_README.md)

```
`src.matrx_orm.schema_builder.views.__init__ → ...to_snake_case(self.name) (line 36)` → ... → `self.generate_unique_name_lookups() (line 50)`
```

### Call graph: src.matrx_orm.schema_builder.relationships

> Full detail in [`src/matrx_orm/MODULE_README.md`](src/matrx_orm/MODULE_README.md)

```
`src.matrx_orm.schema_builder.relationships.__init__ → ...to_camel_case(self.column) (line 21)` → ... → `...to_camel_case(source_table.name) (line 29)`
```

### Call graph: src.matrx_orm.schema_builder.tables

> Full detail in [`src/matrx_orm/MODULE_README.md`](src/matrx_orm/MODULE_README.md)

```
`src.matrx_orm.schema_builder.tables.__init__ → ...to_snake_case(self.name) (line 91)` → ... → `...items() (line 1224)`
```

### Call graph: src.matrx_orm.schema_builder.generator

> Full detail in [`src/matrx_orm/MODULE_README.md`](src/matrx_orm/MODULE_README.md)

```
`src.matrx_orm.schema_builder.generator.get_schema_structure → schema_manager.get_table(table_name) (line 9)` → ... → `join(lines) (line 159)`
```

### Call graph: src.matrx_orm.schema_builder.schema_manager

> Full detail in [`src/matrx_orm/MODULE_README.md`](src/matrx_orm/MODULE_README.md)

```
`src.matrx_orm.schema_builder.schema_manager.__init__ → src.matrx_orm.schema_builder.schema_manager.get_database_config(database_project) (line 33)` → ... → `...save_frontend_junction_analysis_json(frontend_junction_analysis) (line 724)`
```

### Call graph: src.matrx_orm.schema_builder.helpers.entity_generators

> Full detail in [`src/matrx_orm/MODULE_README.md`](src/matrx_orm/MODULE_README.md)

```
`src.matrx_orm.schema_builder.helpers.entity_generators.generate_typescript_entity → overrides.get('schemaType', 'null') (line 19)` → ... → `src.matrx_orm.schema_builder.helpers.entity_generators.generate_all_entity_main_hooks(entity_names) (line 303)`
```

### Call graph: src.matrx_orm.schema_builder.helpers.git_checker

> Full detail in [`src/matrx_orm/MODULE_README.md`](src/matrx_orm/MODULE_README.md)

```
`src.matrx_orm.schema_builder.helpers.git_checker.check_git_status → os.getenv('ADMIN_PYTHON_ROOT', '') (line 17)` → ... → `sys.exit(1) (line 114)`
```

### Call graph: src.matrx_orm.schema_builder.helpers.base_generators

> Full detail in [`src/matrx_orm/MODULE_README.md`](src/matrx_orm/MODULE_README.md)

```
`src.matrx_orm.schema_builder.helpers.base_generators.generate_legacy_dto_manager_class → warnings.warn('generate_legacy_dto_manager_class() is deprecated. Use generate_base_manager_class() which scaffolds a ModelView.', DeprecationWarning) (line 189)` → ... → `src.matrx_orm.schema_builder.helpers.base_generators.plt(file_path, 'Manager class saved') (line 648)`
```

### Call graph: src.matrx_orm.core.config

> Full detail in [`src/matrx_orm/MODULE_README.md`](src/matrx_orm/MODULE_README.md)

```
`Global Scope → src.matrx_orm.core.config.field() (line 26)` → ... → `...join(ADMIN_TS_ROOT, 'constants/') (line 496)`
```

### Call graph: src.matrx_orm.core.signals

> Full detail in [`src/matrx_orm/MODULE_README.md`](src/matrx_orm/MODULE_README.md)

```
`src.matrx_orm.core.signals.connect → ...append(receiver) (line 54)` → ... → `src.matrx_orm.core.signals.Signal('post_delete') (line 99)`
```

### Call graph: src.matrx_orm.core.fields

> Full detail in [`src/matrx_orm/MODULE_README.md`](src/matrx_orm/MODULE_README.md)

```
`Global Scope → src.matrx_orm.core.fields.TypeVar('_JT') (line 15)` → ... → `validate(value) (line 1255)`
```

### Call graph: src.matrx_orm.core.base

> Full detail in [`src/matrx_orm/MODULE_README.md`](src/matrx_orm/MODULE_README.md)

```
`src.matrx_orm.core.base._to_snake_case → lower() (line 43)` → ... → `src.matrx_orm.core.base.QueryBuilder(cls) (line 1392)`
```

### Call graph: src.matrx_orm.core.extended

> Full detail in [`src/matrx_orm/MODULE_README.md`](src/matrx_orm/MODULE_README.md)

```
`Global Scope → src.matrx_orm.core.extended.TypeVar('ModelT') (line 16)` → ... → `self.delete_where() (line 1861)`
```

### Call graph: src.matrx_orm.core.async_db_manager

> Full detail in [`src/matrx_orm/MODULE_README.md`](src/matrx_orm/MODULE_README.md)

```
`async src.matrx_orm.core.async_db_manager._init_vector_codec → conn.set_type_codec('vector') (line 39)` → ... → `src.matrx_orm.core.async_db_manager.cause_error() (line 352)`
```

### Call graph: src.matrx_orm.core.model_view

> Full detail in [`src/matrx_orm/MODULE_README.md`](src/matrx_orm/MODULE_README.md)

```
`src.matrx_orm.core.model_view.__new__ → computed.update(base_computed) (line 86)` → ... → `warnings.warn(f"[ModelView:{view_name}] Prefetch of relation '{relation_name}' failed: {type(exc).__name__}: {exc}. Skipped.", RuntimeWarning) (line 221)`
```

### Call graph: src.matrx_orm.core.registry

> Full detail in [`src/matrx_orm/MODULE_README.md`](src/matrx_orm/MODULE_README.md)

```
`src.matrx_orm.core.registry.register_all → cls.register(model) (line 25)` → ... → `model_registry.get_model(model_name) (line 46)`
```

### Call graph: src.matrx_orm.core.paginator

> Full detail in [`src/matrx_orm/MODULE_README.md`](src/matrx_orm/MODULE_README.md)

```
`Global Scope → src.matrx_orm.core.paginator.TypeVar('ModelT') (line 34)` → ... → `self.page(self._current_page) (line 190)`
```

### Call graph: src.matrx_orm.core.expressions

> Full detail in [`src/matrx_orm/MODULE_README.md`](src/matrx_orm/MODULE_README.md)

```
`src.matrx_orm.core.expressions.__add__ → src.matrx_orm.core.expressions.Expression(self.field_name, '+', other) (line 19)` → ... → `params.append(literal) (line 760)`
```

### Call graph: src.matrx_orm.core.types

> Full detail in [`src/matrx_orm/MODULE_README.md`](src/matrx_orm/MODULE_README.md)

```
`Global Scope → src.matrx_orm.core.types.TypeVar('ModelT') (line 31)` → ... → `src.matrx_orm.core.types.dataclass() (line 192)`
```

### Call graph: src.matrx_orm.core.transaction

> Full detail in [`src/matrx_orm/MODULE_README.md`](src/matrx_orm/MODULE_README.md)

```
`Global Scope → src.matrx_orm.core.transaction.ContextVar('_active_connection') (line 35)` → ... → `...get('MATRX_DEFAULT_DATABASE', 'default') (line 159)`
```

### Call graph: src.matrx_orm.core.relations

> Full detail in [`src/matrx_orm/MODULE_README.md`](src/matrx_orm/MODULE_README.md)

```
`src.matrx_orm.core.relations._related_model → src.matrx_orm.core.relations.get_model_by_name(self.to_model) (line 29)` → ... → `target.lower() (line 478)`
```

### Call graph: src.matrx_orm.operations.delete

> Full detail in [`src/matrx_orm/MODULE_README.md`](src/matrx_orm/MODULE_README.md)

```
`async src.matrx_orm.operations.delete.delete → delete() (line 17)` → ... → `post_delete.send(model_cls) (line 70)`
```

### Call graph: src.matrx_orm.operations.read

> Full detail in [`src/matrx_orm/MODULE_README.md`](src/matrx_orm/MODULE_README.md)

```
`async src.matrx_orm.operations.read.get → get() (line 5)` → ... → `src.matrx_orm.operations.read.QueryBuilder(model_cls) (line 51)`
```

### Call graph: src.matrx_orm.operations.create

> Full detail in [`src/matrx_orm/MODULE_README.md`](src/matrx_orm/MODULE_README.md)

```
`async src.matrx_orm.operations.create.create → src.matrx_orm.operations.create.model_cls() (line 16)` → ... → `src.matrx_orm.operations.create.create(model_cls) (line 188)`
```

### Call graph: src.matrx_orm.operations.update

> Full detail in [`src/matrx_orm/MODULE_README.md`](src/matrx_orm/MODULE_README.md)

```
`async src.matrx_orm.operations.update.update → update() (line 20)` → ... → `post_save.send(model_cls) (line 197)`
```
<!-- /AUTO:call_graph -->
