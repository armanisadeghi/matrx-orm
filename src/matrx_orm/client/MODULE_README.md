# `src.matrx_orm.client` — Module Overview

> This document is partially auto-generated. Sections tagged `<!-- AUTO:id -->` are refreshed by the generator.
> Everything else is yours to edit freely and will never be overwritten.

<!-- AUTO:meta -->
## About This Document

This file is **partially auto-generated**. Sections wrapped in `<!-- AUTO:id -->` tags
are overwritten each time the generator runs. Everything else is yours to edit freely.

| Field | Value |
|-------|-------|
| Module | `src/matrx_orm/client` |
| Last generated | 2026-02-28 14:00 |
| Output file | `src/matrx_orm/client/MODULE_README.md` |
| Signature mode | `signatures` |

**To refresh auto-sections:**
```bash
python utils/code_context/generate_module_readme.py src/matrx_orm/client --mode signatures
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

> Auto-generated. 2 files across 1 directories.

```
src/matrx_orm/client/
├── __init__.py
├── postgres_connection.py
```
<!-- /AUTO:tree -->

<!-- AUTO:signatures -->
## API Signatures

> Auto-generated via `output_mode="signatures"`. ~5-10% token cost vs full source.
> For full source, open the individual files directly.

```
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
```
<!-- /AUTO:signatures -->

<!-- AUTO:call_graph -->
## Call Graph

> Auto-generated. All Python files
> Excluded from call graph: `tests`.
> Shows which functions call which. `async` prefix = caller is an async function.
> Method calls shown as `receiver.method()`. Private methods (`_`) excluded by default.

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
<!-- /AUTO:call_graph -->

<!-- AUTO:dependencies -->
## Dependencies

**External packages:** matrx_orm, matrx_utils, psycopg, psycopg_pool
<!-- /AUTO:dependencies -->

<!-- AUTO:config -->
## Generation Config

> Auto-managed. Contains the exact parameters used to generate this README.
> Used by parent modules to auto-refresh this file when it is stale.
> Do not edit manually — changes will be overwritten on the next run.

```json
{
  "subdirectory": "src/matrx_orm/client",
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
