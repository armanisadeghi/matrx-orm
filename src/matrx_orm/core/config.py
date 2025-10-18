from dataclasses import dataclass, field
from typing import Dict
from matrx_utils import settings, vcprint, redact_object, redact_string
import os

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

    alias: str = ""
    manager_config_overrides: Dict = field(default_factory=dict)


class DatabaseRegistry:
    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseRegistry, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self._configs: Dict[str, DatabaseProjectConfig] = {}
            self._used_aliases: list[str] = []
            self._initialized = True

    def register(self, config: DatabaseProjectConfig) -> None:
        if config.name in self._configs:
            vcprint(f"[Matrx ORM] WARNING! Database configuration '{config.name}' already registered. Ignoring new registration.", color="yellow")
            return
        
        if config.alias == "":
            vcprint(f"[Matrx ORM] Error! Database alias cannot be empty. Please use a different alias.", color="red")
            raise DatabaseConfigError(f"Database alias cannot be empty. Please use a different alias.")

        if config.alias in self._used_aliases:
            vcprint(f"[Matrx ORM] Error! Database alias '{config.alias}' already registered. Ignoring new registration.", color="red")
            raise DatabaseConfigError(f"Database alias '{config.alias}' already used. Please use a different alias.")

        self._used_aliases.append(config.alias)

        required_fields = [config.host, config.port, config.database_name, config.user, config.password, config.alias]

        if not all(required_fields):
            missing = []
            if not config.host: missing.append("host")
            if not config.alias: missing.append("alias")
            if not config.port: missing.append("port")
            if not config.database_name: missing.append("database_name")
            if not config.user: missing.append("user")
            if not config.password: missing.append("password")
            raise DatabaseConfigError(
                f"Missing required configuration fields for '{config.name}': " f"{', '.join(missing)}. Please check your environment variables.")

        self._configs[config.name] = config

    def get_database_config(self, config_name: str) -> dict:
        if config_name not in self._configs:
            raise DatabaseConfigError(f"Configuration '{config_name}' not found in registered databases")

        config = self._configs[config_name]
        return {
            "host": config.host,
            "port": config.port,
            "database_name": config.database_name,
            "user": config.user,
            "password": config.password,
            "alias": config.alias
        }

    def get_config_dataclass(self, config_name: str) -> DatabaseProjectConfig:
        if config_name not in self._configs:
            raise DatabaseConfigError(f"Configuration '{config_name}' not found in registered databases")
        return self._configs[config_name]

    def get_manager_config_by_project_name(self, config_name):
        if config_name not in self._configs:
            raise DatabaseConfigError(f"Configuration '{config_name}' not found in registered databases")
        config = self._configs[config_name]
        return config.manager_config_overrides

    def get_all_database_configs(self) -> Dict[str, dict]:
        all_configs = {}
        for config_name, config in self._configs.items():
            all_configs[config_name] = {
                "host": config.host,
                "port": config.port,
                "database_name": config.database_name,
                "user": config.user,
                "password": config.password,
                "manager_config_overrides": config.manager_config_overrides,
                "alias": config.alias
            }
        return all_configs

    def get_all_database_project_names(self) -> list[str]:
        all_configs = self.get_all_database_configs()
        return list(all_configs.keys())
    
    def get_all_database_projects(self) -> list[dict]:
        items =[]
        all_configs = self.get_all_database_configs()
        for project, config in all_configs.items():
            config["database_project"] = project
            items.append(config)
        return items
    
    def get_all_database_projects_redacted(self) -> list[dict]:
        items = self.get_all_database_projects()
        return redact_object(items)


    def get_database_alias(self, db_project):
        if db_project not in self._configs:
            raise DatabaseConfigError(f"Database project '{db_project}' not found in registered databases")
        return self._configs[db_project].alias


registry = DatabaseRegistry()


def get_database_config(config_name: str) -> dict:
    return registry.get_database_config(config_name)


def get_manager_config(config_name: str) -> dict:
    return registry.get_manager_config_by_project_name(config_name)


def register_database(config: DatabaseProjectConfig) -> None:
    registry.register(config)


def get_connection_string(config_name: str) -> str:
    config = get_database_config(config_name)
    connection_string = f"postgresql://{config['user']}:{redact_string(config['password'])}@{config['host']}:{config['port']}/{config['database_name']}"
    return connection_string


def get_all_database_project_names() -> list[str]:
    return registry.get_all_database_project_names()


def get_all_database_projects_redacted() -> list[dict]:
    return registry.get_all_database_projects_redacted()

def get_database_alias(db_project):
    return registry.get_database_alias(db_project)

def get_code_config(db_project):
    python_root, ts_root = settings.ADMIN_PYTHON_ROOT, settings.ADMIN_TS_ROOT

    usable_name = get_database_alias(db_project)
    ADMIN_PYTHON_ROOT = os.path.join(python_root, "database", usable_name)
    ADMIN_TS_ROOT = ts_root

    CODE_BASICS_PYTHON_MODELS = {
        "temp_path": "models.py",
        "root": ADMIN_PYTHON_ROOT,
        "file_location": f"# File: database/{usable_name}/models.py",
        "import_lines": [
            "import database_registry",
            "from matrx_orm import CharField, EnumField, DateField, TextField, IntegerField, FloatField, BooleanField, DateTimeField, UUIDField, JSONField, DecimalField, BigIntegerField, SmallIntegerField, JSONBField, UUIDArrayField, JSONBArrayField, ForeignKey, Model, model_registry, BaseDTO, BaseManager",
            "from enum import Enum",
            "from dataclasses import dataclass"
        ],
        "additional_top_lines": [
            "verbose = False",
            "debug = False",
            "info = True",
        ],
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
        "import_lines": ['import { AllEntityFieldOverrides, AllFieldOverrides } from "./overrideTypes";'],
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
        "file_location": f"# File: database/{usable_name}/managers/",
        "import_lines": [
            "from matrx_utils import vcprint",
        ],
        "additional_top_lines": [],
        "additional_bottom_lines": [],
    }

    CODE_BASICS_PYTHON_BASE_ALL_MANAGERS = {
        "temp_path": "__init__.py",
        "root": os.path.join(ADMIN_PYTHON_ROOT, "managers"),
        "file_location": f"# File: database/{usable_name}/managers/__init__.py",
        "import_lines": [
        ],
        "additional_top_lines": [],
        "additional_bottom_lines": [],
    }

    CODE_BASICS_PYTHON_AUTO_CONFIG = {
        "temp_path": "auto_config.py",
        "root": os.path.join(ADMIN_PYTHON_ROOT, "helpers"),
        "file_location": f"# File: database/{db_project}/helpers/auto_config.py",
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
        "python_all_managers": CODE_BASICS_PYTHON_BASE_ALL_MANAGERS
    }

    return CODE_BASICS