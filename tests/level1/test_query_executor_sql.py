"""Level 1: _parse_lookup, _build_condition, SQL generation (no DB)."""

import pytest

from matrx_orm.query.executor import QueryExecutor, _SKIP_PARAM


class TestParseLookup:
    def test_simple_field(self):
        field, op = QueryExecutor._parse_lookup("name")
        assert field == "name"
        assert op == "eq"

    def test_eq_explicit(self):
        field, op = QueryExecutor._parse_lookup("name")
        assert op == "eq"

    def test_in(self):
        field, op = QueryExecutor._parse_lookup("id__in")
        assert field == "id"
        assert op == "in"

    def test_gt(self):
        field, op = QueryExecutor._parse_lookup("age__gt")
        assert field == "age"
        assert op == "gt"

    def test_gte(self):
        field, op = QueryExecutor._parse_lookup("age__gte")
        assert field == "age"
        assert op == "gte"

    def test_lt(self):
        field, op = QueryExecutor._parse_lookup("age__lt")
        assert field == "age"
        assert op == "lt"

    def test_lte(self):
        field, op = QueryExecutor._parse_lookup("age__lte")
        assert field == "age"
        assert op == "lte"

    def test_ne(self):
        field, op = QueryExecutor._parse_lookup("status__ne")
        assert field == "status"
        assert op == "ne"

    def test_isnull(self):
        field, op = QueryExecutor._parse_lookup("deleted_at__isnull")
        assert field == "deleted_at"
        assert op == "isnull"

    def test_contains(self):
        field, op = QueryExecutor._parse_lookup("name__contains")
        assert field == "name"
        assert op == "contains"

    def test_icontains(self):
        field, op = QueryExecutor._parse_lookup("name__icontains")
        assert field == "name"
        assert op == "icontains"

    def test_startswith(self):
        field, op = QueryExecutor._parse_lookup("name__startswith")
        assert field == "name"
        assert op == "startswith"

    def test_endswith(self):
        field, op = QueryExecutor._parse_lookup("name__endswith")
        assert field == "name"
        assert op == "endswith"

    def test_exclude(self):
        field, op = QueryExecutor._parse_lookup("role__exclude")
        assert field == "role"
        assert op == "exclude"

    def test_unknown_suffix_treated_as_field_name(self):
        field, op = QueryExecutor._parse_lookup("data__nested_key")
        assert field == "data__nested_key"
        assert op == "eq"

    def test_double_underscore_with_valid_op(self):
        field, op = QueryExecutor._parse_lookup("user__name__contains")
        assert field == "user__name"
        assert op == "contains"


class TestBuildCondition:
    def test_eq(self):
        sql, val = QueryExecutor._build_condition("name", "eq", "Alice", 1)
        assert sql == "name = $1"
        assert val == "Alice"

    def test_ne(self):
        sql, val = QueryExecutor._build_condition("status", "ne", "active", 1)
        assert sql == "status != $1"
        assert val == "active"

    def test_gt(self):
        sql, val = QueryExecutor._build_condition("age", "gt", 18, 2)
        assert sql == "age > $2"
        assert val == 18

    def test_gte(self):
        sql, val = QueryExecutor._build_condition("age", "gte", 18, 3)
        assert sql == "age >= $3"
        assert val == 18

    def test_lt(self):
        sql, val = QueryExecutor._build_condition("age", "lt", 65, 1)
        assert sql == "age < $1"
        assert val == 65

    def test_lte(self):
        sql, val = QueryExecutor._build_condition("age", "lte", 65, 1)
        assert sql == "age <= $1"
        assert val == 65

    def test_in(self):
        sql, val = QueryExecutor._build_condition("id", "in", [1, 2, 3], 1)
        assert sql == "id = ANY($1)"
        assert val == [1, 2, 3]

    def test_isnull_true(self):
        sql, val = QueryExecutor._build_condition("deleted_at", "isnull", True, 1)
        assert sql == "deleted_at IS NULL"
        assert val is _SKIP_PARAM

    def test_isnull_false(self):
        sql, val = QueryExecutor._build_condition("deleted_at", "isnull", False, 1)
        assert sql == "deleted_at IS NOT NULL"
        assert val is _SKIP_PARAM

    def test_contains(self):
        sql, val = QueryExecutor._build_condition("name", "contains", "ali", 1)
        assert sql == "name LIKE $1"
        assert val == "%ali%"

    def test_icontains(self):
        sql, val = QueryExecutor._build_condition("name", "icontains", "ali", 1)
        assert sql == "name ILIKE $1"
        assert val == "%ali%"

    def test_startswith(self):
        sql, val = QueryExecutor._build_condition("name", "startswith", "Al", 1)
        assert sql == "name LIKE $1"
        assert val == "Al%"

    def test_endswith(self):
        sql, val = QueryExecutor._build_condition("name", "endswith", "ce", 1)
        assert sql == "name LIKE $1"
        assert val == "%ce"

    def test_exclude_operator(self):
        sql, val = QueryExecutor._build_condition("role", "exclude", "admin", 1)
        assert sql == "role != $1"
        assert val == "admin"

    def test_fallback_eq(self):
        sql, val = QueryExecutor._build_condition("x", "unknown_op", "val", 1)
        assert sql == "x = $1"
        assert val == "val"

    def test_param_index_used(self):
        sql, _ = QueryExecutor._build_condition("col", "eq", "v", 5)
        assert "$5" in sql
