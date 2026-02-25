# Relations TODOs

The following are some improvements that need to be made to the handling of relations. These notes need to be closely reviewed to ensure this inforation is fresh and still valid.

RULES:
- If you work on any part of this, you must update this document to make sure it remains fresh.
- If you are told to review this, ensure you create a direct and concise task lis in the document for better tracking.
- As parts of this are completed, remove the details of the taks and replace them with a concise note about the changes to reduce the bulk of information.
- When all of this is confirmed to be done, the document must be deleted, with the approval of the manager


## Harder Improvements to Consider Later

These are more architectural and would require new API surface or deeper changes:

### 1. Bulk Prefetch for Collections — the real N+1 fix

When you fetch a list of instances and then call `fetch_fk()` in a loop, you still get N+1 queries even with the concurrency improvements (they just fire in parallel rather than serially). The proper fix is a class-level batch loader:

```python
@classmethod
async def prefetch_related(cls, instances: list[Model], *relation_names: str) -> None:
    """Batch-load named relations across a collection in O(relations) queries."""
```

For FK relations: collect all unique FK values across all instances, issue a single `WHERE id = ANY($1)`, then distribute results back. This reduces N+1 to exactly 2 queries regardless of collection size — the same pattern Django's `prefetch_related()` uses.

### 2. DataLoader / Request-Scoped Batching

For deeply nested fetches (FK → FK → M2M), a DataLoader pattern groups all pending fetches within the same async tick into a single batched query. This is how GraphQL servers handle N+1. It would require a per-request context object to accumulate pending loads, which is a bigger architecture addition.

### 3. Joined IFK Loading

IFKs (inverse foreign keys) currently issue `WHERE parent_id = $1` per relation. When fetching IFKs for a collection of parents this is still N queries. The batch version would be:

```sql
SELECT * FROM child WHERE parent_id = ANY($1)
```

Then group results by `parent_id` in Python and distribute them to the right parent instance.

### 4. `select_related` Extended to IFKs and M2Ms

Currently `select_related()` on the `QueryBuilder` only supports FKs (one `LEFT JOIN` per FK). Extending it to IFKs would require a lateral join or subquery approach, and M2Ms would need a `LEFT JOIN` through the junction table with deduplication (array aggregation). Complex but eliminates extra queries at the queryset level.

### 5. Query Result Caching at the Relation Level

Right now `StateManager` caches model instances, but `fetch_fk()` still calls `related_model.get()` which hits the cache only if the FK target was previously fetched by PK. A relation-level cache key (e.g., `"Order.customer_id:uuid-123"`) would short-circuit the DB call entirely on repeated access to the same related object within a request lifetime.

### 6. Composite PK M2M Support

The M2M `fetch_related` now uses `primary_keys[0]`, which is correct for the vast majority of models. If you ever have M2M targets with composite PKs, the JOIN condition would need to match all PK columns. Worth noting as a known limitation rather than a current bug.