# Desktop App — Supabase Client Integration Guide

> How to securely read/write to a shared Supabase database from a Python
> desktop application distributed to end users.

---

## The Problem

Your desktop Python app needs to read/write to a shared Supabase PostgreSQL
database, but you **cannot ship your service_role key** — that would give
every user full, unrestricted access to every table and every row.

## The Solution

Use the **Supabase anon (publishable) key** + **user JWT** + **Row-Level Security (RLS)**.

```
┌─── User's Machine ──────────────────────────────┐
│                                                   │
│  Python Desktop App                               │
│  ├── SupabaseAuth   → sign in, get JWT           │
│  ├── SupabaseManager → CRUD via PostgREST        │
│  │     (anon key = safe to embed)                │
│  │     (JWT = identifies the user)               │
│  └── ML models, scraping, etc.                   │
│                                                   │
└─────────────────┬─────────────────────────────────┘
                  │ HTTPS (PostgREST API)
                  ▼
┌─── Supabase Cloud ──────────────────────────────┐
│                                                   │
│  PostgREST (REST API)                            │
│  ├── Validates JWT                               │
│  ├── Sets auth.uid() from token                  │
│  └── Enforces RLS policies                       │
│                                                   │
│  PostgreSQL                                      │
│  └── RLS: WHERE user_id = auth.uid()             │
│      (user can ONLY see/modify their own rows)   │
│                                                   │
└───────────────────────────────────────────────────┘
```

**What's safe to embed in the desktop app:**
- Supabase project URL (public)
- Anon key (publishable — designed for client-side use)

**What stays on your server only:**
- `service_role` key (bypasses RLS — NEVER ship this)
- Database connection string (host, port, password)

---

## 1. Installation

```bash
pip install matrx-orm[api]
```

This adds `aiohttp` for the HTTP client.

---

## 2. Supabase Setup (One-Time)

### 2a. Enable RLS on every table

In the Supabase dashboard (or via SQL):

```sql
-- Enable RLS
ALTER TABLE notes ENABLE ROW LEVEL SECURITY;

-- Users can only see their own notes
CREATE POLICY "Users read own notes"
  ON notes FOR SELECT
  USING (user_id = auth.uid());

-- Users can only insert their own notes
CREATE POLICY "Users insert own notes"
  ON notes FOR INSERT
  WITH CHECK (user_id = auth.uid());

-- Users can only update their own notes
CREATE POLICY "Users update own notes"
  ON notes FOR UPDATE
  USING (user_id = auth.uid());

-- Users can only delete their own notes
CREATE POLICY "Users delete own notes"
  ON notes FOR DELETE
  USING (user_id = auth.uid());
```

### 2b. Auto-set user_id on insert

So the desktop app doesn't need to know the user's ID:

```sql
ALTER TABLE notes
  ALTER COLUMN user_id SET DEFAULT auth.uid();
```

### 2c. Repeat for every table

Every table that users read/write must have:
1. RLS enabled
2. Policies that check `auth.uid()`
3. Default `user_id = auth.uid()` on insert

**Tables WITHOUT RLS are invisible to anon key requests by default.**
This is safe — it means tables without policies are simply inaccessible.

---

## 3. Python Desktop App Code

### 3a. Configuration

```python
from matrx_orm.client import SupabaseClientConfig, SupabaseAuth, SupabaseManager

# Safe to embed — these are public values
config = SupabaseClientConfig(
    url="https://your-project.supabase.co",
    anon_key="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
)
```

### 3b. Authentication

```python
auth = SupabaseAuth(config)

# Email + password
session = await auth.sign_in_with_password("user@example.com", "password")

# Magic link
await auth.sign_in_with_otp(email="user@example.com")
session = await auth.verify_otp(email="user@example.com", token="123456")

# Sign up
session = await auth.sign_up(
    email="new@example.com",
    password="secure-password",
    user_metadata={"display_name": "Alice"},
)

# Token auto-refresh
session = await auth.ensure_valid_session()  # refreshes if expired
```

### 3c. CRUD Operations

```python
notes = SupabaseManager("notes", config=config, auth=auth)

# CREATE — user_id is set automatically by the DB default
note = await notes.create_item(
    title="My Note",
    content="Written from desktop app",
)

# READ — RLS ensures you only see YOUR notes
my_notes = await notes.load_items(order=["-created_at"], limit=20)
note = await notes.load_item(note["id"])
note = await notes.load_item_or_none(note["id"])

# FILTER — same operators as the ORM
recent = await notes.load_items(
    created_at__gte="2025-01-01",
    title__icontains="meeting",
)

# UPDATE
updated = await notes.update_item(note["id"], title="New Title")

# DELETE
await notes.delete_item(note["id"])

# COUNT
total = await notes.count()

# EXISTS
found = await notes.exists(note["id"])

# UPSERT
await notes.upsert_item(
    {"id": note["id"], "title": "Upserted"},
    conflict_fields=["id"],
)

# GET OR CREATE
tag, created = await notes.get_or_create(
    defaults={"color": "blue"},
    name="important",
)
```

### 3d. Bulk Operations

```python
# Bulk insert
new_notes = await notes.create_items([
    {"title": "Note 1", "content": "..."},
    {"title": "Note 2", "content": "..."},
])

# Bulk update
await notes.update_where(
    {"status": "archived"},
    created_at__lt="2024-01-01",
)

# Bulk delete
count = await notes.delete_where(status="draft")
```

### 3e. Related Data (PostgREST Foreign Key Embedding)

```python
# Load notes with author profile embedded
notes_with_author = await notes.load_items_with_related(
    "author:profiles(id,display_name,avatar_url)",
    limit=10,
)
# Each note has: {"id": ..., "title": ..., "author": {"display_name": "Alice", ...}}
```

### 3f. RPC (Server-Side Functions)

For complex operations, define a PostgreSQL function and call it:

```sql
-- In Supabase SQL editor
CREATE OR REPLACE FUNCTION search_notes(query text, max_results int DEFAULT 10)
RETURNS SETOF notes AS $$
  SELECT * FROM notes
  WHERE user_id = auth.uid()
    AND (title ILIKE '%' || query || '%' OR content ILIKE '%' || query || '%')
  LIMIT max_results;
$$ LANGUAGE sql SECURITY DEFINER;
```

```python
results = await notes.rpc("search_notes", query="meeting", max_results=5)
```

---

## 4. Filter Operators

The same filter operators work as in the server-side ORM:

| Operator | Example | PostgREST |
|----------|---------|-----------|
| `eq` (default) | `status="active"` | `status=eq.active` |
| `ne` | `status__ne="draft"` | `status=neq.draft` |
| `gt` | `age__gt=18` | `age=gt.18` |
| `gte` | `age__gte=18` | `age=gte.18` |
| `lt` | `age__lt=65` | `age=lt.65` |
| `lte` | `age__lte=65` | `age=lte.65` |
| `in` | `status__in=["a","b"]` | `status=in.(a,b)` |
| `contains` | `title__contains="note"` | `title=like.*note*` |
| `icontains` | `title__icontains="note"` | `title=ilike.*note*` |
| `startswith` | `title__startswith="My"` | `title=like.My*` |
| `endswith` | `title__endswith="txt"` | `title=like.*txt` |
| `isnull` | `deleted_at__isnull=True` | `deleted_at=is.null` |

---

## 5. Security Checklist

- [x] **Anon key only** — service_role key never leaves your server
- [x] **RLS enforced** — PostgreSQL policies check `auth.uid()` on every query
- [x] **User JWT required** — every request is authenticated via Supabase Auth
- [x] **Token auto-refresh** — expired tokens are refreshed transparently
- [x] **No direct DB connection** — all access through PostgREST (HTTPS)
- [x] **No raw SQL** — users can only call PostgREST endpoints, not arbitrary SQL
- [ ] **RLS policies on all tables** — YOU must set these up (see Section 2)
- [ ] **Default user_id** — YOU must add `DEFAULT auth.uid()` on user_id columns

### What a malicious user CANNOT do (even with the anon key):

- Read or modify other users' data (RLS prevents it)
- Drop tables, alter schema, or run DDL (PostgREST doesn't support it)
- Execute arbitrary SQL (PostgREST only exposes defined tables/functions)
- Access tables without RLS policies (they're invisible to anon)
- Use the service_role key (it's not in the app)

### What a malicious user CAN do:

- Read/write their OWN data (that's the point)
- Call any RPC function exposed in your schema (secure these with `auth.uid()` checks)
- See your Supabase project URL and anon key (they're public by design)
- Make lots of requests (add rate limiting in Supabase if needed)

---

## 6. Limitations vs Server-Side ORM

The client-side `SupabaseManager` does NOT support:

| Feature | Why | Workaround |
|---------|-----|------------|
| CTEs / Window functions | PostgREST doesn't support them | Use RPC (server-side functions) |
| Complex JOINs | PostgREST uses FK embedding, not SQL JOINs | Define views or functions |
| Raw SQL | Security — can't allow arbitrary SQL from clients | Use RPC functions |
| Transactions | PostgREST doesn't support multi-statement transactions | Use RPC with `SECURITY DEFINER` |
| `Q()` objects | Complex OR/AND logic isn't directly translatable | Use PostgREST `or` syntax or RPC |
| Vector search | pgvector operators not exposed via PostgREST | Use RPC wrapping the vector query |
| Signals/hooks | Client-side, no ORM lifecycle | Use database triggers instead |

For any operation too complex for PostgREST, create a PostgreSQL function
and call it via `await manager.rpc("function_name", ...)`.

---

## 7. Integration with matrx-local

### What to do in the matrx-local desktop app:

1. **Install**: `pip install matrx-orm[api]`

2. **Store config**: Put the Supabase URL and anon key in the app's config
   (these are public, so no special protection needed).

3. **Auth flow**: On app launch, prompt for login or load saved refresh token.
   Use `SupabaseAuth` for all auth operations.

4. **Create managers**: One `SupabaseManager` per table the app needs.

5. **Use in your ML pipeline**: The managers work like any async Python code:
   ```python
   # In your model runner
   results = await jobs.load_items(status="pending", limit=5)
   for job in results:
       output = run_ml_model(job["input_data"])
       await jobs.update_item(job["id"], status="complete", output=output)
   ```

### Files to create in matrx-local

| File | Purpose |
|------|---------|
| `backend/db.py` | Config + auth initialization |
| `backend/managers.py` | SupabaseManager instances per table |
| `backend/auth_flow.py` | Login/logout/token persistence |

### Example `backend/db.py`:

```python
import os
from matrx_orm.client import SupabaseClientConfig, SupabaseAuth, SupabaseManager

config = SupabaseClientConfig(
    url=os.getenv("SUPABASE_URL", "https://your-project.supabase.co"),
    anon_key=os.getenv("SUPABASE_ANON_KEY", "eyJ..."),
)

auth = SupabaseAuth(config)

# Managers — one per table
users = SupabaseManager("profiles", config=config, auth=auth)
jobs = SupabaseManager("ml_jobs", config=config, auth=auth)
results = SupabaseManager("ml_results", config=config, auth=auth)
files = SupabaseManager("user_files", config=config, auth=auth)
```

---

## 8. Server-Side API (Optional)

The `matrx_orm.api` module (from the previous commit) is still useful for
a **different scenario**: when you run a Python backend on YOUR server and
expose ORM operations via a local HTTP API. This is the right choice when:

- You need the full ORM (CTEs, transactions, complex queries)
- The database credentials stay on your server
- The desktop app talks to your server, not directly to Supabase

Use `matrx_orm.api.APIServer` for that. Use `matrx_orm.client.SupabaseManager`
for the client-side approach described in this document. They solve different
problems and can coexist in the same project.
