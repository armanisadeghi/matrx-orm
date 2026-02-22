"""
Sample Project — Schema Generation Runner
==========================================
Demonstrates the full schema generation workflow against real databases.

Run from the repository root:

    python tests/sample_project/run_schema_generation.py

Or run a specific database only:

    python tests/sample_project/run_schema_generation.py --db primary
    python tests/sample_project/run_schema_generation.py --db secondary

What this script does
---------------------
For each configured database it:
  1. Registers the database config (reads credentials from .env)
  2. Initialises SchemaManager — introspects tables, views, columns, FK/IFK/M2M
  3. Generates Python model + manager files  → generated/<db_name>/models/
  4. Generates JSON schema files            → generated/<db_name>/schema/
  5. Prints a summary analysis to stdout

The ``generated/`` directory is gitignored — it is safe to delete and regenerate
at any time.

Typical output structure
------------------------
tests/sample_project/
├── generated/
│   ├── primary/
│   │   ├── models/          ← Python Model + Manager files
│   │   └── schema/          ← JSON schema files
│   └── secondary/
│       ├── models/
│       └── schema/
"""

import argparse
import sys
import os
from pathlib import Path

# Allow running from the repo root without installing the package
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

# Register databases first
from tests.sample_project.database_registry import setup_databases  # noqa: E402

setup_databases()

from matrx_orm.schema_builder.schema_manager import SchemaManager  # noqa: E402

# Output base directory — gitignored
OUTPUT_BASE = Path(__file__).parent / "generated"

DATABASES = {
    "primary": {
        "database_project": "primary",
        "schema": "public",
        "additional_schemas": ["auth"],
        "description": "Main Supabase project (public + auth schemas)",
    },
    "secondary": {
        "database_project": "secondary",
        "schema": "public",
        "additional_schemas": [],
        "description": "Second Supabase project (public schema only)",
    },
}


def run_generation(db_name: str, cfg: dict) -> dict:
    """Run full schema generation for one database. Returns a summary dict."""
    output_dir = OUTPUT_BASE / db_name
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n{'='*60}")
    print(f"  Database: {db_name}")
    print(f"  {cfg['description']}")
    print(f"  Output:   {output_dir}")
    print(f"{'='*60}")

    print(f"\n[{db_name}] Initialising SchemaManager...")
    sm = SchemaManager(
        schema=cfg["schema"],
        database_project=cfg["database_project"],
        additional_schemas=cfg["additional_schemas"],
        save_direct=False,
    )
    sm.initialize()

    table_count = len(sm.schema.tables) if hasattr(sm.schema, "tables") else "?"
    view_count = len(sm.schema.views) if hasattr(sm.schema, "views") else "?"
    print(f"[{db_name}] Introspected {table_count} tables, {view_count} views.")

    print(f"[{db_name}] Generating schema files...")
    schema_entry = sm.schema.generate_schema_files()

    print(f"[{db_name}] Generating Python model + manager files...")
    models = sm.schema.generate_models()

    print(f"[{db_name}] Running schema analysis...")
    analysis = sm.analyze_schema()

    summary = {
        "db": db_name,
        "tables": table_count,
        "views": view_count,
        "analysis": analysis,
    }

    print(f"[{db_name}] Done.")
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(
        description="matrx-orm sample project — schema generation runner"
    )
    parser.add_argument(
        "--db",
        choices=list(DATABASES.keys()) + ["all"],
        default="all",
        help="Which database to generate (default: all)",
    )
    args = parser.parse_args()

    target_dbs = list(DATABASES.items()) if args.db == "all" else [(args.db, DATABASES[args.db])]

    results = []
    errors = []

    for db_name, cfg in target_dbs:
        try:
            summary = run_generation(db_name, cfg)
            results.append(summary)
        except Exception as exc:
            print(f"\n[{db_name}] ERROR: {exc}")
            errors.append((db_name, exc))

    # Final summary
    print(f"\n{'='*60}")
    print("  Schema Generation Complete")
    print(f"{'='*60}")
    for r in results:
        print(f"  {r['db']:12s}  {r['tables']} tables, {r['views']} views")
    for db_name, exc in errors:
        print(f"  {db_name:12s}  FAILED: {exc}")

    if errors:
        sys.exit(1)


if __name__ == "__main__":
    main()
