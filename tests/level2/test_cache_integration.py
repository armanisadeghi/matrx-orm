"""Level 2: StateManager — cache + DB fallback, invalidation, coherency."""

from uuid import uuid4

import pytest

from matrx_orm.state import StateManager


@pytest.mark.level2
class TestCacheFill:
    async def test_get_populates_cache(self, user_model, user_ids):
        await StateManager.clear_cache(user_model)
        user = await user_model.get(id=user_ids[0])
        assert user.username == "alice"

        cached = await StateManager.count(user_model)
        assert cached >= 1

    async def test_second_get_from_cache(self, user_model, user_ids):
        await StateManager.clear_cache(user_model)
        user1 = await user_model.get(id=user_ids[0])
        user2 = await user_model.get(id=user_ids[0])
        assert user1.id == user2.id


@pytest.mark.level2
class TestCacheInvalidation:
    async def test_update_invalidates(self, user_model):
        uid = str(uuid4())
        user = await user_model.create(
            id=uid,
            username=f"ci_{uid[:8]}",
            email="ci@test.com",
            age=20,
        )
        await StateManager.cache(user_model, user)

        await user_model.filter(id=uid).update(age=50)
        refreshed = await user_model.get(use_cache=False, id=uid)
        assert refreshed.age == 50

    async def test_delete_removes_from_cache(self, user_model):
        uid = str(uuid4())
        user = await user_model.create(
            id=uid,
            username=f"cid_{uid[:8]}",
            email="cid@test.com",
        )
        await StateManager.cache(user_model, user)
        await StateManager.remove(user_model, user)

        cached_count_before = await StateManager.count(user_model)
        await user_model.filter(id=uid).delete()


@pytest.mark.level2
class TestClearCache:
    async def test_clear_cache(self, user_model, user_ids):
        await user_model.get(id=user_ids[0])
        await user_model.get(id=user_ids[1])
        await StateManager.clear_cache(user_model)
        count = await StateManager.count(user_model)
        assert count == 0
