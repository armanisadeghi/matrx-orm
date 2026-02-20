"""Schema diff engine -- compares model definitions against the live database and produces operations."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from matrx_orm.exceptions import MigrationError
from .ddl import (
    AlterColumnChanges,
    ColumnDef,
    DDLGenerator,
    ForeignKeyDef,
)
from .operations import MigrationDB


PG_TYPE_ALIASES: dict[str, str] = {
    "int4": "integer",
    "int8": "bigint",
    "int2": "smallint",
    "float4": "real",
    "float8": "double precision",
    "bool": "boolean",
    "varchar": "character varying",
    "timestamptz": "timestamp with time zone",
    "timestamp": "timestamp without time zone",
    "timetz": "time with time zone",
    "time": "time without time zone",
}

ORM_TO_PG: dict[str, str] = {
    "UUID": "uuid",
    "TEXT": "text",
    "INTEGER": "integer",
    "BIGINT": "bigint",
    "SMALLINT": "smallint",
    "FLOAT": "double precision",
    "BOOLEAN": "boolean",
    "TIMESTAMP": "timestamp with time zone",
    "TIMESTAMPTZ": "timestamp with time zone",
    "DATE": "date",
    "TIME": "time without time zone",
    "JSONB": "jsonb",
    "JSON": "json",
    "BYTEA": "bytea",
    "INET": "inet",
    "CIDR": "cidr",
    "MACADDR": "macaddr",
    "POINT": "point",
    "INTERVAL": "interval",
    "HSTORE": "hstore",
    "CITEXT": "citext",
    "MONEY": "money",
    "NUMERIC": "numeric",
    "SERIAL": "integer",
    "BIGSERIAL": "bigint",
}


def _normalize_pg_type(raw: str) -> str:
    """Normalize a PostgreSQL type string for comparison."""
    lowered = raw.strip().lower()
    return PG_TYPE_ALIASES.get(lowered, lowered)


def _orm_type_to_pg(orm_type: str) -> str:
    """Convert an ORM db_type (like 'VARCHAR(255)') to a normalized PG type."""
    upper = orm_type.upper().strip()
    if upper.startswith("VARCHAR"):
        return f"character varying{upper[7:].lower()}" if "(" in upper else "character varying"
    if upper.startswith("NUMERIC") and "(" in upper:
        return upper.lower()
    for key, val in ORM_TO_PG.items():
        if upper == key or upper.startswith(key + "("):
            suffix = upper[len(key):]
            return f"{val}{suffix.lower()}" if suffix else val
    return upper.lower()


@dataclass
class TableColumnState:
    name: str
    db_type: str
    nullable: bool
    primary_key: bool
    unique: bool
    default: str | None
    fk_table: str | None = None
    fk_column: str | None = None


@dataclass
class TableState:
    name: str
    schema: str
    columns: dict[str, TableColumnState] = field(default_factory=dict)


@dataclass
class Operation:
    """A single schema operation (abstract base)."""
    op_type: str
    table: str
    schema: str | None = None
    details: dict[str, Any] = field(default_factory=dict)

    def to_up_sql(self) -> list[str]:
        """Generate the forward DDL statement(s)."""
        gen = DDLGenerator
        match self.op_type:
            case "create_table":
                cols = self.details["columns"]
                return [gen.create_table(self.table, cols, schema=self.schema)]
            case "drop_table":
                return [gen.drop_table(self.table, schema=self.schema, cascade=True)]
            case "add_column":
                return [gen.add_column(self.table, self.details["column"], schema=self.schema)]
            case "drop_column":
                return [gen.drop_column(self.table, self.details["column_name"], schema=self.schema)]
            case "alter_column":
                return gen.alter_column(
                    self.table,
                    self.details["column_name"],
                    self.details["changes"],
                    schema=self.schema,
                )
            case "add_foreign_key":
                return [gen.add_foreign_key(
                    self.table,
                    self.details["fk"],
                    self.details["column"],
                    schema=self.schema,
                )]
            case "drop_foreign_key":
                return [gen.drop_foreign_key(
                    self.table,
                    self.details["constraint_name"],
                    schema=self.schema,
                )]
            case _:
                raise MigrationError(
                    original_error=f"Unknown operation type: {self.op_type}"
                )

    def to_down_sql(self) -> list[str]:
        """Generate the reverse DDL statement(s)."""
        gen = DDLGenerator
        match self.op_type:
            case "create_table":
                return [gen.drop_table(self.table, schema=self.schema, cascade=True)]
            case "drop_table":
                cols = self.details.get("columns", [])
                if cols:
                    return [gen.create_table(self.table, cols, schema=self.schema)]
                return [f'-- Cannot reverse DROP TABLE "{self.table}" (column info unavailable)']
            case "add_column":
                return [gen.drop_column(self.table, self.details["column"].name, schema=self.schema)]
            case "drop_column":
                old_col = self.details.get("old_column")
                if old_col:
                    return [gen.add_column(self.table, old_col, schema=self.schema)]
                return [f'-- Cannot reverse DROP COLUMN "{self.details["column_name"]}" on "{self.table}"']
            case "alter_column":
                reverse = self.details.get("reverse_changes")
                if reverse:
                    return gen.alter_column(
                        self.table,
                        self.details["column_name"],
                        reverse,
                        schema=self.schema,
                    )
                return [f'-- Cannot reverse ALTER COLUMN "{self.details["column_name"]}" on "{self.table}"']
            case "add_foreign_key":
                cn = self.details["fk"].constraint_name or (
                    f"fk_{self.table}_{self.details['column']}_{self.details['fk'].table}_{self.details['fk'].column}"
                )
                return [gen.drop_foreign_key(self.table, cn, schema=self.schema)]
            case "drop_foreign_key":
                return [f'-- Cannot reverse DROP FOREIGN KEY "{self.details["constraint_name"]}" on "{self.table}"']
            case _:
                return [f"-- Unknown reverse for {self.op_type}"]


INTROSPECT_TABLES_SQL = """
SELECT
    c.relname AS table_name,
    n.nspname AS schema_name
FROM pg_class c
JOIN pg_namespace n ON n.oid = c.relnamespace
WHERE n.nspname = $1
  AND c.relkind = 'r'
ORDER BY c.relname
"""

INTROSPECT_COLUMNS_SQL = """
SELECT
    a.attname AS column_name,
    pg_catalog.format_type(a.atttypid, a.atttypmod) AS full_type,
    NOT a.attnotnull AS nullable,
    pg_get_expr(d.adbin, d.adrelid) AS col_default,
    EXISTS (
        SELECT 1 FROM pg_constraint p
        WHERE p.conrelid = a.attrelid AND p.contype = 'p' AND p.conkey @> ARRAY[a.attnum]
    ) AS is_primary_key,
    EXISTS (
        SELECT 1 FROM pg_constraint u
        WHERE u.conrelid = a.attrelid AND u.contype = 'u' AND u.conkey @> ARRAY[a.attnum]
    ) AS is_unique,
    (
        SELECT json_build_object(
            'table', (SELECT relname FROM pg_class WHERE oid = fk.confrelid),
            'column', (
                SELECT attname FROM pg_attribute ref_att
                WHERE ref_att.attrelid = fk.confrelid
                  AND ref_att.attnum = fk.confkey[array_position(fk.conkey, a.attnum)]
                  AND NOT ref_att.attisdropped
            )
        )
        FROM pg_constraint fk
        WHERE fk.conrelid = a.attrelid
          AND fk.contype = 'f'
          AND array_position(fk.conkey, a.attnum) IS NOT NULL
        LIMIT 1
    ) AS fk_ref
FROM pg_attribute a
LEFT JOIN pg_attrdef d ON (a.attrelid, a.attnum) = (d.adrelid, d.adnum)
WHERE a.attrelid = (
    SELECT c.oid FROM pg_class c
    JOIN pg_namespace n ON n.oid = c.relnamespace
    WHERE c.relname = $1 AND n.nspname = $2
)
AND a.attnum > 0
AND NOT a.attisdropped
ORDER BY a.attnum
"""


class SchemaDiff:
    """Compares model definitions against the live database and produces migration operations."""

    def __init__(self, db: MigrationDB, schema: str = "public") -> None:
        self._db = db
        self._schema = schema

    def capture_model_state(self) -> dict[str, TableState]:
        """Extract the desired schema state from all registered ORM models."""
        from matrx_orm.core.registry import ModelRegistry

        tables: dict[str, TableState] = {}
        all_models = ModelRegistry.all_models()

        for model_name, model_cls in all_models.items():
            meta = getattr(model_cls, "_meta", None)
            if meta is None:
                continue
            if getattr(meta, "unfetchable", False):
                continue
            if meta.db_schema and meta.db_schema != self._schema:
                continue

            table = TableState(name=meta.table_name, schema=self._schema)
            for field_name, field_obj in meta.fields.items():
                pg_type = _orm_type_to_pg(field_obj.db_type)

                fk_table: str | None = None
                fk_column: str | None = None
                fk_ref = meta.foreign_keys.get(field_name)
                if fk_ref:
                    fk_table = fk_ref.to_model
                    fk_column = fk_ref.to_column

                table.columns[field_name] = TableColumnState(
                    name=field_name,
                    db_type=pg_type,
                    nullable=getattr(field_obj, "nullable", True),
                    primary_key=getattr(field_obj, "primary_key", False),
                    unique=getattr(field_obj, "unique", False),
                    default=None,
                    fk_table=fk_table,
                    fk_column=fk_column,
                )

            tables[meta.table_name] = table
        return tables

    async def capture_db_state(self) -> dict[str, TableState]:
        """Introspect the live database and return the current schema state."""
        tables: dict[str, TableState] = {}

        table_rows = await self._db.fetch(INTROSPECT_TABLES_SQL, self._schema)
        for trow in table_rows:
            tname = trow["table_name"]
            if tname == "_matrx_migrations":
                continue
            table = TableState(name=tname, schema=self._schema)

            col_rows = await self._db.fetch(INTROSPECT_COLUMNS_SQL, tname, self._schema)
            for crow in col_rows:
                fk_table: str | None = None
                fk_column: str | None = None
                fk_ref = crow.get("fk_ref")
                if fk_ref and isinstance(fk_ref, dict):
                    fk_table = fk_ref.get("table")
                    fk_column = fk_ref.get("column")

                table.columns[crow["column_name"]] = TableColumnState(
                    name=crow["column_name"],
                    db_type=_normalize_pg_type(crow["full_type"]),
                    nullable=crow["nullable"],
                    primary_key=crow["is_primary_key"],
                    unique=crow["is_unique"],
                    default=crow.get("col_default"),
                    fk_table=fk_table,
                    fk_column=fk_column,
                )
            tables[tname] = table
        return tables

    async def compute_diff(self) -> list[Operation]:
        """Compare model state vs DB state and return a list of operations."""
        model_state = self.capture_model_state()
        db_state = await self.capture_db_state()
        ops: list[Operation] = []

        model_tables = set(model_state.keys())
        db_tables = set(db_state.keys())

        for tname in sorted(model_tables - db_tables):
            mt = model_state[tname]
            cols = [
                ColumnDef(
                    name=cs.name,
                    db_type=cs.db_type,
                    nullable=cs.nullable,
                    primary_key=cs.primary_key,
                    unique=cs.unique,
                    references=ForeignKeyDef(table=cs.fk_table, column=cs.fk_column) if cs.fk_table else None,
                )
                for cs in mt.columns.values()
            ]
            ops.append(Operation(op_type="create_table", table=tname, schema=self._schema, details={"columns": cols}))

        for tname in sorted(db_tables - model_tables):
            dt = db_state[tname]
            cols = [
                ColumnDef(
                    name=cs.name,
                    db_type=cs.db_type,
                    nullable=cs.nullable,
                    primary_key=cs.primary_key,
                    unique=cs.unique,
                )
                for cs in dt.columns.values()
            ]
            ops.append(Operation(op_type="drop_table", table=tname, schema=self._schema, details={"columns": cols}))

        for tname in sorted(model_tables & db_tables):
            mt = model_state[tname]
            dt = db_state[tname]
            model_cols = set(mt.columns.keys())
            db_cols = set(dt.columns.keys())

            for cname in sorted(model_cols - db_cols):
                mc = mt.columns[cname]
                col = ColumnDef(
                    name=mc.name,
                    db_type=mc.db_type,
                    nullable=mc.nullable,
                    primary_key=mc.primary_key,
                    unique=mc.unique,
                    references=ForeignKeyDef(table=mc.fk_table, column=mc.fk_column) if mc.fk_table else None,
                )
                ops.append(Operation(op_type="add_column", table=tname, schema=self._schema, details={"column": col}))

            for cname in sorted(db_cols - model_cols):
                dc = dt.columns[cname]
                old_col = ColumnDef(
                    name=dc.name, db_type=dc.db_type, nullable=dc.nullable,
                    primary_key=dc.primary_key, unique=dc.unique,
                )
                ops.append(Operation(
                    op_type="drop_column", table=tname, schema=self._schema,
                    details={"column_name": cname, "old_column": old_col},
                ))

            for cname in sorted(model_cols & db_cols):
                mc = mt.columns[cname]
                dc = dt.columns[cname]
                changes = AlterColumnChanges()
                reverse = AlterColumnChanges()
                has_changes = False

                mc_type = _normalize_pg_type(mc.db_type)
                dc_type = _normalize_pg_type(dc.db_type)
                if mc_type != dc_type:
                    changes.new_type = mc.db_type
                    reverse.new_type = dc.db_type
                    has_changes = True

                if mc.nullable != dc.nullable:
                    changes.set_nullable = mc.nullable
                    reverse.set_nullable = dc.nullable
                    has_changes = True

                if has_changes:
                    ops.append(Operation(
                        op_type="alter_column", table=tname, schema=self._schema,
                        details={"column_name": cname, "changes": changes, "reverse_changes": reverse},
                    ))

                m_has_fk = bool(mc.fk_table)
                d_has_fk = bool(dc.fk_table)
                if m_has_fk and not d_has_fk:
                    fk = ForeignKeyDef(table=mc.fk_table, column=mc.fk_column)
                    ops.append(Operation(
                        op_type="add_foreign_key", table=tname, schema=self._schema,
                        details={"fk": fk, "column": cname},
                    ))
                elif d_has_fk and not m_has_fk:
                    cn = f"fk_{tname}_{cname}_{dc.fk_table}_{dc.fk_column}"
                    ops.append(Operation(
                        op_type="drop_foreign_key", table=tname, schema=self._schema,
                        details={"constraint_name": cn},
                    ))

        return ops

    async def generate_migration_file(
        self,
        migrations_dir: str | Path,
        name: str | None = None,
        number: int | None = None,
    ) -> Path | None:
        """Compute diff and write a migration file. Returns the path, or None if no changes."""
        from .loader import MigrationLoader

        ops = await self.compute_diff()
        if not ops:
            return None

        if number is None:
            loader = MigrationLoader(migrations_dir)
            number = loader.next_number()

        if name is None:
            name = self._auto_name(ops)

        filename = f"{number:04d}_{name}.py"
        filepath = Path(migrations_dir) / filename

        up_lines: list[str] = []
        down_lines: list[str] = []
        for op in ops:
            for sql in op.to_up_sql():
                up_lines.append(f'    await db.execute("""{sql}""")')
            for sql in op.to_down_sql():
                down_lines.append(f'    await db.execute("""{sql}""")')

        prev_number = number - 1
        deps = f'["{prev_number:04d}"]' if prev_number > 0 else "[]"

        description = self._describe_ops(ops)
        content = (
            f'"""{description}"""\n'
            f"\n"
            f"dependencies = {deps}\n"
            f"\n"
            f"\n"
            f"async def up(db):\n"
            + "\n".join(up_lines)
            + "\n"
            f"\n"
            f"\n"
            f"async def down(db):\n"
            + "\n".join(down_lines)
            + "\n"
        )

        filepath.parent.mkdir(parents=True, exist_ok=True)
        filepath.write_text(content, encoding="utf-8")
        return filepath

    @staticmethod
    def _auto_name(ops: list[Operation]) -> str:
        """Generate a short descriptive name from the operations list."""
        if len(ops) == 1:
            op = ops[0]
            if op.op_type == "create_table":
                return f"create_{op.table}"
            if op.op_type == "drop_table":
                return f"drop_{op.table}"
            if op.op_type == "add_column":
                return f"add_{op.details['column'].name}_to_{op.table}"
            if op.op_type == "drop_column":
                return f"drop_{op.details['column_name']}_from_{op.table}"

        tables = {op.table for op in ops}
        if len(tables) == 1:
            return f"update_{tables.pop()}"
        return "auto"

    @staticmethod
    def _describe_ops(ops: list[Operation]) -> str:
        """Produce a human-readable summary for the migration docstring."""
        parts: list[str] = []
        for op in ops:
            match op.op_type:
                case "create_table":
                    parts.append(f"Create table {op.table}")
                case "drop_table":
                    parts.append(f"Drop table {op.table}")
                case "add_column":
                    parts.append(f"Add column {op.details['column'].name} to {op.table}")
                case "drop_column":
                    parts.append(f"Drop column {op.details['column_name']} from {op.table}")
                case "alter_column":
                    parts.append(f"Alter column {op.details['column_name']} on {op.table}")
                case "add_foreign_key":
                    parts.append(f"Add FK on {op.table}.{op.details['column']}")
                case "drop_foreign_key":
                    parts.append(f"Drop FK {op.details['constraint_name']} on {op.table}")
                case _:
                    parts.append(f"{op.op_type} on {op.table}")
        return "; ".join(parts)
