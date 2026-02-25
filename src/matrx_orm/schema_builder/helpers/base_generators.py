import os
from matrx_utils.fancy_prints.fancy_prints import plt


def generate_base_manager_class(
    models_module_path: str,
    model_pascal: str,
    model_name: str,
    model_name_plural: str,
    model_name_snake: str,
    relations: list[str] | None = None,
) -> str:
    """Generate the minimal core manager class with both ModelView and legacy DTO.

    Both classes are generated so that:
    - Existing code that imports ``{Model}DTO`` from this file continues to work
      without any changes (zero breaking changes).
    - New code can use ``{Model}View`` / ``view_class`` for the flat, zero-
      duplication projection pattern.
    - The manager uses ``view_class`` by default. To revert to the legacy DTO
      path set ``view_class = None`` and pass ``dto_class={Model}DTO`` to super().
    """
    prefetch_list = repr(relations or [])
    return f"""
from dataclasses import dataclass
from typing import Any

from matrx_orm import BaseManager, BaseDTO, ModelView
from matrx_utils import vcprint

from {models_module_path} import {model_pascal}


# ---------------------------------------------------------------------------
# ModelView (new) — preferred projection layer.
# Stores results flat on the model instance; no duplication, no nesting.
# ---------------------------------------------------------------------------

class {model_pascal}View(ModelView):
    \"\"\"
    Declarative view for {model_pascal}.

    Configure what gets fetched and shaped automatically on every load:

      prefetch    — relation names to fetch concurrently (FK / IFK / M2M)
      exclude     — model field names to omit from to_dict() output
      inline_fk   — replace FK id columns with the full related object
                    e.g. {{"customer_id": "customer"}}

    Add async methods (no leading underscore) for computed fields:

        async def display_name(self, model: {model_pascal}) -> str:
            return model.name.title()
    \"\"\"

    prefetch: list = {prefetch_list}
    exclude: list = []
    inline_fk: dict = {{}}

    # ------------------------------------------------------------------ #
    # Computed fields — add async methods below.                          #
    # Each method receives the model instance and returns a plain value.  #
    # Errors in computed fields are logged and stored as None —           #
    # they never abort the load.                                          #
    # ------------------------------------------------------------------ #


# ---------------------------------------------------------------------------
# BaseDTO (legacy) — kept for backward compatibility.
# Existing imports of {model_pascal}DTO from this file continue to work.
# Migrate business logic to {model_pascal}View when ready.
# ---------------------------------------------------------------------------

@dataclass
class {model_pascal}DTO(BaseDTO):
    id: str

    async def _initialize_dto(self, model):
        '''Override to populate DTO fields from the model.'''
        self.id = str(model.id)
        await self._process_core_data(model)
        await self._process_metadata(model)
        await self._initial_validation(model)
        self.initialized = True

    async def _process_core_data(self, model):
        '''Process core data from the model item.'''
        pass

    async def _process_metadata(self, model):
        '''Process metadata from the model item.'''
        pass

    async def _initial_validation(self, model):
        '''Validate fields from the model item.'''
        pass

    async def _final_validation(self):
        '''Final validation of the model item.'''
        return True

    async def get_validated_dict(self):
        '''Get the validated dictionary.'''
        validated = await self._final_validation()
        return self.to_dict()


# ---------------------------------------------------------------------------
# Manager — uses ModelView by default.
# To revert to the legacy DTO path:
#   view_class = None
#   super().__init__({model_pascal}, dto_class={model_pascal}DTO)
# ---------------------------------------------------------------------------

class {model_pascal}Base(BaseManager[{model_pascal}]):
    view_class = {model_pascal}View

    def __init__(self, view_class: Optional[Type[Any]] = None):
        if view_class is not None:
            self.view_class = view_class
        super().__init__({model_pascal})

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, item: {model_pascal}) -> None:
        pass

    async def create_{model_name}(self, **data):
        return await self.create_item(**data)

    async def delete_{model_name}(self, id):
        return await self.delete_item(id)

    async def get_{model_name}_with_all_related(self, id):
        return await self.get_item_with_all_related(id)

    async def load_{model_name}_by_id(self, id):
        return await self.load_by_id(id)

    async def load_{model_name}(self, use_cache=True, **kwargs):
        return await self.load_item(use_cache, **kwargs)

    async def update_{model_name}(self, id, **updates):
        return await self.update_item(id, **updates)

    async def load_{model_name_plural}(self, **kwargs):
        return await self.load_items(**kwargs)

    async def filter_{model_name_plural}(self, **kwargs):
        return await self.filter_items(**kwargs)

    async def get_or_create(self, defaults=None, **kwargs):
        return await self.get_or_create(defaults, **kwargs)
"""


def generate_legacy_dto_manager_class(
    models_module_path: str,
    model_pascal: str,
    model_name: str,
    model_name_plural: str,
    model_name_snake: str,
) -> str:
    """
    Generate a manager using the legacy BaseDTO pattern.
    Preserved for backward compatibility — new code should use
    generate_base_manager_class() with ModelView instead.

    .. deprecated::
        Use generate_base_manager_class() which scaffolds a ModelView.
    """
    import warnings
    warnings.warn(
        "generate_legacy_dto_manager_class() is deprecated. "
        "Use generate_base_manager_class() which scaffolds a ModelView.",
        DeprecationWarning,
        stacklevel=2,
    )
    return f"""
from dataclasses import dataclass
from typing import Any

from matrx_orm import BaseManager, BaseDTO, ModelView
from matrx_utils import vcprint

from {models_module_path} import {model_pascal}

@dataclass
class {model_pascal}DTO(BaseDTO):
    id: str

    async def _initialize_dto(self, model):
        self.id = str(model.id)
        await self._process_core_data(model)
        await self._process_metadata(model)
        await self._initial_validation(model)
        self.initialized = True

    async def _process_core_data(self, model):
        pass

    async def _process_metadata(self, model):
        pass

    async def _initial_validation(self, model):
        pass

    async def _final_validation(self):
        return True

    async def get_validated_dict(self):
        validated = await self._final_validation()
        dict_data = self.to_dict()
        return dict_data


class {model_pascal}Base(BaseManager[{model_pascal}]):
    def __init__(self, view_class: type[Any] | None = None):
        self.dto_class = dto_class or {model_pascal}DTO
        super().__init__({model_pascal}, self.dto_class)

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, item: {model_pascal}) -> None:
        pass

    async def create_{model_name}(self, **data):
        return await self.create_item(**data)

    async def delete_{model_name}(self, id):
        return await self.delete_item(id)

    async def get_{model_name}_with_all_related(self, id):
        return await self.get_item_with_all_related(id)

    async def load_{model_name}_by_id(self, id):
        return await self.load_by_id(id)

    async def load_{model_name}(self, use_cache=True, **kwargs):
        return await self.load_item(use_cache, **kwargs)

    async def update_{model_name}(self, id, **updates):
        return await self.update_item(id, **updates)

    async def load_{model_name_plural}(self, **kwargs):
        return await self.load_items(**kwargs)

    async def filter_{model_name_plural}(self, **kwargs):
        return await self.filter_items(**kwargs)

    async def get_or_create(self, defaults=None, **kwargs):
        return await self.get_or_create(defaults, **kwargs)
"""


def generate_to_dict_methods(model_name: str, model_name_plural: str) -> str:
    """Generate methods that return dict versions of data."""
    return f"""
    async def create_{model_name}_get_dict(self, **data):
        return await self.create_item_get_dict(**data)

    async def filter_{model_name_plural}_get_dict(self, **kwargs):
        return await self.filter_items_get_dict(**kwargs)

    async def get_active_{model_name}_dict(self, id):
        return await self.get_active_item_dict(id)

    async def get_active_{model_name_plural}_dict(self):
        return await self.get_active_items_dict()

    async def get_active_{model_name_plural}_with_all_related_dict(self):
        return await self.get_active_items_with_all_related_dict()

    async def get_active_{model_name_plural}_with_ifks_dict(self):
        return await self.get_active_items_with_ifks_dict()

    async def get_{model_name}_dict(self, id):
        return await self.get_item_dict(id)

    async def get_{model_name_plural}_dict(self, **kwargs):
        return await self.get_items_dict(**kwargs)

    async def get_{model_name_plural}_with_all_related_dict(self):
        return await self.get_items_with_all_related_dict()

    async def load_{model_name}_get_dict(self, use_cache=True, **kwargs):
        return await self.load_item_get_dict(use_cache, **kwargs)

    async def load_{model_name_plural}_by_ids_get_dict(self, ids):
        return await self.load_items_by_ids_get_dict(ids)

    async def update_{model_name}_get_dict(self, id, **updates):
        return await self.update_item_get_dict(id, **updates)
"""


def generate_active_methods(model_name: str, model_name_plural: str) -> str:
    """Generate methods related to handling active items."""
    return f"""
    async def add_active_{model_name}_by_id(self, id):
        return await self.add_active_by_id(id)

    async def add_active_{model_name}_by_ids(self, ids):
        return await self.add_active_by_ids(ids)

    async def get_active_{model_name}(self, id):
        return await self.get_active_item(id)

    async def get_active_{model_name_plural}(self):
        return await self.get_active_items()

    async def get_active_{model_name_plural}_with_all_related(self):
        return await self.get_active_items_with_all_related()

    async def get_active_{model_name_plural}_with_fks(self):
        return await self.get_active_items_with_fks()

    async def get_active_{model_name_plural}_with_ifks(self):
        return await self.get_active_items_with_ifks()

    async def get_active_{model_name_plural}_with_related_models_list(self, related_models_list):
        return await self.get_active_items_with_related_models_list(related_models_list)

    async def get_active_{model_name}_through_ifk(self, id, first_relationship, second_relationship):
        return await self.get_active_item_through_ifk(id, first_relationship, second_relationship)

    async def get_active_{model_name}_with_all_related(self):
        return await self.get_active_item_with_all_related()

    async def get_active_{model_name}_with_fk(self, id, related_model):
        return await self.get_active_item_with_fk(id, related_model)

    async def get_active_{model_name}_with_ifk(self, related_model):
        return await self.get_active_item_with_ifk(related_model)

    async def get_active_{model_name}_with_related_models_list(self, related_models_list):
        return await self.get_active_item_with_related_models_list(related_models_list)

    async def get_active_{model_name}_with_through_fk(self, id, first_relationship, second_relationship):
        return await self.get_active_item_with_through_fk(id, first_relationship, second_relationship)

    async def remove_active_{model_name}_by_id(self, id):
        await self.remove_active_by_id(id)

    async def remove_active_{model_name}_by_ids(self, ids):
        await self.remove_active_by_ids(ids)

    async def remove_all_active(self):
        await self.remove_all_active()
"""


def generate_or_not_methods(model_name: str, model_name_plural: str) -> str:
    """Generate 'or_not' methods that optionally handle items."""
    return f"""
    async def add_active_{model_name}_by_id_or_not(self, id=None):
        return await self.add_active_by_id_or_not(id)

    async def add_active_{model_name}_by_ids_or_not(self, ids=None):
        return await self.add_active_by_ids_or_not(ids)

    async def add_active_{model_name}_by_item_or_not(self, {model_name}=None):
        return await self.add_active_by_item_or_not({model_name})

    async def add_active_{model_name}_by_items_or_not(self, {model_name_plural}=None):
        return await self.add_active_by_items_or_not({model_name_plural})
"""


def generate_core_relation_methods(
    model_name: str, model_name_plural: str, relations: list[str]
) -> str:
    """Generate core relation methods without active filtering."""
    return "".join(
        [
            f"""
    async def get_{model_name}_with_{relation}(self, id):
        return await self.get_item_with_related(id, '{relation}')

    async def get_{model_name_plural}_with_{relation}(self):
        return await self.get_items_with_related('{relation}')
"""
            for relation in relations
        ]
    )


def generate_active_relation_methods(
    model_name: str, model_name_plural: str, relations: list[str]
) -> str:
    """Generate relation methods that include active filtering."""
    return "".join(
        [
            f"""
    async def get_active_{model_name_plural}_with_{relation}(self):
        return await self.get_active_items_with_one_relation('{relation}')

    async def get_active_{model_name}_with_{relation}(self):
        return await self.get_active_item_with_one_relation('{relation}')

    async def get_active_{model_name}_with_through_{relation}(self, id, second_relationship):
        return await self.get_active_item_with_through_fk(id, '{relation}', second_relationship)
"""
            for relation in relations
        ]
    )


def generate_to_dict_relation_methods(
    model_name: str, model_name_plural: str, relations: list[str]
) -> str:
    """Generate to_dict methods specific to each relation."""
    return "".join(
        [
            f"""
    async def get_active_{model_name}_with_{relation}_dict(self):
        return await self.get_active_item_with_one_relation_dict('{relation}')

    async def get_{model_name_plural}_with_{relation}_dict(self):
        return await self.get_items_with_related_dict('{relation}')
"""
            for relation in relations
        ]
    )


def generate_m2m_relation_methods(
    model_name: str, model_name_plural: str, m2m_relations: list[str]
) -> str:
    """Generate named convenience methods for each M2M relationship."""
    return "".join(
        [
            f"""
    async def get_{model_name}_{relation}(self, id):
        return await self.get_item_with_m2m(id, '{relation}')

    async def add_{model_name}_{relation}(self, id, *target_ids):
        return await self.add_m2m(id, '{relation}', *target_ids)

    async def remove_{model_name}_{relation}(self, id, *target_ids):
        return await self.remove_m2m(id, '{relation}', *target_ids)

    async def set_{model_name}_{relation}(self, id, target_ids):
        return await self.set_m2m(id, '{relation}', target_ids)

    async def clear_{model_name}_{relation}(self, id):
        return await self.clear_m2m(id, '{relation}')
"""
            for relation in m2m_relations
        ]
    )


def generate_filter_field_methods(
    model_name: str, model_name_plural: str, filter_fields: list[str]
) -> str:
    """Generate filter-specific methods for each field in filter_fields."""
    return "".join(
        [
            f"""
    async def load_{model_name_plural}_by_{field}(self, {field}):
        return await self.load_items({field}={field})

    async def filter_{model_name_plural}_by_{field}(self, {field}):
        return await self.filter_items({field}={field})
"""
            for field in filter_fields
        ]
    )


def generate_utility_methods(model_name: str, model_name_plural: str) -> str:
    """Generate always-included utility methods for the manager class."""
    return f"""
    async def load_{model_name_plural}_by_ids(self, ids):
        return await self.load_items_by_ids(ids)

    def add_computed_field(self, field):
        self.add_computed_field(field)

    def add_relation_field(self, field):
        self.add_relation_field(field)

    @property
    def active_{model_name}_ids(self):
        return self.active_item_ids
"""


def generate_singleton_manager(model_pascal: str, model_name: str) -> str:
    """Generate singleton manager class for the manager."""
    return f"""
class {model_pascal}Manager({model_pascal}Base):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        super().__init__()

    async def _initialize_runtime_data(self, item: {model_pascal}) -> None:
        pass

{model_name}_manager_instance = {model_pascal}Manager()
"""


def generate_manager_class(
    models_module_path: str,
    model_pascal: str,
    model_name: str,
    model_name_plural: str,
    model_name_snake: str,
    relations: list[str],
    filter_fields: list[str],
    include_core_relations: bool = True,
    include_active_relations: bool = False,
    include_filter_fields: bool = True,
    include_active_methods: bool = False,
    include_or_not_methods: bool = False,
    include_to_dict_methods: bool = False,
    include_to_dict_relations: bool = False,
    m2m_relations: list[str] | None = None,
) -> str:
    """Combine all parts into the full class with fine-grained configuration and singleton manager."""
    base = generate_base_manager_class(
        models_module_path,
        model_pascal,
        model_name,
        model_name_plural,
        model_name_snake,
        relations=relations or [],
    )
    parts = [base]

    # Core relation methods
    if relations and include_core_relations:
        parts.append(
            generate_core_relation_methods(model_name, model_name_plural, relations)
        )

    # Active relation methods
    if relations and include_active_relations:
        parts.append(
            generate_active_relation_methods(model_name, model_name_plural, relations)
        )

    # M2M relation methods
    if m2m_relations:
        parts.append(
            generate_m2m_relation_methods(model_name, model_name_plural, m2m_relations)
        )

    # Filter field methods
    if filter_fields and include_filter_fields:
        parts.append(
            generate_filter_field_methods(model_name, model_name_plural, filter_fields)
        )

    # Active methods
    if include_active_methods:
        print("Generating active methods")
        parts.append(generate_active_methods(model_name, model_name_plural))

    # Or-not methods
    if include_or_not_methods:
        parts.append(generate_or_not_methods(model_name, model_name_plural))

    # To-dict methods
    if include_to_dict_methods:
        parts.append(generate_to_dict_methods(model_name, model_name_plural))

    # To-dict relation methods
    if relations and include_to_dict_relations:
        parts.append(
            generate_to_dict_relation_methods(model_name, model_name_plural, relations)
        )

    # Always included utility methods
    parts.append(generate_utility_methods(model_name, model_name_plural))

    # Add singleton manager with extra linebreaks
    parts.append("\n\n" + generate_singleton_manager(model_pascal, model_name))

    return "".join(parts)


def save_manager_class(
    model_pascal: str,
    model_name: str,
    model_name_plural: str,
    model_name_snake: str,
    relations: list[str],
    filter_fields: list[str],
    include_core_relations: bool = True,
    include_active_relations: bool = False,
    include_filter_fields: bool = True,
    include_active_methods: bool = False,
    include_or_not_methods: bool = True,
    include_to_dict_methods: bool = True,
    include_to_dict_relations: bool = False,
) -> tuple[str, str]:
    file_path = os.path.join(
        "database", "orm", "extended", "managers", f"{model_name}_base.py"
    )
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    model_class_str = generate_manager_class(
        model_pascal,
        model_name,
        model_name_plural,
        model_name_snake,
        relations,
        filter_fields,
        include_core_relations,
        include_active_relations,
        include_filter_fields,
        include_active_methods,
        include_or_not_methods,
        include_to_dict_methods,
        include_to_dict_relations,
    )

    with open(file_path, "w") as f:
        f.write(model_class_str)

    plt(file_path, "Manager class saved")
    return model_class_str, file_path
