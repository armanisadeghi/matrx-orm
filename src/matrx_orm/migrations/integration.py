"""Integration between the migration system and the schema builder.

After migrations run, the schema builder can regenerate models from the
updated database, keeping generated code in sync with the live schema.
"""

from __future__ import annotations

from pathlib import Path

from .operations import MigrationDB
from .loader import MigrationLoader
from .executor import MigrationExecutor


async def migrate_and_rebuild(
    database: str,
    migrations_dir: str | Path = "migrations",
    schema: str = "public",
    database_project: str | None = None,
    additional_schemas: list[str] | None = None,
) -> dict[str, object]:
    """Apply pending migrations then regenerate models from the updated database.

    Parameters
    ----------
    database:
        The database config name used by ``AsyncDatabaseManager``.
    migrations_dir:
        Path to the migrations directory.
    schema:
        The PostgreSQL schema to target (default ``"public"``).
    database_project:
        The ``database_project`` name passed to the schema builder.
        Defaults to *database* if not provided.
    additional_schemas:
        Extra schemas the schema builder should introspect (e.g. ``["auth"]``).

    Returns
    -------
    dict with keys:
        ``applied`` – list of migration names applied
        ``schema_output`` – the dict returned by ``get_full_schema_object``
                           (or *None* if no migrations were applied)
    """
    db = MigrationDB(database)
    loader = MigrationLoader(migrations_dir)
    executor = MigrationExecutor(db, loader)
    applied = await executor.migrate()

    schema_output = None
    if applied:
        schema_output = rebuild_schema(
            schema=schema,
            database_project=database_project or database,
            additional_schemas=additional_schemas,
        )

    return {"applied": applied, "schema_output": schema_output}


def rebuild_schema(
    schema: str = "public",
    database_project: str = "default",
    additional_schemas: list[str] | None = None,
) -> dict[str, object]:
    """Run the schema builder to regenerate models from the current database state.

    This is a synchronous call that uses the existing ``SchemaManager``.
    """
    from matrx_orm.schema_builder.schema_manager import SchemaManager

    manager = SchemaManager(
        schema=schema,
        database_project=database_project,
        additional_schemas=additional_schemas or [],
    )
    manager.initialize()
    schema_entry = manager.schema.generate_schema_files()
    models = manager.schema.generate_models()

    return {"schema": schema_entry, "models": models}
