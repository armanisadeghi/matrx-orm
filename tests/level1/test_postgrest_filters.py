"""Unit tests for PostgREST query parameter building.

Tests the filter translation from ORM-style operators to PostgREST format.
These tests run without a database or network connection (level1).
"""

from __future__ import annotations

import pytest

from matrx_orm.client.postgrest import PostgRESTClient
from matrx_orm.client.supabase_config import SupabaseClientConfig


@pytest.fixture
def client() -> PostgRESTClient:
    config = SupabaseClientConfig(
        url="https://test.supabase.co",
        anon_key="test-anon-key",
    )
    return PostgRESTClient(config)


class TestFilterParsing:
    def test_simple_eq(self, client: PostgRESTClient) -> None:
        params = client._build_query_params(filters={"status": "active"})
        assert params["status"] == "eq.active"

    def test_explicit_eq(self, client: PostgRESTClient) -> None:
        params = client._build_query_params(filters={"status__eq": "active"})
        assert params["status"] == "eq.active"

    def test_ne(self, client: PostgRESTClient) -> None:
        params = client._build_query_params(filters={"status__ne": "draft"})
        assert params["status"] == "neq.draft"

    def test_gt(self, client: PostgRESTClient) -> None:
        params = client._build_query_params(filters={"age__gt": 18})
        assert params["age"] == "gt.18"

    def test_gte(self, client: PostgRESTClient) -> None:
        params = client._build_query_params(filters={"age__gte": 18})
        assert params["age"] == "gte.18"

    def test_lt(self, client: PostgRESTClient) -> None:
        params = client._build_query_params(filters={"age__lt": 65})
        assert params["age"] == "lt.65"

    def test_lte(self, client: PostgRESTClient) -> None:
        params = client._build_query_params(filters={"age__lte": 65})
        assert params["age"] == "lte.65"

    def test_in(self, client: PostgRESTClient) -> None:
        params = client._build_query_params(
            filters={"status__in": ["active", "pending"]}
        )
        assert params["status"] == "in.(active,pending)"

    def test_contains(self, client: PostgRESTClient) -> None:
        params = client._build_query_params(
            filters={"title__contains": "note"}
        )
        assert params["title"] == "like.*note*"

    def test_icontains(self, client: PostgRESTClient) -> None:
        params = client._build_query_params(
            filters={"title__icontains": "Note"}
        )
        assert params["title"] == "ilike.*Note*"

    def test_startswith(self, client: PostgRESTClient) -> None:
        params = client._build_query_params(
            filters={"title__startswith": "My"}
        )
        assert params["title"] == "like.My*"

    def test_endswith(self, client: PostgRESTClient) -> None:
        params = client._build_query_params(
            filters={"title__endswith": ".txt"}
        )
        assert params["title"] == "like.*.txt"

    def test_isnull_true(self, client: PostgRESTClient) -> None:
        params = client._build_query_params(
            filters={"deleted_at__isnull": True}
        )
        assert params["deleted_at"] == "is.null"

    def test_isnull_false(self, client: PostgRESTClient) -> None:
        params = client._build_query_params(
            filters={"deleted_at__isnull": False}
        )
        assert params["deleted_at"] == "not.is.null"

    def test_boolean_value(self, client: PostgRESTClient) -> None:
        params = client._build_query_params(filters={"is_active": True})
        assert params["is_active"] == "eq.true"

    def test_none_value(self, client: PostgRESTClient) -> None:
        params = client._build_query_params(filters={"field": None})
        assert params["field"] == "eq.null"

    def test_uuid_value(self, client: PostgRESTClient) -> None:
        import uuid

        uid = uuid.UUID("12345678-1234-5678-1234-567812345678")
        params = client._build_query_params(filters={"id": uid})
        assert params["id"] == "eq.12345678-1234-5678-1234-567812345678"


class TestOrderBy:
    def test_ascending(self, client: PostgRESTClient) -> None:
        params = client._build_query_params(order=["created_at"])
        assert params["order"] == "created_at.asc"

    def test_descending(self, client: PostgRESTClient) -> None:
        params = client._build_query_params(order=["-created_at"])
        assert params["order"] == "created_at.desc"

    def test_multiple_orders(self, client: PostgRESTClient) -> None:
        params = client._build_query_params(
            order=["-created_at", "title"]
        )
        assert params["order"] == "created_at.desc,title.asc"


class TestPagination:
    def test_limit(self, client: PostgRESTClient) -> None:
        params = client._build_query_params(limit=10)
        assert params["limit"] == "10"

    def test_offset(self, client: PostgRESTClient) -> None:
        params = client._build_query_params(offset=20)
        assert params["offset"] == "20"

    def test_limit_and_offset(self, client: PostgRESTClient) -> None:
        params = client._build_query_params(limit=10, offset=20)
        assert params["limit"] == "10"
        assert params["offset"] == "20"


class TestColumnSelection:
    def test_default_all(self, client: PostgRESTClient) -> None:
        params = client._build_query_params()
        assert "select" not in params

    def test_specific_columns(self, client: PostgRESTClient) -> None:
        params = client._build_query_params(columns="id,title,status")
        assert params["select"] == "id,title,status"


class TestMultipleFilters:
    def test_combined_filters(self, client: PostgRESTClient) -> None:
        params = client._build_query_params(
            filters={"status": "active", "age__gte": 18},
            order=["-created_at"],
            limit=10,
        )
        assert params["status"] == "eq.active"
        assert params["age"] == "gte.18"
        assert params["order"] == "created_at.desc"
        assert params["limit"] == "10"

    def test_empty_filters(self, client: PostgRESTClient) -> None:
        params = client._build_query_params(filters={})
        assert "status" not in params


class TestHeaders:
    def test_auth_headers(self, client: PostgRESTClient) -> None:
        headers = client._headers("my-jwt-token")
        assert headers["Authorization"] == "Bearer my-jwt-token"
        assert headers["apikey"] == "test-anon-key"

    def test_prefer_header(self, client: PostgRESTClient) -> None:
        headers = client._headers(
            "token", prefer="return=representation"
        )
        assert headers["Prefer"] == "return=representation"

    def test_no_prefer(self, client: PostgRESTClient) -> None:
        headers = client._headers("token")
        assert headers.get("Prefer", "") == ""
