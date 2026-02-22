"""Schema builder helpers — generators, git checks, and utilities."""

from matrx_orm.schema_builder.helpers.entity_generators import (
    generate_full_typescript_file,
    generate_typescript_field_overrides,
    merge_component_props,
    generate_all_entity_main_hooks,
    generate_complete_main_hooks_file,
    generate_entity_main_hook,
    generate_main_hook_imports,
    to_camel_case,
    to_pascal_case,
    generate_imports,
    generate_multiple_entities,
    generate_typescript_entity,
)

from matrx_orm.schema_builder.common import ADMIN_PYTHON_ROOT, ADMIN_TS_ROOT
from matrx_orm.schema_builder.helpers.git_checker import check_git_status
from matrx_orm.schema_builder.helpers.base_generators import (
    generate_active_methods,
    generate_active_relation_methods,
    generate_base_manager_class,
    generate_core_relation_methods,
    generate_filter_field_methods,
    generate_manager_class,
    generate_m2m_relation_methods,
    generate_or_not_methods,
    generate_singleton_manager,
    generate_to_dict_methods,
    generate_to_dict_relation_methods,
    generate_utility_methods,
    save_manager_class,
)

__all__ = [
    # git_checker
    "ADMIN_PYTHON_ROOT",
    "ADMIN_TS_ROOT",
    "check_git_status",
    # entity_generators
    "generate_all_entity_main_hooks",
    "generate_complete_main_hooks_file",
    "generate_entity_main_hook",
    "generate_main_hook_imports",
    "to_camel_case",
    "to_pascal_case",
    "generate_imports",
    "generate_multiple_entities",
    "generate_typescript_entity",
    # base_generators
    "generate_active_methods",
    "generate_active_relation_methods",
    "generate_base_manager_class",
    "generate_core_relation_methods",
    "generate_filter_field_methods",
    "generate_manager_class",
    "generate_m2m_relation_methods",
    "generate_or_not_methods",
    "generate_singleton_manager",
    "generate_to_dict_methods",
    "generate_to_dict_relation_methods",
    "generate_utility_methods",
    "save_manager_class",
    
    # other
    "generate_full_typescript_file",
    "generate_typescript_field_overrides",
    "merge_component_props",
]
