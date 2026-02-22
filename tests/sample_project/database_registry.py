"""
Sample Project — Database Registry
===================================
This file demonstrates how to configure matrx-orm for a real-world multi-database
setup. It registers:

  1. ``primary``   — Main Supabase project (public schema + auth schema).
                     All application tables live here. auth.users is automatically
                     reachable because ``additional_schemas=["auth"]`` is set.

  2. ``secondary`` — A second Supabase project (or any remote Postgres database).
                     No cross-database relationships are declared yet; it is
                     registered so you can run queries and schema generation
                     against it independently.

How to use
----------
Import this module once at application startup before any model or query code runs:

    from tests.sample_project.database_registry import setup_databases
    setup_databases()

The setup_databases() call is idempotent — matrx-orm silently skips duplicate
registrations, so it is safe to call from multiple entry points.

Environment variables
---------------------
All credentials are read from the environment (or from .env via python-dotenv).
Copy .env.example → .env and fill in the real passwords before running.

Supabase connection notes
-------------------------
- Host format: db.<project-ref>.supabase.co
- Port: 5432 (direct connection, not the pooler)
- User: postgres
- Database name: postgres
- Password: the "Database Password" from Supabase → Settings → Database
- SSL is required and handled automatically by matrx-orm's connection pool.
"""

import os
from pathlib import Path

# ---------------------------------------------------------------------------
# Load .env from this directory (if present)
# ---------------------------------------------------------------------------
try:
    from dotenv import load_dotenv
    _env_path = Path(__file__).parent / ".env"
    if _env_path.exists():
        load_dotenv(_env_path)
except ImportError:
    # python-dotenv is optional — set env vars directly in your shell or CI
    pass

from matrx_orm import DatabaseProjectConfig, register_database


def setup_databases() -> None:
    """Register all database connections with matrx-orm."""

    # ------------------------------------------------------------------
    # 1. Primary database — main Supabase project (MY_MATRX)
    #
    # additional_schemas=["auth"] makes the auth schema visible to:
    #   - Schema builder (generates auth.users stub model)
    #   - ForeignKey resolution (fetch_fk on user_id columns works without
    #     _unfetchable = True)
    # ------------------------------------------------------------------
    primary_password = os.environ.get("PRIMARY_DB_PASSWORD", "")
    if primary_password:
        primary_config = DatabaseProjectConfig(
            name="primary",
            alias="primary",
            host=os.environ.get("PRIMARY_DB_HOST", "db.viyklljfdhtidwecakwx.supabase.co"),
            port=os.environ.get("PRIMARY_DB_PORT", "5432"),
            database_name=os.environ.get("PRIMARY_DB_NAME", "postgres"),
            user=os.environ.get("PRIMARY_DB_USER", "postgres"),
            password=primary_password,
            additional_schemas=["auth"],   # exposes auth.users and other auth.* tables
        )
        register_database(primary_config)
    else:
        print("[sample_project] PRIMARY_DB_PASSWORD not set — skipping primary database registration.")

    # ------------------------------------------------------------------
    # 2. Secondary database — second Supabase project (MATRX_DM)
    #
    # No additional_schemas declared — only the public schema is introspected.
    # No cross-database ForeignKey relationships are configured here yet.
    # To add cross-database FK fetching later, use:
    #   user_id = ForeignKey(Users, to_column="id", to_db="primary")
    # ------------------------------------------------------------------
    secondary_password = os.environ.get("SECONDARY_DB_PASSWORD", "")
    if secondary_password:
        secondary_config = DatabaseProjectConfig(
            name="secondary",
            alias="secondary",
            host=os.environ.get("SECONDARY_DB_HOST", "db.deayzgwvqfdeskkdwudy.supabase.co"),
            port=os.environ.get("SECONDARY_DB_PORT", "5432"),
            database_name=os.environ.get("SECONDARY_DB_NAME", "postgres"),
            user=os.environ.get("SECONDARY_DB_USER", "postgres"),
            password=secondary_password,
            additional_schemas=[],   # public schema only for now
        )
        register_database(secondary_config)
    else:
        print("[sample_project] SECONDARY_DB_PASSWORD not set — skipping secondary database registration.")


# Run when imported directly for quick validation
if __name__ == "__main__":
    setup_databases()
    print("Database registry configured successfully.")
    print("  primary   → db.viyklljfdhtidwecakwx.supabase.co (auth schema enabled)")
    print("  secondary → db.deayzgwvqfdeskkdwudy.supabase.co (public schema only)")
