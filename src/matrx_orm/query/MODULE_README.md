# `src.matrx_orm.query` — Module Overview

> This document is partially auto-generated. Sections tagged `<!-- AUTO:id -->` are refreshed by the generator.
> Everything else is yours to edit freely and will never be overwritten.

<!-- AUTO:meta -->
## About This Document

This file is **partially auto-generated**. Sections wrapped in `<!-- AUTO:id -->` tags
are overwritten each time the generator runs. Everything else is yours to edit freely.

| Field | Value |
|-------|-------|
| Module | `src/matrx_orm/query` |
| Last generated | 2026-02-28 13:59 |
| Output file | `src/matrx_orm/query/MODULE_README.md` |
| Signature mode | `signatures` |

**To refresh auto-sections:**
```bash
python utils/code_context/generate_module_readme.py src/matrx_orm/query --mode signatures
```

**To add permanent notes:** Write anywhere outside the `<!-- AUTO:... -->` blocks.
<!-- /AUTO:meta -->

<!-- HUMAN-EDITABLE: This section is yours. Agents & Humans can edit this section freely — it will not be overwritten. -->

## Architecture

> **Fill this in.** Describe the execution flow and layer map for this module.
> See `utils/code_context/MODULE_README_SPEC.md` for the recommended format.
>
> Suggested structure:
>
> ### Layers
> | File | Role |
> |------|------|
> | `entry.py` | Public entry point — receives requests, returns results |
> | `engine.py` | Core dispatch logic |
> | `models.py` | Shared data types |
>
> ### Call Flow (happy path)
> ```
> entry_function() → engine.dispatch() → implementation()
> ```


<!-- AUTO:tree -->
## Directory Tree

> Auto-generated. 3 files across 1 directories.

```
src/matrx_orm/query/
├── __init__.py
├── builder.py
├── executor.py
```
<!-- /AUTO:tree -->

<!-- AUTO:signatures -->
## API Signatures

> Auto-generated via `output_mode="signatures"`. ~5-10% token cost vs full source.
> For full source, open the individual files directly.

```
---
Filepath: src/matrx_orm/query/__init__.py  [python]



---
Filepath: src/matrx_orm/query/executor.py  [python]

  class QueryExecutor:
      def __init__(self, query: dict[str, Any]) -> None
      def _parse_lookup(cls, key: str) -> tuple[str, str]
      def _build_condition(field: str, operator: str, value: Any, param_idx: int) -> tuple[str, Any]
      def _build_query(self) -> tuple[str, list[Any]]
      def _resolve_fk_field(self, field_name: str) -> str
      def _build_condition_with_expr(self, field_name: str, operator: str, value: Any, params: list[Any]) -> tuple[str, Any]
      def _render_q(self, q: Any, params: list[Any]) -> str
      def _coerce_param(self, field_name: str, value: Any) -> Any
      def _extract_where_clause(self) -> tuple[str, list[Any]]
      async def _execute(self) -> list[dict[str, Any]]
      def _hydrate_with_select_related(self, rows: list[dict[str, Any]]) -> list[Any]
      async def insert(self, query: dict[str, Any]) -> dict[str, Any]
      async def bulk_insert(self, query: dict[str, Any]) -> list[Model]
      async def upsert(self, query: dict[str, Any]) -> dict[str, Any]
      async def bulk_upsert(self, query: dict[str, Any]) -> list[Model]
      async def update(self, **kwargs: Any) -> UpdateResult
      async def delete(self) -> int
      async def all(self) -> list[Any]
      async def first(self) -> Any
      async def count(self) -> int
      async def exists(self) -> bool
      async def aggregate(self) -> AggregateResult
      async def values(self) -> list[dict[str, Any]]
      async def values_list(self, flat: bool = False) -> list[tuple[Any, ...]] | list[Any]
      def __aiter__(self) -> QueryExecutor
      async def __anext__(self) -> Any


---
Filepath: src/matrx_orm/query/builder.py  [python]

  ModelT = TypeVar('ModelT', bound='Model')
  class QueryBuilder(Generic[ModelT]):
      def __init__(self, model_cls: type[ModelT], database: str | None = None) -> None
      def _set_database(self, model_cls: type[ModelT]) -> str
      def filter(self, *args: Any, **kwargs: Any) -> QueryBuilder[ModelT]
      def exclude(self, **kwargs: Any) -> QueryBuilder[ModelT]
      def order_by(self, *fields: str | Any) -> QueryBuilder[ModelT]
      def limit(self, value: int) -> QueryBuilder[ModelT]
      def offset(self, value: int) -> QueryBuilder[ModelT]
      def select(self, *fields: str) -> QueryBuilder[ModelT]
      def prefetch_related(self, *fields: str) -> QueryBuilder[ModelT]
      def select_related(self, *fields: str) -> QueryBuilder[ModelT]
      def join(self, model_cls: type[Any], on: str, join_type: str = 'INNER') -> QueryBuilder[ModelT]
      def group_by(self, *fields: str) -> QueryBuilder[ModelT]
      def having(self, **kwargs: Any) -> QueryBuilder[ModelT]
      def annotate(self, **kwargs: Any) -> QueryBuilder[ModelT]
      def distinct(self, *fields: str) -> QueryBuilder[ModelT]
      def select_for_update(self, nowait: bool = False, skip_locked: bool = False, of: list[str] | None = None) -> QueryBuilder[ModelT]
      def using(self, database: str) -> QueryBuilder[ModelT]
      def only(self, *fields: str) -> QueryBuilder[ModelT]
      def defer(self, *fields: str) -> QueryBuilder[ModelT]
      def with_cte(self, *ctes: Any) -> QueryBuilder[ModelT]
      def nearest(self, column: str, vector: list[float], metric: str = 'cosine', null_guard: bool = True) -> QueryBuilder[ModelT]
      def reverse(self) -> QueryBuilder[ModelT]
      def _build_query(self) -> dict[str, Any]
      def _effective_select(self) -> list[str]
      def _collect_filters(self) -> list[Any]
      def _merge_filters_excludes(self) -> dict[str, Any]
      def _merge_having(self) -> dict[str, Any]
      def _get_executor(self) -> QueryExecutor
      async def all(self) -> list[ModelT]
      async def first(self) -> ModelT | None
      async def last(self) -> ModelT | None
      async def get(self) -> ModelT
      async def get_or_none(self) -> ModelT | None
      async def update(self, **kwargs: Any) -> UpdateResult
      async def delete(self) -> int
      async def count(self) -> int
      async def exists(self) -> bool
      async def aggregate(self, **kwargs: Any) -> AggregateResult
      async def values(self, *fields: str) -> list[dict[str, Any]]
      async def values_list(self, *fields: str, flat: bool = False) -> list[tuple[Any, ...]] | list[Any]
      def values_sync(self, *fields: str) -> list[dict[str, Any]]
      def values_list_sync(self, *fields: str, flat: bool = False) -> list[tuple[Any, ...]] | list[Any]
      async def __aiter__(self) -> Any
      def __getitem__(self, k: slice) -> QueryBuilder[ModelT]
```
<!-- /AUTO:signatures -->

<!-- AUTO:call_graph -->
## Call Graph

> Auto-generated. All Python files
> Excluded from call graph: `tests`.
> Shows which functions call which. `async` prefix = caller is an async function.
> Method calls shown as `receiver.method()`. Private methods (`_`) excluded by default.

### Call graph: src.matrx_orm.query.executor

```
Global Scope → src.matrx_orm.query.executor.object() (line 21)
  src.matrx_orm.query.executor.__init__ → src.matrx_orm.query.executor.QueryError() (line 36)
  src.matrx_orm.query.executor.__init__ → query.keys() (line 38)
  src.matrx_orm.query.executor.__init__ → src.matrx_orm.query.executor.AsyncDatabaseManager() (line 42)
  src.matrx_orm.query.executor._parse_lookup → key.rsplit('__', 1) (line 63)
  src.matrx_orm.query.executor._build_condition → json.dumps(value) (line 126)
  src.matrx_orm.query.executor._build_condition → json.dumps(value) (line 130)
  src.matrx_orm.query.executor._build_condition → join((str(p) for p in value)) (line 135)
  src.matrx_orm.query.executor._build_query → ...get('ctes', []) (line 150)
  src.matrx_orm.query.executor._build_query → c.as_sql(params) (line 154)
  src.matrx_orm.query.executor._build_query → join(cte_sqls) (line 156)
  src.matrx_orm.query.executor._build_query → ...get('aggregations', []) (line 159)
  src.matrx_orm.query.executor._build_query → ...get('select_related', []) (line 160)
  src.matrx_orm.query.executor._build_query → ...get('select', ['*']) (line 161)
  src.matrx_orm.query.executor._build_query → ...get(fk_field) (line 169)
  src.matrx_orm.query.executor._build_query → join_clauses.append(f'LEFT JOIN {related_table} AS {alias} ON {table}.{fk_ref.column_name} = {alias}.{fk_ref.to_column}') (line 175)
  src.matrx_orm.query.executor._build_query → select_parts.append(f'{alias}.{col} AS __fk_{fk_field}__{col}') (line 182)
  src.matrx_orm.query.executor._build_query → select_parts.insert(0, f'{table}.*') (line 188)
  src.matrx_orm.query.executor._build_query → select_parts.insert(0, '*') (line 190)
  src.matrx_orm.query.executor._build_query → select_parts.insert(0, f) (line 193)
  src.matrx_orm.query.executor._build_query → func.as_sql(params) (line 200)
  src.matrx_orm.query.executor._build_query → select_parts.append(f'{expr} AS {name}') (line 203)
  src.matrx_orm.query.executor._build_query → ...get('vector_order') (line 206)
  src.matrx_orm.query.executor._build_query → src.matrx_orm.query.executor.VectorDistance() (line 210)
  src.matrx_orm.query.executor._build_query → vd.as_sql(params) (line 215)
  src.matrx_orm.query.executor._build_query → select_parts.append(f'{_vector_distance_sql} AS _vector_distance') (line 216)
  src.matrx_orm.query.executor._build_query → ...get('distinct') (line 219)
  src.matrx_orm.query.executor._build_query → join(distinct) (line 225)
  src.matrx_orm.query.executor._build_query → join(select_parts) (line 227)
  src.matrx_orm.query.executor._build_query → join(join_clauses) (line 232)
  src.matrx_orm.query.executor._build_query → ...get('filters', []) (line 235)
  src.matrx_orm.query.executor._build_query → ...get('vector_null_guard', True) (line 239)
  src.matrx_orm.query.executor._build_query → where_conditions.append(f"{vector_order['column']} IS NOT NULL") (line 240)
  src.matrx_orm.query.executor._build_query → where_conditions.append(cond) (line 247)
  src.matrx_orm.query.executor._build_query → item.items() (line 249)
  src.matrx_orm.query.executor._build_query → where_conditions.append(cond_sql) (line 254)
  src.matrx_orm.query.executor._build_query → where_conditions.append(item.as_sql(table, params)) (line 259)
  src.matrx_orm.query.executor._build_query → item.as_sql(table, params) (line 259)
  src.matrx_orm.query.executor._build_query → join(where_conditions) (line 262)
  src.matrx_orm.query.executor._build_query → ...get('group_by', []) (line 265)
  src.matrx_orm.query.executor._build_query → join(group_by) (line 267)
  src.matrx_orm.query.executor._build_query → ...get('having', {}) (line 270)
  src.matrx_orm.query.executor._build_query → having.items() (line 273)
  src.matrx_orm.query.executor._build_query → having_conditions.append(cond_sql) (line 276)
  src.matrx_orm.query.executor._build_query → params.extend(param) (line 279)
  src.matrx_orm.query.executor._build_query → params.append(param) (line 281)
  src.matrx_orm.query.executor._build_query → join(having_conditions) (line 283)
  src.matrx_orm.query.executor._build_query → ...get('order_by', []) (line 286)
  src.matrx_orm.query.executor._build_query → order_by_terms.append('_vector_distance ASC') (line 294)
  src.matrx_orm.query.executor._build_query → term.startswith('-') (line 299)
  src.matrx_orm.query.executor._build_query → order_by_terms.append(f'{term[1:]} DESC') (line 300)
  src.matrx_orm.query.executor._build_query → order_by_terms.append(f'{term} ASC') (line 302)
  src.matrx_orm.query.executor._build_query → ...items() (line 306)
  src.matrx_orm.query.executor._build_query → order_by_terms.append(f'{fname} {direction}') (line 313)
  src.matrx_orm.query.executor._build_query → join(order_by_terms) (line 318)
  src.matrx_orm.query.executor._build_query → ...get('limit') (line 321)
  src.matrx_orm.query.executor._build_query → params.append(self._full_query_dict['limit']) (line 323)
  src.matrx_orm.query.executor._build_query → ...get('offset') (line 325)
  src.matrx_orm.query.executor._build_query → params.append(self._full_query_dict['offset']) (line 327)
  src.matrx_orm.query.executor._build_query → ...get('for_update') (line 330)
  src.matrx_orm.query.executor._build_query → for_update.get('nowait') (line 333)
  src.matrx_orm.query.executor._build_query → for_update.get('skip_locked') (line 335)
  src.matrx_orm.query.executor._build_query → for_update.get('of', []) (line 337)
  src.matrx_orm.query.executor._build_query → join(of_tables) (line 339)
  src.matrx_orm.query.executor._build_condition_with_expr → value.as_sql(params) (line 363)
  src.matrx_orm.query.executor._build_condition_with_expr → value.as_sql(table, params) (line 367)
  src.matrx_orm.query.executor._build_condition_with_expr → value.as_sql(table, params) (line 371)
  src.matrx_orm.query.executor._build_condition_with_expr → params.extend(param) (line 381)
  src.matrx_orm.query.executor._build_condition_with_expr → params.append(param) (line 383)
  src.matrx_orm.query.executor._render_q → ...items() (line 391)
  src.matrx_orm.query.executor._render_q → conditions.append(cond) (line 396)
  src.matrx_orm.query.executor._render_q → join(conditions) (line 397)
  src.matrx_orm.query.executor._render_q → joiner.join(child_sqls) (line 407)
  src.matrx_orm.query.executor._coerce_param → ...get(field_name) (line 419)
  src.matrx_orm.query.executor._coerce_param → field.get_db_prep_value(value) (line 421)
  src.matrx_orm.query.executor._extract_where_clause → strip() (line 429)
  src.matrx_orm.query.executor._extract_where_clause → base_query.split('WHERE', 1) (line 429)
  src.matrx_orm.query.executor._extract_where_clause → strip() (line 433)
  src.matrx_orm.query.executor._extract_where_clause → after_where.split(stopper) (line 433)
  async src.matrx_orm.query.executor._execute → ...execute_query(self.database, self.query, *self.params) (line 441)
  async src.matrx_orm.query.executor._execute → e.enrich() (line 444)
  async src.matrx_orm.query.executor._execute → src.matrx_orm.query.executor.QueryError() (line 447)
  src.matrx_orm.query.executor._hydrate_with_select_related → ...get('select_related', []) (line 454)
  src.matrx_orm.query.executor._hydrate_with_select_related → row.items() (line 461)
  src.matrx_orm.query.executor._hydrate_with_select_related → key.startswith(prefix) (line 465)
  src.matrx_orm.query.executor._hydrate_with_select_related → self.model() (line 473)
  src.matrx_orm.query.executor._hydrate_with_select_related → related_data.items() (line 476)
  src.matrx_orm.query.executor._hydrate_with_select_related → ...get(fk_field) (line 477)
  src.matrx_orm.query.executor._hydrate_with_select_related → fk_row.values() (line 478)
  src.matrx_orm.query.executor._hydrate_with_select_related → fk_ref.related_model() (line 479)
  src.matrx_orm.query.executor._hydrate_with_select_related → instance.set_related(fk_field, related_instance) (line 480)
  src.matrx_orm.query.executor._hydrate_with_select_related → instances.append(instance) (line 482)
  async src.matrx_orm.query.executor.insert → query.get('data', {}) (line 492)
  async src.matrx_orm.query.executor.insert → src.matrx_orm.query.executor.ValidationError() (line 495)
  async src.matrx_orm.query.executor.insert → data.keys() (line 497)
  async src.matrx_orm.query.executor.insert → data.values() (line 498)
  async src.matrx_orm.query.executor.insert → join(columns) (line 501)
  async src.matrx_orm.query.executor.insert → join(placeholders) (line 502)
  async src.matrx_orm.query.executor.insert → ...execute_query(self.database, sql, *values) (line 507)
  async src.matrx_orm.query.executor.insert → src.matrx_orm.query.executor.ValidationError() (line 509)
  async src.matrx_orm.query.executor.insert → lower() (line 512)
  async src.matrx_orm.query.executor.insert → src.matrx_orm.query.executor.IntegrityError() (line 513)
  async src.matrx_orm.query.executor.insert → src.matrx_orm.query.executor.DatabaseError(str(e)) (line 514)
  async src.matrx_orm.query.executor.bulk_insert → query.get('data', []) (line 519)
  async src.matrx_orm.query.executor.bulk_insert → src.matrx_orm.query.executor.ValidationError() (line 525)
  async src.matrx_orm.query.executor.bulk_insert → keys() (line 532)
  async src.matrx_orm.query.executor.bulk_insert → src.matrx_orm.query.executor.ValidationError() (line 534)
  async src.matrx_orm.query.executor.bulk_insert → row_data.keys() (line 545)
  async src.matrx_orm.query.executor.bulk_insert → src.matrx_orm.query.executor.ValidationError() (line 546)
  async src.matrx_orm.query.executor.bulk_insert → row_data.keys() (line 551)
  async src.matrx_orm.query.executor.bulk_insert → row_phs.append(f'${param_index}') (line 556)
  async src.matrx_orm.query.executor.bulk_insert → all_values.append(row_data[col]) (line 557)
  async src.matrx_orm.query.executor.bulk_insert → placeholders_list.append(f"({', '.join(row_phs)})") (line 559)
  async src.matrx_orm.query.executor.bulk_insert → join(row_phs) (line 559)
  async src.matrx_orm.query.executor.bulk_insert → join(columns) (line 562)
  async src.matrx_orm.query.executor.bulk_insert → join(placeholders_list) (line 563)
  async src.matrx_orm.query.executor.bulk_insert → ...execute_query(self.database, sql, *all_values) (line 568)
  async src.matrx_orm.query.executor.bulk_insert → self.model() (line 569)
  async src.matrx_orm.query.executor.bulk_insert → lower() (line 571)
  async src.matrx_orm.query.executor.bulk_insert → src.matrx_orm.query.executor.IntegrityError() (line 572)
  async src.matrx_orm.query.executor.bulk_insert → src.matrx_orm.query.executor.DatabaseError() (line 573)
  async src.matrx_orm.query.executor.bulk_insert → src.matrx_orm.query.executor.QueryError() (line 578)
  async src.matrx_orm.query.executor.upsert → query.get('data', {}) (line 586)
  async src.matrx_orm.query.executor.upsert → query.get('conflict_fields', []) (line 587)
  async src.matrx_orm.query.executor.upsert → query.get('update_fields') (line 588)
  async src.matrx_orm.query.executor.upsert → src.matrx_orm.query.executor.ValidationError() (line 591)
  async src.matrx_orm.query.executor.upsert → src.matrx_orm.query.executor.ValidationError() (line 593)
  async src.matrx_orm.query.executor.upsert → data.keys() (line 595)
  async src.matrx_orm.query.executor.upsert → data.values() (line 596)
  async src.matrx_orm.query.executor.upsert → src.matrx_orm.query.executor.ValidationError() (line 600)
  async src.matrx_orm.query.executor.upsert → join((f'{f} = EXCLUDED.{f}' for f in fields_to_update)) (line 602)
  async src.matrx_orm.query.executor.upsert → join(columns) (line 604)
  async src.matrx_orm.query.executor.upsert → join(placeholders) (line 605)
  async src.matrx_orm.query.executor.upsert → join(conflict_fields) (line 606)
  async src.matrx_orm.query.executor.upsert → ...execute_query(self.database, sql, *values) (line 611)
  async src.matrx_orm.query.executor.upsert → src.matrx_orm.query.executor.ValidationError() (line 613)
  async src.matrx_orm.query.executor.upsert → lower() (line 616)
  async src.matrx_orm.query.executor.upsert → src.matrx_orm.query.executor.IntegrityError() (line 617)
  async src.matrx_orm.query.executor.upsert → src.matrx_orm.query.executor.DatabaseError() (line 618)
  async src.matrx_orm.query.executor.bulk_upsert → query.get('data', []) (line 626)
  async src.matrx_orm.query.executor.bulk_upsert → query.get('conflict_fields', []) (line 627)
  async src.matrx_orm.query.executor.bulk_upsert → query.get('update_fields') (line 628)
  async src.matrx_orm.query.executor.bulk_upsert → src.matrx_orm.query.executor.ValidationError() (line 633)
  async src.matrx_orm.query.executor.bulk_upsert → keys() (line 635)
  async src.matrx_orm.query.executor.bulk_upsert → src.matrx_orm.query.executor.ValidationError() (line 638)
  async src.matrx_orm.query.executor.bulk_upsert → row_data.keys() (line 645)
  async src.matrx_orm.query.executor.bulk_upsert → src.matrx_orm.query.executor.ValidationError() (line 646)
  async src.matrx_orm.query.executor.bulk_upsert → row_data.keys() (line 649)
  async src.matrx_orm.query.executor.bulk_upsert → row_phs.append(f'${param_index}') (line 653)
  async src.matrx_orm.query.executor.bulk_upsert → all_values.append(row_data[col]) (line 654)
  async src.matrx_orm.query.executor.bulk_upsert → placeholders_list.append(f"({', '.join(row_phs)})") (line 656)
  async src.matrx_orm.query.executor.bulk_upsert → join(row_phs) (line 656)
  async src.matrx_orm.query.executor.bulk_upsert → join((f'{f} = EXCLUDED.{f}' for f in fields_to_update)) (line 658)
  async src.matrx_orm.query.executor.bulk_upsert → join(columns) (line 660)
  async src.matrx_orm.query.executor.bulk_upsert → join(placeholders_list) (line 661)
  async src.matrx_orm.query.executor.bulk_upsert → join(conflict_fields) (line 662)
  async src.matrx_orm.query.executor.bulk_upsert → ...execute_query(self.database, sql, *all_values) (line 667)
  async src.matrx_orm.query.executor.bulk_upsert → self.model() (line 668)
  async src.matrx_orm.query.executor.bulk_upsert → lower() (line 670)
  async src.matrx_orm.query.executor.bulk_upsert → src.matrx_orm.query.executor.IntegrityError() (line 671)
  async src.matrx_orm.query.executor.bulk_upsert → src.matrx_orm.query.executor.DatabaseError() (line 672)
  async src.matrx_orm.query.executor.bulk_upsert → src.matrx_orm.query.executor.QueryError() (line 677)
  async src.matrx_orm.query.executor.update → src.matrx_orm.query.executor.ValidationError() (line 686)
  async src.matrx_orm.query.executor.update → kwargs.items() (line 697)
  async src.matrx_orm.query.executor.update → skipped_fields.append(k) (line 704)
  async src.matrx_orm.query.executor.update → invalid_fields.append(k) (line 706)
  async src.matrx_orm.query.executor.update → src.matrx_orm.query.executor.ValidationError() (line 709)
  async src.matrx_orm.query.executor.update → update_data.items() (line 716)
  async src.matrx_orm.query.executor.update → value.as_sql(params) (line 718)
  async src.matrx_orm.query.executor.update → set_clause.append(f'{field_name} = {expr_sql}') (line 719)
  async src.matrx_orm.query.executor.update → value.as_sql(sub_params) (line 723)
  async src.matrx_orm.query.executor.update → params.append(sp) (line 725)
  async src.matrx_orm.query.executor.update → set_clause.append(f'{field_name} = {expr_sql}') (line 726)
  async src.matrx_orm.query.executor.update → set_clause.append(f'{field_name} = ${param_index}') (line 729)
  async src.matrx_orm.query.executor.update → params.append(self._coerce_param(field_name, value)) (line 730)
  async src.matrx_orm.query.executor.update → src.matrx_orm.query.executor.ValidationError() (line 734)
  async src.matrx_orm.query.executor.update → where_clause.replace(f'${i + 1}', f'${param_index + i}') (line 743)
  async src.matrx_orm.query.executor.update → join(set_clause) (line 745)
  async src.matrx_orm.query.executor.update → params.extend(where_params) (line 748)
  async src.matrx_orm.query.executor.update → ...execute_query(self.database, sql + ' RETURNING *', *params) (line 754)
  async src.matrx_orm.query.executor.update → src.matrx_orm.query.executor.UpdateResult() (line 755)
  async src.matrx_orm.query.executor.update → src.matrx_orm.query.executor.QueryError() (line 760)
  async src.matrx_orm.query.executor.delete → ...execute_query(self.database, sql, *where_params) (line 775)
  async src.matrx_orm.query.executor.delete → src.matrx_orm.query.executor.DatabaseError(f'Delete failed: {str(e)}') (line 778)
  async src.matrx_orm.query.executor.all → ...get('select_related', []) (line 789)
  async src.matrx_orm.query.executor.all → self.model() (line 792)
  async src.matrx_orm.query.executor.first → ...get('select_related', []) (line 801)
  async src.matrx_orm.query.executor.first → self.model() (line 805)
  async src.matrx_orm.query.executor.count → ...execute_query(self.database, count_sql, *params) (line 817)
  async src.matrx_orm.query.executor.count → src.matrx_orm.query.executor.DatabaseError(f'Count query failed: {str(e)}') (line 820)
  async src.matrx_orm.query.executor.values_list → ...get('select', ['*']) (line 850)
  async src.matrx_orm.query.executor.values_list → ...get('select') (line 856)
  async src.matrx_orm.query.executor.values_list → row.values() (line 857)
  async src.matrx_orm.query.executor.values_list → ...get('select', []) (line 858)
  async src.matrx_orm.query.executor.__anext__ → self.model() (line 877)
```

### Call graph: src.matrx_orm.query.builder

```
Global Scope → src.matrx_orm.query.builder.TypeVar('ModelT') (line 22)
  src.matrx_orm.query.builder.filter → ...append(arg) (line 95)
  src.matrx_orm.query.builder.filter → ...append(kwargs) (line 99)
  src.matrx_orm.query.builder.exclude → ...append(kwargs) (line 105)
  src.matrx_orm.query.builder.order_by → ...extend(fields) (line 109)
  src.matrx_orm.query.builder.select → ...extend(fields) (line 121)
  src.matrx_orm.query.builder.prefetch_related → ...extend(fields) (line 125)
  src.matrx_orm.query.builder.select_related → ...extend(fields) (line 130)
  src.matrx_orm.query.builder.join → ...append({'model': model_cls, 'on': on, 'type': join_type}) (line 134)
  src.matrx_orm.query.builder.group_by → ...extend(fields) (line 138)
  src.matrx_orm.query.builder.having → ...append(kwargs) (line 142)
  src.matrx_orm.query.builder.annotate → kwargs.items() (line 152)
  src.matrx_orm.query.builder.annotate → ...append({'name': key, 'function': value}) (line 153)
  src.matrx_orm.query.builder.with_cte → ...extend(ctes) (line 223)
  src.matrx_orm.query.builder.reverse → reversed_fields.append(term[1:] if term.startswith('-') else f'-{term}') (line 270)
  src.matrx_orm.query.builder.reverse → term.startswith('-') (line 270)
  src.matrx_orm.query.builder.reverse → reversed_fields.append(term) (line 272)
  src.matrx_orm.query.builder._effective_select → ...keys() (line 313)
  src.matrx_orm.query.builder._collect_filters → result.append(f) (line 322)
  src.matrx_orm.query.builder._collect_filters → result.append(~Q(**e)) (line 325)
  src.matrx_orm.query.builder._collect_filters → src.matrx_orm.query.builder.Q() (line 325)
  src.matrx_orm.query.builder._merge_filters_excludes → combined.update(f) (line 333)
  src.matrx_orm.query.builder._merge_filters_excludes → e.items() (line 335)
  src.matrx_orm.query.builder._merge_having → combined.update(h) (line 342)
  src.matrx_orm.query.builder._get_executor → src.matrx_orm.query.builder.QueryExecutor(self._build_query()) (line 346)
  async src.matrx_orm.query.builder.all → StateManager.cache_bulk(self.model, results) (line 357)
  async src.matrx_orm.query.builder.all → e.enrich() (line 365)
  async src.matrx_orm.query.builder.all → src.matrx_orm.query.builder.QueryError() (line 368)
  async src.matrx_orm.query.builder.first → first() (line 373)
  async src.matrx_orm.query.builder.first → e.enrich() (line 375)
  async src.matrx_orm.query.builder.last → self.order_by(f'-{pk_name}') (line 381)
  async src.matrx_orm.query.builder.last → self.first() (line 382)
  async src.matrx_orm.query.builder.get → src.matrx_orm.query.builder.DoesNotExist() (line 391)
  async src.matrx_orm.query.builder.get → src.matrx_orm.query.builder.MultipleObjectsReturned() (line 393)
  async src.matrx_orm.query.builder.get → e.enrich() (line 396)
  async src.matrx_orm.query.builder.get_or_none → self.get() (line 402)
  async src.matrx_orm.query.builder.update → src.matrx_orm.query.builder.ValidationError() (line 413)
  async src.matrx_orm.query.builder.update → update() (line 414)
  async src.matrx_orm.query.builder.update → e.enrich() (line 418)
  async src.matrx_orm.query.builder.delete → delete() (line 424)
  async src.matrx_orm.query.builder.delete → e.enrich() (line 426)
  async src.matrx_orm.query.builder.count → count() (line 432)
  async src.matrx_orm.query.builder.count → e.enrich() (line 434)
  async src.matrx_orm.query.builder.exists → exists() (line 440)
  async src.matrx_orm.query.builder.exists → e.enrich() (line 442)
  async src.matrx_orm.query.builder.aggregate → kwargs.items() (line 455)
  async src.matrx_orm.query.builder.aggregate → ...append({'name': key, 'function': value}) (line 456)
  async src.matrx_orm.query.builder.aggregate → aggregate() (line 458)
  async src.matrx_orm.query.builder.aggregate → e.enrich() (line 460)
  async src.matrx_orm.query.builder.values → values() (line 466)
  async src.matrx_orm.query.builder.values_list → values_list() (line 471)
  src.matrx_orm.query.builder.values_sync → asyncio.get_running_loop() (line 480)
  src.matrx_orm.query.builder.values_sync → src.matrx_orm.query.builder.run_sync(self.values(*fields)) (line 485)
  src.matrx_orm.query.builder.values_sync → self.values(*fields) (line 485)
  src.matrx_orm.query.builder.values_list_sync → asyncio.get_running_loop() (line 490)
  src.matrx_orm.query.builder.values_list_sync → src.matrx_orm.query.builder.run_sync(self.values_list(*fields, flat=flat)) (line 495)
  src.matrx_orm.query.builder.values_list_sync → self.values_list(*fields) (line 495)
  src.matrx_orm.query.builder.__getitem__ → self.limit(stop - start) (line 511)
  src.matrx_orm.query.builder.__getitem__ → self.offset(start) (line 512)
```
<!-- /AUTO:call_graph -->

<!-- AUTO:dependencies -->
## Dependencies

**External packages:** matrx_orm, matrx_utils
<!-- /AUTO:dependencies -->

<!-- AUTO:config -->
## Generation Config

> Auto-managed. Contains the exact parameters used to generate this README.
> Used by parent modules to auto-refresh this file when it is stale.
> Do not edit manually — changes will be overwritten on the next run.

```json
{
  "subdirectory": "src/matrx_orm/query",
  "mode": "signatures",
  "scope": null,
  "project_noise": null,
  "include_call_graph": true,
  "entry_points": null,
  "call_graph_exclude": [
    "tests"
  ]
}
```
<!-- /AUTO:config -->
