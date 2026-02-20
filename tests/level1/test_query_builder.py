"""Level 1: QueryBuilder — filter, exclude, order_by, limit, offset, select, _build_query."""

import pytest

from matrx_orm.core.fields import UUIDField, CharField, IntegerField
from matrx_orm.core.base import Model, ModelMeta
from matrx_orm.core.registry import ModelRegistry
from matrx_orm.query.builder import QueryBuilder


@pytest.fixture(autouse=True)
def _clean_registry():
    ModelRegistry.clear()
    yield
    ModelRegistry.clear()


def _make_model(name="QBModel"):
    return ModelMeta(name, (Model,), {
        "id": UUIDField(primary_key=True),
        "name": CharField(max_length=100),
        "age": IntegerField(),
        "_database": "test_db",
        "_table_name": "qb_table",
    })


class TestQueryBuilderChaining:
    def test_filter_adds_to_filters(self):
        M = _make_model()
        qb = QueryBuilder(M).filter(name="Alice")
        assert qb.filters == [{"name": "Alice"}]

    def test_multiple_filters(self):
        M = _make_model()
        qb = QueryBuilder(M).filter(name="Alice").filter(age=30)
        assert len(qb.filters) == 2

    def test_exclude_adds_to_excludes(self):
        M = _make_model()
        qb = QueryBuilder(M).exclude(name="Bob")
        assert qb.excludes == [{"name": "Bob"}]

    def test_order_by(self):
        M = _make_model()
        qb = QueryBuilder(M).order_by("name", "-age")
        assert qb.order_by_fields == ["name", "-age"]

    def test_limit(self):
        M = _make_model()
        qb = QueryBuilder(M).limit(10)
        assert qb.limit_val == 10

    def test_offset(self):
        M = _make_model()
        qb = QueryBuilder(M).offset(5)
        assert qb.offset_val == 5

    def test_select(self):
        M = _make_model()
        qb = QueryBuilder(M).select("id", "name")
        assert qb.select_fields == ["id", "name"]

    def test_chaining_returns_self(self):
        M = _make_model()
        qb = QueryBuilder(M)
        result = qb.filter(name="x").exclude(age=0).order_by("name").limit(5).offset(0).select("id")
        assert result is qb

    def test_empty_filter_ignored(self):
        M = _make_model()
        qb = QueryBuilder(M).filter()
        assert qb.filters == []


class TestBuildQuery:
    def test_build_query_basic(self):
        M = _make_model()
        qb = QueryBuilder(M).filter(name="Alice").limit(10)
        q = qb._build_query()
        assert q["model"] is M
        assert q["table"] == "qb_table"
        assert q["filters"]["name"] == "Alice"
        assert q["limit"] == 10

    def test_build_query_default_select(self):
        M = _make_model()
        q = QueryBuilder(M)._build_query()
        assert q["select"] == ["*"]

    def test_build_query_custom_select(self):
        M = _make_model()
        q = QueryBuilder(M).select("id", "name")._build_query()
        assert q["select"] == ["id", "name"]

    def test_build_query_order_by(self):
        M = _make_model()
        q = QueryBuilder(M).order_by("-name")._build_query()
        assert q["order_by"] == ["-name"]


class TestMergeFiltersExcludes:
    def test_filters_merged(self):
        M = _make_model()
        qb = QueryBuilder(M).filter(a=1, b=2)
        merged = qb._merge_filters_excludes()
        assert merged == {"a": 1, "b": 2}

    def test_excludes_prefixed(self):
        M = _make_model()
        qb = QueryBuilder(M).exclude(name="Bob")
        merged = qb._merge_filters_excludes()
        assert merged == {"exclude__name": "Bob"}

    def test_combined(self):
        M = _make_model()
        qb = QueryBuilder(M).filter(active=True).exclude(role="admin")
        merged = qb._merge_filters_excludes()
        assert merged["active"] is True
        assert merged["exclude__role"] == "admin"


class TestQualifiedTableName:
    def test_uses_qualified_name(self):
        M = ModelMeta("SchemaQB", (Model,), {
            "id": UUIDField(primary_key=True),
            "_database": "test_db",
            "_table_name": "my_table",
            "_db_schema": "analytics",
        })
        q = QueryBuilder(M)._build_query()
        assert q["table"] == "analytics.my_table"


class TestSlicing:
    def test_slice_sets_limit_and_offset(self):
        M = _make_model()
        qb = QueryBuilder(M)[5:15]
        assert qb.offset_val == 5
        assert qb.limit_val == 10

    def test_index_raises(self):
        M = _make_model()
        qb = QueryBuilder(M)
        with pytest.raises(TypeError, match="slicing"):
            qb[0]


class TestPrefetchRelated:
    def test_prefetch_related(self):
        M = _make_model()
        qb = QueryBuilder(M).prefetch_related("user", "tags")
        assert qb.prefetch_fields == ["user", "tags"]


class TestDatabaseRequired:
    def test_no_database_raises_at_model_creation(self):
        from matrx_orm.exceptions import ConfigurationError
        with pytest.raises(ConfigurationError):
            ModelMeta("NoDB", (Model,), {
                "id": UUIDField(primary_key=True),
                "_database": None,
            })
