# `tests.level2` — Module Overview

> This document is partially auto-generated. Sections tagged `<!-- AUTO:id -->` are refreshed by the generator.
> Everything else is yours to edit freely and will never be overwritten.

<!-- AUTO:meta -->
## About This Document

This file is **partially auto-generated**. Sections wrapped in `<!-- AUTO:id -->` tags
are overwritten each time the generator runs. Everything else is yours to edit freely.

| Field | Value |
|-------|-------|
| Module | `tests/level2` |
| Last generated | 2026-02-28 13:57 |
| Output file | `tests/level2/MODULE_README.md` |
| Signature mode | `signatures` |

**To refresh auto-sections:**
```bash
python utils/code_context/generate_module_readme.py tests/level2 --mode signatures
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

> Auto-generated. 12 files across 1 directories.

```
tests/level2/
├── MODULE_README.md
├── __init__.py
├── conftest.py
├── test_bulk_ops.py
├── test_cache_integration.py
├── test_crud.py
├── test_foreign_keys.py
├── test_m2m.py
├── test_manager.py
├── test_migrations_live.py
├── test_query_execution.py
├── test_schema_diff.py
# excluded: 1 .md
```
<!-- /AUTO:tree -->

<!-- AUTO:signatures -->
## API Signatures

> Auto-generated via `output_mode="signatures"`. ~5-10% token cost vs full source.
> For full source, open the individual files directly.

```
---
Filepath: tests/level2/__init__.py  [python]



---
Filepath: tests/level2/test_migrations_live.py  [python]

  class TestApplyMigration:
      async def test_apply_creates_table(self, migration_db, tmp_path)
      async def test_apply_idempotent(self, migration_db, tmp_path)
  class TestRollback:
      async def test_rollback_removes_table(self, migration_db, tmp_path)
  class TestMigrationStatus:
      async def test_status_shows_applied(self, migration_db, tmp_path)
  class TestChecksumVerification:
      async def test_checksum_mismatch_detected(self, migration_db, tmp_path)
  def _write_migration(mig_dir: Path, filename: str, up_sql: str, down_sql: str, deps: list[str] | None = None)


---
Filepath: tests/level2/conftest.py  [python]

  DB_PROJECT_NAME = 'matrx_test'
  SEED_SCHEMA_SQL = '\nDROP TABLE IF EXISTS test_post_tag CASCADE;\nDROP TABLE IF EXISTS test_profile CASCADE;\nDROP TABLE IF EXISTS test_po ...
  SEED_USER_IDS = [str(uuid4()) for _ in range(5)]
  SEED_TAG_IDS = [str(uuid4()) for _ in range(3)]
  SEED_POST_IDS = [str(uuid4()) for _ in range(5)]
  SEED_CATEGORY_IDS = [str(uuid4()) for _ in range(3)]
  SEED_PROFILE_IDS = [str(uuid4()) for _ in range(3)]
  SEED_DATA_SQL = f"""\nINSERT INTO test_user (id, username, email, bio, is_active, age) VALUES\n    ('{SEED_USER_IDS[0]}', 'alice', 'alic ...
  CLEANUP_SQL = '\nDROP TABLE IF EXISTS test_post_tag CASCADE;\nDROP TABLE IF EXISTS test_profile CASCADE;\nDROP TABLE IF EXISTS test_po ...
  def _env(key: str, default: str = '') -> str
  def event_loop()
  def db_config()
  def migration_db(db_config)
  def _create_test_models()
  async def seed_database(db_config, migration_db)
  def user_model()
  def post_model()
  def tag_model()
  def category_model()
  def profile_model()
  def user_ids()
  def post_ids()
  def tag_ids()


---
Filepath: tests/level2/test_crud.py  [python]

  class TestCreate:
      async def test_create_instance(self, user_model)
      async def test_create_with_defaults(self, user_model)
  class TestRead:
      async def test_get_by_pk(self, user_model, user_ids)
      async def test_get_nonexistent_raises(self, user_model)
      async def test_get_or_none_found(self, user_model, user_ids)
      async def test_get_or_none_missing(self, user_model)
  class TestUpdate:
      async def test_update_fields(self, user_model)
  class TestDelete:
      async def test_delete(self, user_model)


---
Filepath: tests/level2/test_schema_diff.py  [python]

  class TestCaptureDbState:
      async def test_captures_existing_tables(self, migration_db)
      async def test_captures_columns(self, migration_db)
      async def test_column_properties(self, migration_db)
  class TestComputeDiff:
      async def test_no_diff_for_existing_models(self, migration_db)
      async def test_detects_new_model(self, migration_db)
      async def test_detects_dropped_table(self, migration_db)


---
Filepath: tests/level2/test_query_execution.py  [python]

  class TestFilterAll:
      async def test_filter_by_field(self, user_model)
      async def test_filter_in(self, user_model, user_ids)
      async def test_filter_boolean(self, user_model)
      async def test_filter_isnull(self, user_model)
  class TestExclude:
      async def test_exclude(self, user_model)
  class TestOrderBy:
      async def test_order_by_asc(self, user_model)
      async def test_order_by_desc(self, user_model)
  class TestLimitOffset:
      async def test_limit(self, user_model)
      async def test_limit_offset(self, user_model)
  class TestAggregates:
      async def test_count(self, user_model)
      async def test_exists_true(self, user_model, user_ids)
      async def test_exists_false(self, user_model)
  class TestFirstLast:
      async def test_first(self, user_model)
      async def test_first_empty(self, user_model)
  class TestChainedQueries:
      async def test_complex_chain(self, user_model)


---
Filepath: tests/level2/test_cache_integration.py  [python]

  class TestCacheFill:
      async def test_get_populates_cache(self, user_model, user_ids)
      async def test_second_get_from_cache(self, user_model, user_ids)
  class TestCacheInvalidation:
      async def test_update_invalidates(self, user_model)
      async def test_delete_removes_from_cache(self, user_model)
  class TestClearCache:
      async def test_clear_cache(self, user_model, user_ids)


---
Filepath: tests/level2/test_m2m.py  [python]

  class TestM2MFetch:
      async def test_fetch_m2m(self, post_model, migration_db, post_ids, tag_ids)
  class TestM2MAdd:
      async def test_add_m2m(self, post_model, migration_db, post_ids, tag_ids)
  class TestM2MRemove:
      async def test_remove_m2m(self, post_model, migration_db, post_ids, tag_ids)
  class TestM2MClear:
      async def test_clear_m2m(self, post_model, migration_db, post_ids, tag_ids)
  class TestM2MSet:
      async def test_set_m2m(self, post_model, migration_db, post_ids, tag_ids)
  def _get_m2m_ref(post_model) -> ManyToManyReference | None


---
Filepath: tests/level2/test_bulk_ops.py  [python]

  class TestBulkCreate:
      async def test_bulk_create(self, user_model)
      async def test_bulk_create_empty(self, user_model)
  class TestBulkUpdate:
      async def test_bulk_update_fields(self, user_model)
  class TestBulkDelete:
      async def test_bulk_delete(self, user_model)


---
Filepath: tests/level2/test_foreign_keys.py  [python]

  class TestFetchFK:
      async def test_fetch_fk_returns_parent(self, post_model, user_model, post_ids, user_ids)
      async def test_fetch_fk_caches_related(self, post_model, post_ids)
  class TestFetchIFK:
      async def test_fetch_ifk_returns_children(self, user_model, post_model, user_ids)
      async def test_fetch_ifk_no_children(self, user_model, user_ids)
  class TestSelfReferencingFK:
      async def test_category_parent(self, category_model)
      async def test_root_category_null_parent(self, category_model)


---
Filepath: tests/level2/test_manager.py  [python]

  class TestModelGetAll:
      async def test_get_all_users(self, user_model)
      async def test_get_all_posts(self, post_model)
  class TestModelFilterChain:
      async def test_filter_by_age_range(self, user_model)
      async def test_filter_startswith(self, user_model)
      async def test_filter_contains(self, user_model)
  class TestModelValues:
      async def test_values(self, user_model, user_ids)
      async def test_values_list(self, user_model, user_ids)
  class TestToDict:
      async def test_to_dict(self, user_model, user_ids)
      async def test_to_flat_dict(self, user_model, user_ids)
  class TestJsonField:
      async def test_json_field_read(self, post_model, post_ids)
      async def test_json_field_null(self, post_model, post_ids)
  class TestCreateAndCleanup:
      async def test_full_lifecycle(self, user_model)
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
  "subdirectory": "tests/level2",
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
