# `src.matrx_orm.schema_builder` — Module Overview

> This document is partially auto-generated. Sections tagged `<!-- AUTO:id -->` are refreshed by the generator.
> Everything else is yours to edit freely and will never be overwritten.

<!-- AUTO:meta -->
## About This Document

This file is **partially auto-generated**. Sections wrapped in `<!-- AUTO:id -->` tags
are overwritten each time the generator runs. Everything else is yours to edit freely.

| Field | Value |
|-------|-------|
| Module | `src/matrx_orm/schema_builder` |
| Last generated | 2026-02-28 13:57 |
| Output file | `src/matrx_orm/schema_builder/MODULE_README.md` |
| Signature mode | `signatures` |

**To refresh auto-sections:**
```bash
python utils/code_context/generate_module_readme.py src/matrx_orm/schema_builder --mode signatures
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

> Auto-generated. 16 files across 2 directories.

```
src/matrx_orm/schema_builder/
├── MODULE_README.md
├── __init__.py
├── code_handler.py
├── columns.py
├── common.py
├── generator.py
├── helpers/
│   ├── __init__.py
│   ├── base_generators.py
│   ├── entity_generators.py
│   ├── git_checker.py
├── relationships.py
├── runner.py
├── schema.py
├── schema_manager.py
├── tables.py
├── views.py
# excluded: 1 .md
```
<!-- /AUTO:tree -->

<!-- AUTO:signatures -->
## API Signatures

> Auto-generated via `output_mode="signatures"`. ~5-10% token cost vs full source.
> For full source, open the individual files directly.

```
---
Filepath: src/matrx_orm/schema_builder/code_handler.py  [python]

  class SchemaCodeHandler(CodeHandler):
      def __init__(self, output_config: OutputConfig)
      def _is_allowed(self, path: str) -> bool
      def generate_and_save_code_from_object(self, config_obj, main_code, additional_code = None)
      def save_code_file(self, file_path: str, content: str) -> None
      def write_to_json(self, path, data, root = 'temp', clean = True)


---
Filepath: src/matrx_orm/schema_builder/__init__.py  [python]



---
Filepath: src/matrx_orm/schema_builder/columns.py  [python]

  class Column:
      def __init__(self, database_project, table_name, unique_column_id, name, position, full_type, base_type, domain_type, enum_labels, is_array, nullable, default, character_maximum_length, numeric_precision, numeric_scale, collation, is_identity, is_generated, is_primary_key, is_unique, has_index, check_constraints, foreign_key_reference, comment, parent_table_instance, is_display_field = False)
      def __repr__(self)
      def initit_level_1(self)
      def initit_level_2(self)
      def initit_level_3(self)
      def initit_level_4(self)
      def initit_level_5(self)
      def initit_level_6(self)
      def generate_core_name_variations(self)
      def pre_initialize(self)
      def generate_basic_info(self)
      def initialize_code_generation(self)
      def generate_unique_name_lookups(self)
      def update_prop(self, prop, value, priority = 0)
      def update_component(self, component, priority = 0)
      def generate_name_variations(self)
      def set_typescript_enums(self)
      def set_is_default_filter_field(self)
      def set_python_enum_entry(self)
      def generate_description(self)
      def manage_data_type_impact(self)
      def to_reverse_column_lookup_entry(self)
      def to_typescript_type_entry(self)
      def to_ts_simple_schema_entry(self)
      def to_schema_entry(self)
      def parse_default_value(self)
      def get_default_value(self)
      def get_type_reference(self)
      def get_is_required(self)
      def get_is_array(self)
      def get_is_primary_key(self)
      def get_default_generator_function(self)
      def get_validation_functions(self)
      def get_exclusion_rules(self)
      def get_max_field_length(self)
      def to_python_model_field(self)
      def to_dict(self)
  def clean_value(value, context)


---
Filepath: src/matrx_orm/schema_builder/schema.py  [python]

  class Schema:
      def __init__(self, name = 'public', database_project = None, output_config: OutputConfig = None, manager_flags: dict | None = None)
      def add_table(self, table)
      def add_all_table_instances(self)
      def add_view(self, view)
      def get_table(self, table_name)
      def get_view(self, view_name)
      def get_related_tables(self, table_name)
      def __repr__(self)
      def initialize_code_generation(self)
      def get_file_location(self, code_version)
      def get_import_statements(self, code_version)
      def generate_schema_structure(self)
      def generate_type_inference_entries(self)
      def generate_initial_type_inference_entries(self)
      def generate_typescript_list_tables_and_views(self)
      def generate_primary_key_object(self)
      def generate_type_brand_util(self)
      def generate_data_type(self, data_types = None)
      def generate_data_structure(self, data_structures = None)
      def generate_fetch_strategy(self, fetch_strategies = None)
      def generate_name_formats(self)
      def generate_automation_dynamic_name(self, dynamic_names = None)
      def generate_automation_custom_name(self, custom_names = None)
      def generate_static_ts_Initial_table_schema(self)
      def generate_ts_lookup_file(self)
      def generate_entity_typescript_types_file(self)
      def generate_schema_file(self)
      def generate_types_file(self)
      def convert_to_typescript(self, python_dict)
      def generate_field_name_list(self)
      def generate_entity_overrides(self)
      def generate_entity_main_hooks(self)
      def generate_entity_field_overrides(self)
      def generate_schema_files(self)
      def get_string_user_model(self)
      def get_string_model_registry(self, sorted_tables: list[str]) -> str
      def generate_models(self)
      def save_analysis_json(self, analysis_dict)
      def save_frontend_full_relationships_json(self, analysis_dict)
      def save_frontend_junction_analysis_json(self, analysis_dict)
      def to_dict(self)
  def format_ts_object(ts_object_str)
  def format_key(key)
  def dict_to_ts(d)


---
Filepath: src/matrx_orm/schema_builder/common.py  [python]

  ADMIN_PYTHON_ROOT = os.getenv('ADMIN_PYTHON_ROOT', '')
  ADMIN_TS_ROOT = os.getenv('ADMIN_TS_ROOT', '')
  DEBUG_CONFIG = {6 keys}
  class OutputConfig:
      def from_dict(cls, d: dict) -> OutputConfig


---
Filepath: src/matrx_orm/schema_builder/runner.py  [python]

  def _close_pools() -> None
  def _load_yaml(path: Path) -> dict[str, Any]
  def run_schema_generation(config_path: str | Path = 'matrx_orm.yaml') -> None


---
Filepath: src/matrx_orm/schema_builder/views.py  [python]

  class View:
      def __init__(self, oid, name, type_, schema, database, owner, size_bytes, description, view_definition, column_data)
      def __repr__(self)
      def initialize_code_generation(self)
      def generate_unique_name_lookups(self)
      def to_dict(self)


---
Filepath: src/matrx_orm/schema_builder/relationships.py  [python]

  class Relationship:
      def __init__(self, constraint_name, column, foreign_column, target_table = None, source_table = None)
      def __repr__(self)
      def to_dict(self)


---
Filepath: src/matrx_orm/schema_builder/tables.py  [python]

  class Table:
      def __init__(self, oid, database_project, unique_table_id, name, type_, schema, database, owner, size_bytes, index_size_bytes, rows, last_vacuum, last_analyze, description, estimated_row_count, total_bytes, has_primary_key, index_count, table_columns = None, junction_analysis_ts = None)
      def pre_initialize(self)
      def generate_basic_info(self)
      def identify_display_column(self)
      def get_display_field_metadata(self)
      def add_foreign_key(self, target_table, relationship)
      def get_relationship_mapping(self)
      def add_referenced_by(self, source_table, relationship)
      def add_many_to_many(self, junction_table, related_table)
      def _update_fetch_strategy(self)
      def get_column(self, column_name)
      def get_foreign_key(self, target_table)
      def get_referenced_by(self, source_table)
      def get_foreign_key_column(self, target_table)
      def get_referenced_by_column(self, source_table)
      def get_all_columns(self)
      def get_all_foreign_keys(self)
      def get_all_referenced_by(self)
      def get_all_relations(self)
      def get_all_relations_list(self)
      def get_column_names(self)
      def __repr__(self)
      def initialize_code_generation(self)
      def finalize_initialization(self)
      def get_primary_key_field(self) -> str
      def get_fieldNames_in_groups(self)
      def get_primary_key_fields_list(self)
      def get_column_default_components(self)
      def get_primary_key_metadata(self) -> dict
      def generate_unique_name_lookups(self)
      def generate_unique_field_types(self)
      def to_foreign_key_entry(self, target_table)
      def to_inverse_foreign_key_entry(self, source_table)
      def to_json_inverse_foreign_keys(self)
      def to_typescript_type_entry(self)
      def to_json_foreign_keys(self)
      def to_json_many_to_many(self)
      def to_ts_foreign_keys(self)
      def to_ts_inverse_foreign_keys(self)
      def to_ts_many_to_many(self)
      def to_schema_structure_entry(self)
      def generate_name_variations(self)
      def generate_component_props(self)
      def to_reverse_table_lookup_entry(self)
      def to_reverse_field_name_lookup(self)
      def to_schema_entry(self)
      def to_python_foreign_key_field(self, target_table, relationship)
      def to_python_inverse_foreign_key_field(self, source_table, relationship)
      def to_python_many_to_many_config(self)
      def to_python_model(self)
      def to_python_manager_string(self, global_manager_flags: dict | None = None)
      def to_dict(self)


---
Filepath: src/matrx_orm/schema_builder/generator.py  [python]

  def get_schema_structure(schema_manager, table_name)
  def get_default_component_props()
  def generate_automation_schema()
  def get_relationship_data_model_types()
  def generate_dto_and_manager(name, name_camel)


---
Filepath: src/matrx_orm/schema_builder/schema_manager.py  [python]

  class SchemaManager:
      def __init__(self, database = 'postgres', schema = 'public', database_project = None, additional_schemas = None, output_config: OutputConfig = None, save_direct = False, include_tables = None, exclude_tables = None, manager_flags: dict | None = None)
      def _is_table_included(self, table_name: str) -> bool
      def initialize(self)
      def execute_all_initit_level_1(self)
      def execute_all_initit_level_2(self)
      def execute_all_initit_level_3(self)
      def execute_all_initit_level_4(self)
      def execute_all_initit_level_5(self)
      def execute_all_initit_level_6(self)
      def set_all_schema_data(self)
      def load_objects(self)
      def load_table(self, obj)
      def load_view(self, obj)
      def load_table_relationships(self)
      def detect_many_to_many_relationships(self)
      def analyze_relationships(self)
      def get_table(self, table_name)
      def get_view(self, view_name)
      def get_column(self, table_name, column_name)
      def get_related_tables(self, table_name)
      def get_all_tables(self)
      def get_all_views(self)
      def analyze_schema(self)
      def get_table_instance(self, table_name)
      def get_view_instance(self, view_name)
      def get_column_instance(self, table_name, column_name)
      def get_table_frontend_name(self, table_name)
      def get_view_frontend_name(self, view_name)
      def get_column_frontend_name(self, table_name, column_name)
      def transform_foreign_keys(self, main_table_name, entry)
      def transform_referenced_by(self, table_name, entry)
      def get_frontend_full_relationships(self)
      def get_full_relationship_analysis(self)
      def get_frontend_junction_analysis(self)
      def __repr__(self)


---
Filepath: src/matrx_orm/schema_builder/helpers/__init__.py  [python]



---
Filepath: src/matrx_orm/schema_builder/helpers/entity_generators.py  [python]

  def generate_imports()
  def generate_typescript_entity(entity_name, overrides = None)
  def generate_multiple_entities(entity_names, system_overrides)
  def merge_component_props(overrides = None)
  def format_ts_object(ts_object_str)
  def generate_typescript_field_overrides(entity_name, overrides)
  def generate_full_typescript_file(entity_names, system_overrides)
  def to_camel_case(snake_str)
  def to_pascal_case(snake_str)
  def generate_entity_main_hook(entity_name_snake)
  def generate_all_entity_main_hooks(entity_names)
  def generate_main_hook_imports(entity_names)
  def generate_complete_main_hooks_file(entity_names)


---
Filepath: src/matrx_orm/schema_builder/helpers/git_checker.py  [python]

  def check_git_status(save_direct: bool, python_root: str = '', ts_root: str = '', ignore_path_prefixes: list[str] | None = None) -> bool
  def _is_ignorable(filepath: str) -> bool


---
Filepath: src/matrx_orm/schema_builder/helpers/base_generators.py  [python]

  def generate_base_manager_class(models_module_path: str, model_pascal: str, model_name: str, model_name_plural: str, model_name_snake: str, relations: list[str] | None = None, view_prefetch: list[str] | None = None) -> str
  def generate_legacy_dto_manager_class(models_module_path: str, model_pascal: str, model_name: str, model_name_plural: str, model_name_snake: str) -> str
  def generate_to_dict_methods(model_name: str, model_name_plural: str) -> str
  def generate_active_methods(model_name: str, model_name_plural: str) -> str
  def generate_or_not_methods(model_name: str, model_name_plural: str) -> str
  def generate_core_relation_methods(model_name: str, model_name_plural: str, relations: list[str]) -> str
  def generate_active_relation_methods(model_name: str, model_name_plural: str, relations: list[str]) -> str
  def generate_to_dict_relation_methods(model_name: str, model_name_plural: str, relations: list[str]) -> str
  def generate_m2m_relation_methods(model_name: str, model_name_plural: str, m2m_relations: list[str]) -> str
  def generate_filter_field_methods(model_name: str, model_name_plural: str, filter_fields: list[str]) -> str
  def generate_utility_methods(model_name: str, model_name_plural: str) -> str
  def generate_singleton_manager(model_pascal: str, model_name: str) -> str
  def generate_manager_class(models_module_path: str, model_pascal: str, model_name: str, model_name_plural: str, model_name_snake: str, relations: list[str], filter_fields: list[str], include_core_relations: bool = True, include_active_relations: bool = False, include_filter_fields: bool = True, include_active_methods: bool = False, include_or_not_methods: bool = False, include_to_dict_methods: bool = False, include_to_dict_relations: bool = False, m2m_relations: list[str] | None = None, view_prefetch: list[str] | None = None) -> str
  def save_manager_class(model_pascal: str, model_name: str, model_name_plural: str, model_name_snake: str, relations: list[str], filter_fields: list[str], include_core_relations: bool = True, include_active_relations: bool = False, include_filter_fields: bool = True, include_active_methods: bool = False, include_or_not_methods: bool = True, include_to_dict_methods: bool = True, include_to_dict_relations: bool = False) -> tuple[str, str]
```
<!-- /AUTO:signatures -->

<!-- AUTO:dependencies -->
## Dependencies

**External packages:** dotenv, git, matrx_orm, matrx_utils, yaml
<!-- /AUTO:dependencies -->

<!-- AUTO:config -->
## Generation Config

> Auto-managed. Contains the exact parameters used to generate this README.
> Used by parent modules to auto-refresh this file when it is stale.
> Do not edit manually — changes will be overwritten on the next run.

```json
{
  "subdirectory": "src/matrx_orm/schema_builder",
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
