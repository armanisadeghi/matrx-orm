# TASK: Extended Base Class — Eliminate Tuple-Returning Relation Methods

> **Location:** `src/matrx_orm/core/extended.py`
> **Priority:** `high`
> **Impact:** `breaking`
> **Status:** `ready`
> **Created:** 2025-02-25
> **Updated:** 2025-02-25

## Summary

Refactor all tuple-returning relationship methods in the extended base class to return
only the model instance. Relationship data is already attached via `set_related()` /
`_dynamic_data`, making the tuple a redundant second source of truth. This is a breaking
change — all downstream call sites that destructure tuples will need updating.

## Context

There are two patterns in use today for returning relationship data:

**Pattern A — Tuples (the problem).** Methods like `get_item_with_related()` return
`tuple[item, related]`. The caller destructures the tuple to get the related object,
even though that same object is already attached to the item via `set_related()`.

```python
item, related = await manager.get_item_with_related(order_id, "customer_id")
# 'related' is redundant — item.get_related("customer_id") returns the same thing
```

**Pattern B — Item-only (the target).** Methods like `get_items_with_related()` return
just the model instances, with relationship data already populated via `set_related()`.

```python
items = await manager.get_items_with_related("customer_id")
for item in items:
    customer = item.get_related("customer_id")
```

The tuple pattern creates confusion, inconsistency, and leaky abstractions (e.g.,
`get_item_with_all_related()` exposes internal dict structure with `"foreign_keys"`,
`"inverse_foreign_keys"`, `"many_to_many"` keys).

## Task List

- [ ] Audit all tuple-returning methods and confirm `set_related()` coverage for each
- [ ] Refactor each method to return `ModelT | None` instead of a tuple:
    - [ ] `get_item_with_related()` — `tuple[item, related]` → `ModelT | None`
    - [ ] `get_item_with_related_with_retry()` — `tuple[item, related]` → `ModelT | None`
    - [ ] `get_item_with_all_related()` — `tuple[item, dict]` → `ModelT | None`
    - [ ] `get_item_with_m2m()` — `tuple[item, list]` → `ModelT | None`
    - [ ] `get_active_item_with_fk()` — `tuple[item, related]` → `ModelT | None`
    - [ ] `get_item_through_fk()` — `tuple[item, fk, target]` → `ModelT | None`
    - [ ] `get_active_item_with_through_fk()` — `tuple[item, fk, target]` → `ModelT | None`
    - [ ] `get_active_item_through_ifk()` — `tuple[item, ifk, target]` → `ModelT | None`
- [ ] Ensure multi-hop methods (`get_item_through_fk`) chain `set_related()` so intermediate objects are reachable via `item.get_related("first").get_related("second")`
- [ ] Update all type annotations and docstrings
- [ ] Search the full project for tuple destructuring of these methods and update call sites
- [ ] Create a migration helper script that scans user code for tuple-destructuring patterns and reports affected lines (may be complicated by manager subclasses)
- [ ] Run full test suite and fix any regressions

## Risks & Considerations

- **Breaking changes:** Every call site that destructures these methods will break. This
  is the main cost. A project-wide search is mandatory before merging.
- **Migration path:** The migration script should be built *before* the refactor ships,
  so users can run it against their codebases to get a concrete list of lines to update.
- **Multi-hop methods:** `get_item_through_fk()` is the trickiest — the intermediate
  `fk_instance` is sometimes the point of the call. Verify that chaining `get_related()`
  through the item provides equivalent access.
- **Manager subclasses:** Generated manager classes may override or extend these methods.
  The migration script needs to account for this.

## Proposed Solution

Unify on the item-only return pattern. After refactor, every relationship method returns
the item (or `None` / list of items), with all fetched relationship data accessible via
`get_related()`:

```python
item = await manager.get_item_with_related(order_id, "customer_id")
item.get_related("customer_id")

item = await manager.get_item_with_all_related(order_id)
item.get_related("tags")

items = await manager.get_items_with_all_related()
for item in items:
    item.get_related("customer_id")
```

| Method | Current Return | Target Return |
|--------|---------------|---------------|
| `get_item_with_related()` | `tuple[item, related]` | `ModelT \| None` |
| `get_item_with_related_with_retry()` | `tuple[item, related]` | `ModelT \| None` |
| `get_item_with_all_related()` | `tuple[item, dict]` | `ModelT \| None` |
| `get_item_with_m2m()` | `tuple[item, list]` | `ModelT \| None` |
| `get_active_item_with_fk()` | `tuple[item, related]` | `ModelT \| None` |
| `get_item_through_fk()` | `tuple[item, fk, target]` | `ModelT \| None` |
| `get_active_item_with_through_fk()` | `tuple[item, fk, target]` | `ModelT \| None` |
| `get_active_item_through_ifk()` | `tuple[item, ifk, target]` | `ModelT \| None` |

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
