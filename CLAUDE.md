# CLAUDE.md — Matrx ORM Project Instructions

> Project-specific instructions for AI assistants and new developers.
> Current version: **3.0.0**

---

## What This Is

**Async-first PostgreSQL ORM built for teams who live in their database UI as much as their IDE.**

Two directions of travel, both first-class:
- **DB → Code** (reverse migrations): introspect any existing Postgres schema and auto-generate typed models, managers, relationships, and views.
- **Code → DB** (forward migrations): write models in Python, run the CLI, schema is applied.

---

## Core Architecture — Read This First

### The five objects you will encounter everywhere

| Object | File | Role |
|---|---|---|
| `Model` | `core/base.py` | Maps to a DB table. Fields, PKs, FKs, IFKs, M2Ms declared here. |
| `ModelView` | `core/model_view.py` | Declarative projection: prefetch relations, compute fields, shape output. Applied per-instance, stores results flat. |
| `BaseManager` | `core/extended.py` | Per-table singleton with full CRUD, bulk ops, relation fetchers, cache integration. Subclassed by generated managers. |
| `QueryBuilder` | `query/builder.py` | Chainable query API — `filter`, `order_by`, `limit`, `select_related`, `annotate`, etc. Returns from `Model.filter()`. |
| `QueryExecutor` | `query/executor.py` | SQL builder and runner. Receives the query dict from `QueryBuilder`. Not called directly. |

### How a fetch flows

```
Model.filter(**kwargs)          → QueryBuilder
  .select_related("fk_field")  → JOIN added to SQL
  .limit(20).all()             → QueryExecutor._execute() → asyncpg → list[Model]
                                → StateManager.cache_bulk()
                                → returned to caller
```

---

## Relationship System

Three relationship types, all declared on the model, all fetched concurrently.

### ForeignKey (FK) — outward, one-to-one
```python
# Declaration (on the model)
customer_id = ForeignKey("Customer", to_column="id", related_name="orders")

# Single fetch
customer = await order.fetch_fk("customer_id")

# JOIN-based (no second query)
orders = await Order.filter().select_related("customer_id").all()
customer = orders[0].get_related("customer_id")
```

### InverseForeignKey (IFK) — inward, one-to-many
```python
# Declaration (on the model that is pointed AT)
_inverse_foreign_keys = {
    "line_items": {
        "from_model": "LineItem",
        "from_field": "order_id",
        "referenced_field": "id",
    }
}

# Fetch
line_items = await order.fetch_ifk("line_items")   # list[LineItem]
```

### ManyToMany (M2M) — via junction table
```python
# Declarative (ORM creates the junction table)
tags = ManyToManyField("Tag", related_name="orders")

# Config-based (existing junction table)
_many_to_many = {
    "tags": {
        "junction_table": "order_tags",
        "source_column": "order_id",
        "target_column": "tag_id",
        "target_model": "Tag",
        "related_name": "tags",
    }
}

# Fetch — single JOIN query (not two hops)
tags = await order.fetch_m2m("tags")   # list[Tag]

# Mutations
await order.add_m2m("tags", tag_id_1, tag_id_2)
await order.remove_m2m("tags", tag_id_1)
await order.set_m2m("tags", [tag_id_1, tag_id_2])  # replaces all
await order.clear_m2m("tags")
```

### Fetching everything at once
All three groups fire **concurrently** via `asyncio.gather`:
```python
result = await order.fetch_all_related()
# {"foreign_keys": {...}, "inverse_foreign_keys": {...}, "many_to_many": {...}}

# Or let the manager do it
order = await manager.get_item_with_all_related(order_id)
order.get_related("customer_id")  # already loaded
order.get_related("line_items")   # already loaded
order.get_related("tags")         # already loaded
```

Within each group, individual relation fetches also run concurrently. A model with 3 FKs issues 3 queries in parallel, not in series.

---

## ModelView — The Projection Layer

`ModelView` replaces the old `BaseDTO`. It is not a wrapper object — it is a recipe that runs once at load time and stores results **flat on the model instance**. Nothing is duplicated. `to_dict()` returns the application-shaped output directly.

```python
from matrx_orm import ModelView

class OrderView(ModelView):
    # Fetched concurrently before computed fields run
    prefetch = ["customer_id", "line_items", "tags"]

    # Omit from to_dict() output
    exclude = ["internal_notes", "raw_webhook_payload"]

    # Replace the FK id column with the full related object
    # "customer_id" disappears; "customer" appears with the full object
    inline_fk = {"customer_id": "customer"}

    # Any async method (no leading underscore) = computed field.
    # Receives the model instance. Errors are warnings, never exceptions.
    async def display_name(self, model) -> str:
        customer = model.get_related("customer_id")
        return f"{customer.first_name} {customer.last_name}" if customer else "Unknown"

    async def item_count(self, model) -> int:
        return len(model.get_related("line_items") or [])
```

Wire to a manager (the normal path):
```python
class OrderBase(BaseManager[Order]):
    view_class = OrderView   # applied automatically on every load
```

Or apply directly to any instance:
```python
await OrderView.apply(order)
order.display_name   # "Jane Smith"
order.customer       # full Customer object (not just the UUID)
order.to_dict()      # flat, clean, ready to send to the client
```

**Write path is unaffected.** `_view_data`, `_view_excluded`, `_view_inlined_fks` are all invisible to `update()` and `save()`. Only `_fields` go to the DB.

### Migrating from BaseDTO
`BaseDTO` still works. A `DeprecationWarning` is emitted when a new subclass is *defined* (not on use), so existing deployments are silent. Migrate one manager at a time.

---

## Auto-Generated Managers

Every table gets a generated `{ModelName}Base` class and a singleton `{ModelName}Manager`. The generated code lives in `database/orm/managers/` (or wherever your project configures). **Do not edit generated files directly** — add customisation in the manager subclass.

Generated manager includes:
- `create_{model}`, `delete_{model}`, `update_{model}`
- `load_{model}_by_id`, `load_{model}s`
- `filter_{model}s`
- Named relation methods for every FK, IFK, and M2M
- `get_{model}_with_all_related`
- Dict variants: `get_{model}_dict`, `load_{model}s_get_dict`, etc.

Generated view (`{ModelName}View`) includes:
- `prefetch` pre-filled with all relation names from the schema
- Empty `exclude`, `inline_fk` — configure as needed
- Stubs for computed fields

---

## Schema Introspection — DB → Code

Point the `SchemaManager` at any Postgres database. It reads the live schema, generates models and managers:

```python
from matrx_orm.schema_builder.schema_manager import SchemaManager

sm = SchemaManager(schema="public", database_project="my_project")
sm.initialize()
sm.schema.generate_schema_files()   # writes schema JSON (source of truth)
sm.schema.generate_models()         # writes Model + Manager + View Python files
```

What gets generated:
- `{model}.py` — fully-typed `Model` with all columns, PKs, FKs declared
- `{model}_manager.py` — `{Model}View`, `{Model}Base`, `{Model}Manager` singleton

After any schema change in the DB UI: re-run `generate_models()`. Checksum detection skips unchanged tables.

---

## Forward Migrations — Code → DB

```bash
# Generate migration files from model changes
matrx-orm makemigrations --database my_project --dir migrations

# Apply pending migrations
matrx-orm migrate --database my_project --dir migrations

# Full round-trip: migrate then regenerate models
python -c "
from matrx_orm import migrate_and_rebuild
import asyncio
asyncio.run(migrate_and_rebuild('my_project', './migrations', output_dir='./database/main'))
"
```

---

## QueryBuilder Reference

```python
# Basic
await Order.filter(status="paid").order_by("-created_at").limit(20).all()
await Order.get(id=order_id)
await Order.get_or_none(id=order_id)
await Order.exists(status="paid")
await Order.count(status="paid")

# Q objects for complex conditions
from matrx_orm import Q
await Order.filter(Q(status="paid") | Q(status="refunded")).all()

# Column selection
await Order.filter().only("id", "status", "total").all()
await Order.filter().defer("large_blob_field").all()

# Aggregation
result = await Order.filter(status="paid").aggregate(total=Sum("amount"), count=Count("id"))

# Raw SQL
rows = await Order.raw_sql("SELECT date_trunc('month', created_at) as month, count(*) FROM orders GROUP BY 1")

# Bulk operations
await Order.bulk_create([{"status": "draft", ...}, ...])
await Order.update_where({"status": "draft"}, status="expired")
await Order.delete_where(status="expired")

# Upsert
await Order.upsert(data, conflict_fields=["external_id"], update_fields=["status", "total"])

# Pagination
paginator = Paginator(Order.filter(status="paid"), page_size=20)
page = await paginator.get_page(1)

# pgvector similarity search
results = await Document.nearest("embedding", query_vector, metric="cosine").limit(10).all()
```

---

## Caching

Per-model, transparent, in-memory. Configure on the model class:

```python
class Order(Model):
    _cache_policy = CachePolicy.SHORT_TERM   # PERMANENT | LONG_TERM | SHORT_TERM | INSTANT
    _cache_timeout = 300                      # seconds, or None for policy default
```

Cache is populated automatically on `get()`, `all()`, `filter().all()`. Bypass with `use_cache=False`. Writes invalidate the relevant entry automatically.

---

## Key Files to Know

| File | What it does |
|---|---|
| `core/base.py` | `Model`, `ModelMeta`, `RuntimeMixin`, `ModelOptions` — the entire model layer |
| `core/model_view.py` | `ModelView`, `ModelViewMeta` — the projection/view system |
| `core/extended.py` | `BaseDTO` (legacy), `BaseManager` — manager base class |
| `core/relations.py` | `ForeignKeyReference`, `InverseForeignKeyReference`, `ManyToManyReference` — fetch logic |
| `core/fields.py` | All field types (`CharField`, `UUIDField`, `JSONBField`, `VectorField`, etc.) |
| `core/expressions.py` | `Q`, `F`, `Sum`, `Avg`, `Window`, `CTE`, `Subquery`, `Exists`, `VectorDistance` |
| `query/builder.py` | `QueryBuilder` — chainable query API |
| `query/executor.py` | `QueryExecutor` — SQL construction and execution |
| `schema_builder/schema_manager.py` | `SchemaManager` — DB introspection entry point |
| `schema_builder/helpers/base_generators.py` | Code generators for models, views, managers |
| `state.py` | `StateManager`, `CachePolicy` — the cache layer |
| `migrations/` | Forward migration engine |

---

## Reserved Names

Do not use these as model field names — they conflict with ORM internals. Full list in `RESERVED_NAMES.md`. Key ones: `id`, `save`, `update`, `delete`, `create`, `filter`, `get`, `all`, `runtime`, `dto`, `_meta`, `_fields`, `_dynamic_data`, `_view_data`.

---

## Task Tracking

- **`TASKS.md`** — Central index of all active work, priorities, and status.
- **`TASKS-TEMPLATE.md`** — Copy this to create a new task file.
- Task files live next to the code they affect, named `FEATURE-NAME-TASK.md`.

When working on tracked tasks: check off completed items, update status/date, keep `TASKS.md` in sync.

---

**Stack:** Python 3.10+ · asyncpg · psycopg3 · PostgreSQL (Supabase, RDS, self-hosted, Docker)
