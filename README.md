# matrx-orm

A modern async PostgreSQL ORM with migrations, schema introspection, and full relationship support. Works with any PostgreSQL database—Supabase, AWS RDS, Google Cloud SQL, or self-hosted.

## Features

- **Async-first** — Built on `asyncpg` and `psycopg3` for high-performance database access
- **PostgreSQL-generic** — No vendor lock-in; works with any standard PostgreSQL instance
- **Bidirectional migrations** — Model-first or SQL-first; auto-generate migrations from schema diffs
- **Schema introspection** — Generate Python models and managers from an existing database
- **Relationships** — Foreign keys, inverse FKs, and many-to-many with junction tables
- **Resilient FK fetching** — Optional `_unfetchable` flag for FKs pointing to external tables (e.g. `auth.users`)
- **State management** — Built-in caching with configurable policies (permanent, long-term, short-term, instant)
- **Type-safe** — Full type hints and Pydantic-ready patterns

## Installation

```bash
pip install matrx-orm
# or with uv
uv add matrx-orm
```

## Quick Start

### 1. Register a database

```python
from matrx_orm import register_database, DatabaseProjectConfig

register_database(DatabaseProjectConfig(
    name="my_project",
    host="localhost",
    port="5432",
    database_name="my_db",
    user="postgres",
    password="secret",
    alias="main",
))
```

### 2. Define a model

```python
from matrx_orm import Model, UUIDField, CharField, TextField, ForeignKey

class Recipe(Model):
    id = UUIDField(primary_key=True)
    name = CharField(max_length=200)
    description = TextField(null=True)
    author_id = ForeignKey("User", "id")

    _table_name = "recipe"
    _database = "my_project"
```

### 3. CRUD operations

```python
# Create
recipe = await Recipe.create(id=uuid4(), name="Pasta", author_id=user_id)

# Read
recipe = await Recipe.get(id=recipe_id)
recipes = await Recipe.filter(author_id=user_id).all()

# Update
await Recipe.filter(id=recipe_id).update(name="Updated Pasta")

# Delete
await recipe.delete()
```

### 4. Migrations

```bash
# Generate migration from model changes
matrx-orm makemigrations --database my_project --dir migrations

# Apply migrations
matrx-orm migrate --database my_project --dir migrations

# Rollback
matrx-orm rollback --database my_project --dir migrations --steps 1
```

## Migrations

The migration system supports:

- **Model-first** — Define models in Python; `makemigrations` diffs against the DB and generates migration files
- **SQL-first** — Write hand-crafted migrations with `create_empty` and `up`/`down` functions
- **Hybrid** — Mix both approaches; migrations run in dependency order

See [MIGRATIONS.md](MIGRATIONS.md) for full documentation.

## Testing

Tests are split into two levels:

- **Level 1** — No database required; run with `pytest -m level1`
- **Level 2** — Requires a live PostgreSQL database; run with `pytest -m level2`

Configure Level 2 tests via environment variables: `MATRX_TEST_DB_HOST`, `MATRX_TEST_DB_PORT`, `MATRX_TEST_DB_NAME`, `MATRX_TEST_DB_USER`, `MATRX_TEST_DB_PASSWORD`.

## Publishing

1. Update `version` in `pyproject.toml`
2. Commit and push
3. Create and push a tag: `git tag v1.4.2 && git push origin v1.4.2`
4. GitHub Actions builds and publishes to PyPI

The tag must match the version in `pyproject.toml`.

## Version History

- **v1.4.x** — Migration system, resilient FK fetching, improved error handling
- **v1.2.0** — Upgraded to psycopg3
- **v1.0.x** — Initial releases

## License

MIT
