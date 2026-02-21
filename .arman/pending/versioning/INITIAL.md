That's a fundamentally different use case — and it **does** justify ORM-level support.

What you're describing is **content versioning as a first-class feature**: the version history is user-facing, not a technical audit log. Users navigate it, promote versions, compare them, roll back intentionally. That's a product feature, not an infrastructure concern.

---

## The right data model

The cleanest pattern for this — used by Notion, WordPress revisions, and most CMS platforms — is **separate version rows with a current pointer**:

```sql
-- The canonical "current" record (what most queries see)
CREATE TABLE document (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title       TEXT NOT NULL,
    owner_id    UUID NOT NULL,
    created_at  TIMESTAMPTZ DEFAULT now(),
    current_version_id UUID REFERENCES document_version(id)  -- pointer to live version
);

-- Immutable version rows (append-only, never updated)
CREATE TABLE document_version (
    id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id  UUID NOT NULL REFERENCES document(id) ON DELETE CASCADE,
    version_num  INTEGER NOT NULL,
    content      JSONB NOT NULL,     -- or individual columns
    label        TEXT,               -- user-assigned name, e.g. "Draft v2"
    is_published BOOLEAN DEFAULT false,
    created_by   UUID,
    created_at   TIMESTAMPTZ DEFAULT now(),

    UNIQUE (document_id, version_num)
);
```

Two tables, clean separation of concerns:
- `document` holds identity, metadata, and ownership — rarely changes
- `document_version` is append-only — a new row on every save, never updated in-place

---

## Why two tables beats one table with a version column

The single-table approach (`id | version | is_current | data`) has a critical problem: **foreign keys become ambiguous**. If `comment.document_id` points to `document`, which version does it reference? You end up needing `document_id + version_num` as a composite FK everywhere, which cascades into every join and index in the system.

The two-table model keeps FKs clean: everything references `document.id` (the stable identity), and the version content is a detail inside the versioning subsystem.

---

## What ORM-level support would actually look like

The useful surface is **a mixin or model flag** that wires up the two-table pattern and provides the version operations, while keeping normal access completely transparent:

```python
from matrx_orm import Model, UUIDField, CharField, JSONField
from matrx_orm.versioning import VersionedMixin  # hypothetical

class Document(VersionedMixin, Model):
    id       = UUIDField(primary_key=True)
    title    = CharField(max_length=200)
    owner_id = UUIDField()

    _versioned_fields = ["content"]   # these fields go into version rows
    _table_name = "document"
    _database   = "my_project"
```

The mixin would generate and manage `document_version` automatically, and expose:

```python
doc = await Document.get(id=doc_id)

# Normal access — transparent, returns current version's content
print(doc.content)

# Save creates a new version row, bumps current_version_id
await doc.save_version(content=new_content, created_by=user_id)

# Browse history
versions = await doc.get_versions()             # list, newest first
v3       = await doc.get_version(3)             # specific version by num
v3       = await doc.get_version(label="Draft") # by label

# Promote any version to current (one-liner rollback/restore)
await doc.set_active_version(version_num=3)

# Label a version (like a git tag)
await doc.label_version(version_num=2, label="Published - Feb 2026")

# Compare two versions (returns diff dict)
diff = await doc.diff_versions(2, 3)
```

---

## The key design decisions you'd need to make

**1. What goes in the version row?**

Option A: specific fields (`_versioned_fields = ["content", "title"]`) — surgical, smaller rows
Option B: entire model snapshot — simpler, heavier, enables full rollback of anything

**2. When does a new version get created?**

Option A: explicit — `doc.save_version(...)` — developer controls it
Option B: automatic on every `update()` — always versioned, but can create noise (autosave spam)
Option C: explicit save with a debounce/merge window — like Google Docs (versions within a short window get merged)

**3. What does a normal `.get()` return?**

It should always return the current version's data transparently. The mixin overrides `from_db_result` to merge version fields onto the model instance so callers never know the difference.

---

## My honest take on building this

This is **worth building**, but as a **separate optional package** (`matrx-orm-versioning` or a `versioning` submodule) rather than baked into the core ORM. Reasons:

- Most models don't need versioning — you don't want the mental overhead on every model definition
- The schema for the version table varies by use case (JSONB blob vs. mirrored columns)
- It's cleanly separable — it only touches `save`, `get`, and the schema builder; nothing else needs to change
- It becomes a genuinely useful standalone library that others can adopt

The core ORM already has everything this needs: `Model`, `ForeignKey`, `QueryBuilder`, `DDLGenerator` for generating the version table migration, and `BaseManager` for the version operations. The mixin would just compose those.

---

## What I'd do right now (without building it yet)

The pattern is well-defined enough that you can implement it manually today for any table that needs it — two models, a manager method that writes the version row and updates the pointer, and a `get_versions()` helper. That gives you the user-facing feature immediately while the generic ORM support is a future enhancement.

---- Previous ---
This is a genuinely interesting architectural question, and the honest answer is: **it depends on what you're versioning and why** — and PostgreSQL already has two strong native mechanisms that likely cover most needs without ORM involvement.

---

## What PostgreSQL already gives you for free

### 1. Temporal tables via triggers
You can create a `_history` shadow table and a trigger that copies every `UPDATE`/`DELETE` to it:

```sql
CREATE TABLE post_history (
    LIKE post INCLUDING ALL,
    _version     INTEGER NOT NULL,
    _changed_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    _change_type TEXT NOT NULL  -- 'update' | 'delete'
);

CREATE TRIGGER post_audit
BEFORE UPDATE OR DELETE ON post
FOR EACH ROW EXECUTE FUNCTION record_history();
```

**The ORM sees nothing.** You query `post` normally. History is in `post_history` if you ever need it. Zero application code required.

### 2. Supabase / pgAudit
If you're on Supabase, `pgAudit` is already available. Point it at a table, get a full audit log — again, zero ORM involvement.

---

## When ORM-level versioning *does* make sense

There's one pattern where native PostgreSQL triggers fall short: **when the application needs to actively reason about versions at runtime** — not just recover from accidents, but actually serve "give me version 3 of this document" as a core feature.

That's the **event-sourcing / document-as-rows** pattern:

```
id (content id)  | version | data           | is_current
-----------------+---------+----------------+-----------
abc123           | 1       | {title: "v1"}  | false
abc123           | 2       | {title: "v2"}  | false
abc123           | 3       | {title: "v3"}  | true
```

This is meaningfully different from an audit log — the versions **are** the canonical data, not a side channel. Django's `django-reversion`, Temporal, and some document editors (Notion, Google Docs internals) use this model.

---

## Where ORM-level versioning would add real value

If you wanted to build this into matrx-orm, the genuinely useful surface would be **narrow**:

| Feature | Value |
|---|---|
| `_versioned = True` on a model | Auto-adds `version`, `is_current`, `superseded_at` fields |
| `model.save()` writes a new row instead of updating | The ORM enforces the immutable-row contract |
| `Model.get(id=x)` returns the current version automatically | Transparent to callers |
| `Model.get_version(id=x, version=3)` | Explicit history access |
| `Model.history(id=x)` | Returns all versions sorted |

The "blind to it" part you described — where callers use the model normally without caring about versions — is the right instinct, and it's achievable.

---

## My honest recommendation

**Don't build it into the ORM yet.** Here's why:

1. **PostgreSQL triggers handle the audit case perfectly.** If your goal is recovery, compliance, or "what changed and when," a trigger-based history table is faster, more reliable, and truly invisible to application code. The schema builder could even generate the trigger DDL automatically — that's a much smaller surface than a versioning subsystem.

2. **The event-sourcing case is a product decision, not an infrastructure one.** If a specific table genuinely needs versioned rows as a first-class feature (e.g., a document editor, a config history system), that's better modeled explicitly at the schema level for that table rather than as a generic ORM behavior.

3. **The complexity cost is high.** Versioned models break bulk operations, foreign key semantics (which version does the FK point to?), and cache invalidation in non-obvious ways. `filter(author_id=x)` returning stale versions silently would be a serious footgun.

---

## What I'd suggest instead

A much lighter-weight win would be adding a `schema_builder` option to **generate audit trigger SQL** alongside model files:

```bash
matrx-orm makemigrations --database my_project --with-audit post article config
```

That emits a migration with the `_history` table and trigger for each named table — zero runtime overhead, zero ORM complexity, production-grade auditability in one command.

That's genuinely additive and has no downside. The full versioned-rows feature, if you ever need it, is better as an explicit opt-in model mixin for specific use cases rather than infrastructure-level behavior.