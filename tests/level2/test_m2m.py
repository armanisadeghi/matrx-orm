"""Level 2: ManyToManyReference operations with real DB."""

from uuid import uuid4

import pytest

from matrx_orm.core.registry import ModelRegistry
from matrx_orm.core.relations import ManyToManyReference
from matrx_orm.migrations.operations import MigrationDB


def _get_m2m_ref(post_model) -> ManyToManyReference | None:
    """Get the M2M reference from the post model's meta, if registered."""
    return post_model._meta.many_to_many_keys.get("tags")


@pytest.mark.level2
class TestM2MFetch:
    async def test_fetch_m2m(self, post_model, migration_db, post_ids, tag_ids):
        ref = _get_m2m_ref(post_model)
        if ref is None:
            pytest.skip("M2M not registered on TestPost")
        post = await post_model.get(use_cache=False, id=post_ids[0])
        tags = await ref.fetch_related(post)
        assert len(tags) >= 2


@pytest.mark.level2
class TestM2MAdd:
    async def test_add_m2m(self, post_model, migration_db, post_ids, tag_ids):
        ref = _get_m2m_ref(post_model)
        if ref is None:
            pytest.skip("M2M not registered on TestPost")
        post = await post_model.get(use_cache=False, id=post_ids[3])
        count = await ref.add(post, tag_ids[0])
        assert count >= 1

        count_dup = await ref.add(post, tag_ids[0])
        assert count_dup >= 0


@pytest.mark.level2
class TestM2MRemove:
    async def test_remove_m2m(self, post_model, migration_db, post_ids, tag_ids):
        ref = _get_m2m_ref(post_model)
        if ref is None:
            pytest.skip("M2M not registered on TestPost")
        post = await post_model.get(use_cache=False, id=post_ids[2])
        await ref.add(post, tag_ids[0], tag_ids[1])
        removed = await ref.remove(post, tag_ids[0])
        assert removed >= 1


@pytest.mark.level2
class TestM2MClear:
    async def test_clear_m2m(self, post_model, migration_db, post_ids, tag_ids):
        ref = _get_m2m_ref(post_model)
        if ref is None:
            pytest.skip("M2M not registered on TestPost")
        post = await post_model.get(use_cache=False, id=post_ids[4])
        await ref.add(post, tag_ids[0], tag_ids[1], tag_ids[2])
        cleared = await ref.clear(post)
        assert cleared >= 1

        tags = await ref.fetch_related(post)
        assert len(tags) == 0


@pytest.mark.level2
class TestM2MSet:
    async def test_set_m2m(self, post_model, migration_db, post_ids, tag_ids):
        ref = _get_m2m_ref(post_model)
        if ref is None:
            pytest.skip("M2M not registered on TestPost")
        post = await post_model.get(use_cache=False, id=post_ids[1])
        await ref.set(post, [tag_ids[0], tag_ids[2]])
        tags = await ref.fetch_related(post)
        tag_names = {t.name for t in tags}
        assert len(tags) == 2
