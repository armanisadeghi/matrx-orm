"""Level 1: CachePolicy, cache key generation, staleness checks."""

import asyncio
from datetime import datetime, timedelta
from unittest.mock import patch
from uuid import uuid4

import pytest

from matrx_orm.core.fields import UUIDField, CharField
from matrx_orm.core.base import Model, ModelMeta
from matrx_orm.core.registry import ModelRegistry
from matrx_orm.state import CachePolicy, ModelState, StateManager


def _run(coro):
    return asyncio.get_event_loop().run_until_complete(coro)


@pytest.fixture(autouse=True)
def _clean():
    ModelRegistry.clear()
    StateManager._states.clear()
    yield
    ModelRegistry.clear()
    StateManager._states.clear()


def _make_model(name="CacheModel", policy=CachePolicy.SHORT_TERM, timeout=None):
    attrs = {
        "id": UUIDField(primary_key=True),
        "name": CharField(max_length=100),
        "_database": "test_db",
        "_cache_policy": policy,
    }
    if timeout is not None:
        attrs["_cache_timeout"] = timeout
    return ModelMeta(name, (Model,), attrs)


class TestCachePolicy:
    def test_values(self):
        assert CachePolicy.PERMANENT.value == "permanent"
        assert CachePolicy.LONG_TERM.value == "long_term"
        assert CachePolicy.SHORT_TERM.value == "short_term"
        assert CachePolicy.INSTANT.value == "instant"

    def test_all_members(self):
        assert len(CachePolicy) == 4


class TestModelState:
    def test_cache_key_single_pk(self):
        M = _make_model("CKS")
        state = ModelState(M)
        uid = str(uuid4())
        inst = M(id=uid, name="test")
        key = state._get_record_cache_key(inst)
        assert key == uid

    def test_cache_and_retrieve(self):
        M = _make_model("CR")
        state = ModelState(M)
        uid = str(uuid4())
        inst = M(id=uid, name="Alice")
        _run(state.cache(inst))
        assert state.count() == 1
        assert state._cache[uid] is inst

    def test_remove_from_cache(self):
        M = _make_model("RM")
        state = ModelState(M)
        uid = str(uuid4())
        inst = M(id=uid, name="Bob")
        _run(state.cache(inst))
        _run(state.remove(inst))
        assert state.count() == 0

    def test_clear_cache(self):
        M = _make_model("CL")
        state = ModelState(M)
        for _ in range(5):
            inst = M(id=str(uuid4()), name="x")
            _run(state.cache(inst))
        assert state.count() == 5
        state.clear_cache()
        assert state.count() == 0

    def test_get_all_cached(self):
        M = _make_model("GAC")
        state = ModelState(M)
        instances = []
        for i in range(3):
            inst = M(id=str(uuid4()), name=f"n{i}")
            _run(state.cache(inst))
            instances.append(inst)
        cached = state.get_all_cached()
        assert len(cached) == 3


class TestStaleness:
    def test_permanent_never_stale(self):
        M = _make_model("Perm", policy=CachePolicy.PERMANENT)
        state = ModelState(M)
        uid = str(uuid4())
        inst = M(id=uid, name="test")
        _run(state.cache(inst))
        state._cache_times[uid] = datetime.now() - timedelta(days=365)
        assert state._is_stale(inst) is False

    def test_instant_stale_after_1min(self):
        M = _make_model("Inst", policy=CachePolicy.INSTANT)
        state = ModelState(M)
        uid = str(uuid4())
        inst = M(id=uid, name="test")
        _run(state.cache(inst))
        state._cache_times[uid] = datetime.now() - timedelta(minutes=2)
        assert state._is_stale(inst) is True

    def test_short_term_stale_after_10min(self):
        M = _make_model("Short", policy=CachePolicy.SHORT_TERM)
        state = ModelState(M)
        uid = str(uuid4())
        inst = M(id=uid, name="test")
        _run(state.cache(inst))
        state._cache_times[uid] = datetime.now() - timedelta(minutes=15)
        assert state._is_stale(inst) is True

    def test_short_term_fresh(self):
        M = _make_model("ShortF", policy=CachePolicy.SHORT_TERM)
        state = ModelState(M)
        uid = str(uuid4())
        inst = M(id=uid, name="test")
        _run(state.cache(inst))
        assert state._is_stale(inst) is False

    def test_long_term_stale_after_4h(self):
        M = _make_model("Long", policy=CachePolicy.LONG_TERM)
        state = ModelState(M)
        uid = str(uuid4())
        inst = M(id=uid, name="test")
        _run(state.cache(inst))
        state._cache_times[uid] = datetime.now() - timedelta(hours=5)
        assert state._is_stale(inst) is True

    def test_custom_timeout(self):
        M = _make_model("Cust", timeout=30)
        state = ModelState(M)
        uid = str(uuid4())
        inst = M(id=uid, name="test")
        _run(state.cache(inst))
        state._cache_times[uid] = datetime.now() - timedelta(seconds=60)
        assert state._is_stale(inst) is True

    def test_custom_timeout_fresh(self):
        M = _make_model("CustF", timeout=120)
        state = ModelState(M)
        uid = str(uuid4())
        inst = M(id=uid, name="test")
        _run(state.cache(inst))
        assert state._is_stale(inst) is False

    def test_no_cache_time_is_stale(self):
        M = _make_model("NoTime")
        state = ModelState(M)
        uid = str(uuid4())
        inst = M(id=uid, name="test")
        state._cache[uid] = inst
        assert state._is_stale(inst) is True


class TestFindInCache:
    def test_find_by_criteria(self):
        M = _make_model("FIC")
        state = ModelState(M)
        uid = str(uuid4())
        inst = M(id=uid, name="target")
        _run(state.cache(inst))
        found = state._find_in_cache(name="target")
        assert found is inst

    def test_find_not_found(self):
        M = _make_model("FICNF")
        state = ModelState(M)
        found = state._find_in_cache(name="ghost")
        assert found is None
