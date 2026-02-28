# `tests` — Module Overview

> This document is partially auto-generated. Sections tagged `<!-- AUTO:id -->` are refreshed by the generator.
> Everything else is yours to edit freely and will never be overwritten.

<!-- AUTO:meta -->
## About This Document

This file is **partially auto-generated**. Sections wrapped in `<!-- AUTO:id -->` tags
are overwritten each time the generator runs. Everything else is yours to edit freely.

| Field | Value |
|-------|-------|
| Module | `tests` |
| Last generated | 2026-02-28 13:57 |
| Output file | `tests/MODULE_README.md` |
| Signature mode | `signatures` |


**Child READMEs detected** (signatures collapsed — see links for detail):

| README | |
|--------|---|
| [`tests/level1/MODULE_README.md`](tests/level1/MODULE_README.md) | last generated 2026-02-28 13:57 |
| [`tests/level2/MODULE_README.md`](tests/level2/MODULE_README.md) | last generated 2026-02-28 13:57 |
**To refresh auto-sections:**
```bash
python utils/code_context/generate_module_readme.py tests --mode signatures
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

> Auto-generated. 38 files across 6 directories.

```
tests/
├── MODULE_README.md
├── __init__.py
├── conftest.py
├── level1/
│   ├── MODULE_README.md
│   ├── __init__.py
│   ├── test_config.py
│   ├── test_ddl_generator.py
│   ├── test_exceptions.py
│   ├── test_fields.py
│   ├── test_migration_diff_types.py
│   ├── test_migration_loader.py
│   ├── test_model_instance.py
│   ├── test_model_meta.py
│   ├── test_query_builder.py
│   ├── test_query_executor_sql.py
│   ├── test_registry.py
│   ├── test_relations.py
│   ├── test_state_cache.py
├── level2/
│   ├── MODULE_README.md
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_bulk_ops.py
│   ├── test_cache_integration.py
│   ├── test_crud.py
│   ├── test_foreign_keys.py
│   ├── test_m2m.py
│   ├── test_manager.py
│   ├── test_migrations_live.py
│   ├── test_query_execution.py
│   ├── test_schema_diff.py
├── sample_project/
│   ├── __init__.py
│   ├── generate.py
│   ├── generated/
│   │   ├── .gitkeep
│   │   ├── primary/
│   ├── test_schema_generation.py
├── schema/
│   ├── entity_tests.py
│   ├── test_base_generation.py
│   ├── test_generate_schema.py
├── test_model_cls_refactor.py
# excluded: 4 .md, 1 .example, 1 (no ext), 1 .yaml
```
<!-- /AUTO:tree -->

<!-- AUTO:signatures -->
## API Signatures

> Auto-generated via `output_mode="{mode}"`. ~5-10% token cost vs full source.
> For full source, open the individual files directly.
> Submodules with their own `MODULE_README.md` are collapsed to a single stub line.

```
---
Filepath: tests/__init__.py  [python]




---
Filepath: tests/conftest.py  [python]

  def pytest_configure(config)
  def pytest_collection_modifyitems(config, items)



---
Filepath: tests/test_model_cls_refactor.py  [python]

  class SampleModel(Model):
  def test_model_definition()
  def test_model_instantiation()
  def test_reserved_names_doc()



---
Filepath: tests/sample_project/__init__.py  [python]




---
Filepath: tests/sample_project/generate.py  [python]




---
Filepath: tests/sample_project/test_schema_generation.py  [python]

  class TestPrimaryDatabase:
      def test_schema_manager_initialises(self, primary_schema_manager)
      def test_has_tables(self, primary_schema_manager)
      def test_auth_schema_visible(self, primary_schema_manager)
      def test_generate_schema_files(self, primary_schema_manager)
      def test_generate_models(self, primary_schema_manager)
      def test_analyze_schema(self, primary_schema_manager)
      def test_foreign_key_references_have_schema(self, primary_schema_manager)
      def test_get_specific_table(self, primary_schema_manager)
  class TestSecondaryDatabase:
      def test_schema_manager_initialises(self, secondary_schema_manager)
      def test_has_tables(self, secondary_schema_manager)
      def test_no_auth_schema(self, secondary_schema_manager)
      def test_generate_schema_files(self, secondary_schema_manager)
      def test_generate_models(self, secondary_schema_manager)
      def test_analyze_schema(self, secondary_schema_manager)
  class TestCrossDatabaseIsolation:
      def test_different_table_sets(self, primary_schema_manager, secondary_schema_manager)
      def test_database_project_names_differ(self, primary_schema_manager, secondary_schema_manager)
  def register_sample_databases()
  def primary_schema_manager()
  def secondary_schema_manager()
  def output_dir(tmp_path_factory)



---
Filepath: tests/sample_project/generated/.gitkeep  [unknown ()]

  # signature extraction not supported for this language



---
Submodule: tests/level1/  [14 files — full detail in tests/level1/MODULE_README.md]

---
Filepath: tests/schema/test_base_generation.py  [python]

  def test_generate_manager_class()



---
Filepath: tests/schema/test_generate_schema.py  [python]

  def get_test_schema_manager(schema: str, database_project: str, additional_schemas: list[str])
  def test_generate_full_schema_system(schema_manager: SchemaManager)
  def example_usage(schema_manager)
  def get_full_schema_object(schema, database_project)



---
Filepath: tests/schema/entity_tests.py  [python]

  def test_check_git_status()
  def test_generate_entity_hooks()
  def test_generate_entity_overrides()
  def test_generate_typescript_files()



---
Submodule: tests/level2/  [11 files — full detail in tests/level2/MODULE_README.md]

```
<!-- /AUTO:signatures -->

<!-- AUTO:dependencies -->
## Dependencies

**External packages:** database_registry, dotenv, matrx_orm, matrx_utils, pytest
<!-- /AUTO:dependencies -->

<!-- AUTO:config -->
## Generation Config

> Auto-managed. Contains the exact parameters used to generate this README.
> Used by parent modules to auto-refresh this file when it is stale.
> Do not edit manually — changes will be overwritten on the next run.

```json
{
  "subdirectory": "tests",
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
