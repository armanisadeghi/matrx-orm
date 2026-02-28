import os
from matrx_utils.fancy_prints.fancy_prints import plt


def generate_base_manager_class(
    models_module_path: str,
    model_pascal: str,
    model_name: str,
    model_name_plural: str,
    model_name_snake: str,
    relations: list[str] | None = None,
    view_prefetch: list[str] | None = None,
) -> str:
    """Generate the minimal core manager class with both ModelView and legacy DTO.

    Both classes are always generated so that:
    - The DTO is wired in by default — existing code that relies on item.dto
      continues to work without any changes (zero breaking changes).
    - The View class is scaffolded and ready to use, but is NOT active by default.
    - To opt into the View, set ``view_class = {Model}View`` on the subclass
      OR pass ``view_class={Model}View`` to super().__init__().  When view_class
      is set, the DTO path is skipped automatically by BaseManager.

    Args:
        view_prefetch: Explicit list of relation names to auto-prefetch on every
            load when using the View. Defaults to [] (no automatic prefetching).
            Set specific relation names in matrx_orm.yaml manager_flags.view_prefetch
            to opt in.
    """
    prefetch_list = repr(view_prefetch if view_prefetch is not None else [])
    return f"""from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from matrx_orm import BaseManager, BaseDTO, ModelView
from matrx_utils import vcprint

from {models_module_path} import {model_pascal}


# ---------------------------------------------------------------------------
# ModelView (new) — opt-in projection layer.
# Stores results flat on the model instance; no duplication, no nesting.
# To activate: set view_class = {model_pascal}View on your manager subclass,
# or pass view_class={model_pascal}View to super().__init__().
# When active, the DTO path below is skipped automatically.
# ---------------------------------------------------------------------------

class {model_pascal}View(ModelView[{model_pascal}]):
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

    prefetch: list[str] = {prefetch_list}
    exclude: list[str] = []
    inline_fk: dict[str, str] = {{}}

    # ------------------------------------------------------------------ #
    # Computed fields — add async methods below.                          #
    # Each method receives the model instance and returns a plain value.  #
    # Errors in computed fields are logged and stored as None —           #
    # they never abort the load.                                          #
    # ------------------------------------------------------------------ #


# ---------------------------------------------------------------------------
# BaseDTO (default) — active by default, fully backward compatible.
# Extend _process_core_data / _process_metadata with your business logic.
# When you are ready to migrate to the View above, set view_class on your
# manager subclass and this DTO will be bypassed automatically.
# ---------------------------------------------------------------------------

@dataclass
class {model_pascal}DTO(BaseDTO[{model_pascal}]):
    id: str

    async def _initialize_dto(self, model: {model_pascal}) -> None:
        '''Override to populate DTO fields from the model.'''
        self.id = str(model.id)
        await self._process_core_data(model)
        await self._process_metadata(model)
        await self._initial_validation(model)
        self.initialized = True

    async def _process_core_data(self, model: {model_pascal}) -> None:
        '''Process core data from the model item.'''
        pass

    async def _process_metadata(self, model: {model_pascal}) -> None:
        '''Process metadata from the model item.'''
        pass

    async def _initial_validation(self, model: {model_pascal}) -> None:
        '''Validate fields from the model item.'''
        pass

    async def _final_validation(self) -> bool:
        '''Final validation of the model item.'''
        return True

    async def get_validated_dict(self) -> dict[str, Any]:
        '''Get the validated dictionary.'''
        await self._final_validation()
        return self.to_dict()


# ---------------------------------------------------------------------------
# Manager — DTO is active by default for full backward compatibility.
# To switch to the View (opt-in):
#   1. Quick: set view_class = {model_pascal}View  (replaces DTO automatically)
#   2. Explicit: super().__init__({model_pascal}, view_class={model_pascal}View)
# ---------------------------------------------------------------------------

class {model_pascal}Base(BaseManager[{model_pascal}]):
    view_class = None  # DTO is used by default; set to {model_pascal}View to opt in

    def __init__(
        self,
        dto_class: type[Any] | None = None,
        view_class: type[Any] | None = None,
    ) -> None:
        if view_class is not None:
            self.view_class = view_class
        super().__init__({model_pascal}, dto_class=dto_class or {model_pascal}DTO)

    def _initialize_manager(self) -> None:
        super()._initialize_manager()

    async def _initialize_runtime_data(self, item: {model_pascal}) -> None:
        pass

    async def create_{model_name}(self, **data: Any) -> {model_pascal}:
        return await self.create_item(**data)

    async def delete_{model_name}(self, id: Any) -> bool:
        return await self.delete_item(id)

    async def get_{model_name}_with_all_related(self, id: Any) -> tuple[{model_pascal}, Any]:
        return await self.get_item_with_all_related(id)

    async def load_{model_name}_by_id(self, id: Any) -> {model_pascal}:
        return await self.load_by_id(id)

    async def load_{model_name}(self, use_cache: bool = True, **kwargs: Any) -> {model_pascal}:
        return await self.load_item(use_cache, **kwargs)

    async def update_{model_name}(self, id: Any, **updates: Any) -> {model_pascal}:
        return await self.update_item(id, **updates)

    async def load_{model_name_plural}(self, **kwargs: Any) -> list[{model_pascal}]:
        return await self.load_items(**kwargs)

    async def filter_{model_name_plural}(self, **kwargs: Any) -> list[{model_pascal}]:
        return await self.filter_items(**kwargs)

    async def get_or_create_{model_name}(self, defaults: dict[str, Any] | None = None, **kwargs: Any) -> {model_pascal} | None:
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
    return f"""from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from matrx_orm import BaseManager, BaseDTO, ModelView
from matrx_utils import vcprint

from {models_module_path} import {model_pascal}


@dataclass
class {model_pascal}DTO(BaseDTO[{model_pascal}]):
    id: str

    async def _initialize_dto(self, model: {model_pascal}) -> None:
        self.id = str(model.id)
        await self._process_core_data(model)
        await self._process_metadata(model)
        await self._initial_validation(model)
        self.initialized = True

    async def _process_core_data(self, model: {model_pascal}) -> None:
        pass

    async def _process_metadata(self, model: {model_pascal}) -> None:
        pass

    async def _initial_validation(self, model: {model_pascal}) -> None:
        pass

    async def _final_validation(self) -> bool:
        return True

    async def get_validated_dict(self) -> dict[str, Any]:
        await self._final_validation()
        return self.to_dict()


class {model_pascal}Base(BaseManager[{model_pascal}]):
    def __init__(self, dto_class: type[Any] | None = None) -> None:
        super().__init__({model_pascal}, dto_class=dto_class or {model_pascal}DTO)

    def _initialize_manager(self) -> None:
        super()._initialize_manager()

    async def _initialize_runtime_data(self, item: {model_pascal}) -> None:
        pass

    async def create_{model_name}(self, **data: Any) -> {model_pascal}:
        return await self.create_item(**data)

    async def delete_{model_name}(self, id: Any) -> bool:
        return await self.delete_item(id)

    async def get_{model_name}_with_all_related(self, id: Any) -> tuple[{model_pascal}, Any]:
        return await self.get_item_with_all_related(id)

    async def load_{model_name}_by_id(self, id: Any) -> {model_pascal}:
        return await self.load_by_id(id)

    async def load_{model_name}(self, use_cache: bool = True, **kwargs: Any) -> {model_pascal}:
        return await self.load_item(use_cache, **kwargs)

    async def update_{model_name}(self, id: Any, **updates: Any) -> {model_pascal}:
        return await self.update_item(id, **updates)

    async def load_{model_name_plural}(self, **kwargs: Any) -> list[{model_pascal}]:
        return await self.load_items(**kwargs)

    async def filter_{model_name_plural}(self, **kwargs: Any) -> list[{model_pascal}]:
        return await self.filter_items(**kwargs)

    async def get_or_create_{model_name}(self, defaults: dict[str, Any] | None = None, **kwargs: Any) -> {model_pascal} | None:
        return await self.get_or_create(defaults, **kwargs)
"""


def generate_to_dict_methods(model_name: str, model_name_plural: str) -> str:
    """Generate methods that return dict versions of data."""
    return f"""
    async def create_{model_name}_get_dict(self, **data: Any) -> dict[str, Any] | None:
        return await self.create_item_get_dict(**data)

    async def filter_{model_name_plural}_get_dict(self, **kwargs: Any) -> list[dict[str, Any]]:
        return await self.filter_items_get_dict(**kwargs)

    async def get_active_{model_name}_dict(self, id: Any) -> dict[str, Any] | None:
        return await self.get_active_item_dict(id)

    async def get_active_{model_name_plural}_dict(self) -> list[dict[str, Any] | None]:
        return await self.get_active_items_dict()

    async def get_active_{model_name_plural}_with_all_related_dict(self) -> list[dict[str, Any]]:
        return await self.get_active_items_with_all_related_dict()

    async def get_active_{model_name_plural}_with_ifks_dict(self) -> list[dict[str, Any]]:
        return await self.get_active_items_with_ifks_dict()

    async def get_{model_name}_dict(self, id: Any) -> dict[str, Any] | None:
        return await self.get_item_dict(id)

    async def get_{model_name_plural}_dict(self, **kwargs: Any) -> list[dict[str, Any] | None]:
        return await self.get_items_dict(**kwargs)

    async def get_{model_name_plural}_with_all_related_dict(self) -> list[dict[str, Any]]:
        return await self.get_items_with_all_related_dict()

    async def load_{model_name}_get_dict(self, use_cache: bool = True, **kwargs: Any) -> dict[str, Any] | None:
        return await self.load_item_get_dict(use_cache, **kwargs)

    async def load_{model_name_plural}_by_ids_get_dict(self, ids: list[Any]) -> list[dict[str, Any] | None]:
        return await self.load_items_by_ids_get_dict(ids)

    async def update_{model_name}_get_dict(self, id: Any, **updates: Any) -> dict[str, Any] | None:
        return await self.update_item_get_dict(id, **updates)
"""


def generate_active_methods(model_name: str, model_name_plural: str) -> str:
    """Generate methods related to handling active items."""
    return f"""
    async def add_active_{model_name}_by_id(self, id: Any) -> None:
        return await self.add_active_by_id(id)

    async def add_active_{model_name}_by_ids(self, ids: list[Any]) -> None:
        return await self.add_active_by_ids(ids)

    async def get_active_{model_name}(self, id: Any) -> Any:
        return await self.get_active_item(id)

    async def get_active_{model_name_plural}(self) -> list[Any]:
        return await self.get_active_items()

    async def get_active_{model_name_plural}_with_all_related(self) -> list[Any]:
        return await self.get_active_items_with_all_related()

    async def get_active_{model_name_plural}_with_fks(self) -> list[Any]:
        return await self.get_active_items_with_fks()

    async def get_active_{model_name_plural}_with_ifks(self) -> list[Any]:
        return await self.get_active_items_with_ifks()

    async def get_active_{model_name_plural}_with_related_models_list(self, related_models_list: list[str]) -> list[Any]:
        return await self.get_active_items_with_related_models_list(related_models_list)

    async def get_active_{model_name}_through_ifk(self, id: Any, first_relationship: str, second_relationship: str) -> Any:
        return await self.get_active_item_through_ifk(id, first_relationship, second_relationship)

    async def get_active_{model_name}_with_all_related(self) -> Any:
        return await self.get_active_item_with_all_related()

    async def get_active_{model_name}_with_fk(self, id: Any, related_model: str) -> Any:
        return await self.get_active_item_with_fk(id, related_model)

    async def get_active_{model_name}_with_ifk(self, related_model: str) -> Any:
        return await self.get_active_item_with_ifk(related_model)

    async def get_active_{model_name}_with_related_models_list(self, related_models_list: list[str]) -> Any:
        return await self.get_active_item_with_related_models_list(related_models_list)

    async def get_active_{model_name}_with_through_fk(self, id: Any, first_relationship: str, second_relationship: str) -> Any:
        return await self.get_active_item_with_through_fk(id, first_relationship, second_relationship)

    async def remove_active_{model_name}_by_id(self, id: Any) -> None:
        await self.remove_active_by_id(id)

    async def remove_active_{model_name}_by_ids(self, ids: list[Any]) -> None:
        await self.remove_active_by_ids(ids)

    async def remove_all_active_{model_name_plural}(self) -> None:
        await self.remove_all_active()
"""


def generate_or_not_methods(model_name: str, model_name_plural: str) -> str:
    """Generate 'or_not' methods that optionally handle items."""
    return f"""
    async def add_active_{model_name}_by_id_or_not(self, id: Any | None = None) -> None:
        return await self.add_active_by_id_or_not(id)

    async def add_active_{model_name}_by_ids_or_not(self, ids: list[Any] | None = None) -> None:
        return await self.add_active_by_ids_or_not(ids)

    async def add_active_{model_name}_by_item_or_not(self, {model_name}: Any | None = None) -> None:
        return await self.add_active_by_item_or_not({model_name})

    async def add_active_{model_name}_by_items_or_not(self, {model_name_plural}: list[Any] | None = None) -> None:
        return await self.add_active_by_items_or_not({model_name_plural})
"""


def generate_core_relation_methods(
    model_name: str, model_name_plural: str, relations: list[str]
) -> str:
    """Generate core relation methods without active filtering."""
    return "".join(
        [
            f"""
    async def get_{model_name}_with_{relation}(self, id: Any) -> tuple[Any, Any]:
        return await self.get_item_with_related(id, '{relation}')

    async def get_{model_name_plural}_with_{relation}(self) -> list[Any]:
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
    async def get_active_{model_name_plural}_with_{relation}(self) -> list[Any]:
        return await self.get_active_items_with_one_relation('{relation}')

    async def get_active_{model_name}_with_{relation}(self) -> Any:
        return await self.get_active_item_with_one_relation('{relation}')

    async def get_active_{model_name}_with_through_{relation}(self, id: Any, second_relationship: str) -> Any:
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
    async def get_active_{model_name}_with_{relation}_dict(self) -> dict[str, Any] | None:
        return await self.get_active_item_with_one_relation_dict('{relation}')

    async def get_{model_name_plural}_with_{relation}_dict(self) -> list[dict[str, Any]]:
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
    async def get_{model_name}_{relation}(self, id: Any) -> tuple[Any, list[Any]]:
        return await self.get_item_with_m2m(id, '{relation}')

    async def add_{model_name}_{relation}(self, id: Any, *target_ids: Any) -> int:
        return await self.add_m2m(id, '{relation}', *target_ids)

    async def remove_{model_name}_{relation}(self, id: Any, *target_ids: Any) -> int:
        return await self.remove_m2m(id, '{relation}', *target_ids)

    async def set_{model_name}_{relation}(self, id: Any, target_ids: list[Any]) -> int:
        return await self.set_m2m(id, '{relation}', target_ids)

    async def clear_{model_name}_{relation}(self, id: Any) -> int:
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
    async def load_{model_name_plural}_by_{field}(self, {field}: Any) -> list[Any]:
        return await self.load_items({field}={field})

    async def filter_{model_name_plural}_by_{field}(self, {field}: Any) -> list[Any]:
        return await self.filter_items({field}={field})
"""
            for field in filter_fields
        ]
    )


def generate_utility_methods(model_name: str, model_name_plural: str) -> str:
    """Generate always-included utility methods for the manager class."""
    return f"""
    async def load_{model_name_plural}_by_ids(self, ids: list[Any]) -> list[Any]:
        return await self.load_items_by_ids(ids)

    def add_computed_field(self, field: str) -> None:
        super().add_computed_field(field)

    def add_relation_field(self, field: str) -> None:
        super().add_relation_field(field)

    @property
    def active_{model_name}_ids(self) -> set[Any]:
        return self.active_item_ids
"""


def generate_singleton_manager(model_pascal: str, model_name: str) -> str:
    """Generate singleton manager class for the manager."""
    return f"""
class {model_pascal}Manager({model_pascal}Base):
    _instance: {model_pascal}Manager | None = None

    def __new__(cls, *args: Any, **kwargs: Any) -> {model_pascal}Manager:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
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
    view_prefetch: list[str] | None = None,
) -> str:
    """Combine all parts into the full class with fine-grained configuration and singleton manager."""
    base = generate_base_manager_class(
        models_module_path,
        model_pascal,
        model_name,
        model_name_plural,
        model_name_snake,
        relations=relations or [],
        view_prefetch=view_prefetch,
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
