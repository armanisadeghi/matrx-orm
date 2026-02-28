from __future__ import annotations

from typing import TYPE_CHECKING

from matrx_utils import vcprint

if TYPE_CHECKING:
    from matrx_orm.core.base import Model


class ModelRegistry:
    _models: dict[str, type[Model]] = {}
    _initialized: bool = False

    @classmethod
    def register(cls, model_class: type[Model]) -> None:
        model_name = model_class.__name__
        if model_name in cls._models and cls._models[model_name] is not model_class:
            raise ValueError(f"Model {model_name} is already registered")
        cls._models[model_name] = model_class

    @classmethod
    def register_all(cls, models: list[type[Model]]) -> None:
        for model in models:
            cls.register(model)

    @classmethod
    def get_model(cls, model_name: str) -> type[Model] | None:
        return cls._models.get(model_name)

    @classmethod
    def all_models(cls) -> dict[str, type[Model]]:
        return cls._models.copy()

    @classmethod
    def clear(cls) -> None:
        cls._models.clear()
        cls._initialized = False
        vcprint("Cleared all registered models", color="yellow", inline=True)


model_registry = ModelRegistry()


def get_model_by_name(model_name: str) -> type[Model]:
    model = model_registry.get_model(model_name)
    if model is None:
        raise ValueError(f"Model {model_name} not found: {model_name}")
    return model
