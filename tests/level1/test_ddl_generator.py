"""Level 1: DDLGenerator — every static method."""

import pytest

from matrx_orm.migrations.ddl import (
    AlterColumnChanges,
    ColumnDef,
    ConstraintDef,
    DDLGenerator,
    ForeignKeyDef,
    IndexDef,
)


class TestColumnDefToSql:
    def test_basic(self):
        col = ColumnDef(name="name", db_type="TEXT")
        assert col.to_sql() == '"name" TEXT'

    def test_primary_key(self):
        col = ColumnDef(name="id", db_type="uuid", primary_key=True)
        sql = col.to_sql()
        assert "PRIMARY KEY" in sql
        assert "NOT NULL" not in sql

    def test_not_null(self):
        col = ColumnDef(name="email", db_type="TEXT", nullable=False)
        assert "NOT NULL" in col.to_sql()

    def test_unique(self):
        col = ColumnDef(name="email", db_type="TEXT", unique=True)
        assert "UNIQUE" in col.to_sql()

    def test_default(self):
        col = ColumnDef(name="active", db_type="BOOLEAN", default="true")
        assert "DEFAULT true" in col.to_sql()

    def test_references(self):
        fk = ForeignKeyDef(table="users", column="id", on_delete="CASCADE")
        col = ColumnDef(name="user_id", db_type="uuid", references=fk)
        sql = col.to_sql()
        assert 'REFERENCES "users"("id")' in sql
        assert "ON DELETE CASCADE" in sql


class TestCreateTable:
    def test_basic(self):
        cols = [
            ColumnDef(name="id", db_type="uuid", primary_key=True),
            ColumnDef(name="name", db_type="TEXT"),
        ]
        sql = DDLGenerator.create_table("users", cols)
        assert sql.startswith('CREATE TABLE "users"')
        assert '"id" uuid PRIMARY KEY' in sql
        assert '"name" TEXT' in sql

    def test_with_schema(self):
        cols = [ColumnDef(name="id", db_type="uuid", primary_key=True)]
        sql = DDLGenerator.create_table("users", cols, schema="public")
        assert '"public"."users"' in sql

    def test_with_constraints(self):
        cols = [ColumnDef(name="id", db_type="uuid", primary_key=True)]
        constraints = [ConstraintDef(name="ck_positive", constraint_type="CHECK", expression="id IS NOT NULL")]
        sql = DDLGenerator.create_table("t", cols, constraints=constraints)
        assert 'CONSTRAINT "ck_positive"' in sql


class TestDropTable:
    def test_basic(self):
        sql = DDLGenerator.drop_table("users")
        assert sql == 'DROP TABLE IF EXISTS "users"'

    def test_cascade(self):
        sql = DDLGenerator.drop_table("users", cascade=True)
        assert sql.endswith(" CASCADE")

    def test_with_schema(self):
        sql = DDLGenerator.drop_table("users", schema="public")
        assert '"public"."users"' in sql


class TestAddColumn:
    def test_basic(self):
        col = ColumnDef(name="email", db_type="TEXT")
        sql = DDLGenerator.add_column("users", col)
        assert sql == 'ALTER TABLE "users" ADD COLUMN "email" TEXT'

    def test_with_schema(self):
        col = ColumnDef(name="email", db_type="TEXT")
        sql = DDLGenerator.add_column("users", col, schema="public")
        assert '"public"."users"' in sql


class TestDropColumn:
    def test_basic(self):
        sql = DDLGenerator.drop_column("users", "email")
        assert sql == 'ALTER TABLE "users" DROP COLUMN IF EXISTS "email"'

    def test_with_schema(self):
        sql = DDLGenerator.drop_column("users", "email", schema="s")
        assert '"s"."users"' in sql


class TestAlterColumn:
    def test_rename(self):
        changes = AlterColumnChanges(rename_to="new_name")
        stmts = DDLGenerator.alter_column("users", "old_name", changes)
        assert len(stmts) == 1
        assert 'RENAME COLUMN "old_name" TO "new_name"' in stmts[0]

    def test_type_change(self):
        changes = AlterColumnChanges(new_type="bigint")
        stmts = DDLGenerator.alter_column("t", "col", changes)
        assert len(stmts) == 1
        assert "TYPE bigint" in stmts[0]
        assert 'USING "col"::bigint' in stmts[0]

    def test_set_nullable(self):
        changes = AlterColumnChanges(set_nullable=True)
        stmts = DDLGenerator.alter_column("t", "col", changes)
        assert "DROP NOT NULL" in stmts[0]

    def test_set_not_null(self):
        changes = AlterColumnChanges(set_nullable=False)
        stmts = DDLGenerator.alter_column("t", "col", changes)
        assert "SET NOT NULL" in stmts[0]

    def test_new_default(self):
        changes = AlterColumnChanges(new_default="'hello'")
        stmts = DDLGenerator.alter_column("t", "col", changes)
        assert "SET DEFAULT 'hello'" in stmts[0]

    def test_drop_default(self):
        changes = AlterColumnChanges(drop_default=True)
        stmts = DDLGenerator.alter_column("t", "col", changes)
        assert "DROP DEFAULT" in stmts[0]

    def test_multiple_changes(self):
        changes = AlterColumnChanges(new_type="text", set_nullable=True, new_default="'x'")
        stmts = DDLGenerator.alter_column("t", "col", changes)
        assert len(stmts) == 3

    def test_no_changes(self):
        changes = AlterColumnChanges()
        stmts = DDLGenerator.alter_column("t", "col", changes)
        assert stmts == []

    def test_with_schema(self):
        changes = AlterColumnChanges(set_nullable=True)
        stmts = DDLGenerator.alter_column("t", "col", changes, schema="s")
        assert '"s"."t"' in stmts[0]


class TestAddIndex:
    def test_basic(self):
        idx = IndexDef(name="idx_name", table="users", columns=["name"])
        sql = DDLGenerator.add_index(idx)
        assert sql == 'CREATE INDEX IF NOT EXISTS "idx_name" ON "users" ("name")'

    def test_unique(self):
        idx = IndexDef(name="idx_email", table="users", columns=["email"], unique=True)
        sql = DDLGenerator.add_index(idx)
        assert "UNIQUE INDEX" in sql

    def test_multi_column(self):
        idx = IndexDef(name="idx_multi", table="t", columns=["a", "b"])
        sql = DDLGenerator.add_index(idx)
        assert '("a", "b")' in sql

    def test_custom_method(self):
        idx = IndexDef(name="idx_gin", table="t", columns=["data"], method="gin")
        sql = DDLGenerator.add_index(idx)
        assert "USING gin" in sql

    def test_partial_where(self):
        idx = IndexDef(name="idx_part", table="t", columns=["status"], where="active = true")
        sql = DDLGenerator.add_index(idx)
        assert "WHERE active = true" in sql


class TestDropIndex:
    def test_basic(self):
        assert DDLGenerator.drop_index("idx_name") == 'DROP INDEX IF EXISTS "idx_name"'


class TestAddConstraint:
    def test_basic(self):
        c = ConstraintDef(name="ck_age", constraint_type="CHECK", expression="age > 0")
        sql = DDLGenerator.add_constraint("users", c)
        assert 'CONSTRAINT "ck_age" CHECK (age > 0)' in sql

    def test_with_schema(self):
        c = ConstraintDef(name="ck", constraint_type="CHECK", expression="x > 0")
        sql = DDLGenerator.add_constraint("t", c, schema="s")
        assert '"s"."t"' in sql


class TestDropConstraint:
    def test_basic(self):
        sql = DDLGenerator.drop_constraint("users", "ck_age")
        assert sql == 'ALTER TABLE "users" DROP CONSTRAINT IF EXISTS "ck_age"'


class TestAddForeignKey:
    def test_basic(self):
        fk = ForeignKeyDef(table="users", column="id", on_delete="CASCADE")
        sql = DDLGenerator.add_foreign_key("posts", fk, "user_id")
        assert 'FOREIGN KEY ("user_id") REFERENCES "users"("id")' in sql
        assert "ON DELETE CASCADE" in sql

    def test_custom_constraint_name(self):
        fk = ForeignKeyDef(table="users", column="id", constraint_name="my_fk")
        sql = DDLGenerator.add_foreign_key("posts", fk, "user_id")
        assert '"my_fk"' in sql

    def test_auto_constraint_name(self):
        fk = ForeignKeyDef(table="users", column="id")
        sql = DDLGenerator.add_foreign_key("posts", fk, "user_id")
        assert "fk_posts_user_id_users_id" in sql

    def test_on_update(self):
        fk = ForeignKeyDef(table="users", column="id", on_update="SET NULL")
        sql = DDLGenerator.add_foreign_key("posts", fk, "user_id")
        assert "ON UPDATE SET NULL" in sql


class TestDropForeignKey:
    def test_basic(self):
        sql = DDLGenerator.drop_foreign_key("posts", "fk_posts_user_id")
        assert sql == 'ALTER TABLE "posts" DROP CONSTRAINT IF EXISTS "fk_posts_user_id"'


class TestRenameTable:
    def test_basic(self):
        sql = DDLGenerator.rename_table("old_name", "new_name")
        assert sql == 'ALTER TABLE "old_name" RENAME TO "new_name"'

    def test_with_schema(self):
        sql = DDLGenerator.rename_table("old", "new", schema="s")
        assert '"s"."old"' in sql
