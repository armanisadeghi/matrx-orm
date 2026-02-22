# CLAUDE.md -- Matrx ORM Project Instructions

> Project-specific instructions for AI assistants working on this codebase.
> Current version: **2.0.0**

---

## Project Overview

**Async-first PostgreSQL ORM built for teams who live in their database UI as much as their IDE.**

---

## What Makes This Different

### 1. Reverse Migrations (Schema → Code)
The flagship feature. Point it at any existing PostgreSQL database and run one command — it generates fully-typed Python models, manager classes, all relationships, default values, constraints, and M2M configs. Zero hand-writing. Stay in Supabase's UI, TablePlus, or wherever you prefer, then sync your codebase whenever you want. Forward migrations (code → DB) are also fully supported — both directions work, you choose your workflow.

### 2. Auto-Generated Manager Classes
Every table gets a typed `BaseManager` subclass with the full CRUD surface already implemented — `load_by_id`, `create_item`, `update_item`, `delete_item`, relationship fetchers, M2M helpers, bulk ops, dict serializers, and sync variants. Extend them with business logic. The boilerplate is already gone.

### 3. Transparent Caching
Per-model in-memory cache with configurable TTL policies (`PERMANENT` / `LONG_TERM` / `SHORT_TERM` / `INSTANT`). Write your fetch calls normally — cache hits are invisible, misses fetch-and-populate automatically. Override with `use_cache=False` or `StateManager` when needed. No decorators, no manual invalidation on writes.

### 4. First-Class Relationship Support
- **ForeignKey** — standard FK with `fetch_fk()` / `select_related()`
- **InverseForeignKey** — declared reverse traversal, fetched with `fetch_ifk()`
- **ManyToMany** — both declarative (`ManyToManyField`) and config-based (existing junction tables)
- `fetch_all_related()` — single call returns FKs, IFKs, and M2Ms in one dict
- Cross-schema FKs (`auth.users`) and cross-database FKs both supported natively

### 5. Async-First, Sync Available
Built on `asyncpg`. Every operation is `async/await`. Sync wrappers exist on all methods for scripting or legacy contexts.

---

## Full Feature Surface (at a glance)

Q objects · aggregates · window functions · CTEs · `DISTINCT ON` · `SELECT FOR UPDATE` · JSONB operators · raw SQL · transactions with savepoints · subquery expressions · lifecycle signals · optimistic locking (`VersionField`) · abstract base models · column-level `only()` / `defer()` · `Paginator` · pgvector similarity search (`.nearest()`) · scoped migrations · schema introspection · bidirectional migrations with checksum detection

---

## Entry Points

```python
# Reverse: DB → Code (introspect and generate models/managers)
from matrx_orm.schema_builder.schema_manager import SchemaManager
sm = SchemaManager(schema="public", database_project="my_project")
sm.initialize()
sm.schema.generate_schema_files()   # writes schema JSON
sm.schema.generate_models()         # writes Python model + manager files

# Forward: Code → DB (migration CLI)
# matrx-orm makemigrations --database my_project --dir migrations
# matrx-orm migrate --database my_project --dir migrations

# Keep both in sync after any schema change
from matrx_orm import migrate_and_rebuild
await migrate_and_rebuild("my_project", "./migrations", output_dir="./database/main")
```

---

**Stack:** Python 3.10+ · asyncpg · psycopg3 · any standard PostgreSQL (Supabase, RDS, self-hosted, Docker)