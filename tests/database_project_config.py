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
                               manager_config_overrides=MANAGER_CONFIG_OVERRIDES)

register_database(config)



