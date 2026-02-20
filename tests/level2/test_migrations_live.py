"""Level 2: Apply, rollback, status, checksum verification with real DB."""

import textwrap
from pathlib import Path

import pytest

from matrx_orm.migrations.executor import MigrationExecutor
from matrx_orm.migrations.loader import MigrationLoader
from matrx_orm.migrations.state import MigrationState


def _write_migration(mig_dir: Path, filename: str, up_sql: str, down_sql: str, deps: list[str] | None = None):
    mig_dir.mkdir(parents=True, exist_ok=True)
    dep_str = repr(deps or [])
    content = textwrap.dedent(f"""\
        dependencies = {dep_str}

        async def up(db):
            await db.execute(\"\"\"{up_sql}\"\"\")

        async def down(db):
            await db.execute(\"\"\"{down_sql}\"\"\")
    """)
    (mig_dir / filename).write_text(content, encoding="utf-8")


@pytest.mark.level2
class TestApplyMigration:
    async def test_apply_creates_table(self, migration_db, tmp_path):
        mig_dir = tmp_path / "migs"
        _write_migration(
            mig_dir,
            "0001_create_test_mig.py",
            up_sql="CREATE TABLE _test_migration_table (id SERIAL PRIMARY KEY, val TEXT)",
            down_sql="DROP TABLE IF EXISTS _test_migration_table",
        )

        executor = MigrationExecutor(migration_db, str(mig_dir))
        applied = await executor.migrate()
        assert len(applied) == 1

        rows = await migration_db.fetch(
            "SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = '_test_migration_table')"
        )
        assert rows[0].get("exists") is True

    async def test_apply_idempotent(self, migration_db, tmp_path):
        mig_dir = tmp_path / "migs2"
        _write_migration(
            mig_dir,
            "0001_idempotent.py",
            up_sql="CREATE TABLE IF NOT EXISTS _test_migration_table2 (id SERIAL PRIMARY KEY)",
            down_sql="DROP TABLE IF EXISTS _test_migration_table2",
        )

        executor = MigrationExecutor(migration_db, str(mig_dir))
        first = await executor.migrate()
        second = await executor.migrate()
        assert len(second) == 0

        await migration_db.execute("DROP TABLE IF EXISTS _test_migration_table2")
        state = MigrationState(migration_db)
        await state.unrecord_migration("0001_idempotent")


@pytest.mark.level2
class TestRollback:
    async def test_rollback_removes_table(self, migration_db, tmp_path):
        mig_dir = tmp_path / "migs_rb"
        _write_migration(
            mig_dir,
            "0001_rb_table.py",
            up_sql="CREATE TABLE _test_rb_table (id SERIAL PRIMARY KEY)",
            down_sql="DROP TABLE IF EXISTS _test_rb_table",
        )

        executor = MigrationExecutor(migration_db, str(mig_dir))
        await executor.migrate()
        rolled_back = await executor.rollback()
        assert len(rolled_back) >= 1

        rows = await migration_db.fetch(
            "SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = '_test_rb_table')"
        )
        assert rows[0].get("exists") is False


@pytest.mark.level2
class TestMigrationStatus:
    async def test_status_shows_applied(self, migration_db, tmp_path):
        mig_dir = tmp_path / "migs_st"
        _write_migration(
            mig_dir,
            "0001_status.py",
            up_sql="CREATE TABLE IF NOT EXISTS _test_status_table (id SERIAL PRIMARY KEY)",
            down_sql="DROP TABLE IF EXISTS _test_status_table",
        )

        executor = MigrationExecutor(migration_db, str(mig_dir))
        await executor.migrate()

        state = MigrationState(migration_db)
        applied = await state.applied_names()
        assert "0001_status" in applied

        await executor.rollback()
        await migration_db.execute("DROP TABLE IF EXISTS _test_status_table")


@pytest.mark.level2
class TestChecksumVerification:
    async def test_checksum_mismatch_detected(self, migration_db, tmp_path):
        mig_dir = tmp_path / "migs_ck"
        _write_migration(
            mig_dir,
            "0001_ck.py",
            up_sql="CREATE TABLE IF NOT EXISTS _test_ck_table (id SERIAL PRIMARY KEY)",
            down_sql="DROP TABLE IF EXISTS _test_ck_table",
        )

        executor = MigrationExecutor(migration_db, str(mig_dir))
        await executor.migrate()

        loader = MigrationLoader(str(mig_dir))
        migs = loader.discover()
        original_checksum = migs["0001_ck"].checksum

        (mig_dir / "0001_ck.py").write_text("dependencies = []\nasync def up(db):\n    pass\nasync def down(db):\n    pass\n")

        loader2 = MigrationLoader(str(mig_dir))
        migs2 = loader2.discover()
        new_checksum = migs2["0001_ck"].checksum
        assert new_checksum != original_checksum

        state = MigrationState(migration_db)
        mismatches = await state.verify_checksums({name: m.checksum for name, m in migs2.items()})
        assert "0001_ck" in mismatches

        await executor.rollback()
        await migration_db.execute("DROP TABLE IF EXISTS _test_ck_table")
