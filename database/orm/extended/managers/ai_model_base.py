
from dataclasses import dataclass
from typing import Any

from matrx_orm import BaseManager, BaseDTO, ModelView
from matrx_utils import vcprint

from AiModel import ai_model


# ---------------------------------------------------------------------------
# ModelView (new) — opt-in projection layer.
# Stores results flat on the model instance; no duplication, no nesting.
# To activate: set view_class = ai_modelView on your manager subclass,
# or pass view_class=ai_modelView to super().__init__().
# When active, the DTO path below is skipped automatically.
# ---------------------------------------------------------------------------

class ai_modelView(ModelView):
    """
    Declarative view for ai_model.

    Configure what gets fetched and shaped automatically on every load:

      prefetch    — relation names to fetch concurrently (FK / IFK / M2M)
      exclude     — model field names to omit from to_dict() output
      inline_fk   — replace FK id columns with the full related object
                    e.g. {"customer_id": "customer"}

    Add async methods (no leading underscore) for computed fields:

        async def display_name(self, model: ai_model) -> str:
            return model.name.title()
    """

    prefetch: list = []
    exclude: list = []
    inline_fk: dict = {}

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
class ai_modelDTO(BaseDTO):
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
# Manager — DTO is active by default for full backward compatibility.
# To switch to the View (opt-in):
#   1. Quick: set view_class = ai_modelView  (replaces DTO automatically)
#   2. Explicit: super().__init__(ai_model, view_class=ai_modelView)
# ---------------------------------------------------------------------------

class ai_modelBase(BaseManager[ai_model]):
    view_class = None  # DTO is used by default; set to ai_modelView to opt in

    def __init__(
        self,
        dto_class: type[Any] | None = None,
        view_class: type[Any] | None = None,
    ):
        if view_class is not None:
            self.view_class = view_class
        super().__init__(ai_model, dto_class=dto_class or ai_modelDTO)

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, item: ai_model) -> None:
        pass

    async def create_ai_models(self, **data):
        return await self.create_item(**data)

    async def delete_ai_models(self, id):
        return await self.delete_item(id)

    async def get_ai_models_with_all_related(self, id):
        return await self.get_item_with_all_related(id)

    async def load_ai_models_by_id(self, id):
        return await self.load_by_id(id)

    async def load_ai_models(self, use_cache=True, **kwargs):
        return await self.load_item(use_cache, **kwargs)

    async def update_ai_models(self, id, **updates):
        return await self.update_item(id, **updates)

    async def load_ai_model(self, **kwargs):
        return await self.load_items(**kwargs)

    async def filter_ai_model(self, **kwargs):
        return await self.filter_items(**kwargs)

    async def get_or_create(self, defaults=None, **kwargs):
        return await self.get_or_create(defaults, **kwargs)

    async def get_active_ai_model_with_name(self):
        return await self.get_active_items_with_one_relation('name')

    async def get_active_ai_models_with_name(self):
        return await self.get_active_item_with_one_relation('name')

    async def get_active_ai_models_with_through_name(self, id, second_relationship):
        return await self.get_active_item_with_through_fk(id, 'name', second_relationship)

    async def get_active_ai_model_with_common_name(self):
        return await self.get_active_items_with_one_relation('common_name')

    async def get_active_ai_models_with_common_name(self):
        return await self.get_active_item_with_one_relation('common_name')

    async def get_active_ai_models_with_through_common_name(self, id, second_relationship):
        return await self.get_active_item_with_through_fk(id, 'common_name', second_relationship)

    async def get_active_ai_model_with_provider(self):
        return await self.get_active_items_with_one_relation('provider')

    async def get_active_ai_models_with_provider(self):
        return await self.get_active_item_with_one_relation('provider')

    async def get_active_ai_models_with_through_provider(self, id, second_relationship):
        return await self.get_active_item_with_through_fk(id, 'provider', second_relationship)

    async def get_active_ai_model_with_model_class(self):
        return await self.get_active_items_with_one_relation('model_class')

    async def get_active_ai_models_with_model_class(self):
        return await self.get_active_item_with_one_relation('model_class')

    async def get_active_ai_models_with_through_model_class(self, id, second_relationship):
        return await self.get_active_item_with_through_fk(id, 'model_class', second_relationship)

    async def get_active_ai_model_with_model_provider(self):
        return await self.get_active_items_with_one_relation('model_provider')

    async def get_active_ai_models_with_model_provider(self):
        return await self.get_active_item_with_one_relation('model_provider')

    async def get_active_ai_models_with_through_model_provider(self, id, second_relationship):
        return await self.get_active_item_with_through_fk(id, 'model_provider', second_relationship)

    async def add_active_ai_models_by_id_or_not(self, id=None):
        return await self.add_active_by_id_or_not(id)

    async def add_active_ai_models_by_ids_or_not(self, ids=None):
        return await self.add_active_by_ids_or_not(ids)

    async def add_active_ai_models_by_item_or_not(self, ai_models=None):
        return await self.add_active_by_item_or_not(ai_models)

    async def add_active_ai_models_by_items_or_not(self, ai_model=None):
        return await self.add_active_by_items_or_not(ai_model)

    async def create_ai_models_get_dict(self, **data):
        return await self.create_item_get_dict(**data)

    async def filter_ai_model_get_dict(self, **kwargs):
        return await self.filter_items_get_dict(**kwargs)

    async def get_active_ai_models_dict(self, id):
        return await self.get_active_item_dict(id)

    async def get_active_ai_model_dict(self):
        return await self.get_active_items_dict()

    async def get_active_ai_model_with_all_related_dict(self):
        return await self.get_active_items_with_all_related_dict()

    async def get_active_ai_model_with_ifks_dict(self):
        return await self.get_active_items_with_ifks_dict()

    async def get_ai_models_dict(self, id):
        return await self.get_item_dict(id)

    async def get_ai_model_dict(self, **kwargs):
        return await self.get_items_dict(**kwargs)

    async def get_ai_model_with_all_related_dict(self):
        return await self.get_items_with_all_related_dict()

    async def load_ai_models_get_dict(self, use_cache=True, **kwargs):
        return await self.load_item_get_dict(use_cache, **kwargs)

    async def load_ai_model_by_ids_get_dict(self, ids):
        return await self.load_items_by_ids_get_dict(ids)

    async def update_ai_models_get_dict(self, id, **updates):
        return await self.update_item_get_dict(id, **updates)

    async def load_ai_model_by_ids(self, ids):
        return await self.load_items_by_ids(ids)

    def add_computed_field(self, field):
        self.add_computed_field(field)

    def add_relation_field(self, field):
        self.add_relation_field(field)

    @property
    def active_ai_models_ids(self):
        return self.active_item_ids



class ai_modelManager(ai_modelBase):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        super().__init__()

    async def _initialize_runtime_data(self, item: ai_model) -> None:
        pass

ai_models_manager_instance = ai_modelManager()
