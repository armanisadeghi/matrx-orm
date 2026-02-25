# TASK: Relations Performance & Architecture Improvements

> **Location:** `src/matrx_orm/core/relations.py`
> **Priority:** `medium`
> **Impact:** `non-breaking`
> **Status:** `ready`
> **Created:** 2025-02-25
> **Updated:** 2025-02-25

## Summary

A collection of performance and architecture improvements to the relations system. These
address N+1 query patterns, cache inefficiencies, and missing API surface for batch
loading. All items are additive or internal — existing public APIs should remain unchanged.

## Context

The current relation system works correctly but has known performance gaps when used at
scale. Fetching related objects for a collection of instances still results in N+1 queries
(parallelized, but still N separate DB round-trips). There is no batch prefetch, no
request-scoped deduplication, and `select_related()` only covers FK joins — not IFKs
or M2Ms.

These improvements range from straightforward (bulk prefetch) to architectural (DataLoader
pattern). They are ordered roughly by impact-to-effort ratio.

## Task List

- [ ] **Bulk prefetch for collections** — Implement `prefetch_related(instances, *relations)` that collects unique FK values across all instances and issues a single `WHERE id = ANY($1)` query. Reduces N+1 to exactly 2 queries regardless of collection size.
- [ ] **Joined IFK loading** — IFKs currently issue `WHERE parent_id = $1` per relation. Batch version: `WHERE parent_id = ANY($1)`, then group results by `parent_id` in Python and distribute to parent instances.
- [ ] **Extend `select_related()` to IFKs and M2Ms** — Currently only supports FKs via `LEFT JOIN`. IFKs need a lateral join or subquery approach. M2Ms need a `LEFT JOIN` through the junction table with array aggregation for deduplication.
- [ ] **Relation-level cache keys** — `StateManager` caches model instances by PK, but `fetch_fk()` still hits the DB even if the target was previously fetched. Add relation-level cache keys (e.g., `"Order.customer_id:uuid-123"`) to short-circuit repeated access within a request lifetime.
- [ ] **DataLoader / request-scoped batching** — For deeply nested fetches (FK -> FK -> M2M), implement a DataLoader-style pattern that groups all pending fetches within the same async tick into a single batched query. Requires a per-request context object. Largest architectural change in this list.
- [ ] **Composite PK M2M support** — The M2M `fetch_related` currently uses `primary_keys[0]`. If M2M targets have composite PKs, the JOIN condition needs to match all PK columns. Currently a known limitation, not a bug.

## Risks & Considerations

- **Non-breaking by design:** All items either add new methods or change internal query
  strategies. Existing public APIs (`fetch_fk()`, `fetch_ifk()`, `select_related()`)
  should keep their signatures and behavior.
- **DataLoader is the biggest lift:** It requires a context object threaded through the
  async call stack, similar to what GraphQL servers do. Consider whether this complexity
  is justified by actual usage patterns before starting it.
- **`select_related()` for M2Ms** may produce large result sets with duplication before
  aggregation. Benchmark against the prefetch approach to decide which is actually faster
  for typical workloads.

## Proposed Solution

### Bulk Prefetch (highest priority)

```python
@classmethod
async def prefetch_related(cls, instances: list[Model], *relation_names: str) -> None:
    """Batch-load named relations across a collection in O(relations) queries."""
    for name in relation_names:
        fk_values = [getattr(inst, name) for inst in instances if getattr(inst, name)]
        unique_values = list(set(fk_values))
        related_map = await RelatedModel.filter(id__in=unique_values).as_dict("id")
        for inst in instances:
            val = getattr(inst, name)
            if val and val in related_map:
                inst.set_related(name, related_map[val])
```

The same collector pattern applies to IFK batching — collect parent IDs, single query
with `ANY($1)`, group-by-parent in Python.

### Relation-Level Caching

Add a cache key format to `StateManager`:

```
{ModelName}.{field_name}:{fk_value} → cached related instance
```

Check this key inside `fetch_fk()` before issuing any query. Invalidate on writes to
the related model.

---

<!--
LIFECYCLE RULES (do not remove this block — it governs how this file is maintained):

1. CREATION: Copy this template. Fill in the metadata block and Summary. Register the
   task in TASKS.md. Everything else can be filled incrementally.

2. UPDATES: Anyone working on this task MUST update the metadata block (Status, Updated
   date) and check off completed items. Keep the document an accurate snapshot.

3. COMPLETION: When every item is checked and confirmed working, set Status to `done`,
   add a one-line completion note at the top of the Task List, and notify the project
   lead. The project lead decides whether to archive or delete the file.

4. STALENESS: If you review this and find information that is outdated, fix it immediately
   or add a warning note at the top: "> **STALE:** [what is outdated and why]"
-->
