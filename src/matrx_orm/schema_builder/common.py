from matrx_utils import DataTransformer
import os
import dotenv

dotenv.load_dotenv()

# If this environmental variable is set to your actual project root, auto-generated python files will overwrite the live, existing files
ADMIN_PYTHON_ROOT = os.getenv("ADMIN_PYTHON_ROOT", "")

# If this environmental variable is set to your actual project root, auto-generated typescript files will overwrite the live, existing files
ADMIN_TS_ROOT = os.getenv("ADMIN_TS_ROOT", "")


dt_utils = DataTransformer()

schema_builder_save_direct = True


DEBUG_CONFIG = {
    "tables": [],
    "columns": [],
    "base_type": [],
    "info": True,
    "debug": False,
    "verbose": False,
}
