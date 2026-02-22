from matrx_utils import DataTransformer
import os
import dotenv

dotenv.load_dotenv()

# If this environmental variable is set to your actual project root, auto-generated python files will overwrite the live, existing files
ADMIN_PYTHON_ROOT = os.getenv("ADMIN_PYTHON_ROOT", "")

# If this environmental variable is set to your actual project root, auto-generated typescript files will overwrite the live, existing files
ADMIN_TS_ROOT = os.getenv("ADMIN_TS_ROOT", "")


dt_utils = DataTransformer()

# Central debug configuration for the entire schema builder.
# Values can be overridden at runtime by run_schema_generation() from the yaml
# debug section, or by setting env vars MATRX_DEBUG, MATRX_VERBOSE, MATRX_INFO.
DEBUG_CONFIG = {
    "tables": [],
    "columns": [],
    "base_type": [],
    "info": os.getenv("MATRX_INFO", "").lower() in ("1", "true"),
    "debug": os.getenv("MATRX_DEBUG", "").lower() in ("1", "true"),
    "verbose": os.getenv("MATRX_VERBOSE", "").lower() in ("1", "true"),
}
