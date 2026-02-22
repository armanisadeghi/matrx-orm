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

### Schema builder TypeScript overrides

When the schema builder generates TypeScript output (entity overrides, field overrides, entity hooks), it reads app-specific configuration from the `entity_overrides` and `field_overrides` fields on `DatabaseProjectConfig`. These fields are empty by default — no app-specific values ever live inside the ORM package.

Pass your overrides at registration time:

```python
from matrx_orm import register_database, DatabaseProjectConfig

register_database(DatabaseProjectConfig(
    name="my_project",
    host="...", port="5432", database_name="postgres",
    user="postgres", password="secret",
    alias="main",
    # Entity-level TypeScript overrides (camelCase entity name → override props)
    entity_overrides={
        "recipe": {"defaultFetchStrategy": '"fkAndIfk"'},
        "broker": {
            "displayFieldMetadata": '{ fieldName: "displayName", databaseFieldName: "display_name" }'
        },
    },
    # Field-level TypeScript overrides (camelCase entity name → field name → override props)
    field_overrides={
        "recipe": {
            "tags": {"componentProps": {"subComponent": "tagsManager"}}
        },
        "broker": {
            "displayName": "{ isDisplayField: true }",
        },
        "aiSettings": {
            "temperature": {
                "defaultComponent": "SPECIAL",
                "componentProps": {"subComponent": "SLIDER", "min": 0, "max": 2, "step": 0.01},
            }
        },
    },
))
```

You can also retrieve the registered overrides programmatically:

```python
from matrx_orm import get_schema_builder_overrides

overrides = get_schema_builder_overrides("my_project")
# {"entity_overrides": {...}, "field_overrides": {...}}
```

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

## Advanced Querying (v1.7.0+)

### Q Objects — Boolean Query Composition

```python
from matrx_orm import Q

# OR composition
await User.filter(Q(status="active") | Q(role="admin")).all()

# AND composition (implicit when combined with kwargs)
await User.filter(Q(is_active=True), tenant_id=tid).all()

# NOT
await User.filter(~Q(banned=True)).all()

# Deeply nested
await User.filter((Q(role="admin") | Q(role="staff")) & ~Q(suspended=True)).all()
```

### Aggregate Expressions

```python
from matrx_orm import Sum, Avg, Min, Max, Count

# Scalar aggregation
result = await Order.filter(status="paid").aggregate(
    total=Sum("amount"),
    avg_amount=Avg("amount"),
    order_count=Count("id"),
)
# {"total": 15420.50, "avg_amount": 308.41, "order_count": 50}

# GROUP BY
rows = await Order.filter(status="paid").group_by("customer_id").annotate(
    total=Sum("amount")
).values("customer_id", "total")
```

### Database Functions

```python
from matrx_orm import Lower, Upper, Now, Coalesce, Cast, Extract, Length

# In annotations
await User.filter(is_active=True).annotate(
    name_lower=Lower("username")
).values("id", "name_lower")

# In update SET clause
await Order.update_where({"shipped_at__isnull": True}, shipped_at=Now())

# COALESCE null handling
await Product.filter(is_active=True).annotate(
    display_name=Coalesce("nickname", "name")
).values("id", "display_name")
```

### DISTINCT

```python
# Plain DISTINCT
await User.filter(is_active=True).distinct().values("email")

# DISTINCT ON (PostgreSQL)
await User.filter(is_active=True).distinct("tenant_id").order_by("tenant_id", "-created_at").all()
```

### SELECT FOR UPDATE (row locking)

```python
from matrx_orm import transaction

async with transaction():
    user = await User.filter(id=uid).select_for_update().first()
    await user.update(balance=user.balance - 100)

# With SKIP LOCKED (queue processing pattern)
async with transaction():
    job = await Job.filter(status="pending").select_for_update(skip_locked=True).first()
```

### JSONB Operators

```python
# Key existence
await Config.filter(data__json_has_key="email").all()

# JSON contains (value is a subset)
await Config.filter(data__json_contains={"role": "admin"}).all()

# Has any of these keys
await Config.filter(data__json_has_any=["email", "phone"]).all()

# Has all of these keys
await Config.filter(data__json_has_all=["name", "email"]).all()

# Value is contained by
await Config.filter(data__json_contained_by={"role": "admin", "active": True}).all()

# Nested path extraction
await Config.filter(data__json_path=("settings", "theme")).all()
```

### Transactions

```python
from matrx_orm import transaction

# Top-level transaction
async with transaction():
    user = await User.create(name="alice")
    await Profile.create(user_id=user.id, bio="hello")
    # commits on exit, rolls back on exception

# Nested transaction → savepoint
async with transaction():
    await Order.create(customer_id=cid, total=99.00)
    async with transaction():          # SAVEPOINT
        await AuditLog.create(action="order_created")
        # inner block rollback doesn't affect outer
```

### Raw SQL

```python
# Hydrated model instances
users = await User.raw("SELECT * FROM users WHERE age > $1 ORDER BY name", 18)
# returns list[User]

# Raw dicts (no hydration)
rows = await User.raw_sql(
    "SELECT count(*) as cnt, role FROM users GROUP BY role"
)
# returns list[dict]
```

### select_related — JOIN-based Eager Loading

```python
# Single JOIN query — no N+1 problem
posts = await Post.filter(is_published=True).select_related("author").all()
for post in posts:
    author = post.get_related("author")   # already loaded
    print(author.username)

# BaseManager equivalent (auto-detects FK, uses JOIN)
item, author = await manager.get_item_with_related(post_id, "author")

# Load all items with FK already joined
posts = await manager.get_items_with_related("author")
```

### Subquery Expressions

```python
from matrx_orm import Subquery, Exists, OuterRef

# EXISTS filter
active_orders = Order.filter(user_id=OuterRef("id"), status="active")
users_with_orders = await User.filter(Exists(active_orders)).all()

# Scalar subquery annotation
latest_order = (
    Order.filter(user_id=OuterRef("id"))
    .order_by("-created_at")
    .limit(1)
    .select("total")
)
users = await User.filter(is_active=True).annotate(
    last_total=Subquery(latest_order)
).values("id", "last_total")
```

### Lifecycle Signals

```python
from matrx_orm.core.signals import post_save, pre_delete

# Decorator style
@post_save.connect
async def audit_on_save(sender, instance, created: bool, **kwargs):
    if sender.__name__ == "User":
        await AuditLog.create(action="created" if created else "updated", entity_id=instance.id)

@pre_delete.connect
async def guard_delete(sender, instance, **kwargs):
    if getattr(instance, "protected", False):
        raise ValueError(f"Cannot delete protected {sender.__name__} {instance.id}")

# Manual connect / disconnect
post_save.connect(my_async_handler)
post_save.disconnect(my_async_handler)
```

---

## Cross-Schema & Multi-Database Relationships (v1.9.0+)

### The Problem This Solves

Every Supabase project has `auth.users` — a table that lives in the `auth` schema, not `public`. Before v1.9.0, any FK pointing to `auth.users` was silently blocked by `_unfetchable = True`, and `fetch_fk()` returned `None` without any warning. The same issue affects apps that split data across multiple registered databases.

### Same-Database Cross-Schema FKs (e.g. `auth.users`)

For tables in a different schema on the **same** PostgreSQL database, set `_db_schema` on the target model and add `to_schema` to the `ForeignKey`. The ORM uses `qualified_table_name` (`schema.table`) for all queries:

```python
from matrx_orm import Model, UUIDField, CharField, ForeignKey

# The auth.users stub — generated automatically by schema builder,
# or written manually. No _unfetchable needed.
class Users(Model):
    _database = "myproject"
    _db_schema = "auth"       # makes qualified_table_name = "auth.users"
    id = UUIDField(primary_key=True)
    email = CharField()

class Post(Model):
    _database = "myproject"
    id = UUIDField(primary_key=True)
    title = CharField()
    user_id = ForeignKey(to_model=Users, to_column="id", to_schema="auth")

# fetch_fk works — issues a query to auth.users via the same connection pool
post = await Post.get(id=some_id)
user = await post.fetch_fk("user_id")   # returns Users instance
```

The `to_schema` parameter is informational — the actual schema routing comes from `Users._db_schema`. `to_schema` is stored on `ForeignKeyReference` so callers and schema builders can inspect it.

### Cross-Database FKs (two registered databases)

For FKs that point to a table in a **different** registered database project, use `to_db`. The ORM routes the fetch query to the correct connection pool:

```python
from matrx_orm import Model, UUIDField, CharField, ForeignKey, register_database, DatabaseProjectConfig

register_database(DatabaseProjectConfig(
    name="analytics_db", host="...", port="5432",
    database_name="analytics", user="...", password="...", alias="analytics"
))

class AnalyticsUser(Model):
    _database = "analytics_db"
    id = UUIDField(primary_key=True)
    name = CharField()

class Order(Model):
    _database = "myproject"
    id = UUIDField(primary_key=True)
    # FK to a model in a different database — routes to analytics_db pool
    analytics_user_id = ForeignKey(
        to_model=AnalyticsUser,
        to_column="id",
        to_db="analytics_db",
    )

order = await Order.get(id=some_id)
analytics_user = await order.fetch_fk("analytics_user_id")  # queries analytics_db
```

Cross-database JOINs (`select_related`) are not supported — PostgreSQL doesn't support cross-database SQL joins without Foreign Data Wrappers. Cross-database FKs always use the two-query approach.

### `_unfetchable` Now Warns

If a model is still marked `_unfetchable = True`, `fetch_fk()` now emits a `UserWarning` instead of silently returning `None`. This makes misconfigurations visible:

```python
import warnings

# Will print: "fetch_fk('user_id') skipped: SomeModel is marked _unfetchable = True ..."
with warnings.catch_warnings(record=True) as w:
    result = await instance.fetch_fk("user_id")  # None + warning
```

Keep `_unfetchable = True` only for tables that are genuinely inaccessible (e.g. Supabase internal system tables your Postgres role cannot query).

### `additional_schemas` in Config

Declare which non-public schemas exist in each database so the schema builder introspects them automatically:

```python
from matrx_orm import register_database, DatabaseProjectConfig

register_database(DatabaseProjectConfig(
    name="myproject",
    host="db.abc.supabase.co",
    port="5432",
    database_name="postgres",
    user="postgres",
    password="...",
    alias="myproject",
    additional_schemas=["auth", "storage"],  # introspect these schemas too
))
```

`SchemaManager` and the introspection SQL helpers now read `additional_schemas` from the registry config rather than hardcoding `["auth"]`. Running `SchemaManager(database_project="myproject")` will automatically include `auth` and `storage` schema tables.

### Auto-Generated Code

When the schema builder introspects a FK that points to `auth.users`, the generated model code now includes `to_schema='auth'`:

```python
# Before v1.9.0:
user_id = ForeignKey(to_model=Users, to_column='id', null=True)

# After v1.9.0:
user_id = ForeignKey(to_model=Users, to_column='id', to_schema='auth', null=True)
```

And the `Users` stub no longer has `_unfetchable = True`:

```python
# Before v1.9.0:
class Users(Model):
    _db_schema = "auth"
    _unfetchable = True   # blocked all fetches
    ...

# After v1.9.0:
class Users(Model):
    _db_schema = "auth"   # qualified_table_name = auth.users — fetches work
    ...
```

---

## Advanced Querying (v1.8.0+)

### Window Functions

Annotate rows with ranking, lag/lead, or running aggregates using `Window()`:

```python
from matrx_orm import Window, RowNumber, Rank, DenseRank, Lag, Lead, Sum

# ROW_NUMBER per partition
rows = await Sale.filter().annotate(
    row_num=Window(RowNumber(), partition_by="region", order_by="-amount")
).all()

# RANK (with gaps) ordered by score
rows = await Player.filter().annotate(
    rank=Window(Rank(), order_by=["-score", "id"])
).all()

# DENSE_RANK partitioned by department
rows = await Employee.filter().annotate(
    dept_rank=Window(DenseRank(), partition_by="department_id", order_by="-salary")
).all()

# Running total (SUM as window function)
rows = await Order.filter().annotate(
    running_total=Window(Sum("amount"), partition_by="user_id", order_by="created_at")
).all()

# Previous row value
rows = await StockPrice.filter(ticker="AAPL").annotate(
    prev_close=Window(Lag("close_price"), order_by="date")
).all()

# Available window functions
# RowNumber, Rank, DenseRank, Lag, Lead, FirstValue, LastValue,
# NthValue, Ntile, CumeDist, PercentRank
# Any Aggregate (Sum, Avg, Min, Max, Count) also works as a window function
```

The `Window()` constructor accepts:
- `partition_by` — single field name or list of field names
- `order_by` — single field name, list of names (`"-field"` for DESC)
- `frame` — optional SQL frame clause, e.g. `"ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW"`

### Common Table Expressions (CTEs)

Attach one or more CTEs to any query:

```python
from matrx_orm import CTE

# Non-recursive CTE from raw SQL
recent = CTE("recent_orders", "SELECT * FROM orders WHERE created_at > NOW() - interval '7 days'")
results = await Order.filter(status="paid").with_cte(recent).all()

# CTE from a QueryBuilder
active_qs = User.filter(is_active=True).only("id", "email")
active_cte = CTE("active_users", active_qs)
rows = await Invoice.filter().with_cte(active_cte).all()

# Recursive CTE
tree_sql = """
    SELECT id, parent_id, name, 0 AS depth FROM category WHERE parent_id IS NULL
    UNION ALL
    SELECT c.id, c.parent_id, c.name, t.depth + 1
    FROM category c JOIN category_tree t ON c.parent_id = t.id
"""
tree_cte = CTE("category_tree", tree_sql, recursive=True)
categories = await Category.filter().with_cte(tree_cte).all()

# Multiple CTEs chained
rows = await Order.filter().with_cte(recent, active_cte).all()
```

### Column Selection: `only()` and `defer()`

Load only specific columns or omit heavy ones — unloaded columns are `None` on the returned instances:

```python
# only() — whitelist: fetch exactly these columns
users = await User.filter(is_active=True).only("id", "email").all()

# defer() — blacklist: fetch everything except these columns
products = await Product.filter().defer("description", "large_blob").all()

# Combine with other chainable methods
rows = await Post.filter(published=True).only("id", "title", "author_id").order_by("-created_at").limit(20).all()
```

### Paginator

Split any queryset into pages without writing LIMIT/OFFSET boilerplate:

```python
from matrx_orm import Paginator

# Create paginator (queryset is not executed yet)
paginator = Paginator(
    User.filter(is_active=True).order_by("-created_at"),
    per_page=20
)

# Fetch a specific page (executes COUNT + SELECT)
page = await paginator.page(1)

print(page.items)           # list[User] — rows on this page
print(page.number)          # 1
print(page.total_count)     # total matching rows
print(page.total_pages)     # ceil(total_count / per_page)
print(page.has_next)        # True / False
print(page.has_previous)    # True / False
print(page.next_number)     # int | None
print(page.previous_number) # int | None
print(page.start_index)     # 1-based start index
print(page.end_index)       # 1-based end index

# Iterate over all pages with async for
async for page in paginator:
    for user in page:
        await process(user)
```

### Optimistic Locking with `VersionField`

Add a `version` column to any model to detect concurrent modification conflicts:

```python
from matrx_orm import Model, UUIDField, DecimalField, VersionField, OptimisticLockError
from uuid import uuid4

class Order(Model):
    _database = "default"
    id = UUIDField(primary_key=True, default=uuid4)
    total = DecimalField()
    version = VersionField()   # starts at 1, auto-increments on every save

# Normal save — version increments automatically
order = await Order.get(id=some_id)
order.total = Decimal("99.99")
await order.save()             # version goes 1 → 2

# Stale write detection
order_a = await Order.get(id=some_id)  # version = 2
order_b = await Order.get(id=some_id)  # version = 2 (another process)

order_a.total = Decimal("50.00")
await order_a.save()                   # OK, version 2 → 3

order_b.total = Decimal("75.00")
try:
    await order_b.save()               # RAISES — row now at version 3, not 2
except OptimisticLockError as e:
    print("Conflict detected — re-fetch and retry")
    order_b = await Order.get(id=some_id)
    order_b.total = Decimal("75.00")
    await order_b.save()               # OK now
```

### Abstract Base Models

Mark a model `abstract = True` so it contributes shared fields to subclasses without creating its own table:

```python
from matrx_orm import Model, UUIDField, DateTimeField, CharField
from uuid import uuid4
from datetime import datetime

class AuditedModel(Model):
    _database = "default"

    class Meta:
        abstract = True

    created_by = CharField(max_length=100)
    updated_by = CharField(max_length=100, nullable=True)

class Article(AuditedModel):
    _database = "default"
    id = UUIDField(primary_key=True, default=uuid4)
    title = CharField(max_length=255)
    # Inherits created_by and updated_by from AuditedModel

class Comment(AuditedModel):
    _database = "default"
    id = UUIDField(primary_key=True, default=uuid4)
    body = CharField(max_length=2000)
    # Inherits created_by and updated_by from AuditedModel

# AuditedModel itself has no _meta / table — only concrete subclasses do
article = Article(id=str(uuid4()), title="Hello", created_by="alice")
print(article.created_by)  # alice
```

Rules:
- Declare `abstract = True` inside an inner `class Meta:` **or** set `_abstract = True` as a class attribute.
- Abstract models do **not** get a table, `_meta`, or migration.
- Fields, `_inverse_foreign_keys`, and M2M definitions are all inherited by concrete subclasses.
- Concrete subclasses must still define their own primary key.

---

## Version History

| Version | Highlights |
|---|---|
| **v1.9.0** | Schema builder externalization: app-specific entity/field overrides removed from the ORM package and moved to `DatabaseProjectConfig` (`entity_overrides`, `field_overrides`); new `get_schema_builder_overrides()` accessor; `sql_executor/queries.py` reduced to generic TypedDicts + empty registry with a `register_query()` helper; all hardcoded project-name defaults removed from public APIs |
| **v1.9.0** | Cross-schema & multi-database FK support: `ForeignKey(to_schema='auth')` for same-database cross-schema FKs (e.g. `auth.users`); `ForeignKey(to_db='other_project')` for cross-database routing; `ForeignKeyReference` gains `to_db`/`to_schema`; `_unfetchable` now emits a `UserWarning` instead of silently returning `None`; `Users` stub removes `_unfetchable = True` so `auth.users` fetches work out of the box; introspection SQL captures referenced schema via `pg_namespace`; schema builder emits `to_schema` in generated code; `DatabaseProjectConfig.additional_schemas` replaces hardcoded `["auth"]` everywhere |
| **v1.8.0** | Window functions (`ROW_NUMBER`, `RANK`, `DENSE_RANK`, `LAG`, `LEAD`, `NTILE`, `CUME_DIST`, `PERCENT_RANK`, …) with `Window(expr, partition_by=…, order_by=…)`; CTEs (`CTE`, `with_cte()`, recursive support); `only()` / `defer()` column selection; `Paginator` with `page(n)`, `has_next`, `total_pages`, async iteration; `VersionField` for optimistic locking (raises `OptimisticLockError` on stale writes); abstract base models (`class Meta: abstract = True` with full field inheritance) |
| **v1.7.0** | `Q()` objects for OR/AND/NOT composition; aggregate expressions (`Sum`, `Avg`, `Min`, `Max`, `Count`); database functions (`Coalesce`, `Lower`, `Upper`, `Now`, `Cast`, `Extract`, …); `DISTINCT` / `DISTINCT ON`; `SELECT FOR UPDATE`; JSONB query operators; ORM-level `transaction()` context manager with savepoints; `Model.raw()` / `Model.raw_sql()`; `select_related()` JOIN eager loading; subquery expressions (`Subquery`, `Exists`, `OuterRef`); lifecycle signals (`pre_save`, `post_save`, `pre_create`, `post_create`, `pre_delete`, `post_delete`) |
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
