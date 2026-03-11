from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, cast
import os

from matrx_utils import settings, vcprint, redact_object, redact_string


class DatabaseConfigError(Exception):
    pass


@dataclass
class DatabaseProjectConfig:
    # Basics for project
    name: str
    host: str
    port: str
    database_name: str
    user: str
    password: str

    protocol: str = "postgresql"
    alias: str = ""
    manager_config_overrides: dict[str, Any] = field(default_factory=dict)

    # Schema builder overrides — app-specific TypeScript entity/field configurations.
    # entity_overrides: maps camelCase entity name → dict of entity-level override props
    #   e.g. {"recipe": {"defaultFetchStrategy": '"fkAndIfk"'}}
    # field_overrides: maps camelCase entity name → dict of field-level override props
    #   e.g. {"broker": {"name": "{isDisplayField: false, ...}"}}
    entity_overrides: dict[str, Any] = field(default_factory=dict)
    field_overrides: dict[str, Any] = field(default_factory=dict)

    # Extra PostgreSQL schemas to introspect and include in schema builder output.
    # For Supabase projects this typically includes ["auth", "storage"].
    # These schemas live in the same database but outside the default "public" schema.
    additional_schemas: list = field(default_factory=list)

    # Connection pool settings — "session" uses prepared statements (port 5432),
    # "transaction" disables statement caching for Supavisor transaction pooler (port 6543).
    pool_mode: str = "session"
    pool_min: int = 5
    pool_max: int = 20
    command_timeout: int = 10

    # Write queue — gates write operations behind an async queue so they wait in
    # order instead of racing for pool connections and timing out under load.
    write_queue_enabled: bool = True
    write_concurrency: int = 10
    write_queue_size: int = 200
    write_queue_timeout: float = 30.0


class DatabaseRegistry:
    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseRegistry, cls).__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        if not self._initialized:
            self._configs: dict[str, DatabaseProjectConfig] = {}
            self._used_aliases: list[str] = []
            self._initialized = True

    def register(self, config: DatabaseProjectConfig) -> None:
        if config.name in self._configs:
            vcprint(
                f"[Matrx ORM] WARNING! Database configuration '{config.name}' already registered. Ignoring new registration.",
                color="yellow",
            )
            return

        if config.alias == "":
            vcprint(
                "[Matrx ORM] Error! Database alias cannot be empty. Please use a different alias.",
                color="red",
            )
            raise DatabaseConfigError(
                "Database alias cannot be empty. Please use a different alias."
            )

        if config.alias in self._used_aliases:
            vcprint(
                f"[Matrx ORM] Error! Database alias '{config.alias}' already registered. Ignoring new registration.",
                color="red",
            )
            raise DatabaseConfigError(
                f"Database alias '{config.alias}' already used. Please use a different alias."
            )

        self._used_aliases.append(config.alias)

        required_fields = [
            config.host,
            config.port,
            config.database_name,
            config.user,
            config.password,
            config.alias,
        ]

        if not all(required_fields):
            missing = []
            if not config.host:
                missing.append("host")
            if not config.protocol:
                missing.append("protocol")
            if not config.alias:
                missing.append("alias")
            if not config.port:
                missing.append("port")
            if not config.database_name:
                missing.append("database_name")
            if not config.user:
                missing.append("user")
            if not config.password:
                missing.append("password")
            raise DatabaseConfigError(
                f"Missing required configuration fields for '{config.name}': "
                f"{', '.join(missing)}. Please check your environment variables."
            )

        self._configs[config.name] = config

    def get_database_config(self, config_name: str) -> dict:
        if config_name not in self._configs:
            raise DatabaseConfigError(
                f"Configuration '{config_name}' not found in registered databases"
            )

        config = self._configs[config_name]
        return {
            "host": config.host,
            "port": config.port,
            "protocol": config.protocol,
            "database_name": config.database_name,
            "user": config.user,
            "password": config.password,
            "alias": config.alias,
            "additional_schemas": config.additional_schemas,
            "pool_mode": config.pool_mode,
            "pool_min": config.pool_min,
            "pool_max": config.pool_max,
            "command_timeout": config.command_timeout,
            "write_queue_enabled": config.write_queue_enabled,
            "write_concurrency": config.write_concurrency,
            "write_queue_size": config.write_queue_size,
            "write_queue_timeout": config.write_queue_timeout,
        }

    def get_config_dataclass(self, config_name: str) -> DatabaseProjectConfig:
        if config_name not in self._configs:
            raise DatabaseConfigError(
                f"Configuration '{config_name}' not found in registered databases"
            )
        return self._configs[config_name]

    def get_manager_config_by_project_name(self, config_name):
        if config_name not in self._configs:
            raise DatabaseConfigError(
                f"Configuration '{config_name}' not found in registered databases"
            )
        config = self._configs[config_name]
        return config.manager_config_overrides

    def get_all_database_configs(self) -> dict[str, dict[str, Any]]:
        all_configs = {}
        for config_name, config in self._configs.items():
            all_configs[config_name] = {
                "host": config.host,
                "port": config.port,
                "protocol": config.protocol,
                "database_name": config.database_name,
                "user": config.user,
                "password": config.password,
                "manager_config_overrides": config.manager_config_overrides,
                "alias": config.alias,
            }
        return all_configs

    def get_all_database_project_names(self) -> list[str]:
        all_configs = self.get_all_database_configs()
        return list(all_configs.keys())

    def get_all_database_projects(self) -> list[dict]:
        items = []
        all_configs = self.get_all_database_configs()
        for project, config in all_configs.items():
            config["database_project"] = project
            items.append(config)
        return items

    def get_all_database_projects_redacted(self) -> list[dict[str, Any]]:
        items = self.get_all_database_projects()
        return cast(list[dict[str, Any]], redact_object(items))

    def get_database_alias(self, db_project):
        if db_project not in self._configs:
            raise DatabaseConfigError(
                f"Database project '{db_project}' not found in registered databases"
            )
        return self._configs[db_project].alias


registry = DatabaseRegistry()


def get_database_config(config_name: str) -> dict:
    return registry.get_database_config(config_name)


def get_manager_config(config_name: str) -> dict:
    return registry.get_manager_config_by_project_name(config_name)


def register_database(config: DatabaseProjectConfig) -> None:
    registry.register(config)


def register_database_from_env(
    name: str,
    env_prefix: str,
    alias: str = "",
    additional_schemas: list[str] | None = None,
    entity_overrides: dict[str, Any] | None = None,
    field_overrides: dict[str, Any] | None = None,
    manager_config_overrides: dict[str, Any] | None = None,
    env_var_overrides: dict[str, str] | None = None,
    pool_mode: str | None = None,
    pool_min: int | None = None,
    pool_max: int | None = None,
    command_timeout: int | None = None,
    write_queue_enabled: bool | None = None,
    write_concurrency: int | None = None,
    write_queue_size: int | None = None,
    write_queue_timeout: float | None = None,
) -> bool:
    """
    Read database connection details from environment variables, validate them,
    and register the database. Prints colored diagnostics for missing or defaulted vars.

    Default env var names (using env_prefix, e.g. "PRIMARY_DB"):
        {env_prefix}_HOST, {env_prefix}_PORT, {env_prefix}_NAME,
        {env_prefix}_USER, {env_prefix}_PASSWORD
        {env_prefix}_PROTOCOL  (optional, defaults to "postgresql")

    Pool and write-queue settings can be passed as keyword arguments or read from
    env vars ({env_prefix}_POOL_MODE, _POOL_MIN, _POOL_MAX, _COMMAND_TIMEOUT,
    _WRITE_QUEUE_ENABLED, _WRITE_CONCURRENCY, _WRITE_QUEUE_SIZE, _WRITE_QUEUE_TIMEOUT).
    Keyword arguments take precedence over env vars.

    env_var_overrides lets you remap any key to a different env var name.
    Example: {"NAME": "SUPABASE_MATRIX_DATABASE_NAME"} reads that env var
    instead of constructing {env_prefix}_NAME.

    Returns True if registration succeeded, False otherwise.
    """
    _REQUIRED = ["HOST", "PORT", "NAME", "USER", "PASSWORD"]
    _OPTIONAL = {"PROTOCOL": "postgresql"}
    _overrides = env_var_overrides or {}

    vcprint(name, "\n[MATRX ORM] Registering database", color="cyan")

    missing: list[str] = []
    resolved: dict[str, str] = {}

    for key in _REQUIRED:
        env_var = _overrides.get(key, f"{env_prefix}_{key}")
        val = os.environ.get(env_var, "").strip()
        if val:
            resolved[key] = val
        else:
            missing.append(env_var)

    for key, default in _OPTIONAL.items():
        env_var = _overrides.get(key, f"{env_prefix}_{key}")
        val = os.environ.get(env_var, "").strip()
        if val:
            resolved[key] = val
        else:
            resolved[key] = default
            vcprint(
                f"  '{env_var}' not set — using default: '{default}'",
                color="yellow",
            )

    if missing:
        vcprint(
            f"  Database '{name}' NOT registered — missing required env vars:",
            color="red",
        )
        for var in missing:
            vcprint(f"    • {var}", color="red")
        return False

    _INT_POOL_OPTS: dict[str, tuple[str, int]] = {
        "POOL_MIN": ("pool_min", 5),
        "POOL_MAX": ("pool_max", 20),
        "COMMAND_TIMEOUT": ("command_timeout", 10),
        "WRITE_CONCURRENCY": ("write_concurrency", 10),
        "WRITE_QUEUE_SIZE": ("write_queue_size", 200),
    }
    _FLOAT_POOL_OPTS: dict[str, tuple[str, float]] = {
        "WRITE_QUEUE_TIMEOUT": ("write_queue_timeout", 30.0),
    }

    pool_kwargs: dict[str, Any] = {}

    if pool_mode is not None:
        pool_kwargs["pool_mode"] = pool_mode
    else:
        env_var = _overrides.get("POOL_MODE", f"{env_prefix}_POOL_MODE")
        val = os.environ.get(env_var, "").strip()
        if val:
            pool_kwargs["pool_mode"] = val

    if write_queue_enabled is not None:
        pool_kwargs["write_queue_enabled"] = write_queue_enabled
    else:
        env_var = _overrides.get("WRITE_QUEUE_ENABLED", f"{env_prefix}_WRITE_QUEUE_ENABLED")
        val = os.environ.get(env_var, "").strip().lower()
        if val in ("0", "false", "no", "off"):
            pool_kwargs["write_queue_enabled"] = False
        elif val in ("1", "true", "yes", "on"):
            pool_kwargs["write_queue_enabled"] = True

    local_overrides = {
        "pool_min": pool_min,
        "pool_max": pool_max,
        "command_timeout": command_timeout,
        "write_concurrency": write_concurrency,
        "write_queue_size": write_queue_size,
    }
    for env_key, (attr, default) in _INT_POOL_OPTS.items():
        local_val = local_overrides.get(attr)
        if local_val is not None:
            pool_kwargs[attr] = local_val
        else:
            env_var = _overrides.get(env_key, f"{env_prefix}_{env_key}")
            val = os.environ.get(env_var, "").strip()
            if val:
                try:
                    pool_kwargs[attr] = int(val)
                except ValueError:
                    pass

    if write_queue_timeout is not None:
        pool_kwargs["write_queue_timeout"] = write_queue_timeout
    else:
        for env_key, (attr, default) in _FLOAT_POOL_OPTS.items():
            env_var = _overrides.get(env_key, f"{env_prefix}_{env_key}")
            val = os.environ.get(env_var, "").strip()
            if val:
                try:
                    pool_kwargs[attr] = float(val)
                except ValueError:
                    pass

    try:
        config = DatabaseProjectConfig(
            name=name,
            alias=alias or name,
            host=resolved["HOST"],
            port=resolved["PORT"],
            protocol=resolved["PROTOCOL"],
            database_name=resolved["NAME"],
            user=resolved["USER"],
            password=resolved["PASSWORD"],
            additional_schemas=additional_schemas or [],
            entity_overrides=entity_overrides or {},
            field_overrides=field_overrides or {},
            manager_config_overrides=manager_config_overrides or {},
            **pool_kwargs,
        )
        registry.register(config)
        vcprint(name, "Database registered successfully", color="green")
        return True
    except DatabaseConfigError as e:
        error_message = f"Database registration failed: {e}"
        vcprint(name, error_message, color="red")
        return False


def get_connection_string(config_name: str) -> str:
    config = get_database_config(config_name)
    connection_string = f"{config['protocol']}://{config['user']}:{redact_string(config['password'])}@{config['host']}:{config['port']}/{config['database_name']}"
    return connection_string


def get_all_database_project_names() -> list[str]:
    return registry.get_all_database_project_names()


def get_all_database_projects_redacted() -> list[dict]:
    return registry.get_all_database_projects_redacted()


def get_database_alias(db_project):
    return registry.get_database_alias(db_project)


def get_schema_builder_overrides(db_project: str) -> dict[str, dict[str, Any]]:
    """Return the schema-builder override dicts registered for *db_project*.

    Returns a dict with keys ``entity_overrides`` and ``field_overrides``.
    Both default to empty dicts when not supplied by the caller.
    """
    config = registry.get_config_dataclass(db_project)
    return {
        "entity_overrides": config.entity_overrides,
        "field_overrides": config.field_overrides,
    }


def get_code_config(db_project: str) -> dict[str, Any]:
    python_root: str = str(settings.ADMIN_PYTHON_ROOT)
    ts_root: str = str(settings.ADMIN_TS_ROOT)

    ADMIN_PYTHON_ROOT = os.path.join(python_root, "db")
    ADMIN_TS_ROOT = ts_root

    CODE_BASICS_PYTHON_MODELS = {
        "temp_path": "models.py",
        "root": ADMIN_PYTHON_ROOT,
        "file_location": "# File: db/models.py",
        # Note: import_lines are dynamically replaced by generate_models() in schema.py
        # based on the actual field types used. This is a fallback default only.
        "import_lines": [
            "from matrx_orm import Model, model_registry, BaseDTO, BaseManager",
            "from enum import Enum",
            "from dataclasses import dataclass",
            "from typing import ClassVar",
        ],
        "additional_top_lines": [],
        "additional_bottom_lines": [],
    }

    CODE_BASICS_TYPESCRIPT_ENTITY_FIELDS = {
        "temp_path": "entityFieldNameGroups.ts",
        "root": os.path.join(ADMIN_TS_ROOT, "utils/schema/"),
        "file_location": "// File: utils/schema/entityFieldNameGroups.ts",
        "import_lines": [
            "'use client';",
            "import { EntityAnyFieldKey, EntityKeys } from '@/types';",
        ],
        "additional_top_lines": [
            "export type FieldGroups = {",
            "    nativeFields: EntityAnyFieldKey<EntityKeys>[];",
            "    primaryKeyFields: EntityAnyFieldKey<EntityKeys>[];",
            "    nativeFieldsNoPk: EntityAnyFieldKey<EntityKeys>[];",
            "};",
            "",
            "export type EntityFieldNameGroupsType = Record<EntityKeys, FieldGroups>;",
            "",
            "export const entityFieldNameGroups: EntityFieldNameGroupsType =",
        ],
        "additional_bottom_lines": [],
    }

    CODE_BASICS_PRIMARY_KEYS = {
        "temp_path": "entityPrimaryKeys.ts",
        "root": os.path.join(ADMIN_TS_ROOT, "utils/schema/"),
        "file_location": "// File: utils/schema/entityPrimaryKeys.ts",
        "import_lines": [],
        "additional_top_lines": [],
        "additional_bottom_lines": [],
    }

    CODE_BASICS_TS_SCHEMA = {
        "temp_path": "initialSchemas.ts",
        "root": os.path.join(ADMIN_TS_ROOT, "utils/schema/"),
        "file_location": "// File: utils/schema/initialSchemas.ts",
        "import_lines": [
            "import {AutomationTableName,DataStructure,FetchStrategy,NameFormat,FieldDataOptionsType} from '@/types/AutomationSchemaTypes';",
            "import {AutomationEntity, EntityData, EntityDataMixed, EntityDataOptional, EntityDataWithKey, ProcessedEntityData} from '@/types/entityTypes';",
        ],
        "additional_top_lines": [],
        "additional_bottom_lines": [],
    }

    CODE_BASICS_TS_INDIVIDUAL_TABLE_SCHEMAS = {
        "temp_path": "initialTableSchemas.ts",
        "root": os.path.join(ADMIN_TS_ROOT, "utils/schema/"),
        "file_location": "// File: utils/schema/initialTableSchemas.ts",
        "import_lines": ["import {AutomationEntity, TypeBrand} from '@/types';"],
        "additional_top_lines": [],
        "additional_bottom_lines": [],
    }

    CODE_BASICS_TS_TYPES = {
        "temp_path": "AutomationSchemaTypes.ts",
        "root": os.path.join(ADMIN_TS_ROOT, "types/"),
        "file_location": "// File: types/AutomationSchemaTypes.ts",
        "import_lines": [
            "import {AutomationEntity, EntityData, EntityKeys, EntityDataMixed, EntityDataOptional, EntityDataWithKey, ProcessedEntityData} from '@/types/entityTypes';",
            "import { EntityState } from '@/lib/redux/entity/types/stateTypes';",
        ],
        "additional_top_lines": [],
        "additional_bottom_lines": [],
    }

    CODE_BASICS_TS_ENTITY_OVERRIDES = {
        "temp_path": "entityOverrides.ts",
        "root": os.path.join(ADMIN_TS_ROOT, "utils/schema/schema-processing/"),
        "file_location": "// File: utils/schema/schema-processing/entityOverrides.ts",
        "import_lines": [
            "import { EntityKeys } from '@/types';",
            "import { EntityOverrides } from './overrideTypes';",
        ],
        "additional_top_lines": [],
        "additional_bottom_lines": [],
    }

    CODE_BASICS_TS_ENTITY_FIELD_OVERRIDES = {
        "temp_path": "fieldOverrides.ts",
        "root": os.path.join(ADMIN_TS_ROOT, "utils/schema/schema-processing/"),
        "file_location": "// File: utils/schema/schema-processing/fieldOverrides.ts",
        "import_lines": [
            'import { AllEntityFieldOverrides, AllFieldOverrides } from "./overrideTypes";'
        ],
        "additional_top_lines": [],
        "additional_bottom_lines": [],
    }

    CODE_BASICS_TYPESCRIPT_LOOKUP = {
        "temp_path": "lookupSchema.ts",
        "root": os.path.join(ADMIN_TS_ROOT, "utils/schema/"),
        "file_location": "// File: utils/schema/lookupSchema.ts",
        "import_lines": "import {EntityNameToCanonicalMap,FieldNameToCanonicalMap,EntityNameFormatMap,FieldNameFormatMap} from '@/types/entityTypes';",
        "additional_top_lines": [],
        "additional_bottom_lines": [],
    }

    CODE_BASICS_ENTITY_TYPESCRIPT_TYPES = {
        "temp_path": "entities.ts",
        "root": os.path.join(ADMIN_TS_ROOT, "types/"),
        "file_location": "// File: types/entities.ts",
        "import_lines": [],
        "additional_top_lines": [],
        "additional_bottom_lines": [],
    }

    CODE_BASICS_TS_ENTITY_MAIN_HOOKS = {
        "temp_path": "entityMainHooks.ts",
        "root": os.path.join(ADMIN_TS_ROOT, "lib/redux/entity/hooks/"),
        "file_location": "// File: lib/redux/entity/hooks/entityMainHooks.ts",
        "import_lines": [],
        "additional_top_lines": [],
        "additional_bottom_lines": [],
    }

    CODE_BASICS_PYTHON_BASE_MANAGER = {
        "temp_path": "",
        "root": os.path.join(ADMIN_PYTHON_ROOT, "managers"),
        "file_location": "# File: db/managers/",
        "import_lines": [],
        "additional_top_lines": [],
        "additional_bottom_lines": [],
    }

    CODE_BASICS_PYTHON_BASE_ALL_MANAGERS = {
        "temp_path": "__init__.py",
        "root": os.path.join(ADMIN_PYTHON_ROOT, "managers"),
        "file_location": "# File: db/managers/__init__.py",
        "import_lines": [],
        "additional_top_lines": [],
        "additional_bottom_lines": [],
    }

    CODE_BASICS_PYTHON_AUTO_CONFIG = {
        "temp_path": "auto_config.py",
        "root": os.path.join(ADMIN_PYTHON_ROOT, "helpers"),
        "file_location": "# File: db/helpers/auto_config.py",
        "import_lines": [],
        "additional_top_lines": [],
        "additional_bottom_lines": [],
    }

    SOCKET_SCHEMA_TS_INTERFACES = {
        "temp_path": "socket-schema-types.ts",
        "root": os.path.join(ADMIN_TS_ROOT, "types/"),
        "file_location": "// File: types/socket-schema-types.ts",
        "import_lines": "",
        "additional_top_lines": [],
        "additional_bottom_lines": [],
    }

    SOCKET_SCHEMA_TS_SCHEMAS = {
        "temp_path": "socket-schema.ts",
        "root": os.path.join(ADMIN_TS_ROOT, "constants/"),
        "file_location": "// File Location: constants/socket-schema.ts",
        "import_lines": [],
        "additional_top_lines": [],
        "additional_bottom_lines": [],
    }

    CODE_BASICS = {
        "python_models": CODE_BASICS_PYTHON_MODELS,
        "typescript_entity_fields": CODE_BASICS_TYPESCRIPT_ENTITY_FIELDS,
        "primary_keys": CODE_BASICS_PRIMARY_KEYS,
        "typescript_schema": CODE_BASICS_TS_SCHEMA,
        "typescript_individual_table_schemas": CODE_BASICS_TS_INDIVIDUAL_TABLE_SCHEMAS,
        "typescript_types": CODE_BASICS_TS_TYPES,
        "typescript_entity_overrides": CODE_BASICS_TS_ENTITY_OVERRIDES,
        "typescript_entity_field_overrides": CODE_BASICS_TS_ENTITY_FIELD_OVERRIDES,
        "typescript_lookup": CODE_BASICS_TYPESCRIPT_LOOKUP,
        "entity_typescript_types": CODE_BASICS_ENTITY_TYPESCRIPT_TYPES,
        "socket_ts_interfaces": SOCKET_SCHEMA_TS_INTERFACES,
        "socket_ts_schemas": SOCKET_SCHEMA_TS_SCHEMAS,
        "typescript_entity_main_hooks": CODE_BASICS_TS_ENTITY_MAIN_HOOKS,
        "python_base_manager": CODE_BASICS_PYTHON_BASE_MANAGER,
        "python_auto_config": CODE_BASICS_PYTHON_AUTO_CONFIG,
        "python_all_managers": CODE_BASICS_PYTHON_BASE_ALL_MANAGERS,
    }

    return CODE_BASICS
