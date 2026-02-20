"""Runs pending migrations forward or rolls them back."""

from __future__ import annotations

from typing import TYPE_CHECKING

from matrx_orm.exceptions import MigrationError
from .state import MigrationState

if TYPE_CHECKING:
    from .loader import MigrationLoader
    from .operations import MigrationDB


class MigrationExecutor:
    """Applies and rolls back migrations against a live database."""

    def __init__(self, db: MigrationDB, loader: MigrationLoader) -> None:
        self._db = db
        self._loader = loader
        self._state = MigrationState(db)

    async def migrate(self) -> list[str]:
        """Apply all pending migrations in dependency order.

        Returns the names of newly-applied migrations.
        """
        await self._state.ensure_table()
        applied = await self._state.applied_names()
        order = self._loader.resolve_order()
        migrations = self._loader.migrations

        file_checksums = {name: m.checksum for name, m in migrations.items()}
        mismatches = await self._state.verify_checksums(file_checksums)
        if mismatches:
            raise MigrationError(
                migration=", ".join(mismatches),
                original_error=(
                    "Migration file(s) modified after being applied. "
                    "Create a new migration instead of editing applied ones."
                ),
            )

        newly_applied: list[str] = []
        for name in order:
            if name in applied:
                continue
            mig = migrations[name]
            try:
                await mig.up(self._db)
            except MigrationError:
                raise
            except Exception as exc:
                raise MigrationError(
                    migration=name,
                    original_error=exc,
                )
            await self._state.record_migration(name, mig.checksum)
            newly_applied.append(name)

        return newly_applied

    async def rollback(self, steps: int = 1) -> list[str]:
        """Roll back the last *steps* applied migrations in reverse order.

        Returns the names of rolled-back migrations.
        """
        await self._state.ensure_table()
        applied = await self._state.applied_migrations()
        migrations = self._loader.migrations

        to_rollback = list(reversed(applied))[:steps]
        rolled_back: list[str] = []

        for record in to_rollback:
            mig = migrations.get(record.name)
            if mig is None:
                raise MigrationError(
                    migration=record.name,
                    original_error="Migration file not found on disk – cannot roll back",
                )
            if mig.down is None:
                raise MigrationError(
                    migration=record.name,
                    original_error="Migration has no 'down' function – cannot roll back",
                )
            try:
                await mig.down(self._db)
            except MigrationError:
                raise
            except Exception as exc:
                raise MigrationError(
                    migration=record.name,
                    original_error=exc,
                )
            await self._state.unrecord_migration(record.name)
            rolled_back.append(record.name)

        return rolled_back
