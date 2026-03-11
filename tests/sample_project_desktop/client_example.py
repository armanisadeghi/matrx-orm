"""Python client example for the matrx-orm API server.

Shows how to authenticate and make RPC calls from Python.
This pattern works for:
  - Python desktop apps (e.g. with PySide/PyQt)
  - Testing and scripting
  - Any Python service that needs to talk to the API
"""

from __future__ import annotations

import asyncio
import json
from typing import Any

import aiohttp


class MatrxClient:
    """Simple async client for the matrx-orm API server.

    Usage::

        async with MatrxClient("http://127.0.0.1:8745", secret="...") as client:
            users = await client.call("users.load_items", status="active")
            user = await client.call("users.create_item",
                username="alice",
                email="alice@example.com",
            )
    """

    def __init__(self, base_url: str, secret: str) -> None:
        self._base_url = base_url.rstrip("/")
        self._secret = secret
        self._token: str | None = None
        self._session: aiohttp.ClientSession | None = None
        self._request_id = 0

    async def __aenter__(self) -> MatrxClient:
        self._session = aiohttp.ClientSession()
        await self._authenticate()
        return self

    async def __aexit__(self, *args: Any) -> None:
        if self._session:
            await self._session.close()

    async def _authenticate(self) -> None:
        """Exchange the shared secret for a bearer token."""
        assert self._session is not None
        async with self._session.post(
            f"{self._base_url}/auth/token",
            json={"secret": self._secret, "client_id": "python-client"},
        ) as resp:
            if resp.status != 200:
                raise RuntimeError(f"Authentication failed: {resp.status}")
            data = await resp.json()
            self._token = data["token"]

    async def call(self, method: str, **params: Any) -> Any:
        """Make an RPC call and return the result.

        Raises RuntimeError on RPC errors.
        """
        assert self._session is not None
        self._request_id += 1

        payload = {
            "method": method,
            "params": params,
            "id": self._request_id,
        }

        async with self._session.post(
            f"{self._base_url}/rpc",
            json=payload,
            headers={"Authorization": f"Bearer {self._token}"},
        ) as resp:
            text = await resp.text()
            data = json.loads(text)

            if data.get("error"):
                err = data["error"]
                raise RuntimeError(
                    f"RPC Error {err['code']}: {err['message']}"
                )

            return data.get("result")

    async def call_batch(self, calls: list[tuple[str, dict]]) -> list[Any]:
        """Make multiple RPC calls in a single HTTP request.

        Parameters
        ----------
        calls : list[tuple[str, dict]]
            List of (method, params) tuples.

        Returns
        -------
        list[Any]
            List of results in the same order as the input.
        """
        assert self._session is not None

        batch = []
        for method, params in calls:
            self._request_id += 1
            batch.append({
                "method": method,
                "params": params,
                "id": self._request_id,
            })

        async with self._session.post(
            f"{self._base_url}/rpc",
            json=batch,
            headers={"Authorization": f"Bearer {self._token}"},
        ) as resp:
            text = await resp.text()
            responses = json.loads(text)
            return [r.get("result") for r in responses]

    async def health(self) -> dict:
        """Check server health (no auth required)."""
        assert self._session is not None
        async with self._session.get(f"{self._base_url}/health") as resp:
            return await resp.json()


# ── Example usage ──────────────────────────────────────────────────────────

async def main() -> None:
    # The secret is printed by the server on startup (or set via API_SECRET env var)
    SECRET = "change-me-to-a-real-secret"
    SERVER_URL = "http://127.0.0.1:8745"

    async with MatrxClient(SERVER_URL, secret=SECRET) as client:
        # Health check
        health = await client.health()
        print(f"Server health: {health}")

        # Create a user
        user = await client.call(
            "users.create_item",
            username="alice",
            email="alice@example.com",
        )
        print(f"Created user: {user}")

        # Load all users
        users = await client.call("users.load_items")
        print(f"All users: {users}")

        # Create a note
        note = await client.call(
            "notes.create_item",
            title="My First Note",
            content="Hello from the desktop app!",
            user_id=user["id"],
        )
        print(f"Created note: {note}")

        # Load note with author (FK prefetch via ModelView)
        note_with_author = await client.call(
            "notes.load_item",
            id=note["id"],
        )
        print(f"Note with author: {note_with_author}")

        # Batch request — multiple calls in one HTTP round-trip
        results = await client.call_batch([
            ("users.count", {}),
            ("notes.count", {}),
            ("app.info", {}),
        ])
        print(f"User count: {results[0]}")
        print(f"Note count: {results[1]}")
        print(f"App info: {results[2]}")

        # Update
        updated = await client.call(
            "notes.update_item",
            item_id=note["id"],
            title="Updated Title",
        )
        print(f"Updated note: {updated}")

        # Delete
        deleted = await client.call(
            "notes.delete_item",
            item_id=note["id"],
        )
        print(f"Deleted: {deleted}")


if __name__ == "__main__":
    asyncio.run(main())
