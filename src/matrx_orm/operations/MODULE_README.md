# `src.matrx_orm.operations` — Module Overview

> This document is partially auto-generated. Sections tagged `<!-- AUTO:id -->` are refreshed by the generator.
> Everything else is yours to edit freely and will never be overwritten.

<!-- AUTO:meta -->
## About This Document

This file is **partially auto-generated**. Sections wrapped in `<!-- AUTO:id -->` tags
are overwritten each time the generator runs. Everything else is yours to edit freely.

| Field | Value |
|-------|-------|
| Module | `src/matrx_orm/operations` |
| Last generated | 2026-02-28 13:57 |
| Output file | `src/matrx_orm/operations/MODULE_README.md` |
| Signature mode | `signatures` |

**To refresh auto-sections:**
```bash
python utils/code_context/generate_module_readme.py src/matrx_orm/operations --mode signatures
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

> Auto-generated. 6 files across 1 directories.

```
src/matrx_orm/operations/
├── MODULE_README.md
├── __init__.py
├── create.py
├── delete.py
├── read.py
├── update.py
# excluded: 1 .md
```
<!-- /AUTO:tree -->

<!-- AUTO:signatures -->
## API Signatures

> Auto-generated via `output_mode="signatures"`. ~5-10% token cost vs full source.
> For full source, open the individual files directly.

```
---
Filepath: src/matrx_orm/operations/__init__.py  [python]



---
Filepath: src/matrx_orm/operations/delete.py  [python]

  async def delete(model_cls: type[Model], **kwargs: Any) -> int
  async def bulk_delete(model_cls: type[Model], objects: Sequence[Model]) -> int
  async def soft_delete(model_cls: type[Model], **kwargs: Any) -> UpdateResult
  async def restore(model_cls: type[Model], **kwargs: Any) -> UpdateResult
  async def purge(model_cls: type[Model], **kwargs: Any) -> int
  async def delete_instance(instance: Model) -> None


---
Filepath: src/matrx_orm/operations/read.py  [python]

  async def get(model_cls, *args, **kwargs)
  async def filter(model_cls, *args, **kwargs)
  async def exclude(model_cls, *args, **kwargs)
  async def all(model_cls)
  async def count(model_cls, *args, **kwargs)
  async def exists(model_cls, *args, **kwargs)
  async def first(model_cls, *args, **kwargs)
  async def last(model_cls, *args, **kwargs)
  async def values(model_cls, *fields, **kwargs)
  async def values_list(model_cls, *fields, flat = False, **kwargs)
  async def in_bulk(model_cls, id_list, field = 'id')
  async def iterator(model_cls, chunk_size = 2000, **kwargs)


---
Filepath: src/matrx_orm/operations/create.py  [python]

  async def create(model_cls: type[Model], **kwargs: Any) -> Model
  async def save(instance: Model) -> Model
  async def bulk_create(model_cls: type[Model], objects_data: list[dict[str, Any]]) -> list[Model]
  async def get_or_create(model_cls: type[Model], defaults: dict[str, Any] | None = None, **kwargs: Any) -> tuple[Model, bool]
  async def update_or_create(model_cls: type[Model], defaults: dict[str, Any] | None = None, **kwargs: Any) -> tuple[Model, bool]
  async def upsert(model_cls: type[Model], data: dict[str, Any], conflict_fields: list[str], update_fields: list[str] | None = None) -> Model
  async def bulk_upsert(model_cls: type[Model], objects_data: list[dict[str, Any]], conflict_fields: list[str], update_fields: list[str] | None = None) -> list[Model]
  async def create_instance(model_cls: type[Model], **kwargs: Any) -> Model


---
Filepath: src/matrx_orm/operations/update.py  [python]

  async def update(model_cls: type[Model], filters: dict[str, Any], **kwargs: Any) -> UpdateResult
  async def bulk_update(model_cls: type[Model], objects: Sequence[Model], fields: list[str]) -> int
  async def update_or_create(model_cls: type[Model], defaults: dict[str, Any] | None = None, **kwargs: Any) -> tuple[Model, bool]
  async def increment(model_cls: type[Model], filters: dict[str, Any], **kwargs: Any) -> UpdateResult
  async def decrement(model_cls: type[Model], filters: dict[str, Any], **kwargs: Any) -> UpdateResult
  async def update_instance(instance: Model, fields: Iterable[str] | None = None) -> Model
```
<!-- /AUTO:signatures -->

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
  "subdirectory": "src/matrx_orm/operations",
  "mode": "signatures",
  "scope": null,
  "project_noise": null,
  "include_call_graph": false,
  "entry_points": null,
  "call_graph_exclude": [
    "tests"
  ]
}
```
<!-- /AUTO:config -->
