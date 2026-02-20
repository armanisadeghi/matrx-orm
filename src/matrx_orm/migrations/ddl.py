"""DDL generator – converts high-level schema operations into PostgreSQL SQL strings."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ColumnDef:
    """Describes a single database column for DDL generation."""
    name: str
    db_type: str
    nullable: bool = True
    primary_key: bool = False
    unique: bool = False
    default: str | None = None
    references: ForeignKeyDef | None = None

    def to_sql(self) -> str:
        parts = [f'"{self.name}"', self.db_type]
        if self.primary_key:
            parts.append("PRIMARY KEY")
        if not self.nullable and not self.primary_key:
            parts.append("NOT NULL")
        if self.unique and not self.primary_key:
            parts.append("UNIQUE")
        if self.default is not None:
            parts.append(f"DEFAULT {self.default}")
        if self.references:
            ref = self.references
            on_delete = f" ON DELETE {ref.on_delete}" if ref.on_delete else ""
            parts.append(
                f'REFERENCES "{ref.table}"("{ref.column}"){on_delete}'
            )
        return " ".join(parts)


@dataclass
class ForeignKeyDef:
    """Foreign key reference for column definitions and standalone constraints."""
    table: str
    column: str
    on_delete: str | None = None
    on_update: str | None = None
    constraint_name: str | None = None


@dataclass
class IndexDef:
    """Describes a database index."""
    name: str
    table: str
    columns: list[str]
    unique: bool = False
    method: str = "btree"
    where: str | None = None


@dataclass
class ConstraintDef:
    """Describes a table constraint (CHECK, UNIQUE, EXCLUDE, etc.)."""
    name: str
    constraint_type: str
    expression: str


@dataclass
class AlterColumnChanges:
    """Describes changes to apply to an existing column."""
    new_type: str | None = None
    set_nullable: bool | None = None
    new_default: str | None = None
    drop_default: bool = False
    rename_to: str | None = None


class DDLGenerator:
    """Generates PostgreSQL DDL statements from high-level descriptions."""

    @staticmethod
    def create_table(
        name: str,
        columns: list[ColumnDef],
        constraints: list[ConstraintDef] | None = None,
        schema: str | None = None,
    ) -> str:
        qualified = f'"{schema}"."{name}"' if schema else f'"{name}"'
        col_defs = [col.to_sql() for col in columns]
        if constraints:
            for c in constraints:
                col_defs.append(f'CONSTRAINT "{c.name}" {c.constraint_type} ({c.expression})')
        body = ",\n    ".join(col_defs)
        return f"CREATE TABLE {qualified} (\n    {body}\n)"

    @staticmethod
    def drop_table(name: str, schema: str | None = None, cascade: bool = False) -> str:
        qualified = f'"{schema}"."{name}"' if schema else f'"{name}"'
        suffix = " CASCADE" if cascade else ""
        return f"DROP TABLE IF EXISTS {qualified}{suffix}"

    @staticmethod
    def add_column(table: str, column: ColumnDef, schema: str | None = None) -> str:
        qualified = f'"{schema}"."{table}"' if schema else f'"{table}"'
        return f"ALTER TABLE {qualified} ADD COLUMN {column.to_sql()}"

    @staticmethod
    def drop_column(table: str, column: str, schema: str | None = None) -> str:
        qualified = f'"{schema}"."{table}"' if schema else f'"{table}"'
        return f'ALTER TABLE {qualified} DROP COLUMN IF EXISTS "{column}"'

    @staticmethod
    def alter_column(
        table: str,
        column: str,
        changes: AlterColumnChanges,
        schema: str | None = None,
    ) -> list[str]:
        """Return a list of ALTER TABLE statements for the requested changes."""
        qualified = f'"{schema}"."{table}"' if schema else f'"{table}"'
        stmts: list[str] = []

        if changes.rename_to:
            stmts.append(
                f'ALTER TABLE {qualified} RENAME COLUMN "{column}" TO "{changes.rename_to}"'
            )
            column = changes.rename_to

        if changes.new_type:
            stmts.append(
                f'ALTER TABLE {qualified} ALTER COLUMN "{column}" TYPE {changes.new_type} USING "{column}"::{changes.new_type}'
            )

        if changes.set_nullable is True:
            stmts.append(
                f'ALTER TABLE {qualified} ALTER COLUMN "{column}" DROP NOT NULL'
            )
        elif changes.set_nullable is False:
            stmts.append(
                f'ALTER TABLE {qualified} ALTER COLUMN "{column}" SET NOT NULL'
            )

        if changes.drop_default:
            stmts.append(
                f'ALTER TABLE {qualified} ALTER COLUMN "{column}" DROP DEFAULT'
            )
        elif changes.new_default is not None:
            stmts.append(
                f'ALTER TABLE {qualified} ALTER COLUMN "{column}" SET DEFAULT {changes.new_default}'
            )

        return stmts

    @staticmethod
    def add_index(index: IndexDef) -> str:
        unique = "UNIQUE " if index.unique else ""
        cols = ", ".join(f'"{c}"' for c in index.columns)
        using = f" USING {index.method}" if index.method != "btree" else ""
        where = f" WHERE {index.where}" if index.where else ""
        return f'CREATE {unique}INDEX IF NOT EXISTS "{index.name}" ON "{index.table}"{using} ({cols}){where}'

    @staticmethod
    def drop_index(name: str) -> str:
        return f'DROP INDEX IF EXISTS "{name}"'

    @staticmethod
    def add_constraint(
        table: str,
        constraint: ConstraintDef,
        schema: str | None = None,
    ) -> str:
        qualified = f'"{schema}"."{table}"' if schema else f'"{table}"'
        return (
            f'ALTER TABLE {qualified} ADD CONSTRAINT "{constraint.name}" '
            f"{constraint.constraint_type} ({constraint.expression})"
        )

    @staticmethod
    def drop_constraint(table: str, name: str, schema: str | None = None) -> str:
        qualified = f'"{schema}"."{table}"' if schema else f'"{table}"'
        return f'ALTER TABLE {qualified} DROP CONSTRAINT IF EXISTS "{name}"'

    @staticmethod
    def add_foreign_key(
        table: str,
        fk: ForeignKeyDef,
        column: str,
        schema: str | None = None,
    ) -> str:
        qualified = f'"{schema}"."{table}"' if schema else f'"{table}"'
        constraint_name = fk.constraint_name or f"fk_{table}_{column}_{fk.table}_{fk.column}"
        on_delete = f" ON DELETE {fk.on_delete}" if fk.on_delete else ""
        on_update = f" ON UPDATE {fk.on_update}" if fk.on_update else ""
        return (
            f'ALTER TABLE {qualified} ADD CONSTRAINT "{constraint_name}" '
            f'FOREIGN KEY ("{column}") REFERENCES "{fk.table}"("{fk.column}"){on_delete}{on_update}'
        )

    @staticmethod
    def drop_foreign_key(table: str, constraint_name: str, schema: str | None = None) -> str:
        qualified = f'"{schema}"."{table}"' if schema else f'"{table}"'
        return f'ALTER TABLE {qualified} DROP CONSTRAINT IF EXISTS "{constraint_name}"'

    @staticmethod
    def rename_table(old_name: str, new_name: str, schema: str | None = None) -> str:
        qualified = f'"{schema}"."{old_name}"' if schema else f'"{old_name}"'
        return f'ALTER TABLE {qualified} RENAME TO "{new_name}"'
