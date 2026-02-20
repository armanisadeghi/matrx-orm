"""Level 2: bulk_create, bulk_update, bulk_delete."""

from uuid import uuid4

import pytest


@pytest.mark.level2
class TestBulkCreate:
    async def test_bulk_create(self, user_model):
        data = [
            {
                "id": str(uuid4()),
                "username": f"bulk_{i}_{uuid4().hex[:6]}",
                "email": f"bulk{i}@test.com",
                "age": 20 + i,
            }
            for i in range(5)
        ]
        results = await user_model.bulk_create(data)
        assert len(results) == 5
        for r in results:
            assert r.id is not None

    async def test_bulk_create_empty(self, user_model):
        results = await user_model.bulk_create([])
        assert results == []


@pytest.mark.level2
class TestBulkUpdate:
    async def test_bulk_update_fields(self, user_model):
        data = [
            {
                "id": str(uuid4()),
                "username": f"bu_{i}_{uuid4().hex[:6]}",
                "email": f"bu{i}@test.com",
                "age": 10,
            }
            for i in range(3)
        ]
        instances = await user_model.bulk_create(data)
        for inst in instances:
            inst.age = 99
        count = await user_model.bulk_update(instances, ["age"])
        assert count >= 3

        for inst in instances:
            refreshed = await user_model.get(use_cache=False, id=inst.id)
            assert refreshed.age == 99


@pytest.mark.level2
class TestBulkDelete:
    async def test_bulk_delete(self, user_model):
        data = [
            {
                "id": str(uuid4()),
                "username": f"bd_{i}_{uuid4().hex[:6]}",
                "email": f"bd{i}@test.com",
            }
            for i in range(3)
        ]
        instances = await user_model.bulk_create(data)
        count = await user_model.bulk_delete(instances)
        assert count >= 3

        for inst in instances:
            result = await user_model.get_or_none(use_cache=False, id=inst.id)
            assert result is None
