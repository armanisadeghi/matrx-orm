"""Level 2: SchemaDiff — capture_db_state, compute_diff against live DB."""

import pytest

from matrx_orm.core.fields import UUIDField, CharField
from matrx_orm.core.base import Model, ModelMeta
from matrx_orm.core.registry import ModelRegistry
from matrx_orm.migrations.diff import SchemaDiff


@pytest.mark.level2
class TestCaptureDbState:
    async def test_captures_existing_tables(self, migration_db):
        diff = SchemaDiff(migration_db, schema="public")
        state = await diff.capture_db_state()
        assert "test_user" in state
        assert "test_post" in state
        assert "test_tag" in state

    async def test_captures_columns(self, migration_db):
        diff = SchemaDiff(migration_db, schema="public")
        state = await diff.capture_db_state()
        user_table = state["test_user"]
        assert "id" in user_table.columns
        assert "username" in user_table.columns
        assert "email" in user_table.columns

    async def test_column_properties(self, migration_db):
        diff = SchemaDiff(migration_db, schema="public")
        state = await diff.capture_db_state()
        id_col = state["test_user"].columns["id"]
        assert id_col.primary_key is True
        username_col = state["test_user"].columns["username"]
        assert username_col.unique is True


@pytest.mark.level2
class TestComputeDiff:
    async def test_no_diff_for_existing_models(self, migration_db):
        diff = SchemaDiff(migration_db, schema="public")
        ops = await diff.compute_diff()
        table_ops = {(o.op_type, o.table) for o in ops}
        assert ("create_table", "test_user") not in table_ops

    async def test_detects_new_model(self, migration_db):
        ModelMeta("TestNewTable", (Model,), {
            "id": UUIDField(primary_key=True),
            "label": CharField(max_length=100),
            "_database": "matrx_test",
            "_table_name": "test_new_table",
        })

        try:
            diff = SchemaDiff(migration_db, schema="public")
            ops = await diff.compute_diff()
            create_ops = [o for o in ops if o.op_type == "create_table" and o.table == "test_new_table"]
            assert len(create_ops) == 1
        finally:
            ModelRegistry._models.pop("TestNewTable", None)

    async def test_detects_dropped_table(self, migration_db):
        await migration_db.execute("CREATE TABLE IF NOT EXISTS _test_orphan (id SERIAL PRIMARY KEY)")
        try:
            diff = SchemaDiff(migration_db, schema="public")
            ops = await diff.compute_diff()
            drop_ops = [o for o in ops if o.op_type == "drop_table" and o.table == "_test_orphan"]
            assert len(drop_ops) == 1
        finally:
            await migration_db.execute("DROP TABLE IF EXISTS _test_orphan")
