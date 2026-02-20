"""Level 1: ModelMeta, ModelOptions, field registration, qualified_table_name."""

import pytest

from matrx_orm.core.fields import CharField, IntegerField, UUIDField, ForeignKey, BooleanField
from matrx_orm.core.base import ModelMeta, ModelOptions, Model
from matrx_orm.core.registry import ModelRegistry


@pytest.fixture(autouse=True)
def _clean_registry():
    ModelRegistry.clear()
    yield
    ModelRegistry.clear()


def _make_model(name, attrs, bases=(Model,)):
    """Helper to create a model class with ModelMeta."""
    return ModelMeta(name, bases, attrs)


class TestModelOptions:
    def test_qualified_table_name_no_schema(self):
        opts = ModelOptions(
            table_name="my_table",
            database="test_db",
            fields={},
            primary_keys=["id"],
            unique_fields=set(),
            foreign_keys={},
            inverse_foreign_keys={},
            indexes=[],
            unique_together=[],
            constraints=[],
        )
        assert opts.qualified_table_name == "my_table"

    def test_qualified_table_name_with_schema(self):
        opts = ModelOptions(
            table_name="my_table",
            database="test_db",
            fields={},
            primary_keys=["id"],
            unique_fields=set(),
            foreign_keys={},
            inverse_foreign_keys={},
            indexes=[],
            unique_together=[],
            constraints=[],
            db_schema="custom",
        )
        assert opts.qualified_table_name == "custom.my_table"

    def test_m2m_defaults_to_empty_dict(self):
        opts = ModelOptions(
            table_name="t",
            database="d",
            fields={},
            primary_keys=["id"],
            unique_fields=set(),
            foreign_keys={},
            inverse_foreign_keys={},
            indexes=[],
            unique_together=[],
            constraints=[],
        )
        assert opts.many_to_many_keys == {}


class TestModelMeta:
    def test_fields_registered(self):
        M = _make_model("TestUser", {
            "id": UUIDField(primary_key=True),
            "name": CharField(max_length=100),
            "_database": "test_db",
        })
        assert "id" in M._fields
        assert "name" in M._fields
        assert len(M._meta.fields) == 2

    def test_primary_keys_from_field_flag(self):
        M = _make_model("PKFromField", {
            "id": UUIDField(primary_key=True),
            "val": IntegerField(),
            "_database": "test_db",
        })
        assert M._meta.primary_keys == ["id"]

    def test_primary_keys_from_class_attr(self):
        M = _make_model("PKFromAttr", {
            "id": UUIDField(),
            "val": IntegerField(),
            "_primary_keys": ["id"],
            "_database": "test_db",
        })
        assert M._meta.primary_keys == ["id"]

    def test_duplicate_pk_sources_raises(self):
        with pytest.raises(ValueError, match="cannot have both"):
            _make_model("BadPK", {
                "id": UUIDField(primary_key=True),
                "_primary_keys": ["id"],
                "_database": "test_db",
            })

    def test_no_pk_raises(self):
        with pytest.raises(ValueError, match="must define at least one primary key"):
            _make_model("NoPK", {
                "name": CharField(),
                "_database": "test_db",
            })

    def test_unique_fields(self):
        M = _make_model("Uniq", {
            "id": UUIDField(primary_key=True),
            "email": CharField(unique=True),
            "_database": "test_db",
        })
        assert "email" in M._meta.unique_fields

    def test_fk_registration(self):
        M = _make_model("FKModel", {
            "id": UUIDField(primary_key=True),
            "user_id": ForeignKey(to_model="User", to_column="id"),
            "_database": "test_db",
        })
        assert "user_id" in M._meta.foreign_keys
        ref = M._meta.foreign_keys["user_id"]
        assert ref.to_model == "User"
        assert ref.to_column == "id"

    def test_auto_table_name_snake_case(self):
        M = _make_model("MyFancyModel", {
            "id": UUIDField(primary_key=True),
            "_database": "test_db",
        })
        assert M._meta.table_name == "my_fancy_model"

    def test_custom_table_name(self):
        M = _make_model("Whatever", {
            "id": UUIDField(primary_key=True),
            "_table_name": "custom_table",
            "_database": "test_db",
        })
        assert M._meta.table_name == "custom_table"

    def test_unfetchable_flag(self):
        M = _make_model("Ghost", {
            "id": UUIDField(primary_key=True),
            "_unfetchable": True,
            "_database": "test_db",
        })
        assert M._meta.unfetchable is True

    def test_schema_flag(self):
        M = _make_model("Schemed", {
            "id": UUIDField(primary_key=True),
            "_db_schema": "analytics",
            "_database": "test_db",
        })
        assert M._meta.db_schema == "analytics"
        assert M._meta.qualified_table_name == "analytics.schemed"
