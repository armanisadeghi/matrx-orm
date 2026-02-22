# matrx-orm

**Async-first PostgreSQL ORM** with bidirectional migrations, schema introspection, full relationship support (FK, IFK, M2M), and built-in state caching. Works with any PostgreSQL database — Supabase, AWS RDS, Google Cloud SQL, self-hosted, or Docker.

[![PyPI version](https://badge.fury.io/py/matrx-orm.svg)](https://pypi.org/project/matrx-orm/)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Models and Fields](#models-and-fields)
- [CRUD Operations](#crud-operations)
- [Querying](#querying)
- [Relationships](#relationships)
- [Many-to-Many](#many-to-many)
- [State Caching](#state-caching)
- [Migrations](#migrations)
- [Schema Introspection](#schema-introspection)
- [BaseManager](#basemanager)
- [Error Handling](#error-handling)
- [Testing](#testing)
- [Publishing](#publishing)
- [Version History](#version-history)

---

## Features

| Capability | Detail |
|---|---|
| **Async-first** | Built on `asyncpg` and `psycopg3`; every operation is `async/await` |
| **PostgreSQL-generic** | Zero vendor lock-in; works with any standard PostgreSQL instance |
| **Full field library** | UUID, Char, Text, Integer, Float, Boolean, DateTime, JSON, JSONB, Array, Decimal, Enum, IP, HStore, and more |
| **Relationships** | ForeignKey, InverseForeignKey, ManyToMany (declarative or config-based) |
| **Resilient FK fetch** | `_unfetchable` flag silences errors for FKs pointing to inaccessible tables (e.g., Supabase `auth.users`) |
| **Bidirectional migrations** | Model-first, SQL-first, or hybrid; auto-generate migrations from schema diffs |
| **Scoped migrations** | `TableFilter` lets you include or exclude specific tables from the migration diff — with cross-reference warnings |
| **Schema introspection** | Generate Python models and typed managers from an existing database schema |
| **State caching** | Per-model in-memory cache with configurable TTL policies (permanent, long-term, short-term, instant) |
| **BaseManager** | High-level manager class with built-in CRUD, bulk ops, and relationship helpers |
| **Lookup operators** | `__in`, `__gt`, `__gte`, `__lt`, `__lte`, `__ne`, `__isnull`, `__contains`, `__icontains`, `__startswith`, `__endswith` |
| **Type-safe** | Full type hints throughout; strict mode compatible |

---

## Installation

```bash
pip install matrx-orm
# or with uv (recommended)
uv add matrx-orm
```

**Requirements:** Python 3.10+ and a PostgreSQL database.

---

## Quick Start

### 1. Register a database

```python
from matrx_orm import register_database, DatabaseProjectConfig

register_database(DatabaseProjectConfig(
    name="my_project",       # internal identifier used in models
    host="localhost",
    port="5432",
    database_name="my_db",
    user="postgres",
    password="secret",
    alias="main",            # short alias for connection pooling
))
```

For Supabase, use your **direct connection string** credentials (not the pooler):

```python
register_database(DatabaseProjectConfig(
    name="my_project",
    host="db.xxxxxxxxxxxx.supabase.co",
    port="5432",
    database_name="postgres",
    user="postgres",
    password="your-db-password",
    alias="main",
))
```

### 2. Define models

```python
from matrx_orm import Model, UUIDField, CharField, TextField, BooleanField, ForeignKey

class User(Model):
    id = UUIDField(primary_key=True)
    username = CharField(max_length=100, unique=True)
    email = CharField(max_length=255)
    bio = TextField(null=True)
    is_active = BooleanField(default=True)

    _table_name = "user"
    _database = "my_project"


class Post(Model):
    id = UUIDField(primary_key=True)
    title = CharField(max_length=200)
    body = TextField(null=True)
    author_id = ForeignKey("User", "id")
    is_published = BooleanField(default=False)

    _table_name = "post"
    _database = "my_project"
```

### 3. Use it

```python
from uuid import uuid4

# Create
user = await User.create(id=str(uuid4()), username="alice", email="alice@example.com")
post = await Post.create(id=str(uuid4()), title="Hello World", author_id=user.id)

# Read
alice = await User.get(username="alice")
posts = await Post.filter(author_id=alice.id, is_published=True).all()

# Update
await Post.filter(id=post.id).update(is_published=True)

# Delete
await Post.filter(id=post.id).delete()
```

---

## Models and Fields

### Model class attributes

| Attribute | Type | Description |
|---|---|---|
| `_table_name` | `str` | Database table name (defaults to snake_case of class name) |
| `_database` | `str` | Database project name (must match a registered `DatabaseProjectConfig`) |
| `_db_schema` | `str \| None` | PostgreSQL schema prefix (e.g. `"public"`, `"analytics"`) |
| `_primary_keys` | `list[str]` | Explicit composite PKs (alternative to `primary_key=True` on field) |
| `_unfetchable` | `bool` | Marks the model as a reference-only table that should never be fetched (e.g. `auth.users`) |
| `_cache_policy` | `CachePolicy` | Cache TTL policy: `PERMANENT`, `LONG_TERM`, `SHORT_TERM` (default), `INSTANT` |
| `_cache_timeout` | `int \| None` | Explicit timeout in seconds (overrides policy) |
| `_inverse_foreign_keys` | `dict` | Declare reverse FK relationships |
| `_many_to_many` | `dict` | Declare M2M relationships through existing junction tables |

### Field types

```python
from matrx_orm import (
    UUIDField,          # db: TEXT or UUID
    CharField,          # db: VARCHAR(n)
    TextField,          # db: TEXT
    IntegerField,       # db: INTEGER
    BigIntegerField,    # db: BIGINT
    SmallIntegerField,  # db: SMALLINT
    FloatField,         # db: FLOAT
    DecimalField,       # db: NUMERIC(max_digits, decimal_places)
    BooleanField,       # db: BOOLEAN
    DateTimeField,      # db: TIMESTAMP
    DateField,          # db: DATE
    TimeField,          # db: TIME
    JSONField,          # db: JSONB
    JSONBField,         # db: JSONB (alias)
    ArrayField,         # db: item_type[]
    TextArrayField,     # db: TEXT[]
    IntegerArrayField,  # db: INTEGER[]
    BooleanArrayField,  # db: BOOLEAN[]
    UUIDArrayField,     # db: TEXT[]
    JSONBArrayField,    # db: JSONB[]
    EnumField,          # db: VARCHAR (validates against enum_class or choices)
    IPAddressField,     # db: INET
    IPNetworkField,     # db: CIDR
    MacAddressField,    # db: MACADDR
    HStoreField,        # db: HSTORE
    PointField,         # db: POINT
    MoneyField,         # db: MONEY
    BinaryField,        # db: BYTEA
    TimeDeltaField,     # db: INTERVAL
    ForeignKey,         # db: UUID (stores PK of related model)
)
```

**Common field parameters:**

```python
UUIDField(
    primary_key=False,  # mark as primary key
    null=True,          # allow NULL values
    unique=False,       # add UNIQUE constraint
    default=None,       # default value or callable
    index=False,        # create index
)
```

---

## CRUD Operations

### Create

```python
from uuid import uuid4

# Single create
user = await User.create(id=str(uuid4()), username="alice", email="alice@example.com")

# Bulk create
users = await User.bulk_create([
    {"id": str(uuid4()), "username": "bob",   "email": "bob@example.com"},
    {"id": str(uuid4()), "username": "carol", "email": "carol@example.com"},
])
```

### Read

```python
# Get by PK — raises DoesNotExist if not found
user = await User.get(id=user_id)

# Get or None — returns None if not found
user = await User.get_or_none(id=user_id)

# Skip cache for a fresh DB read
user = await User.get(use_cache=False, id=user_id)
```

### Update

```python
# Update matching rows — returns updated row count
count = await User.filter(id=user_id).update(bio="New bio", is_active=True)

# Bulk update (update specific fields on model instances)
for u in users:
    u.is_active = False
updated = await User.bulk_update(users, ["is_active"])
```

### Delete

```python
# Delete matching rows — returns deleted row count
count = await User.filter(id=user_id).delete()

# Bulk delete
deleted = await User.bulk_delete(users)
```

### Upsert (INSERT … ON CONFLICT DO UPDATE)

```python
# Single upsert — inserts or updates on conflict
user = await User.upsert(
    data={"id": str(uuid4()), "email": "alice@example.com", "username": "alice"},
    conflict_fields=["email"],           # unique constraint columns
    update_fields=["username"],           # columns to SET on conflict (optional — defaults to all non-conflict)
)

# Bulk upsert — same semantics, multiple rows
users = await User.bulk_upsert(
    objects_data=[
        {"email": "bob@example.com",   "username": "bob_v2"},
        {"email": "carol@example.com", "username": "carol_v2"},
    ],
    conflict_fields=["email"],
)
```

### Count, Exists, Update-Where, Delete-Where

```python
# Lightweight count — no model hydration
total  = await User.count()
active = await User.count(is_active=True)

# Existence check
if await User.exists(email="alice@example.com"):
    ...

# Bulk update by filter — no fetch required
result = await User.update_where(
    {"status": "draft", "created_at__lt": cutoff},
    status="archived",
)
# result == {"rows_affected": 42, "updated_rows": [...]}

# Bulk delete by filter — no fetch required
deleted = await User.delete_where(status="expired")
```

---

## Querying

### Filter and lookup operators

```python
# Exact match (default)
await User.filter(username="alice").all()

# Comparison operators
await User.filter(age__gt=18).all()
await User.filter(age__gte=18).all()
await User.filter(age__lt=65).all()
await User.filter(age__lte=65).all()
await User.filter(status__ne="banned").all()

# IN list
await User.filter(id__in=[id1, id2, id3]).all()

# NULL checks
await User.filter(deleted_at__isnull=True).all()
await User.filter(deleted_at__isnull=False).all()

# String matching
await User.filter(username__contains="ali").all()      # LIKE %ali%
await User.filter(username__icontains="ali").all()     # ILIKE %ali%
await User.filter(username__startswith="al").all()     # LIKE al%
await User.filter(username__endswith="ce").all()       # LIKE %ce
```

### Chaining

```python
results = (
    await User
    .filter(is_active=True)
    .exclude(role="admin")
    .order_by("username")
    .limit(20)
    .offset(40)
    .select("id", "username", "email")
    .all()
)
```

### Terminal methods

```python
results  = await User.filter(is_active=True).all()       # list[User]
one      = await User.filter(username="alice").get()      # User (raises if 0 or >1)
first    = await User.filter(is_active=True).first()      # User | None
count    = await User.filter(is_active=True).count()      # int
exists   = await User.filter(username="alice").exists()   # bool
```

### Values / values_list

```python
# Returns list of dicts
rows = await User.filter(is_active=True).values("id", "username")

# Returns list of tuples
rows = await User.filter(is_active=True).values_list("id", "username")

# Returns flat list when flat=True and one field
names = await User.filter(is_active=True).values_list("username", flat=True)
```

### Slicing

```python
# Equivalent to .offset(10).limit(20)
page = await User.filter(is_active=True).order_by("username")[10:30].all()
```

---

## Relationships

### Foreign Key (FK)

```python
class Post(Model):
    id = UUIDField(primary_key=True)
    title = CharField(max_length=200)
    author_id = ForeignKey("User", "id")  # stores user PK

    _table_name = "post"
    _database = "my_project"
```

```python
post = await Post.get(id=post_id)

# Fetch the related User
author = await post.fetch_fk("author_id")       # returns User | None

# Fetch all FKs at once (resilient — continues on per-FK errors)
fk_results = await post.fetch_fks()             # dict[str, Model | None]
```

### Inverse Foreign Key (IFK)

Use `_inverse_foreign_keys` to traverse FK relationships in reverse:

```python
class User(Model):
    id = UUIDField(primary_key=True)
    username = CharField(max_length=100)

    _inverse_foreign_keys = {
        "posts": {
            "from_model": "Post",
            "from_field": "author_id",
            "referenced_field": "id",
        }
    }
    _table_name = "user"
    _database = "my_project"
```

```python
user = await User.get(id=user_id)

# Fetch all posts written by this user
posts = await user.fetch_ifk("posts")           # list[Post]

# Fetch all IFKs at once (resilient)
ifk_results = await user.fetch_ifks()           # dict[str, list[Model]]
```

### Unfetchable FKs (auth.users / external tables)

When a FK points to a table outside your schema (e.g., Supabase `auth.users`), mark the model `_unfetchable = True` to prevent query errors and reduce noise:

```python
class Users(Model):
    id = UUIDField(primary_key=True)
    email = CharField(max_length=255)

    _table_name = "users"
    _db_schema = "auth"
    _unfetchable = True       # never query this table; skip gracefully in fetch_fks()
    _database = "my_project"
```

When `fetch_fks()` or `fetch_all_related()` encounters a FK pointing to an `_unfetchable` model, it logs a single warning line and continues — no exceptions, no cascading error output.

---

## Many-to-Many

### Config-based M2M (existing junction table)

Use `_many_to_many` when your junction table already exists in the database:

```python
class Post(Model):
    id = UUIDField(primary_key=True)
    title = CharField(max_length=200)

    _many_to_many = {
        "tags": {
            "junction_table": "post_tag",
            "source_column": "post_id",
            "target_column": "tag_id",
            "target_model": "Tag",
        }
    }
    _table_name = "post"
    _database = "my_project"
```

### Declarative M2M (ManyToManyField)

Use `ManyToManyField` when defining models from scratch. The ORM auto-generates the junction table name:

```python
from matrx_orm import ManyToManyField

class Post(Model):
    id = UUIDField(primary_key=True)
    title = CharField(max_length=200)
    tags = ManyToManyField("Tag")             # junction table: "post_tag" (sorted names)

    _table_name = "post"
    _database = "my_project"

# Custom junction table name:
class Recipe(Model):
    id = UUIDField(primary_key=True)
    name = CharField(max_length=200)
    ingredients = ManyToManyField("Ingredient", db_table="recipe_ingredients")

    _table_name = "recipe"
    _database = "my_project"
```

### M2M operations

```python
post = await Post.get(id=post_id)

# Fetch related Tags (two-query hop: junction → target)
tags = await post.fetch_m2m("tags")                          # list[Tag]

# Add tags (idempotent — uses ON CONFLICT DO NOTHING)
await post.add_m2m("tags", tag1_id, tag2_id)

# Remove specific tags
await post.remove_m2m("tags", tag3_id)

# Replace all tags at once
await post.set_m2m("tags", [tag1_id, tag2_id, tag4_id])

# Remove all tags
await post.clear_m2m("tags")

# Fetch all M2M relations at once (resilient)
m2m_results = await post.fetch_m2ms()                       # dict[str, list[Model]]
```

### Fetch everything at once

```python
all_related = await post.fetch_all_related()
# Returns:
# {
#     "foreign_keys": {"author_id": <User>},
#     "inverse_foreign_keys": {},
#     "many_to_many": {"tags": [<Tag>, <Tag>]},
# }
```

---

## State Caching

Every model has a per-process in-memory cache managed by `StateManager`. The cache is populated automatically on reads and invalidated on writes.

### Cache policies

```python
from matrx_orm.state import CachePolicy

class Config(Model):
    id = UUIDField(primary_key=True)
    value = TextField()

    _cache_policy = CachePolicy.PERMANENT   # never expires
    _table_name = "config"
    _database = "my_project"
```

| Policy | TTL |
|---|---|
| `PERMANENT` | Never expires |
| `LONG_TERM` | 4 hours |
| `SHORT_TERM` | 10 minutes (default) |
| `INSTANT` | 1 minute |

```python
# Custom timeout (seconds), overrides policy
class Session(Model):
    _cache_timeout = 300   # 5 minutes
```

### Manual cache control

```python
from matrx_orm.state import StateManager

# Force a fresh database read (bypass cache)
user = await User.get(use_cache=False, id=user_id)

# Manually cache a record
await StateManager.cache(User, user)

# Remove a record from cache
await StateManager.remove(User, user)

# Clear the entire cache for a model
await StateManager.clear_cache(User)

# Count cached records
count = await StateManager.count(User)
```

---

## Migrations

The migration system supports three workflows:

| Workflow | Description |
|---|---|
| **Model-first** | Define/change Python models → `makemigrations` diffs against DB → apply |
| **SQL-first** | Write `up()`/`down()` functions manually in Python migration files |
| **Hybrid** | Mix both; migrations always run in declared dependency order |

### CLI commands

```bash
# Generate a migration from model/DB differences
matrx-orm makemigrations --database my_project --dir migrations

# With a custom name
matrx-orm makemigrations --database my_project --dir migrations --name add_posts_table

# Apply all pending migrations
matrx-orm migrate --database my_project --dir migrations

# Roll back the last N migrations (default: 1)
matrx-orm rollback --database my_project --dir migrations --steps 1

# Show migration status (applied / pending)
matrx-orm status --database my_project --dir migrations

# Create a blank migration file for hand-written SQL
matrx-orm create_empty --database my_project --dir migrations --name custom_ddl
```

### Programmatic API

```python
from matrx_orm import makemigrations, migrate, rollback, migration_status

# Generate migration file(s)
path = await makemigrations("my_project", "./migrations")

# Apply pending migrations
applied = await migrate("my_project", "./migrations")
print(f"Applied: {applied}")

# Roll back last migration
rolled_back = await rollback("my_project", "./migrations", steps=1)
```

### Migration file format

```python
"""Create posts table."""

dependencies = ["0001_initial"]

async def up(db):
    await db.execute("""
        CREATE TABLE post (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            title VARCHAR(200) NOT NULL,
            body TEXT,
            author_id UUID NOT NULL REFERENCES "user"(id) ON DELETE CASCADE,
            is_published BOOLEAN DEFAULT false,
            created_at TIMESTAMPTZ DEFAULT now()
        )
    """)
    await db.execute("""
        CREATE INDEX idx_post_author ON post (author_id)
    """)

async def down(db):
    await db.execute("DROP TABLE IF EXISTS post")
```

The `db` parameter provides: `execute(sql, *args)`, `fetch(sql, *args)`, `fetch_one(sql, *args)`, `fetch_val(sql, *args)`, `execute_many(statements)`.

### State tracking

Matrx-orm maintains a `_matrx_migrations` table in your database:

```sql
CREATE TABLE _matrx_migrations (
    id         SERIAL PRIMARY KEY,
    name       VARCHAR(255) NOT NULL UNIQUE,
    applied_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    checksum   VARCHAR(64)  NOT NULL
);
```

The checksum detects if a migration file was modified after being applied, alerting you before the next run.

### Scoped migrations — include or exclude tables

Use `TableFilter` when you only want to diff a subset of your schema. Pass either an **include** list (allowlist) or an **exclude** list (denylist) — never both at the same time.

**CLI — include-only (only diff these tables):**

```bash
matrx-orm makemigrations --database my_project --dir migrations \
    --include-tables user post comment
```

**CLI — exclude (diff everything except these tables):**

```bash
matrx-orm makemigrations --database my_project --dir migrations \
    --exclude-tables legacy_audit scratch_pad
```

`--include-tables` and `--exclude-tables` are mutually exclusive; passing both is a CLI error.

**Programmatic — include-only:**

```python
from matrx_orm import makemigrations

await makemigrations(
    "my_project",
    "./migrations",
    include_tables={"user", "post", "comment"},
)
```

**Programmatic — exclude:**

```python
await makemigrations(
    "my_project",
    "./migrations",
    exclude_tables={"legacy_audit", "scratch_pad"},
)
```

**Using `TableFilter` directly with `SchemaDiff`:**

```python
from matrx_orm import SchemaDiff, TableFilter
from matrx_orm.migrations import MigrationDB

db = MigrationDB("my_project")
f = TableFilter(include={"user", "post"})
diff = SchemaDiff(db, schema="public", table_filter=f)
path = await diff.generate_migration_file("migrations/")
```

#### Cross-reference warnings

When an included table has a foreign key column that references a table *outside* the migration scope, `matrx-orm` emits a `UserWarning` — the FK constraint will still be generated in the SQL, but the referenced table won't be created or managed by this migration set. Ensure it already exists in the target database.

```
UserWarning: [matrx-orm] Cross-scope FK detected: 'post.author_id' references 'user',
which is outside the current migration scope. The FK constraint will be included
in the generated SQL, but 'user' will not be created or managed by this migration
set. Ensure it already exists in the target database.
```

To suppress these warnings intentionally:

```python
import warnings
warnings.filterwarnings("ignore", category=UserWarning, module="matrx_orm")
```

> **Note:** Table filtering applies only to `makemigrations` (the diff/generation step). `migrate` and `rollback` apply already-generated migration files in full — there is nothing to filter at that stage.

See [MIGRATIONS.md](MIGRATIONS.md) for full documentation.

---

## Schema Introspection

If you already have a database, use the schema builder to generate typed Python models and managers:

```python
from matrx_orm.schema_builder.generator import run_generate_models

await run_generate_models(
    database_project="my_project",
    output_dir="./database/main",
)
```

This introspects your database and emits:
- `models.py` — typed `Model` subclasses with all fields
- One manager file per table — `BaseManager` subclasses with CRUD methods
- `_many_to_many` configs auto-detected from junction tables
- `_inverse_foreign_keys` configs auto-detected from FK references

After running migrations, run it again to keep models in sync:

```python
from matrx_orm import migrate_and_rebuild

# Apply pending migrations, then regenerate models
await migrate_and_rebuild("my_project", "./migrations", output_dir="./database/main")
```

### Scoped introspection — include or exclude tables

Pass `include_tables` or `exclude_tables` (mutually exclusive) to limit which tables are introspected, modelled, and code-generated:

```python
from matrx_orm.schema_builder import SchemaManager

# Include-only: generate models for exactly these tables
manager = SchemaManager(
    schema="public",
    database_project="my_project",
    include_tables={"user", "post", "comment"},
)
manager.initialize()
manager.schema.generate_models()

# Exclude: generate models for everything except these tables
manager = SchemaManager(
    schema="public",
    database_project="my_project",
    exclude_tables={"legacy_audit", "scratch_pad"},
)
manager.initialize()
manager.schema.generate_models()
```

---

## BaseManager

`BaseManager` is a high-level manager class with a full suite of methods. Subclass it to add business logic:

```python
from matrx_orm import BaseManager

class PostManager(BaseManager):
    model = Post

    async def get_published(self):
        return await self.load_items(is_published=True)

    async def publish(self, post_id):
        await self.update_item(post_id, is_published=True)
```

### Built-in methods

```python
manager = PostManager()

# Basic CRUD
item   = await manager.load_by_id(post_id)
items  = await manager.load_all()
items  = await manager.load_items(is_published=True)
items  = await manager.load_items_by_ids([id1, id2, id3])
item   = await manager.create_item(id=str(uuid4()), title="Hello")
item   = await manager.update_item(post_id, title="Updated")
count  = await manager.delete_item(post_id)

# With relationships
item, related = await manager.get_item_with_all_related(post_id)
# related = {"foreign_keys": {...}, "inverse_foreign_keys": {...}, "many_to_many": {...}}

# M2M convenience
item, tags    = await manager.get_item_with_m2m(post_id, "tags")
await manager.add_m2m(post_id, "tags", tag1_id, tag2_id)
await manager.remove_m2m(post_id, "tags", tag3_id)
await manager.set_m2m(post_id, "tags", [tag1_id, tag2_id])
await manager.clear_m2m(post_id, "tags")
```

---

## Error Handling

All ORM errors inherit from `ORMException` and carry structured context (model name, query, parameters, operation):

```
================================================================================
[ERROR in Post: QueryExecutor.all()]

Message: Unexpected database error during execute_query: ...

Context:
  query:   SELECT * FROM post WHERE author_id = $1
  params:  ['4cf62e4e-...']
  filters: {'author_id': '4cf62e4e-...'}
================================================================================
```

### Exception hierarchy

```
ORMException
├── ValidationError      — field/model validation failed
├── FieldError           — field-level processing error
├── QueryError           — query construction or execution error
│   ├── DoesNotExist     — zero results when one was expected
│   └── MultipleObjectsReturned
├── DatabaseError        — database-level errors
│   ├── ConnectionError
│   ├── IntegrityError   — constraint violations
│   └── TransactionError
├── ConfigurationError   — missing/invalid ORM config
├── CacheError           — state manager failures
├── StateError           — state management errors
├── RelationshipError    — FK/M2M resolution errors
├── MigrationError       — migration apply/rollback failures
├── ParameterError       — malformed query parameters
└── UnknownDatabaseError — unexpected database errors with full context
```

### Exception enrichment

Exceptions carry context accumulated as they bubble up through layers — no guessing what caused the error:

```python
from matrx_orm.exceptions import DoesNotExist

try:
    post = await Post.get(id=post_id)
except DoesNotExist as e:
    print(e.model)    # "Post"
    print(e.details)  # {"filters": {"id": "..."}}
```

---

## Testing

Tests are split into two levels:

### Level 1 — No database required

```bash
pytest -m level1
```

Covers: fields, model meta, model instances, registry, query builder, SQL generation, DDL generator, migration loader, type normalization, exceptions, relations, config, and cache — 361 tests total.

### Level 2 — Live database

```bash
# Set credentials
export MATRX_TEST_DB_HOST=localhost
export MATRX_TEST_DB_PORT=5432
export MATRX_TEST_DB_NAME=matrx_test
export MATRX_TEST_DB_USER=postgres
export MATRX_TEST_DB_PASSWORD=postgres

pytest -m level2
```

Covers: real CRUD, bulk ops, query execution, FK/IFK fetching, M2M operations, cache integration, live migrations, schema diff, and manager methods — 66 tests total.

---

## Publishing

Releases are triggered by a version tag. GitHub Actions builds the wheel and publishes to PyPI automatically when a matching tag is pushed.

To cut a new release:

1. Update `version` in `pyproject.toml` to the new version string (e.g. `1.5.0`).
2. Commit all changes, tag, and push — replace `X.Y.Z` with the actual version:

```bash
git add -A
git commit -m "chore: release vX.Y.Z"
git tag vX.Y.Z
git push origin main --tags
```

The tag **must** match the `version` field in `pyproject.toml` exactly (e.g. tag `v1.5.0` for version `1.5.0`). A mismatch will fail the publish step.

---

## Version History

| Version | Highlights |
|---|---|
| **v1.6.4** | fix: complete field type coercion audit - get_db_prep_value and to_python for all field types |
| **v1.6.3** | fix: coerce datetime/date/time strings to native types before asyncpg binding |
| **v1.6.2** | fix: schema builder default value parsing overhaul in columns.py |
| **v1.6.1** | fix: numeric defaults no longer emitted as strings in generated Python models |
| **v1.6.0** | `upsert()` / `bulk_upsert()` (INSERT … ON CONFLICT DO UPDATE), `count()`, `exists()`, `update_where()`, `delete_where()` on Model and BaseManager; sync wrappers for all new methods |
| **v1.5.3** | `SchemaManager` now accepts `include_tables` and `exclude_tables` to generate models/managers for a specific subset of tables |
| **v1.5.2** | Fix migration dependency name bug — generated files now reference the full preceding migration stem (e.g. `"0001_baseline"`) instead of just the zero-padded number (`"0001"`) |
| **v1.5.1** | Scoped migrations: `TableFilter` with include-only and exclude modes; cross-scope FK warnings; `--include-tables` / `--exclude-tables` CLI flags |
| **v1.4.3** | Fix `ResourceWarning: unclosed connection` on all sync wrapper methods by closing asyncpg pools before the event loop shuts down |
| **v1.4.2** | Bug fixes: `bulk_create` key error, `ValidationError` API, `IntegrityError` call pattern |
| **v1.4.1** | Fix bulk create and improve error reporting |
| **v1.4.0** | Full PostgreSQL migration system (makemigrations, migrate, rollback, status, DDL generator, schema diff) |
| **v1.3.x** | Many-to-many relationship support (fetch, add, remove, set, clear); resilient FK fetching; improved error context |
| **v1.2.0** | Upgraded to psycopg3 |
| **v1.0.x** | Initial releases |

---

## License

MIT — see [LICENSE](LICENSE) for details.
