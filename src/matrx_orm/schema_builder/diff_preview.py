"""
Schema diff preview — compares existing generated models.py against the live DB
and reports what changed, without writing any files.

Two main entry points:

    run_schema_preview("matrx_orm.yaml")   # console report
    result = preview_schema_changes("matrx_orm.yaml")  # programmatic access

The diff engine works in three phases:
  1. AST-parse the existing models.py → dict[table_name, TableSnapshot]
  2. Run SchemaManager.initialize() → convert Table objects to the same snapshot format
  3. Compare the two dicts field-by-field and produce a SchemaDiffResult
"""

from __future__ import annotations

import ast
import os
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


# ---------------------------------------------------------------------------
# Snapshot dataclasses — the comparison-friendly representation
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class FieldSnapshot:
    name: str
    field_type: str
    primary_key: bool = False
    nullable: bool = True
    default: str | None = None
    unique: bool = False
    max_length: int | None = None
    fk_to_model: str | None = None
    fk_to_column: str | None = None
    fk_to_schema: str | None = None
    enum_class: str | None = None
    dimensions: int | None = None
    element_type: str | None = None

    def diff_against(self, other: FieldSnapshot) -> list[tuple[str, Any, Any]]:
        """Return a list of (attribute, old_value, new_value) for every difference."""
        changes = []
        for attr in (
            "field_type", "primary_key", "nullable", "default", "unique",
            "max_length", "fk_to_model", "fk_to_column", "fk_to_schema",
            "enum_class", "dimensions", "element_type",
        ):
            old = getattr(self, attr)
            new = getattr(other, attr)
            if old != new:
                changes.append((attr, old, new))
        return changes


@dataclass
class TableSnapshot:
    class_name: str
    table_name: str
    database: str | None = None
    fields: dict[str, FieldSnapshot] = field(default_factory=dict)
    inverse_foreign_keys: dict[str, dict[str, str]] = field(default_factory=dict)
    many_to_many: dict[str, dict[str, str]] = field(default_factory=dict)
    enum_classes: dict[str, list[str]] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Diff result dataclasses
# ---------------------------------------------------------------------------

@dataclass
class FieldChange:
    field_name: str
    attribute: str
    old_value: Any
    new_value: Any


@dataclass
class TableDiff:
    table_name: str
    class_name: str
    added_fields: list[str] = field(default_factory=list)
    removed_fields: list[str] = field(default_factory=list)
    changed_fields: list[FieldChange] = field(default_factory=list)
    ifk_added: list[str] = field(default_factory=list)
    ifk_removed: list[str] = field(default_factory=list)
    ifk_changed: list[str] = field(default_factory=list)
    m2m_added: list[str] = field(default_factory=list)
    m2m_removed: list[str] = field(default_factory=list)
    m2m_changed: list[str] = field(default_factory=list)
    enum_added: list[str] = field(default_factory=list)
    enum_removed: list[str] = field(default_factory=list)
    enum_changed: list[str] = field(default_factory=list)

    @property
    def has_changes(self) -> bool:
        return bool(
            self.added_fields or self.removed_fields or self.changed_fields
            or self.ifk_added or self.ifk_removed or self.ifk_changed
            or self.m2m_added or self.m2m_removed or self.m2m_changed
            or self.enum_added or self.enum_removed or self.enum_changed
        )


@dataclass
class SchemaDiffResult:
    database: str
    schema: str
    added_tables: list[str] = field(default_factory=list)
    removed_tables: list[str] = field(default_factory=list)
    modified_tables: list[TableDiff] = field(default_factory=list)
    unchanged_tables: list[str] = field(default_factory=list)

    @property
    def has_changes(self) -> bool:
        return bool(self.added_tables or self.removed_tables or self.modified_tables)

    @property
    def changed_table_names(self) -> set[str]:
        """All table names that have any kind of change (add, remove, or modify)."""
        names: set[str] = set()
        names.update(self.added_tables)
        names.update(self.removed_tables)
        for td in self.modified_tables:
            names.add(td.table_name)
        return names

    def to_dict(self) -> dict[str, Any]:
        return {
            "database": self.database,
            "schema": self.schema,
            "added_tables": self.added_tables,
            "removed_tables": self.removed_tables,
            "modified_tables": [
                {
                    "table_name": td.table_name,
                    "class_name": td.class_name,
                    "added_fields": td.added_fields,
                    "removed_fields": td.removed_fields,
                    "changed_fields": [
                        {"field": fc.field_name, "attr": fc.attribute,
                         "old": fc.old_value, "new": fc.new_value}
                        for fc in td.changed_fields
                    ],
                    "ifk_added": td.ifk_added,
                    "ifk_removed": td.ifk_removed,
                    "ifk_changed": td.ifk_changed,
                    "m2m_added": td.m2m_added,
                    "m2m_removed": td.m2m_removed,
                    "m2m_changed": td.m2m_changed,
                    "enum_added": td.enum_added,
                    "enum_removed": td.enum_removed,
                    "enum_changed": td.enum_changed,
                }
                for td in self.modified_tables
            ],
            "unchanged_count": len(self.unchanged_tables),
            "summary": (
                f"{len(self.added_tables)} added, "
                f"{len(self.removed_tables)} removed, "
                f"{len(self.modified_tables)} modified, "
                f"{len(self.unchanged_tables)} unchanged"
            ),
        }

    def to_console_report(self) -> str:
        lines: list[str] = []
        header = f"Schema Diff Preview — database '{self.database}', schema '{self.schema}'"
        lines.append(header)
        lines.append("=" * len(header))
        lines.append("")

        if not self.has_changes:
            lines.append("No changes detected.")
            lines.append(f"Unchanged: {len(self.unchanged_tables)} tables")
            return "\n".join(lines)

        if self.added_tables:
            lines.append(f"Added tables ({len(self.added_tables)}):")
            for t in sorted(self.added_tables):
                lines.append(f"  + {t}")
            lines.append("")

        if self.removed_tables:
            lines.append(f"Removed tables ({len(self.removed_tables)}):")
            for t in sorted(self.removed_tables):
                lines.append(f"  - {t}")
            lines.append("")

        if self.modified_tables:
            lines.append(f"Modified tables ({len(self.modified_tables)}):")
            for td in sorted(self.modified_tables, key=lambda x: x.table_name):
                lines.append(f"  {td.class_name} ({td.table_name}):")
                for f_name in td.added_fields:
                    lines.append(f"    + added field: {f_name}")
                for f_name in td.removed_fields:
                    lines.append(f"    - removed field: {f_name}")
                for fc in td.changed_fields:
                    lines.append(
                        f"    ~ changed field: {fc.field_name} — "
                        f"{fc.attribute}: {fc.old_value!r} -> {fc.new_value!r}"
                    )
                for name in td.ifk_added:
                    lines.append(f"    + added IFK: {name}")
                for name in td.ifk_removed:
                    lines.append(f"    - removed IFK: {name}")
                for name in td.ifk_changed:
                    lines.append(f"    ~ changed IFK: {name}")
                for name in td.m2m_added:
                    lines.append(f"    + added M2M: {name}")
                for name in td.m2m_removed:
                    lines.append(f"    - removed M2M: {name}")
                for name in td.m2m_changed:
                    lines.append(f"    ~ changed M2M: {name}")
                for name in td.enum_added:
                    lines.append(f"    + added enum: {name}")
                for name in td.enum_removed:
                    lines.append(f"    - removed enum: {name}")
                for name in td.enum_changed:
                    lines.append(f"    ~ changed enum: {name}")
                lines.append("")

        lines.append(f"Unchanged: {len(self.unchanged_tables)} tables")
        lines.append("")
        lines.append(
            f"Summary: {len(self.added_tables)} added, "
            f"{len(self.removed_tables)} removed, "
            f"{len(self.modified_tables)} modified, "
            f"{len(self.unchanged_tables)} unchanged"
        )
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# AST parser — extract TableSnapshot from an existing models.py
# ---------------------------------------------------------------------------

def _extract_keyword_value(node: ast.keyword) -> Any:
    """Best-effort extraction of a keyword argument value from an AST node."""
    try:
        return ast.literal_eval(node.value)
    except (ValueError, TypeError):
        pass
    if isinstance(node.value, ast.Name):
        return node.value.id
    if isinstance(node.value, ast.Attribute):
        parts = []
        n = node.value
        while isinstance(n, ast.Attribute):
            parts.append(n.attr)
            n = n.value
        if isinstance(n, ast.Name):
            parts.append(n.id)
        return ".".join(reversed(parts))
    return repr(ast.dump(node.value))


def _parse_field_call(call_node: ast.Call) -> tuple[str, dict[str, Any]]:
    """Extract field type name and keyword arguments from a field constructor call."""
    if isinstance(call_node.func, ast.Name):
        field_type = call_node.func.id
    elif isinstance(call_node.func, ast.Attribute):
        field_type = call_node.func.attr
    else:
        field_type = "Unknown"

    kwargs: dict[str, Any] = {}
    for kw in call_node.keywords:
        if kw.arg is not None:
            kwargs[kw.arg] = _extract_keyword_value(kw)

    if call_node.args and field_type == "PrimitiveArrayField":
        try:
            kwargs["_positional_0"] = ast.literal_eval(call_node.args[0])
        except (ValueError, TypeError):
            pass

    return field_type, kwargs


def _kwargs_to_field_snapshot(name: str, field_type: str, kwargs: dict[str, Any]) -> FieldSnapshot:
    """Convert parsed kwargs into a FieldSnapshot."""
    null_val = kwargs.get("null", True)
    if isinstance(null_val, str):
        null_val = null_val.lower() != "false"

    default_val = kwargs.get("default")
    if default_val is not None:
        default_val = repr(default_val)

    return FieldSnapshot(
        name=name,
        field_type=field_type,
        primary_key=bool(kwargs.get("primary_key", False)),
        nullable=bool(null_val),
        default=default_val,
        unique=bool(kwargs.get("unique", False)),
        max_length=kwargs.get("max_length"),
        fk_to_model=str(kwargs["to_model"]) if "to_model" in kwargs else None,
        fk_to_column=kwargs.get("to_column"),
        fk_to_schema=kwargs.get("to_schema"),
        enum_class=str(kwargs["enum_class"]) if "enum_class" in kwargs else None,
        dimensions=kwargs.get("dimensions"),
        element_type=kwargs.get("_positional_0"),
    )


def parse_models_file(path: str | Path) -> tuple[dict[str, TableSnapshot], dict[str, list[str]]]:
    """Parse a generated models.py and return table snapshots + enum definitions.

    Returns:
        (tables, enums) where tables is {snake_table_name: TableSnapshot} and
        enums is {EnumClassName: [member_values]}.
    """
    path = Path(path)
    if not path.exists():
        return {}, {}

    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source)

    enums: dict[str, list[str]] = {}
    tables: dict[str, TableSnapshot] = {}

    for node in ast.iter_child_nodes(tree):
        if not isinstance(node, ast.ClassDef):
            continue

        base_names = []
        for base in node.bases:
            if isinstance(base, ast.Name):
                base_names.append(base.id)
            elif isinstance(base, ast.Attribute):
                base_names.append(base.attr)

        if "Enum" in base_names:
            members = []
            for item in node.body:
                if isinstance(item, ast.Assign):
                    for target in item.targets:
                        if isinstance(target, ast.Name):
                            try:
                                members.append(ast.literal_eval(item.value))
                            except (ValueError, TypeError):
                                members.append(target.id)
            enums[node.name] = members
            continue

        if "Model" not in base_names:
            continue

        class_name = node.name
        fields: dict[str, FieldSnapshot] = {}
        ifk_config: dict[str, dict[str, str]] = {}
        m2m_config: dict[str, dict[str, str]] = {}
        database: str | None = None
        table_name_override: str | None = None
        db_schema: str | None = None

        for item in node.body:
            if isinstance(item, (ast.Assign, ast.AnnAssign)):
                targets = []
                value = None

                if isinstance(item, ast.Assign):
                    for t in item.targets:
                        if isinstance(t, ast.Name):
                            targets.append(t.id)
                    value = item.value
                elif isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
                    targets.append(item.target.id)
                    value = item.value

                if not targets or value is None:
                    continue

                attr_name = targets[0]

                if attr_name == "_database":
                    try:
                        database = ast.literal_eval(value)
                    except (ValueError, TypeError):
                        pass
                    continue

                if attr_name == "_table_name":
                    try:
                        table_name_override = ast.literal_eval(value)
                    except (ValueError, TypeError):
                        pass
                    continue

                if attr_name == "_db_schema":
                    try:
                        db_schema = ast.literal_eval(value)
                    except (ValueError, TypeError):
                        pass
                    continue

                if attr_name == "_inverse_foreign_keys":
                    try:
                        ifk_config = ast.literal_eval(value)
                    except (ValueError, TypeError):
                        pass
                    continue

                if attr_name == "_many_to_many":
                    try:
                        m2m_config = ast.literal_eval(value)
                    except (ValueError, TypeError):
                        pass
                    continue

                if attr_name.startswith("_"):
                    continue

                if isinstance(value, ast.Call):
                    field_type, kwargs = _parse_field_call(value)
                    fields[attr_name] = _kwargs_to_field_snapshot(attr_name, field_type, kwargs)

        # Skip cross-schema stub models (e.g. Users with _db_schema="auth").
        # They are hardcoded in generate_models() and don't correspond to any
        # introspected table in the target schema.
        if db_schema is not None:
            continue

        snake_name = table_name_override or _pascal_to_snake(class_name)

        snapshot = TableSnapshot(
            class_name=class_name,
            table_name=snake_name,
            database=database,
            fields=fields,
            inverse_foreign_keys=ifk_config,
            many_to_many=m2m_config,
            enum_classes={},
        )
        tables[snake_name] = snapshot

    for snap in tables.values():
        for f_snap in snap.fields.values():
            if f_snap.enum_class and f_snap.enum_class in enums:
                snap.enum_classes[f_snap.enum_class] = enums[f_snap.enum_class]

    return tables, enums


def _pascal_to_snake(name: str) -> str:
    """Convert PascalCase to snake_case.

    Uses the same regex as ``ModelMeta._to_snake_case`` in ``core/base.py``
    so table-name derivation is identical.
    """
    import re
    return re.sub(r"(?<!^)(?=[A-Z])", "_", name).lower()


# ---------------------------------------------------------------------------
# Table-to-snapshot converter — extract TableSnapshot from a schema_builder Table
# ---------------------------------------------------------------------------

def _normalize_python_default(value: Any) -> Any:
    """Apply the same default-value normalization as Column.to_python_model_field().

    The generator converts raw ``clean_default["python"]`` values before writing
    them into model source code (e.g. the string ``"false"`` becomes the Python
    boolean ``False``).  This function mirrors that logic so the snapshot
    produced from a Table object is directly comparable to what the AST parser
    extracts from generated code.
    """
    if isinstance(value, (bool, int, float, dict, list)):
        return value
    if isinstance(value, str):
        if value == "false":
            return False
        if value == "true":
            return True
        try:
            import ast as _ast
            parsed = _ast.literal_eval(value)
            if isinstance(parsed, (bool, int, float, dict, list)):
                return parsed
            return value
        except (ValueError, SyntaxError):
            return value
    return value


def table_to_snapshot(table: Any) -> TableSnapshot:
    """Convert a schema_builder.tables.Table into a TableSnapshot."""
    from matrx_orm.schema_builder.common import dt_utils

    fields: dict[str, FieldSnapshot] = {}
    enum_classes: dict[str, list[str]] = {}

    for column in table.columns:
        fk_to_model: str | None = None
        fk_to_column: str | None = None
        fk_to_schema: str | None = None
        enum_class: str | None = None
        dimensions: int | None = None
        element_type: str | None = None

        field_type = column.python_field_type

        if column.foreign_key_reference:
            field_type = "ForeignKey"
            fk_to_model = dt_utils.to_pascal_case(column.foreign_key_reference["table"])
            fk_to_column = column.foreign_key_reference["column"]
            fk_schema = column.foreign_key_reference.get("schema")
            if fk_schema and fk_schema != "public":
                fk_to_schema = fk_schema
        elif column.has_enum_labels:
            field_type = "EnumField"
            enum_class = dt_utils.to_pascal_case(column.base_type)
            if column.enum_labels:
                enum_classes[enum_class] = list(column.enum_labels)

        if column.full_type.startswith("vector(") or column.full_type == "vector":
            field_type = "VectorField"
            try:
                dimensions = int(column.full_type.replace("vector(", "").rstrip(")"))
            except ValueError:
                dimensions = 0

        if column.python_field_type == "PrimitiveArrayField":
            field_type = "PrimitiveArrayField"
            element_type = column.full_type.rstrip("[]").strip() or "text"

        default_val = None
        if column.clean_default is not None:
            py_default = column.clean_default.get("python")
            if py_default is not None and py_default != "":
                default_val = repr(_normalize_python_default(py_default))

        fields[column.name] = FieldSnapshot(
            name=column.name,
            field_type=field_type,
            primary_key=column.is_primary_key,
            nullable=column.nullable,
            default=default_val,
            unique=column.is_unique,
            max_length=column.character_maximum_length,
            fk_to_model=fk_to_model,
            fk_to_column=fk_to_column,
            fk_to_schema=fk_to_schema,
            enum_class=enum_class,
            dimensions=dimensions,
            element_type=element_type,
        )

    ifk_config: dict[str, dict[str, str]] = {}
    for source_table, relationship in table.get_all_referenced_by().items():
        ifk_field = table.to_python_inverse_foreign_key_field(source_table, relationship)
        for key, val in ifk_field.items():
            ifk_config[key] = val

    m2m_config: dict[str, dict[str, str]] = {}
    raw_m2m = table.to_python_many_to_many_config()
    if raw_m2m:
        for key, val in raw_m2m.items():
            m2m_config[key] = {k: str(v) for k, v in val.items()}

    return TableSnapshot(
        class_name=table.python_model_name,
        table_name=table.name,
        database=table.database_project,
        fields=fields,
        inverse_foreign_keys=ifk_config,
        many_to_many=m2m_config,
        enum_classes=enum_classes,
    )


# ---------------------------------------------------------------------------
# Diff engine
# ---------------------------------------------------------------------------

def _diff_dict_configs(
    old_config: dict[str, dict],
    new_config: dict[str, dict],
) -> tuple[list[str], list[str], list[str]]:
    """Compare two relation config dicts. Returns (added, removed, changed) key lists."""
    old_keys = set(old_config.keys())
    new_keys = set(new_config.keys())
    added = sorted(new_keys - old_keys)
    removed = sorted(old_keys - new_keys)
    changed = []
    for key in sorted(old_keys & new_keys):
        if old_config[key] != new_config[key]:
            changed.append(key)
    return added, removed, changed


def compute_diff(
    existing: dict[str, TableSnapshot],
    desired: dict[str, TableSnapshot],
    database: str = "",
    schema: str = "public",
) -> SchemaDiffResult:
    """Compare existing (from disk) vs desired (from DB) table snapshots."""
    existing_names = set(existing.keys())
    desired_names = set(desired.keys())

    added = sorted(desired_names - existing_names)
    removed = sorted(existing_names - desired_names)
    shared = sorted(existing_names & desired_names)

    modified: list[TableDiff] = []
    unchanged: list[str] = []

    for table_name in shared:
        old = existing[table_name]
        new = desired[table_name]

        td = TableDiff(
            table_name=table_name,
            class_name=new.class_name,
        )

        old_fields = set(old.fields.keys())
        new_fields = set(new.fields.keys())
        td.added_fields = sorted(new_fields - old_fields)
        td.removed_fields = sorted(old_fields - new_fields)

        for fname in sorted(old_fields & new_fields):
            changes = old.fields[fname].diff_against(new.fields[fname])
            for attr, old_val, new_val in changes:
                td.changed_fields.append(FieldChange(
                    field_name=fname,
                    attribute=attr,
                    old_value=old_val,
                    new_value=new_val,
                ))

        td.ifk_added, td.ifk_removed, td.ifk_changed = _diff_dict_configs(
            old.inverse_foreign_keys, new.inverse_foreign_keys,
        )
        td.m2m_added, td.m2m_removed, td.m2m_changed = _diff_dict_configs(
            old.many_to_many, new.many_to_many,
        )

        old_enums = old.enum_classes
        new_enums = new.enum_classes
        td.enum_added = sorted(set(new_enums) - set(old_enums))
        td.enum_removed = sorted(set(old_enums) - set(new_enums))
        td.enum_changed = [
            k for k in sorted(set(old_enums) & set(new_enums))
            if old_enums[k] != new_enums[k]
        ]

        if td.has_changes:
            modified.append(td)
        else:
            unchanged.append(table_name)

    return SchemaDiffResult(
        database=database,
        schema=schema,
        added_tables=added,
        removed_tables=removed,
        modified_tables=modified,
        unchanged_tables=unchanged,
    )


# ---------------------------------------------------------------------------
# High-level entry points
# ---------------------------------------------------------------------------

def _resolve_models_path(python_root: str) -> Path:
    """Resolve the models.py path from the python root."""
    return Path(python_root) / "db" / "models.py"


def preview_schema_changes(
    config_path: str | Path = "matrx_orm.yaml",
) -> list[SchemaDiffResult]:
    """Run the diff engine for every generate entry in the config. Returns one
    SchemaDiffResult per generate entry.

    This mirrors the setup logic in runner.run_schema_generation() but instead
    of writing files, it compares the existing output against what would be
    generated.
    """
    from dotenv import load_dotenv
    from matrx_orm.core.config import register_database_from_env
    from matrx_orm.schema_builder.common import DEBUG_CONFIG, OutputConfig
    from matrx_orm.schema_builder.schema_manager import SchemaManager

    caller_dir = Path(sys.argv[0]).parent.resolve()
    config_path = (caller_dir / config_path).resolve()

    if not config_path.exists():
        raise FileNotFoundError(f"matrx-orm config not found: {config_path}")

    try:
        import yaml
    except ImportError:
        raise ImportError("PyYAML is required. Install with: pip install pyyaml")
    with open(config_path) as f:
        cfg = yaml.safe_load(f) or {}

    env_file = None
    search = config_path.parent
    while True:
        candidate = search / ".env"
        if candidate.exists():
            env_file = candidate
            break
        parent = search.parent
        if parent == search:
            break
        search = parent
    if env_file:
        load_dotenv(env_file)
    else:
        load_dotenv()

    debug_cfg = cfg.get("debug", {})
    DEBUG_CONFIG["info"] = bool(debug_cfg.get("info", False))
    DEBUG_CONFIG["debug"] = bool(debug_cfg.get("debug", False))
    DEBUG_CONFIG["verbose"] = bool(debug_cfg.get("verbose", False))

    python_root = os.environ.get("MATRX_PYTHON_ROOT", "").strip()
    if not python_root:
        raise RuntimeError("MATRX_PYTHON_ROOT is not set in the environment.")

    os.environ["ADMIN_PYTHON_ROOT"] = python_root
    ts_root = os.environ.get("MATRX_TS_ROOT", "").strip()
    if ts_root:
        os.environ["ADMIN_TS_ROOT"] = ts_root

    for db in cfg.get("databases", []):
        name = db.get("name")
        prefix = db.get("env_prefix")
        if not name or not prefix:
            continue
        register_database_from_env(
            name=name,
            env_prefix=prefix,
            alias=db.get("alias", ""),
            additional_schemas=db.get("additional_schemas", []),
            entity_overrides=db.get("entity_overrides") or {},
            field_overrides=db.get("field_overrides") or {},
            manager_config_overrides=db.get("manager_config_overrides") or {},
            env_var_overrides=db.get("env_var_overrides") or {},
        )

    output_config = OutputConfig(save_direct=False)

    results: list[SchemaDiffResult] = []

    for entry in cfg.get("generate", []):
        db_name = entry.get("database")
        schema_name = entry.get("schema", "public")
        include_tables = entry.get("include_tables") or None
        exclude_tables = entry.get("exclude_tables") or None
        manager_flags = entry.get("manager_flags") or None

        manager = SchemaManager(
            schema=schema_name,
            database_project=db_name,
            output_config=output_config,
            include_tables=include_tables,
            exclude_tables=exclude_tables,
            manager_flags=manager_flags,
        )
        manager.initialize()

        models_path = _resolve_models_path(python_root)
        existing_tables, _ = parse_models_file(models_path)

        desired_tables: dict[str, TableSnapshot] = {}
        for table in manager.schema._filtered_tables.values():
            snap = table_to_snapshot(table)
            desired_tables[snap.table_name] = snap

        if include_tables is not None:
            inc = set(include_tables)
            existing_tables = {k: v for k, v in existing_tables.items() if k in inc}
        elif exclude_tables is not None:
            exc = set(exclude_tables)
            existing_tables = {k: v for k, v in existing_tables.items() if k not in exc}

        result = compute_diff(existing_tables, desired_tables, database=db_name, schema=schema_name)
        results.append(result)

    return results


def run_schema_preview(config_path: str | Path = "matrx_orm.yaml") -> None:
    """Print a human-readable diff report to stdout."""
    from matrx_orm.schema_builder.runner import _close_pools

    try:
        results = preview_schema_changes(config_path)
        for result in results:
            print(result.to_console_report())
            print()
    finally:
        _close_pools()
