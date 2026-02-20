"""Level 1: type normalization, ORM-to-PG mapping, Operation.to_up_sql / to_down_sql."""

import pytest

from matrx_orm.migrations.diff import (
    Operation,
    PG_TYPE_ALIASES,
    ORM_TO_PG,
    _normalize_pg_type,
    _orm_type_to_pg,
)
from matrx_orm.migrations.ddl import (
    AlterColumnChanges,
    ColumnDef,
    ForeignKeyDef,
)


class TestNormalizePgType:
    @pytest.mark.parametrize("alias,expected", list(PG_TYPE_ALIASES.items()))
    def test_known_aliases(self, alias, expected):
        assert _normalize_pg_type(alias) == expected

    def test_already_normalized(self):
        assert _normalize_pg_type("integer") == "integer"

    def test_unknown_type(self):
        assert _normalize_pg_type("CUSTOM_TYPE") == "custom_type"

    def test_whitespace_stripped(self):
        assert _normalize_pg_type("  int4  ") == "integer"


class TestOrmTypeToPg:
    @pytest.mark.parametrize("orm,expected", [
        ("UUID", "uuid"),
        ("TEXT", "text"),
        ("INTEGER", "integer"),
        ("BIGINT", "bigint"),
        ("SMALLINT", "smallint"),
        ("FLOAT", "double precision"),
        ("BOOLEAN", "boolean"),
        ("TIMESTAMP", "timestamp with time zone"),
        ("DATE", "date"),
        ("JSONB", "jsonb"),
        ("NUMERIC", "numeric"),
    ])
    def test_direct_mappings(self, orm, expected):
        assert _orm_type_to_pg(orm) == expected

    def test_varchar_with_length(self):
        assert _orm_type_to_pg("VARCHAR(255)") == "character varying(255)"

    def test_varchar_no_length(self):
        assert _orm_type_to_pg("VARCHAR") == "character varying"

    def test_numeric_with_precision(self):
        assert _orm_type_to_pg("NUMERIC(10,2)") == "numeric(10,2)"

    def test_serial_to_integer(self):
        assert _orm_type_to_pg("SERIAL") == "integer"

    def test_bigserial_to_bigint(self):
        assert _orm_type_to_pg("BIGSERIAL") == "bigint"

    def test_unknown_lowered(self):
        assert _orm_type_to_pg("CUSTOM_TYPE") == "custom_type"


class TestOperationToUpSql:
    def test_create_table(self):
        cols = [ColumnDef(name="id", db_type="uuid", primary_key=True)]
        op = Operation(op_type="create_table", table="users", details={"columns": cols})
        sql_list = op.to_up_sql()
        assert len(sql_list) == 1
        assert 'CREATE TABLE "users"' in sql_list[0]

    def test_drop_table(self):
        op = Operation(op_type="drop_table", table="users")
        sql_list = op.to_up_sql()
        assert 'DROP TABLE IF EXISTS "users"' in sql_list[0]
        assert "CASCADE" in sql_list[0]

    def test_add_column(self):
        col = ColumnDef(name="email", db_type="text")
        op = Operation(op_type="add_column", table="users", details={"column": col})
        sql_list = op.to_up_sql()
        assert "ADD COLUMN" in sql_list[0]

    def test_drop_column(self):
        op = Operation(op_type="drop_column", table="users", details={"column_name": "email"})
        sql_list = op.to_up_sql()
        assert "DROP COLUMN" in sql_list[0]

    def test_alter_column(self):
        changes = AlterColumnChanges(set_nullable=True)
        op = Operation(op_type="alter_column", table="t", details={"column_name": "col", "changes": changes})
        sql_list = op.to_up_sql()
        assert "DROP NOT NULL" in sql_list[0]

    def test_add_foreign_key(self):
        fk = ForeignKeyDef(table="users", column="id", on_delete="CASCADE")
        op = Operation(op_type="add_foreign_key", table="posts", details={"fk": fk, "column": "user_id"})
        sql_list = op.to_up_sql()
        assert "FOREIGN KEY" in sql_list[0]

    def test_drop_foreign_key(self):
        op = Operation(op_type="drop_foreign_key", table="posts", details={"constraint_name": "fk_x"})
        sql_list = op.to_up_sql()
        assert "DROP CONSTRAINT" in sql_list[0]

    def test_unknown_op_raises(self):
        op = Operation(op_type="fly_to_moon", table="x")
        with pytest.raises(Exception):
            op.to_up_sql()


class TestOperationToDownSql:
    def test_create_table_reverses_to_drop(self):
        cols = [ColumnDef(name="id", db_type="uuid", primary_key=True)]
        op = Operation(op_type="create_table", table="users", details={"columns": cols})
        sql_list = op.to_down_sql()
        assert "DROP TABLE" in sql_list[0]

    def test_drop_table_reverses_to_create(self):
        cols = [ColumnDef(name="id", db_type="uuid", primary_key=True)]
        op = Operation(op_type="drop_table", table="users", details={"columns": cols})
        sql_list = op.to_down_sql()
        assert "CREATE TABLE" in sql_list[0]

    def test_drop_table_no_columns_comment(self):
        op = Operation(op_type="drop_table", table="users", details={})
        sql_list = op.to_down_sql()
        assert sql_list[0].startswith("--")

    def test_add_column_reverses_to_drop(self):
        col = ColumnDef(name="email", db_type="text")
        op = Operation(op_type="add_column", table="users", details={"column": col})
        sql_list = op.to_down_sql()
        assert "DROP COLUMN" in sql_list[0]

    def test_drop_column_with_old_col(self):
        old_col = ColumnDef(name="email", db_type="text")
        op = Operation(op_type="drop_column", table="users", details={"column_name": "email", "old_column": old_col})
        sql_list = op.to_down_sql()
        assert "ADD COLUMN" in sql_list[0]

    def test_alter_column_with_reverse(self):
        reverse = AlterColumnChanges(set_nullable=False)
        op = Operation(op_type="alter_column", table="t", details={
            "column_name": "col",
            "changes": AlterColumnChanges(set_nullable=True),
            "reverse_changes": reverse,
        })
        sql_list = op.to_down_sql()
        assert "SET NOT NULL" in sql_list[0]

    def test_add_foreign_key_reverses_to_drop(self):
        fk = ForeignKeyDef(table="users", column="id", constraint_name="fk_custom")
        op = Operation(op_type="add_foreign_key", table="posts", details={"fk": fk, "column": "user_id"})
        sql_list = op.to_down_sql()
        assert "DROP CONSTRAINT" in sql_list[0]


class TestOperationWithSchema:
    def test_create_table_with_schema(self):
        cols = [ColumnDef(name="id", db_type="uuid", primary_key=True)]
        op = Operation(op_type="create_table", table="users", schema="custom", details={"columns": cols})
        sql = op.to_up_sql()[0]
        assert '"custom"."users"' in sql
