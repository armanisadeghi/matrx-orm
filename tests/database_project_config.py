import os
from matrx_utils.conf import settings, NotConfiguredError
from matrx_utils import vcprint
from matrx_orm import DatabaseProjectConfig, register_database

# EXAMPLE ,NOT A TEST REALLY
try:
    ADMIN_SAVE_DIRECT_ROOT = settings.ADMIN_SAVE_DIRECT_ROOT
except (AttributeError, NotConfiguredError):
    ADMIN_SAVE_DIRECT_ROOT = ""
    vcprint("ADMIN_SAVE_DIRECT_ROOT not found in settings or environment. Defaulting to : '' ", color="red")

# ====== IMPORTANT: If save_direct = True in generator.py, live files will be overwritten with auto-generated files ======

# If this environmental variable is set to your actual project root, auto-generated python files will overwrite the live, existing files
try:
    ADMIN_PYTHON_ROOT = settings.ADMIN_PYTHON_ROOT
except (AttributeError, NotConfiguredError):
    ADMIN_PYTHON_ROOT = ""
    vcprint("ADMIN_PYTHON_ROOT not found in settings or environment. Defaulting to : '' ", color="red")


# If this environmental variable is set to your actual project root, auto-generated typescript files will overwrite the live, existing files
try:
    ADMIN_TS_ROOT = settings.ADMIN_TS_ROOT
except (AttributeError, NotConfiguredError):
    ADMIN_TS_ROOT = ""
    vcprint("ADMIN_TS_ROOT not found in settings or environment. Defaulting to : '' ", color="red")

# =========================================================================================================================

DEBUG_MODE = False

if DEBUG_MODE:
    print("DEBUG.....")
    print("ADMIN_PYTHON_ROOT", ADMIN_PYTHON_ROOT)
    print("ADMIN_TS_ROOT", ADMIN_TS_ROOT)
    print("-----------------------------\n")

CODE_BASICS_PYTHON_MODELS = {
    "temp_path": "models.py",
    "root": os.path.join(ADMIN_PYTHON_ROOT, "database/orm"),
    "file_location": "# File: database/orm/models.py",
    "import_lines": [
        "from matrx_orm import (CharField, EnumField, DateField, TextField, IntegerField, FloatField, BooleanField, DateTimeField, UUIDField, JSONField, DecimalField, BigIntegerField, SmallIntegerField, JSONBField, UUIDArrayField, JSONBArrayField, ForeignKey)",
        "from matrx_orm import Model",
        "from matrx_orm import model_registry",
        "from enum import Enum",
        "from dataclasses import dataclass",
        "from matrx_orm import BaseDTO, BaseManager",
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
    "import_lines": ["import {AutomationEntity, TypeBrand} from '@/types/entityTypes';"],
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
    "temp_path": "all_managers.py",
    "root": os.path.join(ADMIN_PYTHON_ROOT, "database/orm/extended/managers/"),
    "file_location": "# File: database/orm/extended/managers/all_managers.py",
    "import_lines": [
        "from matrx_utils import vcprint",
    ],
    "additional_top_lines": [],
    "additional_bottom_lines": [],
}

CODE_BASICS_PYTHON_AUTO_CONFIG = {
    "temp_path": "auto_config.py",
    "root": os.path.join(ADMIN_PYTHON_ROOT, "database/schema_builder/helpers/"),
    "file_location": "# File: database/schema_builder/helpers/auto_config.py",
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
}



data_input_component_overrides = {
    "relations": ["message_broker", "broker", "data_broker"],
    "filter_fields": [
        "options",
        "component",
    ],
}

ai_model_overrides = {
    "relations": ["ai_provider", "ai_model_endpoint", "ai_settings", "recipe_model"],
    "filter_fields": [
        "name",
        "common_name",
        "provider",
        "model_class",
        "model_provider",
    ],
}

compiled_recipe_overrides = {
    "relations": ["recipe", "applet"],
    "filter_fields": ["recipe_id", "user_id", "version"],
    "include_core_relations": True,
    "include_filter_fields": True,
}


MANAGER_CONFIG_OVERRIDES = {
    "ai_model": ai_model_overrides,
    "data_input_component": data_input_component_overrides,
    "compiled_recipe": compiled_recipe_overrides,
}




####

config = DatabaseProjectConfig(name="supabase_automation_matrix",
                               user=settings.DB_USER,
                               password=settings.DB_PASS,
                               host=settings.DB_HOST,
                               port=settings.DB_PORT,
                               database_name=settings.DB_NAME,
                               code_basics=CODE_BASICS,
                               manager_config_overrides=MANAGER_CONFIG_OVERRIDES)

register_database(config)



