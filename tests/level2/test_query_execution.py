"""Level 2: QueryBuilder.all/get/first/last/count/exists with real DB."""

from uuid import uuid4

import pytest


@pytest.mark.level2
class TestFilterAll:
    async def test_filter_by_field(self, user_model):
        results = await user_model.filter(username="alice").all()
        assert len(results) == 1
        assert results[0].username == "alice"

    async def test_filter_in(self, user_model, user_ids):
        results = await user_model.filter(id__in=user_ids[:2]).all()
        assert len(results) == 2

    async def test_filter_boolean(self, user_model):
        active = await user_model.filter(is_active=True).all()
        assert len(active) >= 4

    async def test_filter_isnull(self, user_model):
        results = await user_model.filter(bio__isnull=True).all()
        assert any(r.username == "charlie" for r in results)


@pytest.mark.level2
class TestExclude:
    async def test_exclude(self, user_model):
        results = await user_model.filter(is_active=True).exclude(username="alice").all()
        assert all(r.username != "alice" for r in results)


@pytest.mark.level2
class TestOrderBy:
    async def test_order_by_asc(self, user_model):
        results = await user_model.filter(is_active=True).order_by("age").all()
        ages = [r.age for r in results if r.age is not None]
        assert ages == sorted(ages)

    async def test_order_by_desc(self, user_model):
        results = await user_model.filter(is_active=True).order_by("-age").all()
        ages = [r.age for r in results if r.age is not None]
        assert ages == sorted(ages, reverse=True)


@pytest.mark.level2
class TestLimitOffset:
    async def test_limit(self, user_model):
        results = await user_model.filter(is_active=True).limit(2).all()
        assert len(results) <= 2

    async def test_limit_offset(self, user_model):
        all_active = await user_model.filter(is_active=True).order_by("username").all()
        page = await user_model.filter(is_active=True).order_by("username").limit(2).offset(1).all()
        if len(all_active) > 1:
            assert page[0].username == all_active[1].username


@pytest.mark.level2
class TestAggregates:
    async def test_count(self, user_model):
        count = await user_model.filter(is_active=True).count()
        assert count >= 4

    async def test_exists_true(self, user_model, user_ids):
        assert await user_model.filter(id=user_ids[0]).exists() is True

    async def test_exists_false(self, user_model):
        fake_id = str(uuid4())
        assert await user_model.filter(id=fake_id).exists() is False


@pytest.mark.level2
class TestFirstLast:
    async def test_first(self, user_model):
        first = await user_model.filter(is_active=True).order_by("username").first()
        assert first is not None

    async def test_first_empty(self, user_model):
        first = await user_model.filter(username="nonexistent_xyz").first()
        assert first is None


@pytest.mark.level2
class TestChainedQueries:
    async def test_complex_chain(self, user_model):
        results = (
            await user_model
            .filter(is_active=True)
            .exclude(username="alice")
            .order_by("age")
            .limit(3)
            .all()
        )
        assert len(results) <= 3
        assert all(r.username != "alice" for r in results)
