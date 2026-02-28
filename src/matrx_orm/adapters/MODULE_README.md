# `src.matrx_orm.adapters` — Module Overview

> This document is partially auto-generated. Sections tagged `<!-- AUTO:id -->` are refreshed by the generator.
> Everything else is yours to edit freely and will never be overwritten.

<!-- AUTO:meta -->
## About This Document

This file is **partially auto-generated**. Sections wrapped in `<!-- AUTO:id -->` tags
are overwritten each time the generator runs. Everything else is yours to edit freely.

| Field | Value |
|-------|-------|
| Module | `src/matrx_orm/adapters` |
| Last generated | 2026-02-28 13:59 |
| Output file | `src/matrx_orm/adapters/MODULE_README.md` |
| Signature mode | `signatures` |

**To refresh auto-sections:**
```bash
python utils/code_context/generate_module_readme.py src/matrx_orm/adapters --mode signatures
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

> Auto-generated. 3 files across 1 directories.

```
src/matrx_orm/adapters/
├── __init__.py
├── base_adapter.py
├── postgresql.py
```
<!-- /AUTO:tree -->

<!-- AUTO:signatures -->
## API Signatures

> Auto-generated via `output_mode="signatures"`. ~5-10% token cost vs full source.
> For full source, open the individual files directly.

```
---
Filepath: src/matrx_orm/adapters/__init__.py  [python]



---
Filepath: src/matrx_orm/adapters/postgresql.py  [python]

  class PostgreSQLAdapter(BaseAdapter):
      def __init__(self)
      async def _get_connection(self)
      async def execute_query(self, query: Dict[str, Any]) -> List[Dict[str, Any]]
      async def count(self, query: Dict[str, Any]) -> int
      async def exists(self, query: Dict[str, Any]) -> bool
      async def insert(self, query: Dict[str, Any]) -> Dict[str, Any]
      async def bulk_insert(self, query: Dict[str, Any]) -> List[Dict[str, Any]]
      async def update(self, query: Dict[str, Any], data: Dict[str, Any]) -> int
      async def bulk_update(self, query: Dict[str, Any]) -> int
      async def delete(self, query: Dict[str, Any]) -> int
      async def raw_sql(self, sql: str, params: List[Any] = None) -> Union[List[Dict[str, Any]], int]
      async def close(self)
      async def transaction(self)
      async def savepoint(self, name: str)
      async def rollback_to_savepoint(self, name: str)
      async def release_savepoint(self, name: str)
      def _build_sql(self, query: Dict[str, Any]) -> Tuple[str, List[Any]]
      def _build_count_sql(self, query: Dict[str, Any]) -> Tuple[str, List[Any]]
      def _build_exists_sql(self, query: Dict[str, Any]) -> Tuple[str, List[Any]]
      def _build_insert_sql(self, query: Dict[str, Any]) -> Tuple[str, List[Any]]
      def _build_bulk_insert_sql(self, query: Dict[str, Any]) -> Tuple[str, List[Any]]
      def _build_update_sql(self, query: Dict[str, Any], data: Dict[str, Any]) -> Tuple[str, List[Any]]
      def _build_bulk_update_sql(self, query: Dict[str, Any]) -> Tuple[str, List[Any]]
      def _build_delete_sql(self, query: Dict[str, Any]) -> Tuple[str, List[Any]]


---
Filepath: src/matrx_orm/adapters/base_adapter.py  [python]

  class BaseAdapter(ABC):
      async def execute_query(self, query: Dict[str, Any]) -> List[Dict[str, Any]]
      async def fetch(self, query: Dict[str, Any]) -> Optional[Dict[str, Any]]
      async def fetch_by_id(self, model: Any, record_id: Union[str, int]) -> Optional[Dict[str, Any]]
      async def count(self, query: Dict[str, Any]) -> int
      async def exists(self, query: Dict[str, Any]) -> bool
      async def insert(self, query: Dict[str, Any]) -> Dict[str, Any]
      async def bulk_insert(self, query: Dict[str, Any]) -> List[Dict[str, Any]]
      async def update(self, query: Dict[str, Any], data: Dict[str, Any]) -> int
      async def bulk_update(self, query: Dict[str, Any]) -> int
      async def delete(self, query: Dict[str, Any]) -> int
      async def raw_sql(self, sql: str, params: List[Any] = None) -> Union[List[Dict[str, Any]], int]
      async def transaction(self)
      async def close(self)
      async def __aenter__(self)
      async def __aexit__(self, exc_type: Optional[Type[BaseException]], exc_val: Optional[BaseException], exc_tb: Optional[TracebackType])
```
<!-- /AUTO:signatures -->

<!-- AUTO:call_graph -->
## Call Graph

> Auto-generated. All Python files
> Excluded from call graph: `tests`.
> Shows which functions call which. `async` prefix = caller is an async function.
> Method calls shown as `receiver.method()`. Private methods (`_`) excluded by default.

### Call graph: src.matrx_orm.adapters.postgresql

```
src.matrx_orm.adapters.postgresql.__init__ → src.matrx_orm.adapters.postgresql.get_database_config() (line 10)
  async src.matrx_orm.adapters.postgresql._get_connection → ...is_closed() (line 16)
  async src.matrx_orm.adapters.postgresql._get_connection → asyncpg.connect() (line 17)
  async src.matrx_orm.adapters.postgresql.execute_query → connection.fetch(sql, *params) (line 29)
  async src.matrx_orm.adapters.postgresql.count → connection.fetchrow(sql, *params) (line 35)
  async src.matrx_orm.adapters.postgresql.exists → connection.fetchrow(sql, *params) (line 41)
  async src.matrx_orm.adapters.postgresql.insert → connection.fetchrow(sql, *params) (line 47)
  async src.matrx_orm.adapters.postgresql.bulk_insert → connection.executemany(sql, params) (line 53)
  async src.matrx_orm.adapters.postgresql.bulk_insert → connection.fetch(sql, *params) (line 54)
  async src.matrx_orm.adapters.postgresql.update → connection.execute(sql, *params) (line 59)
  async src.matrx_orm.adapters.postgresql.bulk_update → connection.executemany(sql, params) (line 65)
  async src.matrx_orm.adapters.postgresql.delete → connection.execute(sql, *params) (line 71)
  async src.matrx_orm.adapters.postgresql.raw_sql → startswith('SELECT') (line 76)
  async src.matrx_orm.adapters.postgresql.raw_sql → upper() (line 76)
  async src.matrx_orm.adapters.postgresql.raw_sql → sql.strip() (line 76)
  async src.matrx_orm.adapters.postgresql.raw_sql → connection.fetch(sql, *params) (line 77)
  async src.matrx_orm.adapters.postgresql.raw_sql → connection.execute(sql, *params) (line 80)
  async src.matrx_orm.adapters.postgresql.close → ...is_closed() (line 83)
  async src.matrx_orm.adapters.postgresql.close → ...close() (line 84)
  async src.matrx_orm.adapters.postgresql.transaction → connection.transaction() (line 88)
  async src.matrx_orm.adapters.postgresql.savepoint → connection.execute(f'SAVEPOINT {name}') (line 93)
  async src.matrx_orm.adapters.postgresql.rollback_to_savepoint → connection.execute(f'ROLLBACK TO SAVEPOINT {name}') (line 97)
  async src.matrx_orm.adapters.postgresql.release_savepoint → connection.execute(f'RELEASE SAVEPOINT {name}') (line 101)
  src.matrx_orm.adapters.postgresql._build_sql → items() (line 108)
  src.matrx_orm.adapters.postgresql._build_sql → filters.append(f'{field} = ${len(params) + 1}') (line 109)
  src.matrx_orm.adapters.postgresql._build_sql → params.append(value) (line 110)
  src.matrx_orm.adapters.postgresql._build_sql → join(filters) (line 111)
  src.matrx_orm.adapters.postgresql._build_count_sql → items() (line 118)
  src.matrx_orm.adapters.postgresql._build_count_sql → filters.append(f'{field} = ${len(params) + 1}') (line 119)
  src.matrx_orm.adapters.postgresql._build_count_sql → params.append(value) (line 120)
  src.matrx_orm.adapters.postgresql._build_count_sql → join(filters) (line 121)
  src.matrx_orm.adapters.postgresql._build_exists_sql → items() (line 128)
  src.matrx_orm.adapters.postgresql._build_exists_sql → filters.append(f'{field} = ${len(params) + 1}') (line 129)
  src.matrx_orm.adapters.postgresql._build_exists_sql → params.append(value) (line 130)
  src.matrx_orm.adapters.postgresql._build_exists_sql → join(filters) (line 131)
  src.matrx_orm.adapters.postgresql._build_insert_sql → join(query['data'].keys()) (line 135)
  src.matrx_orm.adapters.postgresql._build_insert_sql → keys() (line 135)
  src.matrx_orm.adapters.postgresql._build_insert_sql → join([f'${i + 1}' for i in range(len(query['data']))]) (line 136)
  src.matrx_orm.adapters.postgresql._build_insert_sql → values() (line 138)
  src.matrx_orm.adapters.postgresql._build_bulk_insert_sql → join(query['data'][0].keys()) (line 142)
  src.matrx_orm.adapters.postgresql._build_bulk_insert_sql → keys() (line 142)
  src.matrx_orm.adapters.postgresql._build_bulk_insert_sql → join([f'${i + 1}' for i in range(len(query['data'][0]))]) (line 143)
  src.matrx_orm.adapters.postgresql._build_bulk_insert_sql → row.values() (line 145)
  src.matrx_orm.adapters.postgresql._build_update_sql → join([f'{key} = ${i + 1}' for i, key in enumerate(data.keys())]) (line 149)
  src.matrx_orm.adapters.postgresql._build_update_sql → data.keys() (line 149)
  src.matrx_orm.adapters.postgresql._build_update_sql → data.values() (line 152)
  src.matrx_orm.adapters.postgresql._build_update_sql → items() (line 153)
  src.matrx_orm.adapters.postgresql._build_update_sql → filters.append(f'{field} = ${len(params) + 1}') (line 154)
  src.matrx_orm.adapters.postgresql._build_update_sql → params.append(value) (line 155)
  src.matrx_orm.adapters.postgresql._build_update_sql → join(filters) (line 156)
  src.matrx_orm.adapters.postgresql._build_delete_sql → items() (line 167)
  src.matrx_orm.adapters.postgresql._build_delete_sql → filters.append(f'{field} = ${len(params) + 1}') (line 168)
  src.matrx_orm.adapters.postgresql._build_delete_sql → params.append(value) (line 169)
  src.matrx_orm.adapters.postgresql._build_delete_sql → join(filters) (line 170)
```

### Call graph: src.matrx_orm.adapters.base_adapter

```
async src.matrx_orm.adapters.base_adapter.__aexit__ → self.close() (line 69)
```
<!-- /AUTO:call_graph -->

<!-- AUTO:dependencies -->
## Dependencies

**External packages:** asyncpg, matrx_orm, matrx_utils
<!-- /AUTO:dependencies -->

<!-- AUTO:config -->
## Generation Config

> Auto-managed. Contains the exact parameters used to generate this README.
> Used by parent modules to auto-refresh this file when it is stale.
> Do not edit manually — changes will be overwritten on the next run.

```json
{
  "subdirectory": "src/matrx_orm/adapters",
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
