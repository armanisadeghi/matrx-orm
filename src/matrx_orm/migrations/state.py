"""Migration state tracking – reads/writes the ``_matrx_migrations`` table."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING

from matrx_orm.exceptions import MigrationError

if TYPE_CHECKING:
    from .operations import MigrationDB

TRACKING_TABLE = "_matrx_migrations"

CREATE_TRACKING_TABLE_SQL = f"""
CREATE TABLE IF NOT EXISTS {TRACKING_TABLE} (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    applied_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    checksum VARCHAR(64) NOT NULL
)
"""


@dataclass
class AppliedMigration:
    id: int
    name: str
    applied_at: datetime
    checksum: str


class MigrationState:
    """Reads and manipulates the migration tracking table."""

    def __init__(self, db: MigrationDB) -> None:
        self._db = db

    async def ensure_table(self) -> None:
        """Create the tracking table if it doesn't exist."""
        await self._db.execute(CREATE_TRACKING_TABLE_SQL)

    async def applied_migrations(self) -> list[AppliedMigration]:
        """Return all applied migrations ordered by id."""
        await self.ensure_table()
        rows = await self._db.fetch(
            f"SELECT id, name, applied_at, checksum FROM {TRACKING_TABLE} ORDER BY id"
        )
        return [
            AppliedMigration(
                id=r["id"],
                name=r["name"],
                applied_at=r["applied_at"],
                checksum=r["checksum"],
            )
            for r in rows
        ]

    async def applied_names(self) -> set[str]:
        """Return the set of migration names that have been applied."""
        applied = await self.applied_migrations()
        return {m.name for m in applied}

    async def record_migration(self, name: str, checksum: str) -> None:
        """Record a migration as applied."""
        await self._db.execute(
            f"INSERT INTO {TRACKING_TABLE} (name, checksum) VALUES ($1, $2)",
            name,
            checksum,
        )

    async def unrecord_migration(self, name: str) -> None:
        """Remove a migration record (for rollback)."""
        await self._db.execute(
            f"DELETE FROM {TRACKING_TABLE} WHERE name = $1",
            name,
        )

    async def verify_checksums(self, file_checksums: dict[str, str]) -> list[str]:
        """Return list of migration names whose stored checksum doesn't match the file."""
        applied = await self.applied_migrations()
        mismatches: list[str] = []
        for m in applied:
            if m.name in file_checksums and file_checksums[m.name] != m.checksum:
                mismatches.append(m.name)
        return mismatches

    @staticmethod
    def compute_checksum(source: str) -> str:
        """Compute SHA-256 checksum of migration file content."""
        return hashlib.sha256(source.encode("utf-8")).hexdigest()
