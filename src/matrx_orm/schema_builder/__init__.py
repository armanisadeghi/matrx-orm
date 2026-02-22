"""Schema builder — reverse migrations (DB → Code) and model generation."""

from matrx_orm.schema_builder import helpers
from matrx_orm.schema_builder.common import (
    DEBUG_CONFIG,
    OutputConfig,
)
from matrx_orm.schema_builder.generator import (
    get_schema_structure,
    generate_dto_and_manager,
)

from matrx_orm.schema_builder.helpers import (
    check_git_status,
    generate_manager_class,
)
from matrx_orm.schema_builder.schema_manager import (
    SchemaManager,
)
from matrx_orm.schema_builder.runner import (
    run_schema_generation,
)


__all__ = [
    "ADMIN_PYTHON_ROOT",
    "ADMIN_TS_ROOT",
    "DEBUG_CONFIG",
    "OutputConfig",
    "schema_builder_verbose",
    "SchemaManager",
    "run_schema_generation",
    "check_git_status",
    "get_schema_structure",
    "generate_dto_and_manager",
    "generate_manager_class",
    "helpers",
]
