from __future__ import annotations

from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    pass

# ---------------------------------------------------------------------------
# F() — field reference (arithmetic expressions)
# ---------------------------------------------------------------------------

class F:
    """Reference a model field by name for use in database-level expressions."""

    def __init__(self, field_name: str) -> None:
        self.field_name = field_name

    def __add__(self, other: Any) -> Expression:
        return Expression(self.field_name, "+", other)

    def __radd__(self, other: Any) -> Expression:
        return Expression(self.field_name, "+", other)

    def __sub__(self, other: Any) -> Expression:
        return Expression(self.field_name, "-", other)

    def __mul__(self, other: Any) -> Expression:
        return Expression(self.field_name, "*", other)

    def __truediv__(self, other: Any) -> Expression:
        return Expression(self.field_name, "/", other)

    def __repr__(self) -> str:
        return f"F({self.field_name!r})"


class Expression:
    """Arithmetic expression on a field, e.g. F('balance') - 100 → balance = balance - 100."""

    def __init__(self, field_name: str, operator: str, value: Any) -> None:
        self.field_name = field_name
        self.operator = operator
        self.value = value

    def as_sql(self, params: list[Any]) -> str:
        """Render as SQL fragment, appending any params needed."""
        if isinstance(self.value, F):
            return f"{self.field_name} {self.operator} {self.value.field_name}"
        params.append(self.value)
        return f"{self.field_name} {self.operator} ${len(params)}"

    def __repr__(self) -> str:
        return f"Expression({self.field_name!r} {self.operator} {self.value!r})"


# ---------------------------------------------------------------------------
# Q() — boolean query composition
# ---------------------------------------------------------------------------

class Q:
    """Encapsulate filter kwargs for boolean composition (AND / OR / NOT).

    Usage::

        await User.filter(Q(status="active") | Q(role="admin")).all()
        await User.filter(~Q(banned=True), tenant_id=tid).all()
        await User.filter(Q(a=1) & Q(b=2)).all()
    """

    AND = "AND"
    OR = "OR"
    NOT = "NOT"

    def __init__(self, *args: "Q", **kwargs: Any) -> None:
        self.connector: str = self.AND
        self.negated: bool = False
        # Children is a list of (Q | None) for compound nodes, or kwargs for leaf nodes.
        self.children: list[Q] = list(args)
        self.kwargs: dict[str, Any] = kwargs

    # -- Boolean operators --------------------------------------------------

    def __and__(self, other: "Q") -> "Q":
        node = Q()
        node.connector = self.AND
        node.children = [self, other]
        return node

    def __or__(self, other: "Q") -> "Q":
        node = Q()
        node.connector = self.OR
        node.children = [self, other]
        return node

    def __invert__(self) -> "Q":
        node = Q(**self.kwargs)
        node.connector = self.connector
        node.children = list(self.children)
        node.negated = not self.negated
        return node

    @property
    def is_leaf(self) -> bool:
        """True when this Q node directly holds filter kwargs (no children)."""
        return not self.children

    def __repr__(self) -> str:
        if self.is_leaf:
            prefix = "~" if self.negated else ""
            return f"{prefix}Q({', '.join(f'{k}={v!r}' for k, v in self.kwargs.items())})"
        prefix = "~" if self.negated else ""
        inner = f" {self.connector} ".join(repr(c) for c in self.children)
        return f"{prefix}({inner})"


# ---------------------------------------------------------------------------
# OuterRef — correlated subquery field reference
# ---------------------------------------------------------------------------

class OuterRef:
    """Reference a field from the outer query in a correlated subquery.

    Usage::

        latest = Order.filter(user_id=OuterRef("id")).order_by("-created_at").limit(1)
        users = await User.filter(Exists(latest)).all()
    """

    def __init__(self, field_name: str) -> None:
        self.field_name = field_name

    def __repr__(self) -> str:
        return f"OuterRef({self.field_name!r})"


# ---------------------------------------------------------------------------
# Subquery / Exists — subquery expressions
# ---------------------------------------------------------------------------

class Subquery:
    """Wrap a QueryBuilder as a scalar subquery.

    Usage::

        latest_total = Order.filter(user_id=OuterRef("id")).order_by("-created_at").limit(1).select("total")
        users = await User.filter(is_active=True).annotate(last_total=Subquery(latest_total)).values("id", "last_total")
    """

    def __init__(self, queryset: Any) -> None:
        self.queryset = queryset

    def as_sql(self, outer_table: str, params: list[Any]) -> str:
        """Render as a parenthesised SQL sub-select, appending params."""
        return _render_subquery(self.queryset, outer_table, params)

    def __repr__(self) -> str:
        return f"Subquery({self.queryset!r})"


class Exists:
    """Wrap a QueryBuilder as an EXISTS (...) subquery filter.

    Usage::

        active_orders = Order.filter(user_id=OuterRef("id"), status="active")
        users = await User.filter(Exists(active_orders)).all()
    """

    def __init__(self, queryset: Any) -> None:
        self.queryset = queryset

    def as_sql(self, outer_table: str, params: list[Any]) -> str:
        inner = _render_subquery(self.queryset, outer_table, params, exists=True)
        return f"EXISTS {inner}"

    def __repr__(self) -> str:
        return f"Exists({self.queryset!r})"


def _render_subquery(queryset: Any, outer_table: str, params: list[Any], exists: bool = False) -> str:
    """Convert a QueryBuilder into a SQL subquery string.

    OuterRef placeholders are replaced with ``outer_table.field_name``.
    Bound parameters from the subquery are appended to ``params`` with
    renumbered placeholders so they don't conflict with the outer query.
    """
    from matrx_orm.query.builder import QueryBuilder  # local import avoids circularity

    if not isinstance(queryset, QueryBuilder):
        raise TypeError(f"Subquery/Exists requires a QueryBuilder, got {type(queryset)}")

    query_dict = queryset._build_query()
    table = query_dict["table"]

    if exists:
        select_clause = "1"
    else:
        sel = query_dict.get("select", ["*"])
        select_clause = ", ".join(sel) if sel != ["*"] else "*"

    sub_params: list[Any] = []
    where_conditions: list[str] = []

    filters = query_dict.get("filters", {})
    for key, value in filters.items():
        field_name, operator = _parse_lookup_simple(key)
        # Resolve OuterRef → outer_table.field
        if isinstance(value, OuterRef):
            condition = f"{field_name} = {outer_table}.{value.field_name}"
            where_conditions.append(condition)
            continue
        from matrx_orm.query.executor import QueryExecutor, _SKIP_PARAM
        cond, param = QueryExecutor._build_condition(field_name, operator, value, len(params) + len(sub_params) + 1)
        where_conditions.append(cond)
        if param is not _SKIP_PARAM:
            sub_params.append(param)

    sql = f"SELECT {select_clause} FROM {table}"
    if where_conditions:
        sql += " WHERE " + " AND ".join(where_conditions)

    order_by = query_dict.get("order_by", [])
    if order_by:
        terms = []
        for term in order_by:
            if isinstance(term, str):
                terms.append(f"{term[1:]} DESC" if term.startswith("-") else f"{term} ASC")
        if terms:
            sql += " ORDER BY " + ", ".join(terms)

    limit = query_dict.get("limit")
    if limit is not None:
        sub_params.append(limit)
        sql += f" LIMIT ${len(params) + len(sub_params)}"

    params.extend(sub_params)
    return f"({sql})"


def _parse_lookup_simple(key: str) -> tuple[str, str]:
    _LOOKUP_OPERATORS = {
        "in", "gt", "gte", "lt", "lte", "ne",
        "isnull", "contains", "icontains",
        "startswith", "endswith", "exclude",
    }
    if "__" in key:
        parts = key.rsplit("__", 1)
        if parts[1] in _LOOKUP_OPERATORS:
            return parts[0], parts[1]
    return key, "eq"


# ---------------------------------------------------------------------------
# Func — SQL database functions
# ---------------------------------------------------------------------------

class Func:
    """Base class for SQL function wrappers.

    Subclass and set ``function`` to the SQL function name.  Arguments may be
    field name strings, other ``Func`` instances, ``F()`` references, or
    literal values.
    """

    function: str = ""

    def __init__(self, *args: Any, output_field: str | None = None) -> None:
        self.args = args
        self.output_field = output_field

    def as_sql(self, params: list[Any]) -> str:
        """Render to SQL, appending bound parameters to *params*."""
        rendered: list[str] = []
        for arg in self.args:
            rendered.append(_render_func_arg(arg, params))
        return f"{self.function}({', '.join(rendered)})"

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({', '.join(repr(a) for a in self.args)})"


def _render_func_arg(arg: Any, params: list[Any]) -> str:
    """Render a single function argument to a SQL fragment."""
    if isinstance(arg, Func):
        return arg.as_sql(params)
    if isinstance(arg, F):
        return arg.field_name
    if isinstance(arg, str):
        # Treat bare strings as field/column names (no quoting — same convention as order_by)
        return arg
    if isinstance(arg, Cast):
        return arg.as_sql(params)
    # Literal value — bind as parameter
    params.append(arg)
    return f"${len(params)}"


# -- Concrete database functions --------------------------------------------

class Coalesce(Func):
    """COALESCE(a, b, ...) — returns first non-NULL argument."""
    function = "COALESCE"


class Lower(Func):
    """LOWER(field) — convert to lower-case."""
    function = "LOWER"


class Upper(Func):
    """UPPER(field) — convert to upper-case."""
    function = "UPPER"


class Length(Func):
    """LENGTH(field) — character length."""
    function = "LENGTH"


class Trim(Func):
    """TRIM(field) — remove leading/trailing whitespace."""
    function = "TRIM"


class Now(Func):
    """NOW() — current timestamp."""
    function = "NOW"

    def __init__(self) -> None:
        super().__init__()

    def as_sql(self, params: list[Any]) -> str:
        return "NOW()"


class Concat(Func):
    """CONCAT(a, b, ...) — concatenate strings."""
    function = "CONCAT"


class Greatest(Func):
    """GREATEST(a, b, ...) — largest of arguments."""
    function = "GREATEST"


class Least(Func):
    """LEAST(a, b, ...) — smallest of arguments."""
    function = "LEAST"


class Abs(Func):
    """ABS(field) — absolute value."""
    function = "ABS"


class Round(Func):
    """ROUND(field[, decimals]) — round to decimals places."""
    function = "ROUND"


class Cast(Func):
    """CAST(expr AS type) — explicit type cast."""
    function = "CAST"

    def __init__(self, expr: Any, as_type: str) -> None:
        super().__init__(expr)
        self.as_type = as_type

    def as_sql(self, params: list[Any]) -> str:
        inner = _render_func_arg(self.args[0], params)
        return f"CAST({inner} AS {self.as_type})"


class Extract(Func):
    """EXTRACT(part FROM field) — extract date/time component."""
    function = "EXTRACT"

    def __init__(self, part: str, field: str | F | Func) -> None:
        super().__init__(field)
        self.part = part

    def as_sql(self, params: list[Any]) -> str:
        inner = _render_func_arg(self.args[0], params)
        return f"EXTRACT({self.part} FROM {inner})"


class DateTrunc(Func):
    """DATE_TRUNC(precision, field) — truncate to date/time precision."""
    function = "DATE_TRUNC"

    def __init__(self, precision: str, field: str | F | Func) -> None:
        super().__init__(field)
        self.precision = precision

    def as_sql(self, params: list[Any]) -> str:
        inner = _render_func_arg(self.args[0], params)
        params.append(self.precision)
        return f"DATE_TRUNC(${len(params)}, {inner})"


# ---------------------------------------------------------------------------
# Aggregate expressions
# ---------------------------------------------------------------------------

class Aggregate(Func):
    """Base class for SQL aggregate functions (SUM, AVG, MIN, MAX, COUNT)."""

    def __init__(self, field: str | F | Func | None = None, *, distinct: bool = False) -> None:
        args = (field,) if field is not None else ()
        super().__init__(*args)
        self.distinct = distinct

    def as_sql(self, params: list[Any]) -> str:
        if not self.args:
            return f"{self.function}(*)"
        inner = _render_func_arg(self.args[0], params)
        distinct_clause = "DISTINCT " if self.distinct else ""
        return f"{self.function}({distinct_clause}{inner})"


class Sum(Aggregate):
    """SUM(field)."""
    function = "SUM"


class Avg(Aggregate):
    """AVG(field)."""
    function = "AVG"


class Min(Aggregate):
    """MIN(field)."""
    function = "MIN"


class Max(Aggregate):
    """MAX(field)."""
    function = "MAX"


class Count(Aggregate):
    """COUNT(field) or COUNT(*)."""
    function = "COUNT"

    def __init__(self, field: str | F | Func | None = None, *, distinct: bool = False) -> None:
        # COUNT(*) when no field
        super().__init__(field, distinct=distinct)


class StdDev(Aggregate):
    """STDDEV(field) — population standard deviation."""
    function = "STDDEV"


class Variance(Aggregate):
    """VARIANCE(field) — population variance."""
    function = "VARIANCE"


# ---------------------------------------------------------------------------
# Window expressions
# ---------------------------------------------------------------------------

class Window:
    """Wrap an aggregate or ranking function with an OVER (...) clause.

    Usage::

        .annotate(row_num=Window(RowNumber(), partition_by="tenant_id", order_by="-created_at"))
        .annotate(rank=Window(Rank(), order_by=["-score", "id"]))
        .annotate(running_total=Window(Sum("amount"), partition_by=["user_id"], order_by="created_at"))
    """

    def __init__(
        self,
        expression: "Func | Aggregate",
        *,
        partition_by: str | list[str] | None = None,
        order_by: str | list[str] | None = None,
        frame: str | None = None,
    ) -> None:
        self.expression = expression
        self.partition_by: list[str] = (
            [partition_by] if isinstance(partition_by, str) else (partition_by or [])
        )
        self.order_by: list[str] = (
            [order_by] if isinstance(order_by, str) else (order_by or [])
        )
        self.frame = frame  # e.g. "ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW"

    def as_sql(self, params: list[Any]) -> str:
        expr_sql = self.expression.as_sql(params)
        over_parts: list[str] = []

        if self.partition_by:
            over_parts.append("PARTITION BY " + ", ".join(self.partition_by))

        if self.order_by:
            terms: list[str] = []
            for term in self.order_by:
                if term.startswith("-"):
                    terms.append(f"{term[1:]} DESC")
                else:
                    terms.append(f"{term} ASC")
            over_parts.append("ORDER BY " + ", ".join(terms))

        if self.frame:
            over_parts.append(self.frame)

        over_clause = "OVER (" + " ".join(over_parts) + ")"
        return f"{expr_sql} {over_clause}"

    def __repr__(self) -> str:
        return f"Window({self.expression!r})"


class RowNumber(Func):
    """ROW_NUMBER() — sequential row number within the window partition."""
    function = "ROW_NUMBER"

    def __init__(self) -> None:
        super().__init__()

    def as_sql(self, params: list[Any]) -> str:
        return "ROW_NUMBER()"


class Rank(Func):
    """RANK() — rank with gaps for ties."""
    function = "RANK"

    def __init__(self) -> None:
        super().__init__()

    def as_sql(self, params: list[Any]) -> str:
        return "RANK()"


class DenseRank(Func):
    """DENSE_RANK() — rank without gaps for ties."""
    function = "DENSE_RANK"

    def __init__(self) -> None:
        super().__init__()

    def as_sql(self, params: list[Any]) -> str:
        return "DENSE_RANK()"


class Lag(Func):
    """LAG(field[, offset[, default]]) — value from previous row."""
    function = "LAG"

    def __init__(self, field: str | F | Func, offset: int = 1, default: Any = None) -> None:
        super().__init__(field)
        self.offset = offset
        self.default = default

    def as_sql(self, params: list[Any]) -> str:
        inner = _render_func_arg(self.args[0], params)
        if self.default is not None:
            params.append(self.default)
            return f"LAG({inner}, {self.offset}, ${len(params)})"
        return f"LAG({inner}, {self.offset})"


class Lead(Func):
    """LEAD(field[, offset[, default]]) — value from following row."""
    function = "LEAD"

    def __init__(self, field: str | F | Func, offset: int = 1, default: Any = None) -> None:
        super().__init__(field)
        self.offset = offset
        self.default = default

    def as_sql(self, params: list[Any]) -> str:
        inner = _render_func_arg(self.args[0], params)
        if self.default is not None:
            params.append(self.default)
            return f"LEAD({inner}, {self.offset}, ${len(params)})"
        return f"LEAD({inner}, {self.offset})"


class FirstValue(Func):
    """FIRST_VALUE(field) — first value in the window frame."""
    function = "FIRST_VALUE"


class LastValue(Func):
    """LAST_VALUE(field) — last value in the window frame."""
    function = "LAST_VALUE"


class NthValue(Func):
    """NTH_VALUE(field, n) — nth value in the window frame."""
    function = "NTH_VALUE"

    def __init__(self, field: str | F | Func, n: int) -> None:
        super().__init__(field)
        self.n = n

    def as_sql(self, params: list[Any]) -> str:
        inner = _render_func_arg(self.args[0], params)
        return f"NTH_VALUE({inner}, {self.n})"


class Ntile(Func):
    """NTILE(n) — divide rows into n buckets."""
    function = "NTILE"

    def __init__(self, n: int) -> None:
        super().__init__()
        self.n = n

    def as_sql(self, params: list[Any]) -> str:
        return f"NTILE({self.n})"


class CumeDist(Func):
    """CUME_DIST() — cumulative distribution."""
    function = "CUME_DIST"

    def __init__(self) -> None:
        super().__init__()

    def as_sql(self, params: list[Any]) -> str:
        return "CUME_DIST()"


class PercentRank(Func):
    """PERCENT_RANK() — relative rank as a fraction."""
    function = "PERCENT_RANK"

    def __init__(self) -> None:
        super().__init__()

    def as_sql(self, params: list[Any]) -> str:
        return "PERCENT_RANK()"


# ---------------------------------------------------------------------------
# CTE (Common Table Expressions)
# ---------------------------------------------------------------------------

class CTE:
    """Define a named Common Table Expression for use in a query.

    A CTE can wrap either a raw SQL string or a QueryBuilder instance.

    Usage::

        # Raw SQL CTE
        recent_cte = CTE("recent_orders", "SELECT * FROM orders WHERE created_at > NOW() - interval '7 days'")

        # QueryBuilder CTE
        active_users = CTE("active_users", User.filter(is_active=True))

        results = await Order.filter(is_active=True).with_cte(recent_cte).all()

        # Recursive CTE
        tree_cte = CTE(
            "org_tree",
            \"""
            SELECT id, parent_id, name FROM org WHERE parent_id IS NULL
            UNION ALL
            SELECT o.id, o.parent_id, o.name FROM org o JOIN org_tree t ON o.parent_id = t.id
            \""",
            recursive=True,
        )
    """

    def __init__(
        self,
        name: str,
        query: "str | Any",  # str or QueryBuilder
        *,
        recursive: bool = False,
    ) -> None:
        self.name = name
        self.query = query
        self.recursive = recursive

    def as_sql(self, params: list[Any]) -> str:
        """Render as ``name AS (...)`` — used inside a WITH clause."""
        if isinstance(self.query, str):
            return f"{self.name} AS ({self.query})"
        # QueryBuilder
        from matrx_orm.query.builder import QueryBuilder
        if isinstance(self.query, QueryBuilder):
            query_dict = self.query._build_query()
            # Build a minimal SELECT for the CTE
            from matrx_orm.query.executor import QueryExecutor
            executor = QueryExecutor(query_dict)
            # Renumber params to continue from current offset
            sub_sql, sub_params = executor.query, executor.params
            # Shift param indices
            offset = len(params)
            if offset > 0:
                for i, _ in enumerate(sub_params):
                    sub_sql = sub_sql.replace(f"${i + 1}", f"${offset + i + 1}", 1)
            params.extend(sub_params)
            return f"{self.name} AS ({sub_sql})"
        raise TypeError(f"CTE query must be str or QueryBuilder, got {type(self.query)}")

    def __repr__(self) -> str:
        return f"CTE({self.name!r})"
