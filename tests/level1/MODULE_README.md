# `tests.level1` — Module Overview

> This document is partially auto-generated. Sections tagged `<!-- AUTO:id -->` are refreshed by the generator.
> Everything else is yours to edit freely and will never be overwritten.

<!-- AUTO:meta -->
## About This Document

This file is **partially auto-generated**. Sections wrapped in `<!-- AUTO:id -->` tags
are overwritten each time the generator runs. Everything else is yours to edit freely.

| Field | Value |
|-------|-------|
| Module | `tests/level1` |
| Last generated | 2026-02-28 13:57 |
| Output file | `tests/level1/MODULE_README.md` |
| Signature mode | `signatures` |

**To refresh auto-sections:**
```bash
python utils/code_context/generate_module_readme.py tests/level1 --mode signatures
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
tests/level1/
├── MODULE_README.md
├── __init__.py
├── test_config.py
├── test_ddl_generator.py
├── test_exceptions.py
├── test_fields.py
├── test_migration_diff_types.py
├── test_migration_loader.py
├── test_model_instance.py
├── test_model_meta.py
├── test_query_builder.py
├── test_query_executor_sql.py
├── test_registry.py
├── test_relations.py
├── test_state_cache.py
# excluded: 1 .md
```
<!-- /AUTO:tree -->

<!-- AUTO:signatures -->
## API Signatures

> Auto-generated via `output_mode="signatures"`. ~5-10% token cost vs full source.
> For full source, open the individual files directly.

```
---
Filepath: tests/level1/__init__.py  [python]



---
Filepath: tests/level1/test_state_cache.py  [python]

  class TestCachePolicy:
      def test_values(self)
      def test_all_members(self)
  class TestModelState:
      def test_cache_key_single_pk(self)
      def test_cache_and_retrieve(self)
      def test_remove_from_cache(self)
      def test_clear_cache(self)
      def test_get_all_cached(self)
  class TestStaleness:
      def test_permanent_never_stale(self)
      def test_instant_stale_after_1min(self)
      def test_short_term_stale_after_10min(self)
      def test_short_term_fresh(self)
      def test_long_term_stale_after_4h(self)
      def test_custom_timeout(self)
      def test_custom_timeout_fresh(self)
      def test_no_cache_time_is_stale(self)
  class TestFindInCache:
      def test_find_by_criteria(self)
      def test_find_not_found(self)
  def _run(coro)
  def _clean()
  def _make_model(name = 'CacheModel', policy = CachePolicy.SHORT_TERM, timeout = None)


---
Filepath: tests/level1/test_ddl_generator.py  [python]

  class TestColumnDefToSql:
      def test_basic(self)
      def test_primary_key(self)
      def test_not_null(self)
      def test_unique(self)
      def test_default(self)
      def test_references(self)
  class TestCreateTable:
      def test_basic(self)
      def test_with_schema(self)
      def test_with_constraints(self)
  class TestDropTable:
      def test_basic(self)
      def test_cascade(self)
      def test_with_schema(self)
  class TestAddColumn:
      def test_basic(self)
      def test_with_schema(self)
  class TestDropColumn:
      def test_basic(self)
      def test_with_schema(self)
  class TestAlterColumn:
      def test_rename(self)
      def test_type_change(self)
      def test_set_nullable(self)
      def test_set_not_null(self)
      def test_new_default(self)
      def test_drop_default(self)
      def test_multiple_changes(self)
      def test_no_changes(self)
      def test_with_schema(self)
  class TestAddIndex:
      def test_basic(self)
      def test_unique(self)
      def test_multi_column(self)
      def test_custom_method(self)
      def test_partial_where(self)
  class TestDropIndex:
      def test_basic(self)
  class TestAddConstraint:
      def test_basic(self)
      def test_with_schema(self)
  class TestDropConstraint:
      def test_basic(self)
  class TestAddForeignKey:
      def test_basic(self)
      def test_custom_constraint_name(self)
      def test_auto_constraint_name(self)
      def test_on_update(self)
  class TestDropForeignKey:
      def test_basic(self)
  class TestRenameTable:
      def test_basic(self)
      def test_with_schema(self)


---
Filepath: tests/level1/test_exceptions.py  [python]

  class FakeModel:
  class TestORMExceptionBase:
      def test_default_message(self)
      def test_custom_message(self)
      def test_model_name(self)
      def test_model_default(self)
      def test_format_message_contains_model(self)
      def test_format_message_with_class_method(self)
      def test_str_equals_format_message(self)
  class TestEnrich:
      def test_enrich_sets_model(self)
      def test_enrich_sets_operation(self)
      def test_enrich_sets_args(self)
      def test_enrich_extra_kwargs(self)
      def test_enrich_does_not_overwrite(self)
      def test_enrich_returns_self(self)
  class TestSanitizeDetails:
      def test_nested_orm_exception_flattened(self)
      def test_normal_values_passed_through(self)
  class TestSubclasses:
      def test_validation_error(self)
      def test_validation_error_positional_message(self)
      def test_validation_error_with_details(self)
      def test_does_not_exist(self)
      def test_multiple_objects_returned(self)
      def test_connection_error(self)
      def test_integrity_error(self)
      def test_transaction_error(self)
      def test_configuration_error(self)
      def test_cache_error(self)
      def test_state_error(self)
      def test_relationship_error(self)
      def test_adapter_error(self)
      def test_field_error(self)
      def test_migration_error(self)
      def test_parameter_error(self)
      def test_unknown_database_error(self)
  class TestInheritance:
      def test_query_error_is_orm_exception(self)
      def test_does_not_exist_is_query_error(self)
      def test_database_error_is_orm_exception(self)
      def test_connection_error_is_database_error(self)
      def test_all_subclasses_are_orm_exception(self)


---
Filepath: tests/level1/test_query_executor_sql.py  [python]

  class TestParseLookup:
      def test_simple_field(self)
      def test_eq_explicit(self)
      def test_in(self)
      def test_gt(self)
      def test_gte(self)
      def test_lt(self)
      def test_lte(self)
      def test_ne(self)
      def test_isnull(self)
      def test_contains(self)
      def test_icontains(self)
      def test_startswith(self)
      def test_endswith(self)
      def test_exclude(self)
      def test_unknown_suffix_treated_as_field_name(self)
      def test_double_underscore_with_valid_op(self)
  class TestBuildCondition:
      def test_eq(self)
      def test_ne(self)
      def test_gt(self)
      def test_gte(self)
      def test_lt(self)
      def test_lte(self)
      def test_in(self)
      def test_isnull_true(self)
      def test_isnull_false(self)
      def test_contains(self)
      def test_icontains(self)
      def test_startswith(self)
      def test_endswith(self)
      def test_exclude_operator(self)
      def test_fallback_eq(self)
      def test_param_index_used(self)


---
Filepath: tests/level1/test_model_meta.py  [python]

  class TestModelOptions:
      def test_qualified_table_name_no_schema(self)
      def test_qualified_table_name_with_schema(self)
      def test_m2m_defaults_to_empty_dict(self)
  class TestModelMeta:
      def test_fields_registered(self)
      def test_primary_keys_from_field_flag(self)
      def test_primary_keys_from_class_attr(self)
      def test_duplicate_pk_sources_raises(self)
      def test_no_pk_raises(self)
      def test_unique_fields(self)
      def test_fk_registration(self)
      def test_auto_table_name_snake_case(self)
      def test_custom_table_name(self)
      def test_unfetchable_flag(self)
      def test_schema_flag(self)
  def _clean_registry()
  def _make_model(name, attrs, bases = (Model,))


---
Filepath: tests/level1/test_config.py  [python]

  class TestRegisterSuccess:
      def test_basic_registration(self, _fresh_registry)
      def test_get_database_config(self, _fresh_registry)
      def test_get_config_dataclass(self, _fresh_registry)
  class TestRegisterValidation:
      def test_empty_alias_raises(self, _fresh_registry)
      def test_duplicate_alias_raises(self, _fresh_registry)
      def test_duplicate_name_ignored(self, _fresh_registry)
      def test_missing_host_raises(self, _fresh_registry)
      def test_missing_password_raises(self, _fresh_registry)
      def test_missing_port_raises(self, _fresh_registry)
  class TestGetErrors:
      def test_get_nonexistent_config(self, _fresh_registry)
      def test_get_nonexistent_dataclass(self, _fresh_registry)
  class TestListHelpers:
      def test_get_all_project_names(self, _fresh_registry)
      def test_get_all_configs(self, _fresh_registry)
  class TestAlias:
      def test_get_database_alias(self, _fresh_registry)
      def test_get_alias_nonexistent(self, _fresh_registry)
  def _fresh_registry()
  def _config(name = 'test_project', alias = 'test_alias', **overrides)


---
Filepath: tests/level1/test_relations.py  [python]

  class TestManyToManyFieldJunctionName:
      def test_auto_generated_sorted(self)
      def test_auto_generated_reverse_order(self)
      def test_custom_db_table(self)
      def test_same_model_name(self)
  class TestForeignKeyReference:
      def test_attributes(self)
      def test_defaults(self)
  class TestInverseForeignKeyReference:
      def test_attributes(self)
      def test_defaults(self)
  class TestManyToManyReference:
      def test_attributes(self)
      def test_junction_schema_default(self)
      def test_junction_schema_set(self)
  class TestManyToManyFieldIsNative:
      def test_not_native(self)


---
Filepath: tests/level1/test_fields.py  [python]

  class TestBaseField:
      def test_db_type(self)
      def test_to_python_passthrough(self)
      def test_get_db_prep_value_none(self)
      def test_nullable_default(self)
      def test_not_nullable(self)
      def test_validate_rejects_none_when_not_nullable(self)
      def test_validate_allows_none_when_nullable(self)
      def test_primary_key_flag(self)
      def test_unique_flag(self)
      def test_index_flag(self)
  class TestUUIDField:
      def test_db_type(self)
      def test_to_python_string(self)
      def test_to_python_none(self)
  class TestUUIDFieldREAL:
      def test_db_type(self)
      def test_to_python_converts_to_str(self)
      def test_to_python_none(self)
      def test_validate_rejects_bad_uuid(self)
      def test_validate_accepts_valid_uuid(self)
  class TestCharField:
      def test_db_type_default_max_length(self)
      def test_db_type_custom_max_length(self)
      def test_get_db_prep_value_truncates(self)
      def test_get_db_prep_value_none(self)
      def test_validate_rejects_non_string(self)
      def test_validate_rejects_too_long(self)
      def test_validate_accepts_valid(self)
  class TestTextField:
      def test_db_type(self)
      def test_get_db_prep_value_casts_to_str(self)
      def test_get_db_prep_value_none(self)
      def test_validate_rejects_non_string(self)
  class TestIntegerField:
      def test_db_type(self)
      def test_to_python_int(self)
      def test_to_python_none(self)
      def test_to_python_bad_value(self)
      def test_get_db_prep_value_int(self)
      def test_get_db_prep_value_none(self)
      def test_validate_rejects_non_int(self)
  class TestFloatField:
      def test_db_type(self)
      def test_validate_accepts_float(self)
      def test_validate_accepts_int(self)
      def test_validate_rejects_string(self)
  class TestBooleanField:
      def test_db_type(self)
      def test_to_python_coercion(self, input_val, expected)
      def test_to_python_none(self)
      def test_get_db_prep_value_returns_bool(self)
      def test_get_db_prep_value_none(self)
  class TestDateTimeField:
      def test_db_type(self)
      def test_to_python_from_string(self)
      def test_to_python_passthrough_datetime(self)
      def test_auto_now_flag(self)
  class TestDateField:
      def test_db_type(self)
      def test_to_python_from_string(self)
  class TestTimeField:
      def test_db_type(self)
      def test_to_python_from_string(self)
  class TestJSONField:
      def test_db_type(self)
      def test_to_python_from_string(self)
      def test_to_python_passthrough_dict(self)
      def test_get_db_prep_value_serializes(self)
      def test_get_db_prep_value_none(self)
  class TestArrayField:
      def test_db_type(self)
      def test_to_python_converts_items(self)
      def test_to_python_none(self)
      def test_validate_rejects_non_list(self)
      def test_get_db_prep_value_converts_items(self)
  class Color(Enum):
  class TestEnumField:
      def test_db_type(self)
      def test_init_requires_enum_or_choices(self)
      def test_init_rejects_both(self)
      def test_get_db_prep_value_enum_member(self)
      def test_get_db_prep_value_string(self)
      def test_to_python_returns_enum(self)
      def test_to_python_none(self)
      def test_validate_rejects_invalid_choice(self)
      def test_choices_mode(self)
      def test_to_python_choices_mode(self)
  class TestDecimalField:
      def test_db_type_with_precision(self)
      def test_db_type_no_precision(self)
      def test_validate_too_many_digits(self)
      def test_validate_too_many_decimals(self)
      def test_validate_accepts_valid(self)
  class TestForeignKeyField:
      def test_db_type(self)
      def test_to_python(self)
      def test_to_python_none(self)
      def test_validate_rejects_bad_uuid(self)
      def test_on_delete_default(self)
      def test_on_delete_custom(self)
  class TestEmailField:
      def test_db_type(self)
      def test_validate_accepts_valid(self)
      def test_validate_rejects_invalid(self)
  def _run(coro)


---
Filepath: tests/level1/test_migration_diff_types.py  [python]

  class TestNormalizePgType:
      def test_known_aliases(self, alias, expected)
      def test_already_normalized(self)
      def test_unknown_type(self)
      def test_whitespace_stripped(self)
  class TestOrmTypeToPg:
      def test_direct_mappings(self, orm, expected)
      def test_varchar_with_length(self)
      def test_varchar_no_length(self)
      def test_numeric_with_precision(self)
      def test_serial_to_integer(self)
      def test_bigserial_to_bigint(self)
      def test_unknown_lowered(self)
  class TestOperationToUpSql:
      def test_create_table(self)
      def test_drop_table(self)
      def test_add_column(self)
      def test_drop_column(self)
      def test_alter_column(self)
      def test_add_foreign_key(self)
      def test_drop_foreign_key(self)
      def test_unknown_op_raises(self)
  class TestOperationToDownSql:
      def test_create_table_reverses_to_drop(self)
      def test_drop_table_reverses_to_create(self)
      def test_drop_table_no_columns_comment(self)
      def test_add_column_reverses_to_drop(self)
      def test_drop_column_with_old_col(self)
      def test_alter_column_with_reverse(self)
      def test_add_foreign_key_reverses_to_drop(self)
  class TestOperationWithSchema:
      def test_create_table_with_schema(self)


---
Filepath: tests/level1/test_query_builder.py  [python]

  class TestQueryBuilderChaining:
      def test_filter_adds_to_filters(self)
      def test_multiple_filters(self)
      def test_exclude_adds_to_excludes(self)
      def test_order_by(self)
      def test_limit(self)
      def test_offset(self)
      def test_select(self)
      def test_chaining_returns_self(self)
      def test_empty_filter_ignored(self)
  class TestBuildQuery:
      def test_build_query_basic(self)
      def test_build_query_default_select(self)
      def test_build_query_custom_select(self)
      def test_build_query_order_by(self)
  class TestMergeFiltersExcludes:
      def test_filters_merged(self)
      def test_excludes_prefixed(self)
      def test_combined(self)
  class TestQualifiedTableName:
      def test_uses_qualified_name(self)
  class TestSlicing:
      def test_slice_sets_limit_and_offset(self)
      def test_index_raises(self)
  class TestPrefetchRelated:
      def test_prefetch_related(self)
  class TestDatabaseRequired:
      def test_no_database_raises_at_model_creation(self)
  def _clean_registry()
  def _make_model(name = 'QBModel')


---
Filepath: tests/level1/test_migration_loader.py  [python]

  class TestNameRegex:
      def test_valid_names(self)
      def test_invalid_names(self)
  class TestDiscover:
      def test_discovers_files(self, mig_dir)
      def test_ignores_dunder_files(self, mig_dir)
      def test_empty_dir(self, mig_dir)
      def test_nonexistent_dir(self, tmp_path)
      def test_missing_up_raises(self, mig_dir)
  class TestDependencyValidation:
      def test_missing_dependency_raises(self, mig_dir)
  class TestResolveOrder:
      def test_linear_chain(self, mig_dir)
      def test_diamond_deps(self, mig_dir)
      def test_circular_dependency_raises(self, mig_dir)
  class TestNextNumber:
      def test_first_migration(self, mig_dir)
      def test_after_existing(self, mig_dir)
  class TestChecksum:
      def test_deterministic(self)
      def test_different_content(self)
      def test_sha256_length(self)
  def mig_dir(tmp_path)
  def _write_migration(mig_dir: Path, filename: str, deps: list[str] | None = None, has_down: bool = True)


---
Filepath: tests/level1/test_registry.py  [python]

  class TestModelRegistry:
      def test_register_and_get(self)
      def test_get_nonexistent_returns_none(self)
      def test_all_models(self)
      def test_clear(self)
      def test_duplicate_registration_same_class(self)
      def test_duplicate_registration_different_class_raises(self)
  class TestGetModelByName:
      def test_found(self)
      def test_not_found_raises(self)
  def _clean_registry()
  def _make_model(name)


---
Filepath: tests/level1/test_model_instance.py  [python]

  class TestModelInit:
      def test_init_with_kwargs(self)
      def test_init_defaults(self)
      def test_extra_data(self)
  class TestToDict:
      def test_to_dict_includes_fields(self)
      def test_to_flat_dict(self)
  class TestFromDbResult:
      def test_from_db_result_sets_uuid_field(self)
      def test_from_db_result_extra_columns(self)
  class TestCacheKey:
      def test_single_pk(self)
      def test_composite_pk(self)
  def _clean_registry()
  def _make_model(name, fields_dict)
```
<!-- /AUTO:signatures -->

<!-- AUTO:dependencies -->
## Dependencies

**External packages:** matrx_orm, pytest
<!-- /AUTO:dependencies -->

<!-- AUTO:config -->
## Generation Config

> Auto-managed. Contains the exact parameters used to generate this README.
> Used by parent modules to auto-refresh this file when it is stale.
> Do not edit manually — changes will be overwritten on the next run.

```json
{
  "subdirectory": "tests/level1",
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
