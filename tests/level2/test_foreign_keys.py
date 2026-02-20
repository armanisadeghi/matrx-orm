"""Level 2: fetch_fk, fetch_ifk, FK relationships with real DB."""

import pytest


@pytest.mark.level2
class TestFetchFK:
    async def test_fetch_fk_returns_parent(self, post_model, user_model, post_ids, user_ids):
        post = await post_model.get(use_cache=False, id=post_ids[0])
        author = await post.fetch_fk("author_id")
        assert author is not None
        assert author.id == user_ids[0]
        assert author.username == "alice"

    async def test_fetch_fk_caches_related(self, post_model, post_ids):
        post = await post_model.get(use_cache=False, id=post_ids[0])
        author1 = await post.fetch_fk("author_id")
        related = post.get_related("author_id")
        assert related is not None


@pytest.mark.level2
class TestFetchIFK:
    async def test_fetch_ifk_returns_children(self, user_model, post_model, user_ids):
        user = await user_model.get(use_cache=False, id=user_ids[0])
        posts = await user.fetch_ifk("author_id")
        assert isinstance(posts, list)
        assert len(posts) >= 2

    async def test_fetch_ifk_no_children(self, user_model, user_ids):
        user = await user_model.get(use_cache=False, id=user_ids[4])
        posts = await user.fetch_ifk("author_id")
        assert isinstance(posts, list)


@pytest.mark.level2
class TestSelfReferencingFK:
    async def test_category_parent(self, category_model):
        from tests.level2.conftest import SEED_CATEGORY_IDS
        child = await category_model.get(use_cache=False, id=SEED_CATEGORY_IDS[1])
        parent = await child.fetch_fk("parent_id")
        assert parent is not None
        assert parent.name == "Tech"

    async def test_root_category_null_parent(self, category_model):
        from tests.level2.conftest import SEED_CATEGORY_IDS
        root = await category_model.get(use_cache=False, id=SEED_CATEGORY_IDS[0])
        assert root.parent_id is None
