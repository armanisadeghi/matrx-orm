# `src.matrx_orm.python_sql` — Module Overview

> This document is partially auto-generated. Sections tagged `<!-- AUTO:id -->` are refreshed by the generator.
> Everything else is yours to edit freely and will never be overwritten.

<!-- AUTO:meta -->
## About This Document

This file is **partially auto-generated**. Sections wrapped in `<!-- AUTO:id -->` tags
are overwritten each time the generator runs. Everything else is yours to edit freely.

| Field | Value |
|-------|-------|
| Module | `src/matrx_orm/python_sql` |
| Last generated | 2026-02-28 13:59 |
| Output file | `src/matrx_orm/python_sql/MODULE_README.md` |
| Signature mode | `signatures` |

**To refresh auto-sections:**
```bash
python utils/code_context/generate_module_readme.py src/matrx_orm/python_sql --mode signatures
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

> Auto-generated. 4 files across 1 directories.

```
src/matrx_orm/python_sql/
├── __init__.py
├── db_objects.py
├── table_detailed_relationships.py
├── table_typescript_relationship.py
```
<!-- /AUTO:tree -->

<!-- AUTO:signatures -->
## API Signatures

> Auto-generated via `output_mode="signatures"`. ~5-10% token cost vs full source.
> For full source, open the individual files directly.

```
---
Filepath: src/matrx_orm/python_sql/__init__.py  [python]



---
Filepath: src/matrx_orm/python_sql/table_typescript_relationship.py  [python]

  def transform_relationships_for_typescript(relationships_data, junction_analysis)
  def get_ts_object(schema = 'public', database_project = None, additional_schemas = None)


---
Filepath: src/matrx_orm/python_sql/table_detailed_relationships.py  [python]

  def get_table_relationships(schema, database_project)
  def analyze_junction_tables(schema, database_project, additional_schemas = None)
  def analyze_relationships(results)
  def analyze_many_to_many_relationships(all_relationships_list)


---
Filepath: src/matrx_orm/python_sql/db_objects.py  [python]

  def get_full_db_objects(schema, database_project)
  def get_db_objects(schema, database_project)
  def map_datatypes_to_components(datatypes)
  def extract_unique_values_and_counts(db_objects_tuple, fields = '*')
```
<!-- /AUTO:signatures -->

<!-- AUTO:call_graph -->
## Call Graph

> Auto-generated. All Python files
> Excluded from call graph: `tests`.
> Shows which functions call which. `async` prefix = caller is an async function.
> Method calls shown as `receiver.method()`. Private methods (`_`) excluded by default.

### Call graph: src.matrx_orm.python_sql.table_typescript_relationship

```
src.matrx_orm.python_sql.table_typescript_relationship.transform_relationships_for_typescript → items() (line 34)
  src.matrx_orm.python_sql.table_typescript_relationship.transform_relationships_for_typescript → junction_analysis.items() (line 56)
  src.matrx_orm.python_sql.table_typescript_relationship.transform_relationships_for_typescript → append(relationship) (line 81)
  src.matrx_orm.python_sql.table_typescript_relationship.transform_relationships_for_typescript → items() (line 85)
  src.matrx_orm.python_sql.table_typescript_relationship.transform_relationships_for_typescript → append(relationship) (line 105)
  src.matrx_orm.python_sql.table_typescript_relationship.get_ts_object → src.matrx_orm.python_sql.table_typescript_relationship.get_table_relationships() (line 115)
  src.matrx_orm.python_sql.table_typescript_relationship.get_ts_object → src.matrx_orm.python_sql.table_typescript_relationship.analyze_junction_tables() (line 116)
  src.matrx_orm.python_sql.table_typescript_relationship.get_ts_object → src.matrx_orm.python_sql.table_typescript_relationship.analyze_relationships(relationships) (line 121)
  src.matrx_orm.python_sql.table_typescript_relationship.get_ts_object → src.matrx_orm.python_sql.table_typescript_relationship.transform_relationships_for_typescript(relationships, junction_analysis) (line 124)
  Global Scope → src.matrx_orm.python_sql.table_typescript_relationship.get_table_relationships() (line 138)
  Global Scope → src.matrx_orm.python_sql.table_typescript_relationship.analyze_junction_tables() (line 141)
  Global Scope → src.matrx_orm.python_sql.table_typescript_relationship.transform_relationships_for_typescript(relationships, junction_analysis) (line 148)
  Global Scope → src.matrx_orm.python_sql.table_typescript_relationship.analyze_relationships(relationships) (line 150)
```

### Call graph: src.matrx_orm.python_sql.table_detailed_relationships

```
src.matrx_orm.python_sql.table_detailed_relationships.get_table_relationships → src.matrx_orm.python_sql.table_detailed_relationships.execute_sql_query(query, (schema, schema), database_project) (line 118)
  src.matrx_orm.python_sql.table_detailed_relationships.analyze_junction_tables → schemas.extend(additional_schemas) (line 128)
  src.matrx_orm.python_sql.table_detailed_relationships.analyze_junction_tables → src.matrx_orm.python_sql.table_detailed_relationships.execute_sql_query(query, (schemas, schemas, schemas, schemas), database_project) (line 274)
  src.matrx_orm.python_sql.table_detailed_relationships.analyze_junction_tables → split(',') (line 286)
  src.matrx_orm.python_sql.table_detailed_relationships.analyze_junction_tables → additional_fields.strip('{}') (line 286)
  src.matrx_orm.python_sql.table_detailed_relationships.analyze_junction_tables → split(',') (line 293)
  src.matrx_orm.python_sql.table_detailed_relationships.analyze_junction_tables → primary_keys.strip('{}') (line 293)
  src.matrx_orm.python_sql.table_detailed_relationships.analyze_junction_tables → key.strip() (line 294)
  src.matrx_orm.python_sql.table_detailed_relationships.analyze_junction_tables → key.strip() (line 294)
  src.matrx_orm.python_sql.table_detailed_relationships.analyze_junction_tables → relationship.copy() (line 307)
  src.matrx_orm.python_sql.table_detailed_relationships.analyze_junction_tables → all_relationships.append(relationship_with_fields) (line 309)
  src.matrx_orm.python_sql.table_detailed_relationships.analyze_relationships → items() (line 350)
  src.matrx_orm.python_sql.table_detailed_relationships.analyze_relationships → append(related_table) (line 353)
  src.matrx_orm.python_sql.table_detailed_relationships.analyze_relationships → add(f'{table_name} → {related_table}') (line 354)
  src.matrx_orm.python_sql.table_detailed_relationships.analyze_relationships → keys() (line 358)
  src.matrx_orm.python_sql.table_detailed_relationships.analyze_relationships → append(related_table) (line 359)
  src.matrx_orm.python_sql.table_detailed_relationships.analyze_relationships → add(f'{related_table} → {table_name}') (line 360)
  src.matrx_orm.python_sql.table_detailed_relationships.analyze_relationships → relationship_types.items() (line 368)
  src.matrx_orm.python_sql.table_detailed_relationships.analyze_relationships → rel_type.upper() (line 370)
  src.matrx_orm.python_sql.table_detailed_relationships.analyze_relationships → summary.items() (line 376)
  src.matrx_orm.python_sql.table_detailed_relationships.analyze_relationships → rels.items() (line 378)
  src.matrx_orm.python_sql.table_detailed_relationships.analyze_many_to_many_relationships → joined_relationships.items() (line 419)
  src.matrx_orm.python_sql.table_detailed_relationships.analyze_many_to_many_relationships → final_relationships.append(final_rel) (line 432)
  Global Scope → src.matrx_orm.python_sql.table_detailed_relationships.get_table_relationships() (line 448)
  Global Scope → src.matrx_orm.python_sql.table_detailed_relationships.analyze_junction_tables() (line 449)
  Global Scope → src.matrx_orm.python_sql.table_detailed_relationships.analyze_relationships(relationships) (line 464)
  Global Scope → src.matrx_orm.python_sql.table_detailed_relationships.analyze_many_to_many_relationships(all_relationships_list) (line 489)
```

### Call graph: src.matrx_orm.python_sql.db_objects

```
src.matrx_orm.python_sql.db_objects.get_full_db_objects → src.matrx_orm.python_sql.db_objects.execute_sql_query(query, (schema,), database_project) (line 172)
  src.matrx_orm.python_sql.db_objects.get_db_objects → src.matrx_orm.python_sql.db_objects.get_full_db_objects(schema, database_project) (line 192)
  src.matrx_orm.python_sql.db_objects.get_db_objects → src.matrx_orm.python_sql.db_objects.get_database_config(database_project) (line 200)
  src.matrx_orm.python_sql.db_objects.get_db_objects → _cfg.get('additional_schemas', []) (line 201)
  src.matrx_orm.python_sql.db_objects.get_db_objects → src.matrx_orm.python_sql.db_objects.get_ts_object(schema, database_project) (line 204)
  src.matrx_orm.python_sql.db_objects.get_db_objects → column.get('enum_labels') (line 241)
  src.matrx_orm.python_sql.db_objects.get_db_objects → column.get('base_type') (line 242)
  src.matrx_orm.python_sql.db_objects.get_db_objects → all_enum_base_types.add(base_type) (line 246)
  src.matrx_orm.python_sql.db_objects.get_db_objects → obj.get('name') (line 249)
  src.matrx_orm.python_sql.db_objects.get_db_objects → obj.items() (line 255)
  src.matrx_orm.python_sql.db_objects.get_db_objects → processed_objects.append(processed_obj) (line 260)
  src.matrx_orm.python_sql.db_objects.map_datatypes_to_components → datatypes.items() (line 302)
  src.matrx_orm.python_sql.db_objects.extract_unique_values_and_counts → obj.get('table_columns') (line 331)
  src.matrx_orm.python_sql.db_objects.extract_unique_values_and_counts → column.items() (line 335)
  src.matrx_orm.python_sql.db_objects.extract_unique_values_and_counts → unique_values_count.items() (line 351)
  Global Scope → src.matrx_orm.python_sql.db_objects.get_db_objects() (line 389)
```
<!-- /AUTO:call_graph -->

<!-- AUTO:dependencies -->
## Dependencies

**External packages:** matrx_orm, matrx_utils
<!-- /AUTO:dependencies -->

<!-- AUTO:config -->
## Generation Config

> Auto-managed. Contains the exact parameters used to generate this README.
> Used by parent modules to auto-refresh this file when it is stale.
> Do not edit manually — changes will be overwritten on the next run.

```json
{
  "subdirectory": "src/matrx_orm/python_sql",
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
