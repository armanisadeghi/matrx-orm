"""Level 1: Model init, to_dict, to_flat_dict, from_db_result, get_cache_key."""

from uuid import uuid4

import pytest

from matrx_orm.core.fields import CharField, IntegerField, UUIDField, BooleanField
from matrx_orm.core.base import Model, ModelMeta
from matrx_orm.core.registry import ModelRegistry


@pytest.fixture(autouse=True)
def _clean_registry():
    ModelRegistry.clear()
    yield
    ModelRegistry.clear()


def _make_model(name, fields_dict):
    return ModelMeta(name, (Model,), {**fields_dict, "_database": "test_db"})


class TestModelInit:
    def test_init_with_kwargs(self):
        M = _make_model("InitTest", {
            "id": UUIDField(primary_key=True),
            "name": CharField(max_length=100),
        })
        uid = str(uuid4())
        inst = M(id=uid, name="Alice")
        assert inst.id == uid
        assert inst.name == "Alice"

    def test_init_defaults(self):
        M = _make_model("DefaultTest", {
            "id": UUIDField(primary_key=True),
            "active": BooleanField(default=True),
        })
        uid = str(uuid4())
        inst = M(id=uid)
        assert inst.active is True

    def test_extra_data(self):
        M = _make_model("ExtraTest", {
            "id": UUIDField(primary_key=True),
        })
        uid = str(uuid4())
        inst = M(id=uid, unknown_field="hello")
        assert inst._extra_data.get("unknown_field") == "hello"


class TestToDict:
    def test_to_dict_includes_fields(self):
        M = _make_model("DictTest", {
            "id": UUIDField(primary_key=True),
            "name": CharField(max_length=50),
        })
        uid = str(uuid4())
        inst = M(id=uid, name="Bob")
        d = inst.to_dict()
        assert d["id"] == uid
        assert d["name"] == "Bob"

    def test_to_flat_dict(self):
        M = _make_model("FlatTest", {
            "id": UUIDField(primary_key=True),
            "count": IntegerField(),
        })
        uid = str(uuid4())
        inst = M(id=uid, count=42)
        d = inst.to_flat_dict()
        assert d["id"] == uid
        assert d["count"] == 42


class TestFromDbResult:
    def test_from_db_result_sets_uuid_field(self):
        M = _make_model("DbResTest", {
            "id": UUIDField(primary_key=True),
            "ref_id": UUIDField(),
        })
        uid = str(uuid4())
        ref = str(uuid4())
        inst = M.from_db_result({"id": uid, "ref_id": ref})
        assert inst.id == uid
        assert inst.ref_id == ref

    def test_from_db_result_extra_columns(self):
        M = _make_model("DbResExtra", {
            "id": UUIDField(primary_key=True),
        })
        uid = str(uuid4())
        inst = M.from_db_result({"id": uid, "extra_col": "val"})
        assert inst._extra_data.get("extra_col") == "val"


class TestCacheKey:
    def test_single_pk(self):
        M = _make_model("CKSingle", {
            "id": UUIDField(primary_key=True),
            "name": CharField(),
        })
        uid = str(uuid4())
        inst = M(id=uid, name="test")
        assert inst.get_cache_key() == uid

    def test_composite_pk(self):
        M = _make_model("CKComposite", {
            "org_id": UUIDField(),
            "user_id": UUIDField(),
            "_primary_keys": ["org_id", "user_id"],
        })
        oid = str(uuid4())
        uid = str(uuid4())
        inst = M(org_id=oid, user_id=uid)
        assert inst.get_cache_key() == f"{oid}_{uid}"
