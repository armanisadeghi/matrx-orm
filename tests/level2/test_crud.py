"""Level 2: Create, read, update, delete via Model class methods."""

from uuid import uuid4

import pytest

from matrx_orm.exceptions import DoesNotExist


@pytest.mark.level2
class TestCreate:
    async def test_create_instance(self, user_model):
        uid = str(uuid4())
        user = await user_model.create(
            id=uid,
            username=f"create_test_{uid[:8]}",
            email="create@test.com",
            is_active=True,
            age=22,
        )
        assert user.id == uid
        assert user.username.startswith("create_test_")

    async def test_create_with_defaults(self, user_model):
        uid = str(uuid4())
        user = await user_model.create(
            id=uid,
            username=f"defaults_{uid[:8]}",
            email="default@test.com",
        )
        assert user.is_active is True


@pytest.mark.level2
class TestRead:
    async def test_get_by_pk(self, user_model, user_ids):
        user = await user_model.get(id=user_ids[0])
        assert user.username == "alice"

    async def test_get_nonexistent_raises(self, user_model):
        fake_id = str(uuid4())
        with pytest.raises(Exception):
            await user_model.get(id=fake_id)

    async def test_get_or_none_found(self, user_model, user_ids):
        user = await user_model.get_or_none(id=user_ids[1])
        assert user is not None
        assert user.username == "bob"

    async def test_get_or_none_missing(self, user_model):
        fake_id = str(uuid4())
        result = await user_model.get_or_none(id=fake_id)
        assert result is None


@pytest.mark.level2
class TestUpdate:
    async def test_update_fields(self, user_model):
        uid = str(uuid4())
        user = await user_model.create(
            id=uid,
            username=f"upd_{uid[:8]}",
            email="upd@test.com",
            age=20,
        )
        await user_model.filter(id=uid).update(age=99)
        updated = await user_model.get(use_cache=False, id=uid)
        assert updated.age == 99


@pytest.mark.level2
class TestDelete:
    async def test_delete(self, user_model):
        uid = str(uuid4())
        await user_model.create(
            id=uid,
            username=f"del_{uid[:8]}",
            email="del@test.com",
        )
        count = await user_model.filter(id=uid).delete()
        assert count >= 1

        result = await user_model.get_or_none(use_cache=False, id=uid)
        assert result is None
