"""Example: Desktop Python app using matrx-orm Supabase client.

This shows the complete flow for a desktop application that needs to
read/write data to a shared Supabase database using the publishable
anon key + user authentication. RLS enforces per-user data access.

Requirements:
    pip install matrx-orm[api]   # includes aiohttp

No database credentials are shipped. Only the public anon key and
project URL, which are designed to be exposed to clients.
"""

from __future__ import annotations

import asyncio
import os

from matrx_orm.client import (
    SupabaseClientConfig,
    SupabaseAuth,
    SupabaseManager,
)


# ── Configuration ──────────────────────────────────────────────────────
# These values are safe to embed in your desktop app.
# They are public — security comes from RLS, not from hiding these.

SUPABASE_URL = os.getenv("SUPABASE_URL", "https://your-project.supabase.co")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY", "eyJ...")


async def main() -> None:
    # 1. Create configuration (safe to embed — anon key is publishable)
    config = SupabaseClientConfig(
        url=SUPABASE_URL,
        anon_key=SUPABASE_ANON_KEY,
    )

    # 2. Authenticate the user
    auth = SupabaseAuth(config)

    # Option A: Email + password sign-in
    session = await auth.sign_in_with_password(
        email="user@example.com",
        password="user-password",
    )
    print(f"Signed in as: {session.email} (uid: {session.user_id})")

    # Option B: Sign up a new user (uncomment to use)
    # session = await auth.sign_up(
    #     email="newuser@example.com",
    #     password="secure-password",
    #     user_metadata={"display_name": "New User"},
    # )

    # Option C: Magic link / OTP (uncomment to use)
    # await auth.sign_in_with_otp(email="user@example.com")
    # # User receives email, enters the code:
    # session = await auth.verify_otp(
    #     email="user@example.com",
    #     token="123456",
    # )

    # 3. Create managers for your tables
    # These work like BaseManager but go through PostgREST + RLS
    notes = SupabaseManager("notes", config=config, auth=auth)
    tags = SupabaseManager("tags", config=config, auth=auth)

    # ── CRUD Operations ────────────────────────────────────────────────

    # CREATE — insert a new note (user_id set automatically by RLS default)
    note = await notes.create_item(
        title="My First Note",
        content="Written from the desktop app!",
    )
    print(f"Created note: {note}")

    # READ — load by ID
    loaded = await notes.load_item(note["id"])
    print(f"Loaded: {loaded}")

    # READ — load with filters (only returns YOUR notes due to RLS)
    my_notes = await notes.load_items(
        order=["-created_at"],
        limit=10,
    )
    print(f"My notes ({len(my_notes)}): {[n['title'] for n in my_notes]}")

    # READ — filter with operators
    recent = await notes.load_items(
        created_at__gte="2025-01-01",
        title__icontains="first",
    )
    print(f"Filtered: {recent}")

    # UPDATE
    updated = await notes.update_item(
        note["id"],
        title="Updated Title",
        content="Modified from the desktop app!",
    )
    print(f"Updated: {updated}")

    # COUNT
    total = await notes.count()
    print(f"Total notes: {total}")

    # EXISTS
    found = await notes.exists(note["id"])
    print(f"Note exists: {found}")

    # UPSERT
    upserted = await notes.upsert_item(
        {"id": note["id"], "title": "Upserted Title"},
        conflict_fields=["id"],
    )
    print(f"Upserted: {upserted}")

    # GET OR CREATE
    tag, was_created = await tags.get_or_create(
        defaults={"color": "blue"},
        name="important",
    )
    print(f"Tag: {tag}, created: {was_created}")

    # ── Bulk operations ────────────────────────────────────────────────

    # Bulk insert
    new_notes = await notes.create_items([
        {"title": "Bulk Note 1", "content": "Content 1"},
        {"title": "Bulk Note 2", "content": "Content 2"},
    ])
    print(f"Bulk created: {len(new_notes)} notes")

    # Bulk update (all matching rows)
    updated_rows = await notes.update_where(
        {"content": "Bulk updated!"},
        title__icontains="Bulk Note",
    )
    print(f"Bulk updated: {len(updated_rows)} rows")

    # ── Related data (PostgREST foreign key embedding) ─────────────────

    # Load notes with their author data embedded
    # Requires foreign key relationship in your schema
    notes_with_author = await notes.load_items_with_related(
        "author:profiles(id,display_name,avatar_url)",
        limit=5,
    )
    print(f"Notes with author: {notes_with_author}")

    # ── RPC (server-side functions) ────────────────────────────────────

    # Call a PostgreSQL function defined in your Supabase project
    # result = await notes.rpc("search_notes", query="desktop", limit=5)
    # print(f"Search results: {result}")

    # ── Cleanup ────────────────────────────────────────────────────────

    # DELETE
    deleted = await notes.delete_item(note["id"])
    print(f"Deleted: {deleted}")

    # Delete bulk-created notes
    deleted_count = await notes.delete_where(title__icontains="Bulk Note")
    print(f"Bulk deleted: {deleted_count} rows")

    # ── Session management ─────────────────────────────────────────────

    # Token auto-refresh: the manager calls ensure_valid_session()
    # before every request, so expired tokens are refreshed automatically.

    # Manual refresh (if needed):
    # new_session = await auth.refresh_session()

    # Get current user profile
    user_profile = await auth.get_user()
    print(f"User profile: {user_profile}")

    # Sign out
    await auth.sign_out()
    print("Signed out")


if __name__ == "__main__":
    asyncio.run(main())
