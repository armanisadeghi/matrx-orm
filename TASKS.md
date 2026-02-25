# Project Tasks

Central registry for all tracked work. Each entry links to a detailed task file located
near the code it affects. This file is the **index** — keep entries concise.

---

## How This System Works

### Structure

```
TASKS.md                          ← You are here. The index.
TASKS-TEMPLATE.md                 ← Copy this to create a new task file.
src/
  matrx_orm/
    core/
      EXTENDED-TASK.md            ← Task file lives next to the code it changes.
      RELATIONS-TASKS.md          ← Another task file in the same directory.
    query/
      QUERY-BUILDER-TASK.md       ← (example) Would live here if query work was tracked.
```

### Conventions

- **One task file per feature or workstream** — not per individual bug or line change.
- **Task files live in the directory they primarily affect.** If a task spans multiple
  directories, place it in the nearest common ancestor and note the affected paths.
- **File naming:** `FEATURE-NAME-TASK.md` (uppercase, hyphenated, always ends in `-TASK.md`).
- **Creating a task:** Copy `TASKS-TEMPLATE.md`, fill in metadata + summary, add an entry below.
- **Completing a task:** Check all items, set status to `done`, update the entry below.
  The project lead decides whether to archive or delete the file.

### Rules

1. **Keep this file in sync.** If you create, update, or complete a task file, update
   its entry here in the same commit.
2. **Task files are living documents.** Update them as you work — check off items, revise
   estimates, flag blockers. Stale docs are worse than no docs.
3. **Completed items stay checked, not deleted.** The history of what was done and when
   is valuable for anyone coming in later.
4. **Don't dump raw analysis here.** Task files are for distilled, actionable content.
   If an AI model or developer produced a wall of analysis, extract the useful parts
   into the task file's Context and Proposed Solution sections.

---

## Active Tasks

| Status | Priority | Impact | Task | Location |
|--------|----------|--------|------|----------|
| ready | high | breaking | [Extended base class relation refactor](#extended-base-class-relation-refactor) | `src/matrx_orm/core/EXTENDED-TASK.md` |
| ready | medium | non-breaking | [Relations performance improvements](#relations-performance-improvements) | `src/matrx_orm/core/RELATIONS-TASKS.md` |

---

### Extended Base Class Relation Refactor

> **File:** `src/matrx_orm/core/EXTENDED-TASK.md`
> **Priority:** high | **Impact:** breaking | **Status:** ready

Eliminate tuple-returning relation methods in favor of a consistent item-only return
pattern. All relationship data is already attached via `set_related()` — the tuple
variants are redundant and create a dual-source-of-truth problem. Includes a migration
script task for downstream call sites.

---

### Relations Performance Improvements

> **File:** `src/matrx_orm/core/RELATIONS-TASKS.md`
> **Priority:** medium | **Impact:** non-breaking | **Status:** ready

Batch prefetch for collections (N+1 fix), joined IFK loading, `select_related` extension
to IFKs/M2Ms, relation-level cache keys, and composite PK M2M support. Architectural
improvements that should not break existing APIs if done correctly.

---

## Completed Tasks

*None yet. Move entries here when a task is fully done and confirmed.*

<!-- When moving a task here, keep the one-line summary and add a completion date:
| 2025-12-15 | Task name — brief note about what shipped | `path/to/DELETED-TASK.md` |
-->
