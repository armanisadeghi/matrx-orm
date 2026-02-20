"""Level 2: High-level model operations with real DB — get, filter, create, update, delete."""

from uuid import uuid4

import pytest


@pytest.mark.level2
class TestModelGetAll:
    async def test_get_all_users(self, user_model):
        users = await user_model.filter().all()
        assert len(users) >= 5

    async def test_get_all_posts(self, post_model):
        posts = await post_model.filter().all()
        assert len(posts) >= 5


@pytest.mark.level2
class TestModelFilterChain:
    async def test_filter_by_age_range(self, user_model):
        results = await user_model.filter(age__gte=25, age__lte=35).all()
        for r in results:
            assert 25 <= r.age <= 35

    async def test_filter_startswith(self, user_model):
        results = await user_model.filter(username__startswith="a").all()
        assert all(r.username.startswith("a") for r in results)

    async def test_filter_contains(self, user_model):
        results = await user_model.filter(username__contains="li").all()
        assert all("li" in r.username for r in results)


@pytest.mark.level2
class TestModelValues:
    async def test_values(self, user_model, user_ids):
        vals = await user_model.filter(id=user_ids[0]).values("id", "username")
        assert len(vals) == 1
        assert "username" in vals[0]

    async def test_values_list(self, user_model, user_ids):
        vals = await user_model.filter(id=user_ids[0]).values_list("username", flat=True)
        assert isinstance(vals, list)
        assert vals[0] == "alice"


@pytest.mark.level2
class TestToDict:
    async def test_to_dict(self, user_model, user_ids):
        user = await user_model.get(use_cache=False, id=user_ids[0])
        d = user.to_dict()
        assert d["username"] == "alice"
        assert "id" in d

    async def test_to_flat_dict(self, user_model, user_ids):
        user = await user_model.get(use_cache=False, id=user_ids[0])
        d = user.to_flat_dict()
        assert d["username"] == "alice"


@pytest.mark.level2
class TestJsonField:
    async def test_json_field_read(self, post_model, post_ids):
        post = await post_model.get(use_cache=False, id=post_ids[0])
        assert post.metadata is not None
        assert isinstance(post.metadata, dict) or isinstance(post.metadata, str)

    async def test_json_field_null(self, post_model, post_ids):
        post = await post_model.get(use_cache=False, id=post_ids[1])
        assert post.metadata is None


@pytest.mark.level2
class TestCreateAndCleanup:
    async def test_full_lifecycle(self, user_model):
        uid = str(uuid4())
        user = await user_model.create(
            id=uid,
            username=f"lifecycle_{uid[:8]}",
            email="lc@test.com",
            bio="Lifecycle test",
            age=33,
        )
        assert user.id == uid

        fetched = await user_model.get(use_cache=False, id=uid)
        assert fetched.username == user.username

        await user_model.filter(id=uid).update(bio="Updated bio")
        refreshed = await user_model.get(use_cache=False, id=uid)
        assert refreshed.bio == "Updated bio"

        deleted = await user_model.filter(id=uid).delete()
        assert deleted >= 1

        gone = await user_model.get_or_none(use_cache=False, id=uid)
        assert gone is None
