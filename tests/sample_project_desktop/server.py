"""Sample desktop API server.

This script starts a local API server that exposes your matrx-orm
managers over HTTP and WebSocket. Run it as the Python backend for
your desktop application.

Usage:
    python server.py
"""

from __future__ import annotations

import asyncio
import os
import sys

# ── Database setup ─────────────────────────────────────────────────────────

from matrx_orm import (
    DatabaseProjectConfig,
    register_database,
    Model,
    BaseManager,
    ModelView,
)
from matrx_orm.core.fields import (
    UUIDField,
    CharField,
    IntegerField,
    BooleanField,
    DateTimeField,
    TextField,
    ForeignKey,
)
from matrx_orm.api import APIServer, APIConfig


# ── Models ─────────────────────────────────────────────────────────────────
# Replace these with your actual models (or import from your generated code).

class User(Model):
    _database = "desktop_app"
    _table_name = "users"

    id = UUIDField(primary_key=True)
    username = CharField(max_length=100)
    email = CharField(max_length=255)
    is_active = BooleanField(default=True)
    created_at = DateTimeField(auto_now_add=True)


class Note(Model):
    _database = "desktop_app"
    _table_name = "notes"

    id = UUIDField(primary_key=True)
    title = CharField(max_length=200)
    content = TextField()
    user_id = ForeignKey("User", to_column="id", related_name="notes")
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)


# ── Views ──────────────────────────────────────────────────────────────────

class NoteView(ModelView):
    prefetch = ["user_id"]
    inline_fk = {"user_id": "author"}

    async def excerpt(self, model) -> str:
        content = model.content or ""
        return content[:100] + "..." if len(content) > 100 else content


# ── Managers ───────────────────────────────────────────────────────────────

class UserManager(BaseManager[User]):
    pass


class NoteManager(BaseManager[Note]):
    view_class = NoteView


# ── Server startup ─────────────────────────────────────────────────────────

async def main() -> None:
    # 1. Register database
    config = DatabaseProjectConfig(
        name="desktop_app",
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432"),
        database_name=os.getenv("DB_NAME", "myapp"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD", "postgres"),
    )
    register_database(config)

    # 2. Create manager instances
    user_mgr = UserManager(model=User)
    note_mgr = NoteManager(model=Note)

    # 3. Configure API server
    api_config = APIConfig(
        secret=os.getenv("API_SECRET", ""),  # Auto-generates if empty
        port=int(os.getenv("API_PORT", "8745")),
    )

    server = APIServer(config=api_config)

    # 4. Register managers under namespaces
    server.register_manager("users", user_mgr)
    server.register_manager("notes", note_mgr)

    # 5. Register custom methods (optional)
    async def app_info(**params):
        return {
            "name": "My Desktop App",
            "version": "1.0.0",
            "models": ["users", "notes"],
        }

    server.register_method("app.info", app_info)

    # 6. Start the server (blocking)
    await server.start()


if __name__ == "__main__":
    asyncio.run(main())
