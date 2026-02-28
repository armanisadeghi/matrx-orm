# `src.matrx_orm.migrations` — Module Overview

> This document is partially auto-generated. Sections tagged `<!-- AUTO:id -->` are refreshed by the generator.
> Everything else is yours to edit freely and will never be overwritten.

<!-- AUTO:meta -->
## About This Document

This file is **partially auto-generated**. Sections wrapped in `<!-- AUTO:id -->` tags
are overwritten each time the generator runs. Everything else is yours to edit freely.

| Field | Value |
|-------|-------|
| Module | `src/matrx_orm/migrations` |
| Last generated | 2026-02-28 13:57 |
| Output file | `src/matrx_orm/migrations/MODULE_README.md` |
| Signature mode | `signatures` |

**To refresh auto-sections:**
```bash
python utils/code_context/generate_module_readme.py src/matrx_orm/migrations --mode signatures
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

> Auto-generated. 11 files across 1 directories.

```
src/matrx_orm/migrations/
├── MODULE_README.md
├── __init__.py
├── cli.py
├── ddl.py
├── diff.py
├── executor.py
├── integration.py
├── loader.py
├── operations.py
├── state.py
├── table_filter.py
# excluded: 1 .md
```
<!-- /AUTO:tree -->

<!-- AUTO:signatures -->
## API Signatures

> Auto-generated via `output_mode="signatures"`. ~5-10% token cost vs full source.
> For full source, open the individual files directly.

```
---
Filepath: src/matrx_orm/migrations/integration.py  [python]

  async def migrate_and_rebuild(database: str, migrations_dir: str | Path = 'migrations', schema: str = 'public', database_project: str | None = None, additional_schemas: list[str] | None = None) -> dict[str, list[str] | dict[str, object] | None]
  def rebuild_schema(schema: str = 'public', database_project: str = 'default', additional_schemas: list[str] | None = None) -> dict[str, object]


---
Filepath: src/matrx_orm/migrations/__init__.py  [python]



---
Filepath: src/matrx_orm/migrations/state.py  [python]

  TRACKING_TABLE = '_matrx_migrations'
  CREATE_TRACKING_TABLE_SQL = f'\nCREATE TABLE IF NOT EXISTS {TRACKING_TABLE} (\n    id SERIAL PRIMARY KEY,\n    name VARCHAR(255) NOT NULL UNIQUE,\n ...
  class AppliedMigration:
  class MigrationState:
      def __init__(self, db: MigrationDB) -> None
      async def ensure_table(self) -> None
      async def applied_migrations(self) -> list[AppliedMigration]
      async def applied_names(self) -> set[str]
      async def record_migration(self, name: str, checksum: str) -> None
      async def unrecord_migration(self, name: str) -> None
      async def verify_checksums(self, file_checksums: dict[str, str]) -> list[str]
      def compute_checksum(source: str) -> str


---
Filepath: src/matrx_orm/migrations/ddl.py  [python]

  class ColumnDef:
      def to_sql(self) -> str
  class ForeignKeyDef:
  class IndexDef:
  class ConstraintDef:
  class AlterColumnChanges:
  class DDLGenerator:
      def create_table(name: str, columns: list[ColumnDef], constraints: list[ConstraintDef] | None = None, schema: str | None = None) -> str
      def drop_table(name: str, schema: str | None = None, cascade: bool = False) -> str
      def add_column(table: str, column: ColumnDef, schema: str | None = None) -> str
      def drop_column(table: str, column: str, schema: str | None = None) -> str
      def alter_column(table: str, column: str, changes: AlterColumnChanges, schema: str | None = None) -> list[str]
      def add_index(index: IndexDef) -> str
      def drop_index(name: str) -> str
      def add_constraint(table: str, constraint: ConstraintDef, schema: str | None = None) -> str
      def drop_constraint(table: str, name: str, schema: str | None = None) -> str
      def add_foreign_key(table: str, fk: ForeignKeyDef, column: str, schema: str | None = None) -> str
      def drop_foreign_key(table: str, constraint_name: str, schema: str | None = None) -> str
      def rename_table(old_name: str, new_name: str, schema: str | None = None) -> str


---
Filepath: src/matrx_orm/migrations/executor.py  [python]

  class MigrationExecutor:
      def __init__(self, db: MigrationDB, loader: MigrationLoader) -> None
      async def migrate(self) -> list[str]
      async def rollback(self, steps: int = 1) -> list[str]


---
Filepath: src/matrx_orm/migrations/table_filter.py  [python]

  class TableFilter:
      def __post_init__(self) -> None
      def is_included(self, table_name: str) -> bool
      def apply(self, tables: dict[str, object]) -> dict[str, object]
      def warn_cross_references(self, included_tables: dict) -> None


---
Filepath: src/matrx_orm/migrations/operations.py  [python]

  class MigrationDB:
      def __init__(self, config_name: str) -> None
      async def execute(self, sql: str, *args: Any, timeout: float = 30.0) -> list[dict]
      async def execute_many(self, statements: list[str], timeout: float = 30.0) -> None
      async def fetch(self, sql: str, *args: Any, timeout: float = 30.0) -> list[dict]
      async def fetch_one(self, sql: str, *args: Any, timeout: float = 30.0) -> dict | None
      async def fetch_val(self, sql: str, *args: Any, timeout: float = 30.0) -> Any


---
Filepath: src/matrx_orm/migrations/loader.py  [python]

  class MigrationFile:
  class MigrationLoader:
      def __init__(self, migrations_dir: str | Path) -> None
      def discover(self) -> dict[str, MigrationFile]
      def migrations(self) -> dict[str, MigrationFile]
      def resolve_order(self) -> list[str]
      def next_number(self) -> int
      def _load_module(self, filepath: Path, name: str) -> Any
      def _validate_graph(self) -> None
  def visit(name: str) -> None


---
Filepath: src/matrx_orm/migrations/diff.py  [python]

  INTROSPECT_TABLES_SQL = "\nSELECT\n    c.relname AS table_name,\n    n.nspname AS schema_name\nFROM pg_class c\nJOIN pg_namespace n ON n.oid = c ...
  INTROSPECT_COLUMNS_SQL = "\nSELECT\n    a.attname AS column_name,\n    pg_catalog.format_type(a.atttypid, a.atttypmod) AS full_type,\n    NOT a.a ...
  class TableColumnState:
  class TableState:
  class Operation:
      def to_up_sql(self) -> list[str]
      def to_down_sql(self) -> list[str]
  class SchemaDiff:
      def __init__(self, db: MigrationDB, schema: str = 'public', table_filter: TableFilter | None = None) -> None
      def capture_model_state(self) -> dict[str, TableState]
      async def capture_db_state(self) -> dict[str, TableState]
      async def compute_diff(self) -> list[Operation]
      async def generate_migration_file(self, migrations_dir: str | Path, name: str | None = None, number: int | None = None) -> Path | None
      def _auto_name(ops: list[Operation]) -> str
      def _describe_ops(ops: list[Operation]) -> str
  def _normalize_pg_type(raw: str) -> str
  def _orm_type_to_pg(orm_type: str) -> str


---
Filepath: src/matrx_orm/migrations/cli.py  [python]

  def _out(msg: str, stream: TextIO = sys.stdout) -> None
  async def makemigrations(database: str, migrations_dir: str | Path = 'migrations', name: str | None = None, schema: str = 'public', include_tables: set[str] | None = None, exclude_tables: set[str] | None = None) -> Path | None
  async def migrate(database: str, migrations_dir: str | Path = 'migrations') -> list[str]
  async def rollback(database: str, migrations_dir: str | Path = 'migrations', steps: int = 1) -> list[str]
  async def status(database: str, migrations_dir: str | Path = 'migrations') -> dict[str, str]
  async def create_empty(database: str, migrations_dir: str | Path = 'migrations', name: str = 'custom') -> Path
  async def migrate_rebuild(database: str, migrations_dir: str | Path = 'migrations', schema: str = 'public', database_project: str | None = None) -> dict[str, list[str] | dict[str, object] | None]
  def _build_parser() -> argparse.ArgumentParser
  def main(argv: list[str] | None = None) -> None
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
  "subdirectory": "src/matrx_orm/migrations",
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
