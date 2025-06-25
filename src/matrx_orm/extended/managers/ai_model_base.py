# TODO Changes required

from dataclasses import dataclass
from matrx_orm.core.extended import BaseManager, BaseDTO
from matrx_orm.orm.models import AiModel
from typing import Optional, Type, Any
from matrx_utils import vcprint


@dataclass
class AiModelDTO(BaseDTO):
    id: str

    async def _initialize_dto(self, ai_model_item):
        """Override the base initialization method."""
        self.id = str(ai_model_item.id)
        await self._process_core_data(ai_model_item)
        await self._process_metadata(ai_model_item)
        await self._initial_validation(ai_model_item)
        self.initialized = True

    async def _process_core_data(self, ai_model_item):
        """Process core data from the model item."""
        pass

    async def _process_metadata(self, ai_model_item):
        """Process metadata from the model item."""
        pass

    async def _initial_validation(self, ai_model_item):
        """Validate fields from the model item."""
        pass

    async def _final_validation(self):
        """Final validation of the model item."""
        return True

    async def get_validated_dict(self):
        """Get the validated dictionary."""
        validated = await self._final_validation()
        dict_data = self.to_dict()
        if not validated:
            vcprint(
                dict_data,
                "[AiModelDTO] Validation Failed",
                verbose=True,
                pretty=True,
                color="red",
            )
        return dict_data


class AiModelBase(BaseManager):
    def __init__(self, dto_class: Optional[Type[Any]] = None):
        self.dto_class = dto_class or AiModelDTO
        super().__init__(AiModel, self.dto_class)

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, ai_model):
        pass

    async def create_ai_model(self, **data):
        return await self.create_item(**data)

    async def delete_ai_model(self, id):
        return await self.delete_item(id)

    async def get_ai_model_with_all_related(self, id):
        return await self.get_item_with_all_related(id)

    async def load_ai_model_by_id(self, id):
        return await self.load_by_id(id)

    async def load_ai_model(self, use_cache=True, **kwargs):
        return await self.load_item(use_cache, **kwargs)

    async def update_ai_model(self, id, **updates):
        return await self.update_item(id, **updates)

    async def exists(self, id):
        return await self.exists(id)

    async def load_ai_models(self, **kwargs):
        return await self.load_items(**kwargs)

    async def filter_ai_models(self, **kwargs):
        return await self.filter_items(**kwargs)

    async def get_or_create(self, defaults=None, **kwargs):
        return await self.get_or_create(defaults, **kwargs)

    async def get_ai_model_with_ai_provider(self, id):
        return await self.get_item_with_related(id, "ai_provider")

    async def get_ai_models_with_ai_provider(self):
        return await self.get_items_with_related("ai_provider")

    async def get_ai_model_with_ai_model_endpoint(self, id):
        return await self.get_item_with_related(id, "ai_model_endpoint")

    async def get_ai_models_with_ai_model_endpoint(self):
        return await self.get_items_with_related("ai_model_endpoint")

    async def get_ai_model_with_ai_settings(self, id):
        return await self.get_item_with_related(id, "ai_settings")

    async def get_ai_models_with_ai_settings(self):
        return await self.get_items_with_related("ai_settings")

    async def get_ai_model_with_recipe_model(self, id):
        return await self.get_item_with_related(id, "recipe_model")

    async def get_ai_models_with_recipe_model(self):
        return await self.get_items_with_related("recipe_model")

    async def load_ai_models_by_name(self, name):
        return await self.load_items(name=name)

    async def filter_ai_models_by_name(self, name):
        return await self.filter_items(name=name)

    async def load_ai_models_by_common_name(self, common_name):
        return await self.load_items(common_name=common_name)

    async def filter_ai_models_by_common_name(self, common_name):
        return await self.filter_items(common_name=common_name)

    async def load_ai_models_by_provider(self, provider):
        return await self.load_items(provider=provider)

    async def filter_ai_models_by_provider(self, provider):
        return await self.filter_items(provider=provider)

    async def load_ai_models_by_model_class(self, model_class):
        return await self.load_items(model_class=model_class)

    async def filter_ai_models_by_model_class(self, model_class):
        return await self.filter_items(model_class=model_class)

    async def load_ai_models_by_model_provider(self, model_provider):
        return await self.load_items(model_provider=model_provider)

    async def filter_ai_models_by_model_provider(self, model_provider):
        return await self.filter_items(model_provider=model_provider)

    async def create_ai_model_get_dict(self, **data):
        return await self.create_item_get_dict(**data)

    async def filter_ai_models_get_dict(self, **kwargs):
        return await self.filter_items_get_dict(**kwargs)

    async def get_active_ai_model_dict(self, id):
        return await self.get_active_item_dict(id)

    async def get_active_ai_models_dict(self):
        return await self.get_active_items_dict()

    async def get_active_ai_models_with_all_related_dict(self):
        return await self.get_active_items_with_all_related_dict()

    async def get_active_ai_models_with_ifks_dict(self):
        return await self.get_active_items_with_ifks_dict()

    async def get_ai_model_dict(self, id):
        return await self.get_item_dict(id)

    async def get_ai_models_dict(self, **kwargs):
        return await self.get_items_dict(**kwargs)

    async def get_ai_models_with_all_related_dict(self):
        return await self.get_items_with_all_related_dict()

    async def load_ai_model_get_dict(self, use_cache=True, **kwargs):
        return await self.load_item_get_dict(use_cache, **kwargs)

    async def load_ai_models_by_ids_get_dict(self, ids):
        return await self.load_items_by_ids_get_dict(ids)

    async def update_ai_model_get_dict(self, id, **updates):
        return await self.update_item_get_dict(id, **updates)

    async def get_active_ai_model_with_ai_provider_dict(self):
        return await self.get_active_item_with_one_relation_dict("ai_provider")

    async def get_ai_models_with_ai_provider_dict(self):
        return await self.get_items_with_related_dict("ai_provider")

    async def get_active_ai_model_with_ai_model_endpoint_dict(self):
        return await self.get_active_item_with_one_relation_dict("ai_model_endpoint")

    async def get_ai_models_with_ai_model_endpoint_dict(self):
        return await self.get_items_with_related_dict("ai_model_endpoint")

    async def get_active_ai_model_with_ai_settings_dict(self):
        return await self.get_active_item_with_one_relation_dict("ai_settings")

    async def get_ai_models_with_ai_settings_dict(self):
        return await self.get_items_with_related_dict("ai_settings")

    async def get_active_ai_model_with_recipe_model_dict(self):
        return await self.get_active_item_with_one_relation_dict("recipe_model")

    async def get_ai_models_with_recipe_model_dict(self):
        return await self.get_items_with_related_dict("recipe_model")

    async def load_ai_models_by_ids(self, ids):
        return await self.load_items_by_ids(ids)

    def add_computed_field(self, field):
        self.add_computed_field(field)

    def add_relation_field(self, field):
        self.add_relation_field(field)

    @property
    def active_ai_model_ids(self):
        return self.active_item_ids


class AiModelManager(AiModelBase):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(AiModelManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        super().__init__()


ai_model_manager_instance = AiModelManager()
