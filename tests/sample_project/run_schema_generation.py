import sys
from pathlib import Path

# Put this directory on the path so `import database_registry` works directly,
# and put the src/ dir on the path so matrx_orm is importable without installing.
_here = Path(__file__).parent.resolve()
sys.path.insert(0, str(_here))
sys.path.insert(0, str(_here.parent.parent / "src"))

import database_registry  # noqa: E402  — registers primary + secondary databases

from matrx_utils import clear_terminal, vcprint  # noqa: E402
from matrx_orm.schema_builder import SchemaManager  # noqa: E402

clear_terminal()

# ---------------------------------------------------------------------------
# Primary database — run this block to generate from the primary Supabase DB
# ---------------------------------------------------------------------------
schema = "public"
database_project = "primary"
additional_schemas = ["auth"]
save_direct = False   # set True to write directly to ADMIN_PYTHON_ROOT

schema_manager = SchemaManager(
    schema=schema,
    database_project=database_project,
    additional_schemas=additional_schemas,
    save_direct=save_direct,
)
schema_manager.initialize()

matrx_schema_entry = schema_manager.schema.generate_schema_files()
matrx_models = schema_manager.schema.generate_models()

analysis = schema_manager.analyze_schema()
vcprint(
    data=analysis,
    title="Schema Analysis — primary",
    pretty=True,
    verbose=False,
    color="yellow",
)

schema_manager.schema.code_handler.print_all_batched()

# ---------------------------------------------------------------------------
# Secondary database — uncomment to also generate from the secondary DB
# ---------------------------------------------------------------------------
# schema_manager_2 = SchemaManager(
#     schema="public",
#     database_project="secondary",
#     additional_schemas=[],
#     save_direct=False,
# )
# schema_manager_2.initialize()
# schema_manager_2.schema.generate_schema_files()
# schema_manager_2.schema.generate_models()
# analysis_2 = schema_manager_2.analyze_schema()
# vcprint(data=analysis_2, title="Schema Analysis — secondary", pretty=True, verbose=False, color="cyan")
# schema_manager_2.schema.code_handler.print_all_batched()
