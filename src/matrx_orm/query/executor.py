from __future__ import annotations

import json
from typing import Any, TYPE_CHECKING

from matrx_utils import vcprint
from matrx_orm.core.async_db_manager import AsyncDatabaseManager
from matrx_orm.exceptions import (
    DatabaseError,
    ValidationError,
    IntegrityError,
    QueryError,
)

if TYPE_CHECKING:
    from matrx_orm.core.base import Model

debug = False

_SKIP_PARAM = object()


class QueryExecutor:
    model: type[Model]
    database: str
    db: AsyncDatabaseManager
    _full_query_dict: dict[str, Any]
    query: str
    params: list[Any]

    def __init__(self, query: dict[str, Any]) -> None:
        _required = ("model", "database", "table")
        _missing = [k for k in _required if k not in query]
        if _missing:
            raise QueryError(
                message=f"Query dict missing required keys: {_missing}. Use QueryBuilder._build_query() to construct query dicts.",
                details={"missing_keys": _missing, "provided_keys": list(query.keys())},
            )
        self.model = query["model"]
        self.database = query["database"]
        self.db = AsyncDatabaseManager()
        self._full_query_dict = query
        self.query, self.params = self._build_query()

    # ------------------------------------------------------------------
    # Lookup operator registry
    # ------------------------------------------------------------------

    _LOOKUP_OPERATORS = {
        "in", "gt", "gte", "lt", "lte", "ne",
        "isnull", "contains", "icontains",
        "startswith", "endswith", "exclude",
        # JSONB operators
        "json_key", "json_has_key", "json_has_any",
        "json_has_all", "json_contains", "json_contained_by", "json_path",
    }

    @classmethod
    def _parse_lookup(cls, key: str) -> tuple[str, str]:
        """Parse 'field__operator' into (field_name, operator). Default operator is 'eq'."""
        if "__" in key:
            parts = key.rsplit("__", 1)
            if parts[1] in cls._LOOKUP_OPERATORS:
                return parts[0], parts[1]
        return key, "eq"

    @staticmethod
    def _build_condition(field: str, operator: str, value: Any, param_idx: int) -> tuple[str, Any]:
        """Build a SQL condition and its parameter for a given lookup operator.

        Returns (condition_sql, param_value). param_value is _SKIP_PARAM for
        parameterless operators (IS NULL / JSONB key-exists etc.).
        """
        placeholder = f"${param_idx}"
        # Standard operators
        if operator == "eq":
            return f"{field} = {placeholder}", value
        if operator == "ne":
            return f"{field} != {placeholder}", value
        if operator == "gt":
            return f"{field} > {placeholder}", value
        if operator == "gte":
            return f"{field} >= {placeholder}", value
        if operator == "lt":
            return f"{field} < {placeholder}", value
        if operator == "lte":
            return f"{field} <= {placeholder}", value
        if operator == "in":
            return f"{field} = ANY({placeholder})", value
        if operator == "isnull":
            return (f"{field} IS NULL", _SKIP_PARAM) if value else (f"{field} IS NOT NULL", _SKIP_PARAM)
        if operator == "contains":
            return f"{field} LIKE {placeholder}", f"%{value}%"
        if operator == "icontains":
            return f"{field} ILIKE {placeholder}", f"%{value}%"
        if operator == "startswith":
            return f"{field} LIKE {placeholder}", f"{value}%"
        if operator == "endswith":
            return f"{field} LIKE {placeholder}", f"%{value}"
        if operator == "exclude":
            return f"{field} != {placeholder}", value
        # JSONB operators
        if operator == "json_key":
            # field ->> 'key' = $n   (value is (key, expected_value))
            if isinstance(value, tuple) and len(value) == 2:
                key, expected = value
                return f"{field} ->> {placeholder}", key
            # Single arg — just test extraction (non-null)
            return f"{field} ->> {placeholder} IS NOT NULL", value
        if operator == "json_has_key":
            # field ? 'key'  — key-exists, no param needed when literal
            if isinstance(value, str):
                return f"{field} ? {placeholder}", value
            return f"{field} ? {placeholder}", str(value)
        if operator == "json_has_any":
            # field ?| array[$1]
            return f"{field} ?| {placeholder}", list(value)
        if operator == "json_has_all":
            # field ?& array[$1]
            return f"{field} ?& {placeholder}", list(value)
        if operator == "json_contains":
            # field @> $1::jsonb
            v = json.dumps(value) if not isinstance(value, str) else value
            return f"{field} @> {placeholder}::jsonb", v
        if operator == "json_contained_by":
            # field <@ $1::jsonb
            v = json.dumps(value) if not isinstance(value, str) else value
            return f"{field} <@ {placeholder}::jsonb", v
        if operator == "json_path":
            # field #>> '{key1,key2}' = $1  (value is (path_tuple, expected))
            if isinstance(value, (list, tuple)):
                path = "{" + ",".join(str(p) for p in value) + "}"
                return f"{field} #>> {placeholder}", path
            return f"{field} #>> {placeholder}", str(value)
        return f"{field} = {placeholder}", value

    # ------------------------------------------------------------------
    # Main SQL builder
    # ------------------------------------------------------------------

    def _build_query(self) -> tuple[str, list[Any]]:
        """Construct the SELECT SQL statement and bound parameter list."""
        params: list[Any] = []
        table = self._full_query_dict["table"]

        # -- SELECT clause -----------------------------------------------
        aggregations: list[dict[str, Any]] = self._full_query_dict.get("aggregations", [])
        select_related: list[str] = self._full_query_dict.get("select_related", [])
        raw_select: list[str] = self._full_query_dict.get("select", ["*"])

        select_parts: list[str] = []

        # 1. select_related JOIN columns (prefixed aliases)
        join_clauses: list[str] = []
        if select_related and hasattr(self.model, "_meta"):
            for fk_field in select_related:
                fk_ref = self.model._meta.foreign_keys.get(fk_field)
                if fk_ref is None:
                    continue
                related_model = fk_ref.related_model
                if related_model is None:
                    continue
                related_table = related_model._meta.qualified_table_name
                alias = f"__sr_{fk_field}__"
                join_clauses.append(
                    f"LEFT JOIN {related_table} AS {alias} "
                    f"ON {table}.{fk_ref.column_name} = {alias}.{fk_ref.to_column}"
                )
                # Add all columns from related model with prefix
                if hasattr(related_model, "_fields"):
                    for col in related_model._fields:
                        select_parts.append(f"{alias}.{col} AS __fk_{fk_field}__{col}")

        # 2. Regular columns
        if raw_select == ["*"]:
            if select_related:
                # Need explicit table prefix to avoid ambiguity
                select_parts.insert(0, f"{table}.*")
            else:
                select_parts.insert(0, "*")
        else:
            for f in raw_select:
                select_parts.insert(0, f)

        # 3. Aggregation columns
        for agg in aggregations:
            name = agg["name"]
            func = agg["function"]
            if hasattr(func, "as_sql"):
                expr = func.as_sql(params)
            else:
                expr = str(func)
            select_parts.append(f"{expr} AS {name}")

        # -- DISTINCT clause ---------------------------------------------
        distinct = self._full_query_dict.get("distinct")
        if distinct is None:
            distinct_clause = ""
        elif distinct == [] or not distinct:
            distinct_clause = "DISTINCT "
        else:
            distinct_clause = f"DISTINCT ON ({', '.join(distinct)}) "

        select_clause = ", ".join(select_parts) if select_parts else "*"
        sql = f"SELECT {distinct_clause}{select_clause} FROM {table}"

        # -- JOINs -------------------------------------------------------
        if join_clauses:
            sql += " " + " ".join(join_clauses)

        # -- WHERE clause ------------------------------------------------
        filter_items: list[Any] = self._full_query_dict.get("filters", [])
        where_conditions: list[str] = []

        for item in filter_items:
            from matrx_orm.core.expressions import Q as _Q
            if isinstance(item, _Q):
                cond = self._render_q(item, params)
                if cond:
                    where_conditions.append(cond)
            elif isinstance(item, dict):
                for key, value in item.items():
                    field_name, operator = self._parse_lookup(key)
                    field_name = self._resolve_fk_field(field_name)
                    cond_sql, _ = self._build_condition_with_expr(field_name, operator, value, params)
                    if cond_sql:
                        where_conditions.append(cond_sql)
            else:
                # Exists expression passed directly as positional filter arg
                from matrx_orm.core.expressions import Exists as ExistsExpr
                if isinstance(item, ExistsExpr):
                    where_conditions.append(item.as_sql(table, params))

        if where_conditions:
            sql += " WHERE " + " AND ".join(where_conditions)

        # -- GROUP BY ---------------------------------------------------
        group_by: list[str] = self._full_query_dict.get("group_by", [])
        if group_by:
            sql += " GROUP BY " + ", ".join(group_by)

        # -- HAVING -----------------------------------------------------
        having: dict[str, Any] = self._full_query_dict.get("having", {})
        if having:
            having_conditions: list[str] = []
            for key, value in having.items():
                field_name, operator = self._parse_lookup(key)
                cond_sql, param = self._build_condition(field_name, operator, value, len(params) + 1)
                having_conditions.append(cond_sql)
                if param is not _SKIP_PARAM:
                    params.append(param)
            if having_conditions:
                sql += " HAVING " + " AND ".join(having_conditions)

        # -- ORDER BY ---------------------------------------------------
        order_by = self._full_query_dict.get("order_by", [])
        if order_by:
            order_by_terms: list[str] = []
            for term in order_by:
                if isinstance(term, str):
                    if term.startswith("-"):
                        order_by_terms.append(f"{term[1:]} DESC")
                    else:
                        order_by_terms.append(f"{term} ASC")
                elif hasattr(term, "_order_direction"):
                    fname = term.name
                    if fname is None:
                        for fn, field in self.model._fields.items():
                            if field is term:
                                fname = fn
                                break
                        if fname is None:
                            raise ValueError(f"Field object in order_by could not be matched to a model field: {term}")
                    direction = term._order_direction or "ASC"
                    order_by_terms.append(f"{fname} {direction}")
                else:
                    raise ValueError(f"Invalid order_by term: {term}")
            sql += " ORDER BY " + ", ".join(order_by_terms)

        # -- LIMIT / OFFSET ---------------------------------------------
        if self._full_query_dict.get("limit") is not None:
            sql += f" LIMIT ${len(params) + 1}"
            params.append(self._full_query_dict["limit"])

        if self._full_query_dict.get("offset") is not None:
            sql += f" OFFSET ${len(params) + 1}"
            params.append(self._full_query_dict["offset"])

        # -- FOR UPDATE -------------------------------------------------
        for_update = self._full_query_dict.get("for_update")
        if for_update:
            clause = " FOR UPDATE"
            if for_update.get("nowait"):
                clause += " NOWAIT"
            elif for_update.get("skip_locked"):
                clause += " SKIP LOCKED"
            of_tables = for_update.get("of", [])
            if of_tables:
                clause += " OF " + ", ".join(of_tables)
            sql += clause

        if debug:
            vcprint(sql, "Built SQL", verbose=debug, color="cyan")
            vcprint(params, "With params", verbose=debug, color="cyan")

        return sql, params

    def _resolve_fk_field(self, field_name: str) -> str:
        """Map FK model attribute name to the actual DB column name."""
        if hasattr(self.model, "_meta") and field_name in self.model._meta.foreign_keys:
            return self.model._meta.foreign_keys[field_name].field_name
        return field_name

    def _build_condition_with_expr(
        self, field_name: str, operator: str, value: Any, params: list[Any]
    ) -> tuple[str, Any]:
        """Build a condition, handling Func/Subquery/Exists values."""
        from matrx_orm.core.expressions import Func, Subquery, Exists, OuterRef

        table = self._full_query_dict["table"]

        if isinstance(value, Func):
            expr_sql = value.as_sql(params)
            return f"{field_name} = {expr_sql}", _SKIP_PARAM

        if isinstance(value, Subquery):
            sub_sql = value.as_sql(table, params)
            return f"{field_name} = {sub_sql}", _SKIP_PARAM

        if isinstance(value, Exists):
            return value.as_sql(table, params), _SKIP_PARAM

        if isinstance(value, OuterRef):
            # Used inside subqueries — outer ref already resolved by Subquery renderer
            return f"{field_name} = {value.field_name}", _SKIP_PARAM

        cond, param = self._build_condition(field_name, operator, value, len(params) + 1)
        if param is not _SKIP_PARAM:
            params.append(param)
        return cond, param

    def _render_q(self, q: Any, params: list[Any]) -> str:
        """Recursively render a Q tree to a SQL WHERE fragment."""
        from matrx_orm.core.expressions import Q  # noqa: F401 (needed for isinstance)

        if q.is_leaf:
            conditions: list[str] = []
            for key, value in q.kwargs.items():
                field_name, operator = self._parse_lookup(key)
                field_name = self._resolve_fk_field(field_name)
                cond, _ = self._build_condition_with_expr(field_name, operator, value, params)
                if cond:
                    conditions.append(cond)
            sql = " AND ".join(conditions) if conditions else ""
        else:
            child_sqls = [self._render_q(child, params) for child in q.children]
            child_sqls = [c for c in child_sqls if c]
            if not child_sqls:
                return ""
            joiner = f" {q.connector} "
            if len(child_sqls) == 1:
                sql = child_sqls[0]
            else:
                sql = "(" + joiner.join(child_sqls) + ")"

        if sql and q.negated:
            sql = f"NOT ({sql})"
        return sql

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _coerce_param(self, field_name: str, value: Any) -> Any:
        """Pass a value through its field's get_db_prep_value() when available."""
        field = self.model._fields.get(field_name)
        if field is not None and hasattr(field, "get_db_prep_value"):
            return field.get_db_prep_value(value)
        return value

    def _extract_where_clause(self) -> tuple[str, list[Any]]:
        """Extract just the WHERE clause and its params from the built SELECT."""
        base_query, where_params = self._build_query()
        where_clause = ""
        if "WHERE" in base_query:
            after_where = base_query.split("WHERE", 1)[1].strip()
            # Strip trailing clauses
            for stopper in ("ORDER BY", "GROUP BY", "HAVING", "LIMIT", "OFFSET", "FOR UPDATE"):
                if stopper in after_where:
                    after_where = after_where.split(stopper)[0].strip()
            where_clause = after_where
        return where_clause, where_params

    async def _execute(self) -> list[dict[str, Any]]:
        """Execute the built SELECT SQL with error handling."""
        from matrx_orm.exceptions import ORMException
        try:
            results = await self.db.execute_query(self.database, self.query, *self.params)
            return results
        except ORMException as e:
            e.enrich(model=self.model, query=self.query, params=self.params)
            raise
        except Exception as e:
            raise QueryError(
                model=self.model,
                details={"query": self.query, "params": self.params, "error": str(e)},
            )

    def _hydrate_with_select_related(self, rows: list[dict[str, Any]]) -> list[Any]:
        """Hydrate rows that include prefixed select_related columns."""
        select_related: list[str] = self._full_query_dict.get("select_related", [])
        instances = []
        for row in rows:
            # Separate main model columns from related ones
            main_data: dict[str, Any] = {}
            related_data: dict[str, dict[str, Any]] = {fk: {} for fk in select_related}

            for key, val in row.items():
                matched = False
                for fk_field in select_related:
                    prefix = f"__fk_{fk_field}__"
                    if key.startswith(prefix):
                        col = key[len(prefix):]
                        related_data[fk_field][col] = val
                        matched = True
                        break
                if not matched:
                    main_data[key] = val

            instance = self.model(**main_data)

            # Hydrate and attach related instances
            for fk_field, fk_row in related_data.items():
                fk_ref = self.model._meta.foreign_keys.get(fk_field)
                if fk_ref and fk_row and any(v is not None for v in fk_row.values()):
                    related_instance = fk_ref.related_model(**fk_row)
                    instance.set_related(fk_field, related_instance)

            instances.append(instance)
        return instances

    # ------------------------------------------------------------------
    # DML methods (INSERT / UPSERT / UPDATE / DELETE)
    # ------------------------------------------------------------------

    async def insert(self, query: dict[str, Any]) -> dict[str, Any]:
        """INSERT a single row, RETURNING *."""
        table = query["table"]
        data = query.get("data", {})

        if not data:
            raise ValidationError(message="No data provided for insert")

        columns = list(data.keys())
        values = list(data.values())
        placeholders = [f"${i + 1}" for i in range(len(values))]
        sql = (
            f"INSERT INTO {table} ({', '.join(columns)}) "
            f"VALUES ({', '.join(placeholders)}) "
            f"RETURNING *"
        )

        try:
            rows = await self.db.execute_query(self.database, sql, *values)
            if not rows:
                raise ValidationError(message="Insert succeeded but returned no data")
            return rows[0]
        except DatabaseError as e:
            if "unique constraint" in str(e).lower():
                raise IntegrityError(original_error=e)
            raise DatabaseError(str(e))

    async def bulk_insert(self, query: dict[str, Any]) -> list[Model]:
        """Bulk INSERT, RETURNING *."""
        table = query["table"]
        data_list = query.get("data", [])

        if not data_list:
            return []

        if not isinstance(data_list, list):
            raise ValidationError(
                model=self.model,
                reason="Data must be a list of dictionaries",
                details={"provided_type": type(data_list).__name__},
            )

        try:
            columns = list(data_list[0].keys())
        except (IndexError, AttributeError) as e:
            raise ValidationError(
                model=self.model,
                reason="First item in data list is invalid",
                details={"error": str(e)},
            )

        all_values: list[Any] = []
        placeholders_list: list[str] = []
        param_index = 1

        for i, row_data in enumerate(data_list):
            if set(row_data.keys()) != set(columns):
                raise ValidationError(
                    model=self.model,
                    reason=f"Row {i} has different columns than first row",
                    details={
                        "expected_columns": columns,
                        "received_columns": list(row_data.keys()),
                    },
                )
            row_phs: list[str] = []
            for col in columns:
                row_phs.append(f"${param_index}")
                all_values.append(row_data[col])
                param_index += 1
            placeholders_list.append(f"({', '.join(row_phs)})")

        sql = (
            f"INSERT INTO {table} ({', '.join(columns)}) "
            f"VALUES {', '.join(placeholders_list)} "
            f"RETURNING *"
        )

        try:
            results = await self.db.execute_query(self.database, sql, *all_values)
            return [self.model(**row) for row in results]
        except DatabaseError as e:
            if "unique constraint" in str(e).lower():
                raise IntegrityError(model=self.model, constraint="unique", original_error=e)
            raise DatabaseError(model=self.model, operation="bulk_insert", original_error=e)
        except Exception as e:
            raise QueryError(
                model=self.model,
                details={"operation": "bulk_insert", "row_count": len(data_list), "error": str(e)},
            )

    async def upsert(self, query: dict[str, Any]) -> dict[str, Any]:
        """INSERT ... ON CONFLICT (conflict_fields) DO UPDATE SET ... RETURNING *"""
        table = query["table"]
        data = query.get("data", {})
        conflict_fields: list[str] = query.get("conflict_fields", [])
        update_fields: list[str] | None = query.get("update_fields")

        if not data:
            raise ValidationError(message="No data provided for upsert")
        if not conflict_fields:
            raise ValidationError(message="No conflict fields provided for upsert")

        columns = list(data.keys())
        values = list(data.values())
        placeholders = [f"${i + 1}" for i in range(len(values))]
        fields_to_update = update_fields or [c for c in columns if c not in conflict_fields]
        if not fields_to_update:
            raise ValidationError(message="No fields to update on conflict — all columns are conflict keys")

        set_clause = ", ".join(f"{f} = EXCLUDED.{f}" for f in fields_to_update)
        sql = (
            f"INSERT INTO {table} ({', '.join(columns)}) "
            f"VALUES ({', '.join(placeholders)}) "
            f"ON CONFLICT ({', '.join(conflict_fields)}) DO UPDATE SET {set_clause} "
            f"RETURNING *"
        )

        try:
            rows = await self.db.execute_query(self.database, sql, *values)
            if not rows:
                raise ValidationError(message="Upsert succeeded but returned no data")
            return rows[0]
        except DatabaseError as e:
            if "unique constraint" in str(e).lower():
                raise IntegrityError(model=self.model, constraint="unique", original_error=e)
            raise DatabaseError(model=self.model, operation="upsert", original_error=e)

    async def bulk_upsert(self, query: dict[str, Any]) -> list[Model]:
        """Bulk INSERT ... ON CONFLICT DO UPDATE."""
        table = query["table"]
        data_list: list[dict[str, Any]] = query.get("data", [])
        conflict_fields: list[str] = query.get("conflict_fields", [])
        update_fields: list[str] | None = query.get("update_fields")

        if not data_list:
            return []
        if not conflict_fields:
            raise ValidationError(message="No conflict fields provided for bulk upsert")

        columns = list(data_list[0].keys())
        fields_to_update = update_fields or [c for c in columns if c not in conflict_fields]
        if not fields_to_update:
            raise ValidationError(message="No fields to update on conflict — all columns are conflict keys")

        all_values: list[Any] = []
        placeholders_list: list[str] = []
        param_index = 1

        for i, row_data in enumerate(data_list):
            if set(row_data.keys()) != set(columns):
                raise ValidationError(
                    model=self.model,
                    reason=f"Row {i} has different columns than first row",
                    details={"expected_columns": columns, "received_columns": list(row_data.keys())},
                )
            row_phs: list[str] = []
            for col in columns:
                row_phs.append(f"${param_index}")
                all_values.append(row_data[col])
                param_index += 1
            placeholders_list.append(f"({', '.join(row_phs)})")

        set_clause = ", ".join(f"{f} = EXCLUDED.{f}" for f in fields_to_update)
        sql = (
            f"INSERT INTO {table} ({', '.join(columns)}) "
            f"VALUES {', '.join(placeholders_list)} "
            f"ON CONFLICT ({', '.join(conflict_fields)}) DO UPDATE SET {set_clause} "
            f"RETURNING *"
        )

        try:
            results = await self.db.execute_query(self.database, sql, *all_values)
            return [self.model(**row) for row in results]
        except DatabaseError as e:
            if "unique constraint" in str(e).lower():
                raise IntegrityError(model=self.model, constraint="unique", original_error=e)
            raise DatabaseError(model=self.model, operation="bulk_upsert", original_error=e)
        except Exception as e:
            raise QueryError(
                model=self.model,
                details={"operation": "bulk_upsert", "row_count": len(data_list), "error": str(e)},
            )

    async def update(self, **kwargs: Any) -> dict[str, Any]:
        """UPDATE rows matching the WHERE clause built from filters."""
        try:
            if not kwargs:
                raise ValidationError(model=self.model, reason="No update data provided")

            table = self._full_query_dict["table"]
            set_clause: list[str] = []
            params: list[Any] = []
            update_data: dict[str, Any] = {}
            invalid_fields: list[str] = []
            skipped_fields: list[str] = []

            from matrx_orm.core.expressions import Func, Expression

            for k, v in kwargs.items():
                if k in self.model._fields:
                    field = self.model._fields[k]
                    if getattr(field, "is_native", True):
                        field_name = getattr(field, "field_name", k)
                        update_data[field_name] = v
                    else:
                        skipped_fields.append(k)
                else:
                    invalid_fields.append(k)

            if invalid_fields:
                raise ValidationError(
                    model=self.model,
                    reason="Invalid fields in update data",
                    details={"invalid_fields": invalid_fields, "skipped_fields": skipped_fields},
                )

            param_index = 1
            for field_name, value in update_data.items():
                if isinstance(value, Func):
                    expr_sql = value.as_sql(params)
                    set_clause.append(f"{field_name} = {expr_sql}")
                    param_index = len(params) + 1
                elif isinstance(value, Expression):
                    sub_params: list[Any] = []
                    expr_sql = value.as_sql(sub_params)
                    # Re-number params
                    for sp in sub_params:
                        params.append(sp)
                    set_clause.append(f"{field_name} = {expr_sql}")
                    param_index = len(params) + 1
                else:
                    set_clause.append(f"{field_name} = ${param_index}")
                    params.append(self._coerce_param(field_name, value))
                    param_index += 1

            if not set_clause:
                raise ValidationError(
                    model=self.model,
                    reason="No valid fields to update",
                    details={"skipped_fields": skipped_fields},
                )

            where_clause, where_params = self._extract_where_clause()
            # Renumber where params
            if where_clause:
                for i in range(len(where_params)):
                    where_clause = where_clause.replace(f"${i + 1}", f"${param_index + i}")

            sql = f"UPDATE {table} SET {', '.join(set_clause)}"
            if where_clause:
                sql += f" WHERE {where_clause}"
            params.extend(where_params)

            if debug:
                vcprint(sql, "Built SQL", verbose=debug, color="cyan")
                vcprint(params, "With params", verbose=debug, color="cyan")

            result = await self.db.execute_query(self.database, sql + " RETURNING *", *params)
            rows_affected = len(result)
            return {"rows_affected": rows_affected, "updated_rows": result}

        except (ValidationError, IntegrityError, DatabaseError):
            raise
        except Exception as e:
            raise QueryError(
                model=self.model,
                details={"operation": "update", "error": str(e)},
            )

    async def delete(self) -> int:
        """DELETE rows matching the WHERE clause."""
        table = self._full_query_dict["table"]
        where_clause, where_params = self._extract_where_clause()

        sql = f"DELETE FROM {table}"
        if where_clause:
            sql += f" WHERE {where_clause}"

        try:
            result = await self.db.execute_query(self.database, sql, *where_params)
            return len(result)
        except DatabaseError as e:
            raise DatabaseError(f"Delete failed: {str(e)}")

    # ------------------------------------------------------------------
    # SELECT terminal methods
    # ------------------------------------------------------------------

    async def all(self) -> list[Any]:
        """Fetch all matching rows as model instances."""
        results = await self._execute()
        if not results:
            return []
        select_related = self._full_query_dict.get("select_related", [])
        if select_related:
            return self._hydrate_with_select_related(results)
        return [self.model(**row) for row in results]

    async def first(self) -> Any:
        """Fetch the first matching row as a model instance."""
        self._full_query_dict["limit"] = 1
        self.query, self.params = self._build_query()
        results = await self._execute()
        if not results:
            return None
        select_related = self._full_query_dict.get("select_related", [])
        if select_related:
            instances = self._hydrate_with_select_related(results)
            return instances[0] if instances else None
        return self.model(**results[0])

    async def count(self) -> int:
        """COUNT(*) for the current WHERE clause."""
        table_name = self._full_query_dict["table"]
        where_clause, params = self._extract_where_clause()

        count_sql = f"SELECT COUNT(*) as count FROM {table_name}"
        if where_clause:
            count_sql += f" WHERE {where_clause}"

        try:
            result = await self.db.execute_query(self.database, count_sql, *params)
            return result[0]["count"] if result else 0
        except DatabaseError as e:
            raise DatabaseError(f"Count query failed: {str(e)}")

    async def exists(self) -> bool:
        """EXISTS check for the current WHERE clause."""
        self._full_query_dict["limit"] = 1
        self.query, self.params = self._build_query()
        results = await self._execute()
        return len(results) > 0

    async def aggregate(self) -> dict[str, Any]:
        """Execute the query and return the first row as a dict (for aggregation queries)."""
        results = await self._execute()
        if not results:
            return {}
        return dict(results[0])

    async def values(self) -> list[dict[str, Any]]:
        """Return results as a list of dicts."""
        results = await self._execute()
        if not results:
            return []
        return [dict(row) for row in results]

    async def values_list(self, flat: bool = False) -> list[tuple[Any, ...]] | list[Any]:
        """Return results as tuples (or a flat list when flat=True)."""
        results = await self._execute()
        if not results:
            return []

        if flat:
            select_fields = self._full_query_dict.get("select", ["*"])
            if select_fields == ["*"] or len(select_fields) != 1:
                raise ValueError("values_list with flat=True requires exactly one field to be selected")
            field_name = select_fields[0]
            return [row[field_name] for row in results]
        else:
            if self._full_query_dict.get("select") == ["*"]:
                return [tuple(row.values()) for row in results]
            select_fields = self._full_query_dict.get("select", [])
            return [tuple(row[f] for f in select_fields) for row in results]

    # ------------------------------------------------------------------
    # Async iteration
    # ------------------------------------------------------------------

    def __aiter__(self) -> QueryExecutor:
        self._iter_index = 0
        self._iter_results: list[Any] | None = None
        return self

    async def __anext__(self) -> Any:
        if self._iter_results is None:
            self._iter_results = await self._execute()
        if self._iter_index >= len(self._iter_results):
            raise StopAsyncIteration
        row = self._iter_results[self._iter_index]
        self._iter_index += 1
        return self.model(**row)
