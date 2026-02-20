"""Level 1: ModelRegistry — register, get, all_models, clear, error cases."""

import pytest

from matrx_orm.core.fields import UUIDField, CharField
from matrx_orm.core.base import Model, ModelMeta
from matrx_orm.core.registry import ModelRegistry, get_model_by_name


@pytest.fixture(autouse=True)
def _clean_registry():
    ModelRegistry.clear()
    yield
    ModelRegistry.clear()


def _make_model(name):
    return ModelMeta(name, (Model,), {
        "id": UUIDField(primary_key=True),
        "_database": "test_db",
    })


class TestModelRegistry:
    def test_register_and_get(self):
        M = _make_model("RegTest1")
        ModelRegistry.register(M)
        assert ModelRegistry.get_model("RegTest1") is M

    def test_get_nonexistent_returns_none(self):
        assert ModelRegistry.get_model("DoesNotExist") is None

    def test_all_models(self):
        M1 = _make_model("AllA")
        M2 = _make_model("AllB")
        ModelRegistry.register(M1)
        ModelRegistry.register(M2)
        models = ModelRegistry.all_models()
        assert "AllA" in models
        assert "AllB" in models

    def test_clear(self):
        M = _make_model("ClearMe")
        ModelRegistry.register(M)
        ModelRegistry.clear()
        assert ModelRegistry.get_model("ClearMe") is None

    def test_duplicate_registration_same_class(self):
        M = _make_model("Dup1")
        ModelRegistry.register(M)
        ModelRegistry.register(M)
        assert ModelRegistry.get_model("Dup1") is M

    def test_duplicate_registration_different_class_raises(self):
        M1 = _make_model("Dup2")
        M2 = _make_model("Dup2")
        ModelRegistry.register(M1)
        with pytest.raises(ValueError, match="already registered"):
            ModelRegistry.register(M2)


class TestGetModelByName:
    def test_found(self):
        M = _make_model("ByName1")
        ModelRegistry.register(M)
        assert get_model_by_name("ByName1") is M

    def test_not_found_raises(self):
        with pytest.raises(ValueError, match="not found"):
            get_model_by_name("Missing")
