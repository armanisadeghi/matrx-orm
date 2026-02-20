# Matrx ORM Migration System

A bidirectional PostgreSQL migration system that adds the push direction to the ORM.

## Overview

- **Write path:** Python Models or SQL --> Migration Files --> PostgreSQL DB
- **Read path:** PostgreSQL DB --> Schema Builder --> Python Models + Managers

Works with any PostgreSQL database: Supabase, AWS RDS, Google Cloud SQL, self-hosted, Docker.

## Quick Start

1. Create an empty migration: `create_empty(database, migrations_dir, name)`
2. Write your migration with `async def up(db)` and `async def down(db)`
3. Apply migrations: `migrate(database, migrations_dir)`
4. Regenerate models: `migrate_and_rebuild(database, migrations_dir, database_project)`

## CLI

```
matrx-orm makemigrations --database my_db --dir migrations --schema public
matrx-orm migrate --database my_db --dir migrations
matrx-orm rollback --database my_db --dir migrations --steps 1
matrx-orm status --database my_db --dir migrations
matrx-orm create_empty --database my_db --dir migrations --name my_migration
matrx-orm migrate_rebuild --database my_db --dir migrations --schema public
```

## Programmatic API

```
makemigrations    - Auto-detect changes, generate migration file
migrate           - Apply pending migrations
rollback          - Roll back N migrations
status            - Show applied/pending status
create_empty      - Create empty migration file
migrate_and_rebuild - Apply + regenerate models
```

## Migration File Format

Files named NNNN_description.py in migrations/ directory.
Each has: docstring, dependencies list, async def up(db), async def down(db).

### The db object

- db.execute(sql, *args) - Execute SQL, return list of row dicts
- db.execute_many(statements) - Execute multiple SQL statements
- db.fetch(sql, *args) - Alias for execute
- db.fetch_one(sql, *args) - Return first row or None
- db.fetch_val(sql, *args) - Return first column of first row

## Auto-Generated Migrations (makemigrations)

Diffs ORM models vs live DB. Detects: new/dropped tables, added/dropped columns,
type changes, nullability changes, FK additions/removals.
Generates both up() and down() for automatic rollback.

## State Tracking

_matrx_migrations table auto-created. SHA-256 checksums detect post-apply modifications.

## DDL Generator

DDLGenerator provides: create_table, drop_table, add_column, drop_column, alter_column,
add_index, drop_index, add_foreign_key, drop_foreign_key, add_constraint, drop_constraint,
rename_table.

## Schema Builder Integration

migrate_and_rebuild() applies migrations then regenerates models.
rebuild_schema() regenerates models without migrating.

## Module Structure

- operations.py - MigrationDB wrapper
- state.py - _matrx_migrations tracking table
- loader.py - File discovery, dependency graph
- executor.py - Apply and rollback logic
- ddl.py - DDL SQL generation
- diff.py - Schema diff engine
- cli.py - CLI entry points
- integration.py - Schema builder integration
