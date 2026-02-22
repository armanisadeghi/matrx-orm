# matrx-orm — Sample Project

This directory contains a complete, runnable example of how to use matrx-orm
with real Supabase databases. It demonstrates:

- Database config registration (`database_registry.py`)
- Schema generation against live databases (`run_schema_generation.py`)
- pytest integration tests for schema generation (`test_schema_generation.py`)

## Setup

### 1. Add your credentials

```bash
cp .env.example .env
# then edit .env and fill in PRIMARY_DB_PASSWORD and SECONDARY_DB_PASSWORD
```

The `.env` file is gitignored and will never be committed.

**Where to find your Supabase database password:**
Supabase dashboard → Settings → Database → Connection string section → Password

### 2. Install dependencies (if not already done)

```bash
cd <repo root>
uv sync
# or: pip install -e ".[dev]"
```

## Database layout

| Name        | Supabase project             | Schemas        | Purpose                                 |
|-------------|------------------------------|----------------|-----------------------------------------|
| `primary`   | viyklljfdhtidwecakwx         | public + auth  | Main application database               |
| `secondary` | deayzgwvqfdeskkdwudy         | public         | Second project (no cross-DB FKs yet)    |

The `primary` database has `additional_schemas=["auth"]`, which means:
- The schema builder introspects and generates code for `auth.users` and other `auth.*` tables
- `ForeignKey` fields pointing at `auth.users` resolve correctly via `fetch_fk()` without hitting `_unfetchable = True`

## Running schema generation

```bash
# From the repo root — generates models for both databases
python tests/sample_project/run_schema_generation.py

# Primary database only
python tests/sample_project/run_schema_generation.py --db primary

# Secondary database only
python tests/sample_project/run_schema_generation.py --db secondary
```

Generated files land in `tests/sample_project/generated/` (gitignored).

## Running the pytest tests

```bash
# Run sample project tests only
pytest tests/sample_project/ -v -s

# Run just primary or secondary
pytest tests/sample_project/ -v -s -k "Primary"
pytest tests/sample_project/ -v -s -k "Secondary"

# Run all tests except schema tests (useful for CI without DB credentials)
pytest --ignore=tests/sample_project/ --ignore=tests/level2/
```

## Generated output structure

```
generated/
├── primary/
│   ├── models/          ← Python Model + Manager files
│   └── schema/          ← JSON schema files
└── secondary/
    ├── models/
    └── schema/
```

The `generated/` directory is gitignored. Delete it and rerun at any time.

## Using the registry in your own project

Copy `database_registry.py` into your project and adapt it:

```python
from matrx_orm import DatabaseProjectConfig, register_database

config = DatabaseProjectConfig(
    name="my_project",
    alias="my_project",
    host="db.<ref>.supabase.co",
    port="5432",
    database_name="postgres",
    user="postgres",
    password=os.environ["DB_PASSWORD"],
    additional_schemas=["auth"],        # include auth.users
)
register_database(config)
```

Then call `register_database()` once at application startup before any ORM query runs.

## Cross-database FK example (future)

When you want a model in `secondary` to reference a model in `primary`:

```python
# In a secondary-database model
class Order(Model):
    user_id = ForeignKey(
        to_model="Users",
        to_column="id",
        to_db="primary",          # routes fetch_fk() to the primary pool
        to_schema="auth",         # qualifies the table as auth.users
    )
```

`fetch_fk("user_id")` will automatically use the `primary` connection pool and
return the `Users` instance from the auth schema.
