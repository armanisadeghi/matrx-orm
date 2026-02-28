# `src.matrx_orm.sql_executor` — Module Overview

> This document is partially auto-generated. Sections tagged `<!-- AUTO:id -->` are refreshed by the generator.
> Everything else is yours to edit freely and will never be overwritten.

<!-- AUTO:meta -->
## About This Document

This file is **partially auto-generated**. Sections wrapped in `<!-- AUTO:id -->` tags
are overwritten each time the generator runs. Everything else is yours to edit freely.

| Field | Value |
|-------|-------|
| Module | `src/matrx_orm/sql_executor` |
| Last generated | 2026-02-28 13:57 |
| Output file | `src/matrx_orm/sql_executor/MODULE_README.md` |
| Signature mode | `signatures` |

**To refresh auto-sections:**
```bash
python utils/code_context/generate_module_readme.py src/matrx_orm/sql_executor --mode signatures
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

> Auto-generated. 7 files across 1 directories.

```
src/matrx_orm/sql_executor/
├── MODULE_README.md
├── __init__.py
├── executor.py
├── queries.py
├── registry.py
├── types.py
├── utils.py
# excluded: 1 .md
```
<!-- /AUTO:tree -->

<!-- AUTO:signatures -->
## API Signatures

> Auto-generated via `output_mode="signatures"`. ~5-10% token cost vs full source.
> For full source, open the individual files directly.

```
---
Filepath: src/matrx_orm/sql_executor/__init__.py  [python]



---
Filepath: src/matrx_orm/sql_executor/utils.py  [python]

  def list_available_queries()
  def get_query_details(query_name: str)
  def generate_documentation()
  def display_help()


---
Filepath: src/matrx_orm/sql_executor/executor.py  [python]

  def validate_params(query_name: str, params: dict[str, Any])
  def execute_query(query_name: str, params: dict[str, Any] | None = None, batch_params: list[dict[str, Any]] | None = None, batch_size: int = 50)
  def execute_standard_query(query_name: str, params: dict[str, Any] | None = None)
  def execute_transaction_query(query_name: str, params: dict[str, Any] | None = None)
  def execute_batch_query(query_name: str, batch_params: list[dict[str, Any]], batch_size: int = 50)


---
Filepath: src/matrx_orm/sql_executor/registry.py  [python]

  class QueryRegistry:
      def __init__(self)
      def register(self, name: str, query: SQLQuery) -> None
      def get(self, name: str) -> Optional[SQLQuery]
      def exists(self, name: str) -> bool
      def list_names(self) -> List[str]
      def get_all(self) -> Dict[str, SQLQuery]
      def clear(self) -> None
      def unregister(self, name: str) -> bool
  def get_registry() -> QueryRegistry
  def register_query(name: str, query: SQLQuery) -> None


---
Filepath: src/matrx_orm/sql_executor/types.py  [python]

  class QueryParam(TypedDict):
  class SQLQuery(TypedDict):


---
Filepath: src/matrx_orm/sql_executor/queries.py  [python]

  class QueryParam(TypedDict):
  class SQLQuery(TypedDict):
  def register_query(name: str, query: SQLQuery) -> None
```
<!-- /AUTO:signatures -->

<!-- AUTO:dependencies -->
## Dependencies

**External packages:** matrx_orm
<!-- /AUTO:dependencies -->

<!-- AUTO:config -->
## Generation Config

> Auto-managed. Contains the exact parameters used to generate this README.
> Used by parent modules to auto-refresh this file when it is stale.
> Do not edit manually — changes will be overwritten on the next run.

```json
{
  "subdirectory": "src/matrx_orm/sql_executor",
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
