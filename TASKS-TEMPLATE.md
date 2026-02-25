# TASK: [Short, Descriptive Title]

> **Location:** `path/to/relevant/file_or_directory`
> **Priority:** `critical` | `high` | `medium` | `low`
> **Impact:** `breaking` | `non-breaking` | `internal-only`
> **Status:** `draft` | `ready` | `in-progress` | `blocked` | `done`
> **Created:** YYYY-MM-DD
> **Updated:** YYYY-MM-DD

## Summary

One to three sentences explaining **what** needs to change and **why**. This should be
understandable without reading the rest of the document. Anyone skimming `TASKS.md` will
see this same text as the task's description.

## Context

Background that someone unfamiliar with this area needs to understand the task. Include:

- What the current behavior or architecture looks like
- Why the current approach is problematic or insufficient
- Any prior discussion, analysis, or failed attempts worth knowing about

Keep this factual. If analysis was done by a model or developer, preserve the substance
but don't leave raw chat output — distill it into clear technical writing.

## Task List

Concrete, checkable items. Each item should be independently actionable and testable.
Mark status with standard checkboxes. Nest sub-tasks only when they are true dependencies.

- [ ] First task item — brief description of what to do
- [ ] Second task item — brief description of what to do
- [ ] Third task item — brief description with sub-tasks below
    - [ ] Sub-task A
    - [ ] Sub-task B
- [ ] Fourth task item — brief description of what to do

When an item is completed, check the box and add a **brief inline note** about what changed.
Do not remove it — the history is useful. Example:

- [x] Refactored `fetch_fk()` to batch queries — *done: uses `ANY($1)` collector, 2025-12-15*

## Risks & Considerations

Anything that could go wrong, requires coordination, or might affect other parts of the
system. Skip this section if there are none.

- **Breaking changes:** List affected public APIs and what downstream code needs updating
- **Migration path:** How existing users or call sites should transition
- **Dependencies:** Other tasks, PRs, or decisions that must happen first or in parallel
- **Performance:** Expected impact (positive or negative) and how to verify

## Proposed Solution

*(Optional — include only when the approach has been analyzed and is worth preserving.)*

Describe the recommended implementation. Use code snippets, tables, or diagrams where they
add clarity. This section exists to save the next developer from re-deriving the solution.

If there are multiple viable approaches, list them with trade-offs so a decision can be made.

## References

*(Optional — include only when there are links worth preserving.)*

- Related task files, docs, issues, or PRs
- External resources (library docs, blog posts, RFCs) that informed the analysis

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
