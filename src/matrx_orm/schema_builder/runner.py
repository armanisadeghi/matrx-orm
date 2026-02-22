"""
run_schema_generation() — the single entry point for yaml-driven reverse migrations.

Usage:
    from matrx_orm.schema_builder import run_schema_generation
    run_schema_generation("matrx_orm.yaml")
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from matrx_utils import vcprint

from matrx_orm.core.config import register_database_from_env, DatabaseConfigError
from matrx_orm.schema_builder.common import DEBUG_CONFIG
from matrx_orm.schema_builder.helpers.git_checker import check_git_status
from matrx_orm.schema_builder.schema_manager import SchemaManager


def _load_yaml(path: Path) -> dict[str, Any]:
    try:
        import yaml
    except ImportError:
        raise ImportError(
            "PyYAML is required for yaml-based configuration. "
            "Install it with: pip install pyyaml"
        )
    with open(path) as f:
        return yaml.safe_load(f) or {}


def run_schema_generation(config_path: str | Path = "matrx_orm.yaml") -> None:
    """
    Read a matrx_orm.yaml config file, register all databases, apply debug
    settings, then run reverse-migration schema generation for each entry in
    the ``generate`` list.

    The config file is looked up relative to the calling script's directory
    (i.e. the directory that contains generate.py), so users never need to
    think about working-directory quirks.
    """
    # Resolve config path relative to the caller's file location
    caller_dir = Path(sys.argv[0]).parent.resolve()
    config_path = (caller_dir / config_path).resolve()

    if not config_path.exists():
        raise FileNotFoundError(
            f"matrx-orm config not found: {config_path}\n"
            f"Create a matrx_orm.yaml file next to your generate.py script."
        )

    vcprint(f"[matrx-orm] Loading config: {config_path}", color="cyan")

    # Load .env from the same directory as the config file
    env_file = config_path.parent / ".env"
    if env_file.exists():
        load_dotenv(env_file)
    else:
        load_dotenv()  # fallback to default search

    cfg = _load_yaml(config_path)

    # -------------------------------------------------------------------------
    # Debug settings
    # -------------------------------------------------------------------------
    debug_cfg = cfg.get("debug", {})
    DEBUG_CONFIG["info"] = bool(debug_cfg.get("info", False))
    DEBUG_CONFIG["debug"] = bool(debug_cfg.get("debug", False))
    DEBUG_CONFIG["verbose"] = bool(debug_cfg.get("verbose", False))

    # -------------------------------------------------------------------------
    # Output directories + save_direct
    # -------------------------------------------------------------------------
    output_cfg = cfg.get("output", {})
    base = config_path.parent
    save_direct = bool(output_cfg.get("save_direct", False))

    python_root = ""
    ts_root = ""

    if "python_root" in output_cfg:
        python_root = str((base / output_cfg["python_root"]).resolve())
        os.environ["ADMIN_PYTHON_ROOT"] = python_root

    if "typescript_root" in output_cfg:
        ts_root = str((base / output_cfg["typescript_root"]).resolve())
        os.environ["ADMIN_TS_ROOT"] = ts_root

    # -------------------------------------------------------------------------
    # Git safety check — must run before any generation when save_direct=True
    # -------------------------------------------------------------------------
    check_git_status(save_direct, python_root=python_root, ts_root=ts_root)

    # -------------------------------------------------------------------------
    # Register databases
    # -------------------------------------------------------------------------
    databases = cfg.get("databases", [])
    if not databases:
        vcprint("[matrx-orm] No databases defined in matrx_orm.yaml — nothing to do.", color="yellow")
        return

    for db in databases:
        name = db.get("name")
        prefix = db.get("env_prefix")
        if not name or not prefix:
            vcprint(f"[matrx-orm] Skipping database entry missing 'name' or 'env_prefix': {db}", color="yellow")
            continue

        register_database_from_env(
            name=name,
            env_prefix=prefix,
            additional_schemas=db.get("additional_schemas", []),
        )

    # -------------------------------------------------------------------------
    # Run generation for each configured target
    # -------------------------------------------------------------------------
    generate_list = cfg.get("generate", [])
    if not generate_list:
        vcprint("[matrx-orm] No entries in 'generate' — databases registered but nothing generated.", color="yellow")
        return

    for entry in generate_list:
        db_name = entry.get("database")
        schema = entry.get("schema", "public")

        vcprint(
            f"[matrx-orm] Generating schema for database='{db_name}' schema='{schema}'",
            color="cyan",
        )

        try:
            manager = SchemaManager(
                schema=schema,
                database_project=db_name,
                save_direct=save_direct,
            )
            manager.initialize()
            manager.schema.generate_schema_files()
            manager.schema.generate_models()
            vcprint(
                f"[matrx-orm] Done — database='{db_name}' schema='{schema}'",
                color="green",
            )
        except DatabaseConfigError as e:
            vcprint(
                f"[matrx-orm] Skipping '{db_name}': {e}",
                color="red",
            )
        except Exception as e:
            vcprint(
                f"[matrx-orm] Error generating '{db_name}': {e}",
                color="red",
            )
            raise
