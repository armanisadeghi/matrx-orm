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
from matrx_orm.schema_builder.common import DEBUG_CONFIG, OutputConfig
from matrx_orm.schema_builder.helpers.git_checker import check_git_status
from matrx_orm.schema_builder.schema_manager import SchemaManager


def _close_pools() -> None:
    """Close all open psycopg_pool ConnectionPools to suppress thread warnings on exit."""
    try:
        from matrx_orm.client.postgres_connection import connection_pools
        for name, pool in list(connection_pools.items()):
            try:
                pool.close()
            except Exception:
                pass
    except Exception:
        pass


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

    vcprint(config_path, f"[MATRX ORM] Loading config", color="cyan")

    # Load .env — search from the config file's directory upward, stopping at
    # the filesystem root.  This mirrors how git, Node, and most tooling work:
    # the .env lives at the project root, not necessarily next to generate.py.
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
        load_dotenv()  # last-resort: let python-dotenv search from cwd

    cfg = _load_yaml(config_path)

    # -------------------------------------------------------------------------
    # Debug settings
    # -------------------------------------------------------------------------
    debug_cfg = cfg.get("debug", {})
    DEBUG_CONFIG["info"] = bool(debug_cfg.get("info", False))
    DEBUG_CONFIG["debug"] = bool(debug_cfg.get("debug", False))
    DEBUG_CONFIG["verbose"] = bool(debug_cfg.get("verbose", False))

    # -------------------------------------------------------------------------
    # Output config — all paths come from .env only, never from the yaml.
    #
    # Required env var:
    #   MATRX_PYTHON_ROOT   absolute path to the Python project root
    #
    # Optional env vars:
    #   MATRX_TS_ROOT       absolute path to the Next.js project root
    #                       (only needed when output.typescript: true)
    #   MATRX_SAVE_DIRECT   true/false override for save_direct
    # -------------------------------------------------------------------------
    output_cfg = cfg.get("output", {})

    python_root = os.environ.get("MATRX_PYTHON_ROOT", "").strip()
    ts_root = os.environ.get("MATRX_TS_ROOT", "").strip()

    typescript_enabled = output_cfg.get("typescript", False)

    if not python_root:
        vcprint(
            "\n[MATRX ORM] ERROR: MATRX_PYTHON_ROOT is not set.\n"
            "  Add it to your .env file:\n"
            "    MATRX_PYTHON_ROOT=/absolute/path/to/your/python/project\n",
            color="red",
        )
        sys.exit(1)

    if typescript_enabled and not ts_root:
        vcprint(
            "\n[MATRX ORM] ERROR: MATRX_TS_ROOT is not set but output.typescript is true.\n"
            "  Add it to your .env file:\n"
            "    MATRX_TS_ROOT=/absolute/path/to/your/nextjs/project\n"
            "  Or set  typescript: false  in matrx_orm.yaml if this is a Python-only project.\n",
            color="red",
        )
        sys.exit(1)

    os.environ["ADMIN_PYTHON_ROOT"] = python_root
    if ts_root:
        os.environ["ADMIN_TS_ROOT"] = ts_root

    # save_direct: .env wins over yaml
    env_save_direct = os.environ.get("MATRX_SAVE_DIRECT", "").strip().lower()
    if env_save_direct in ("1", "true"):
        output_cfg = {**output_cfg, "save_direct": True}
    elif env_save_direct in ("0", "false"):
        output_cfg = {**output_cfg, "save_direct": False}

    output_config = OutputConfig.from_dict(output_cfg)

    # -------------------------------------------------------------------------
    # Git safety check — must run before any generation when save_direct=True
    # -------------------------------------------------------------------------
    # Collect output subdirectory prefixes (relative to the repo root) so the
    # checker can ignore previously-generated files that show as "dirty".
    _ignore_prefixes: list[str] = []
    if python_root and output_config.save_direct:
        try:
            from git import Repo, InvalidGitRepositoryError
            _repo = Repo(python_root, search_parent_directories=True)
            _repo_root = _repo.working_tree_dir or python_root
            _abs = os.path.join(python_root, "db")
            try:
                _rel = os.path.relpath(_abs, _repo_root)
                _ignore_prefixes.append(_rel)
            except ValueError:
                pass
        except Exception:
            pass
    check_git_status(output_config.save_direct, python_root=python_root, ts_root=ts_root, ignore_path_prefixes=_ignore_prefixes)

    # -------------------------------------------------------------------------
    # Register databases
    # -------------------------------------------------------------------------
    databases = cfg.get("databases", [])
    if not databases:
        vcprint("[MATRX ORM] No databases defined in matrx_orm.yaml — nothing to do.", color="yellow")
        return

    for db in databases:
        name = db.get("name")
        prefix = db.get("env_prefix")
        if not name or not prefix:
            vcprint(f"[MATRX ORM] Skipping database entry missing 'name' or 'env_prefix': {db}", color="yellow")
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

    # -------------------------------------------------------------------------
    # Run generation for each configured target
    # -------------------------------------------------------------------------
    generate_list = cfg.get("generate", [])
    if not generate_list:
        vcprint("[MATRX ORM] No entries in 'generate' — databases registered but nothing generated.", color="yellow")
        return

    for entry in generate_list:
        db_name = entry.get("database")
        schema = entry.get("schema", "public")

        # Table filters — mutually exclusive
        include_tables = entry.get("include_tables") or None
        exclude_tables = entry.get("exclude_tables") or None

        # manager_flags: yaml-level defaults for all tables in this generation run.
        # Per-table manager_config_overrides (from the databases section) stack on top.
        manager_flags = entry.get("manager_flags") or None

        vcprint(f"[MATRX ORM] Generating schema... \n\n- Database: '{db_name}'\n- Schema: '{schema}'", verbose=DEBUG_CONFIG["verbose"], color="cyan")

        try:
            manager = SchemaManager(
                schema=schema,
                database_project=db_name,
                output_config=output_config,
                include_tables=include_tables,
                exclude_tables=exclude_tables,
                manager_flags=manager_flags,
            )
            manager.initialize()
            manager.schema.generate_schema_files()
            manager.schema.generate_models()
            vcprint(
                f"[MATRX ORM] Done — database='{db_name}' schema='{schema}'\n",
                color="green",
            )

            manager.schema.code_handler.print_all_batched()
        except DatabaseConfigError as e:
            vcprint(
                f"[MATRX ORM] Skipping '{db_name}': {e}",
                color="red",
            )
        except Exception as e:
            vcprint(
                f"[MATRX ORM] Error generating '{db_name}': {e}",
                color="red",
            )
            _close_pools()
            raise

    _close_pools()
