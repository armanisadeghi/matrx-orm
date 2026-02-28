"""CLI-callable migration functions and ``matrx-orm`` entry-point subcommands.

Every public function here is usable both programmatically (``await makemigrations(...)``)
and from the command line (``matrx-orm makemigrations --database mydb``).
"""

from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path
from typing import TextIO

from .operations import MigrationDB
from .loader import MigrationLoader
from .state import MigrationState
from .executor import MigrationExecutor
from .diff import SchemaDiff
from .table_filter import TableFilter
from .integration import migrate_and_rebuild as _migrate_and_rebuild


def _out(msg: str, stream: TextIO = sys.stdout) -> None:
    stream.write(msg + "\n")
    stream.flush()


async def makemigrations(
    database: str,
    migrations_dir: str | Path = "migrations",
    name: str | None = None,
    schema: str = "public",
    include_tables: set[str] | None = None,
    exclude_tables: set[str] | None = None,
) -> Path | None:
    """Run the diff engine and generate a new migration file.

    Returns the path to the generated migration file, or ``None`` if
    there are no pending changes.

    Parameters
    ----------
    database:
        Database config name.
    migrations_dir:
        Directory where migration files are stored.
    name:
        Optional name suffix for the generated file.
    schema:
        PostgreSQL schema to diff (default ``"public"``).
    include_tables:
        When provided, *only* these table names are included in the diff.
        Mutually exclusive with ``exclude_tables``.
    exclude_tables:
        When provided, these table names are skipped during the diff.
        Mutually exclusive with ``include_tables``.
    """
    table_filter: TableFilter | None = None
    if include_tables is not None or exclude_tables is not None:
        table_filter = TableFilter(include=include_tables, exclude=exclude_tables)

    db = MigrationDB(database)
    diff = SchemaDiff(db, schema=schema, table_filter=table_filter)
    path = await diff.generate_migration_file(migrations_dir, name=name)
    if path:
        _out(f"Created migration: {path}")
    else:
        _out("No changes detected.")
    return path


async def migrate(
    database: str,
    migrations_dir: str | Path = "migrations",
) -> list[str]:
    """Apply all pending migrations.

    Returns the list of migration names that were applied.
    """
    db = MigrationDB(database)
    loader = MigrationLoader(migrations_dir)
    executor = MigrationExecutor(db, loader)
    applied = await executor.migrate()
    if applied:
        for name in applied:
            _out(f"  Applied: {name}")
        _out(f"Applied {len(applied)} migration(s).")
    else:
        _out("No pending migrations.")
    return applied


async def rollback(
    database: str,
    migrations_dir: str | Path = "migrations",
    steps: int = 1,
) -> list[str]:
    """Roll back the last *steps* migrations.

    Returns the list of migration names that were rolled back.
    """
    db = MigrationDB(database)
    loader = MigrationLoader(migrations_dir)
    executor = MigrationExecutor(db, loader)
    rolled_back = await executor.rollback(steps=steps)
    if rolled_back:
        for name in rolled_back:
            _out(f"  Rolled back: {name}")
        _out(f"Rolled back {len(rolled_back)} migration(s).")
    else:
        _out("Nothing to roll back.")
    return rolled_back


async def status(
    database: str,
    migrations_dir: str | Path = "migrations",
) -> dict[str, str]:
    """Show the status of all discovered migrations.

    Returns a dict of ``{name: "applied"|"pending"}``.
    """
    db = MigrationDB(database)
    loader = MigrationLoader(migrations_dir)
    state = MigrationState(db)
    await state.ensure_table()
    applied_names = await state.applied_names()
    order = loader.resolve_order()
    result: dict[str, str] = {}
    for name in order:
        is_applied = name in applied_names
        label = "applied" if is_applied else "pending"
        mark = "[x]" if is_applied else "[ ]"
        _out(f"  {mark} {name}")
        result[name] = label
    if not order:
        _out("  No migrations found.")
    return result


async def create_empty(
    database: str,
    migrations_dir: str | Path = "migrations",
    name: str = "custom",
) -> Path:
    """Create an empty migration file for hand-written SQL.

    Returns the path to the created file.
    """
    dir_path = Path(migrations_dir)
    dir_path.mkdir(parents=True, exist_ok=True)
    loader = MigrationLoader(dir_path)
    number = loader.next_number()
    filename = f"{number:04d}_{name}.py"
    filepath = dir_path / filename

    prev_number = number - 1
    deps = f'["{prev_number:04d}"]' if prev_number > 0 else "[]"

    content = (
        f'"""TODO: describe this migration."""\n'
        f"\n"
        f"dependencies = {deps}\n"
        f"\n"
        f"\n"
        f"async def up(db):\n"
        f"    pass\n"
        f"\n"
        f"\n"
        f"async def down(db):\n"
        f"    pass\n"
    )
    filepath.write_text(content, encoding="utf-8")
    _out(f"Created empty migration: {filepath}")
    return filepath


async def migrate_rebuild(
    database: str,
    migrations_dir: str | Path = "migrations",
    schema: str = "public",
    database_project: str | None = None,
) -> dict[str, list[str] | dict[str, object] | None]:
    """Apply pending migrations then regenerate models from the updated DB.

    Returns the result dict from ``migrate_and_rebuild``.

    Note: table filtering (``include_tables`` / ``exclude_tables``) applies only
    to :func:`makemigrations` (the diff/generation step).  This command applies
    already-generated migration files in full, so no filtering is relevant here.
    """
    result = await _migrate_and_rebuild(
        database=database,
        migrations_dir=migrations_dir,
        schema=schema,
        database_project=database_project,
    )
    applied = result["applied"]
    if applied:
        for name in applied:
            _out(f"  Applied: {name}")
        _out(f"Applied {len(applied)} migration(s).")
        _out("Regenerating models from updated schema...")
        _out("Done.")
    else:
        _out("No pending migrations – skipping schema rebuild.")
    return result


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="matrx-orm", description="Matrx ORM migration CLI")
    sub = parser.add_subparsers(dest="command")

    mk = sub.add_parser("makemigrations", help="Auto-detect schema changes and generate a migration file")
    mk.add_argument("--database", required=True, help="Database config name")
    mk.add_argument("--dir", default="migrations", help="Migrations directory")
    mk.add_argument("--name", default=None, help="Migration name suffix")
    mk.add_argument("--schema", default="public", help="Database schema to diff")
    mk_scope = mk.add_mutually_exclusive_group()
    mk_scope.add_argument(
        "--include-tables",
        nargs="+",
        metavar="TABLE",
        default=None,
        help="Only diff these tables (space-separated). Mutually exclusive with --exclude-tables.",
    )
    mk_scope.add_argument(
        "--exclude-tables",
        nargs="+",
        metavar="TABLE",
        default=None,
        help="Skip these tables during diff (space-separated). Mutually exclusive with --include-tables.",
    )

    mg = sub.add_parser("migrate", help="Apply all pending migrations")
    mg.add_argument("--database", required=True, help="Database config name")
    mg.add_argument("--dir", default="migrations", help="Migrations directory")

    rb = sub.add_parser("rollback", help="Roll back recent migrations")
    rb.add_argument("--database", required=True, help="Database config name")
    rb.add_argument("--dir", default="migrations", help="Migrations directory")
    rb.add_argument("--steps", type=int, default=1, help="Number of migrations to roll back")

    st = sub.add_parser("status", help="Show migration status")
    st.add_argument("--database", required=True, help="Database config name")
    st.add_argument("--dir", default="migrations", help="Migrations directory")

    ce = sub.add_parser("create_empty", help="Create an empty migration file")
    ce.add_argument("--database", required=True, help="Database config name (for numbering)")
    ce.add_argument("--dir", default="migrations", help="Migrations directory")
    ce.add_argument("--name", default="custom", help="Migration name suffix")

    mr = sub.add_parser("migrate_rebuild", help="Apply migrations then regenerate models")
    mr.add_argument("--database", required=True, help="Database config name")
    mr.add_argument("--dir", default="migrations", help="Migrations directory")
    mr.add_argument("--schema", default="public", help="Database schema")
    mr.add_argument("--database-project", default=None, help="Schema builder database_project name")

    return parser


def main(argv: list[str] | None = None) -> None:
    """Entry point for ``matrx-orm`` CLI."""
    parser = _build_parser()
    args = parser.parse_args(argv)

    if not args.command:
        parser.print_help()
        return

    match args.command:
        case "makemigrations":
            asyncio.run(makemigrations(
                args.database, args.dir,
                name=args.name,
                schema=args.schema,
                include_tables=set(args.include_tables) if args.include_tables else None,
                exclude_tables=set(args.exclude_tables) if args.exclude_tables else None,
            ))
        case "migrate":
            asyncio.run(migrate(args.database, args.dir))
        case "rollback":
            asyncio.run(rollback(args.database, args.dir, steps=args.steps))
        case "status":
            asyncio.run(status(args.database, args.dir))
        case "create_empty":
            asyncio.run(create_empty(args.database, args.dir, name=args.name))
        case "migrate_rebuild":
            asyncio.run(migrate_rebuild(
                args.database, args.dir,
                schema=args.schema,
                database_project=args.database_project,
            ))
        case _:
            parser.print_help()
