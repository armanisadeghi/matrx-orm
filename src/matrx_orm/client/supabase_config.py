"""Supabase client configuration for desktop/client-side applications.

This module provides configuration for connecting to Supabase via the
PostgREST API using the **anon (publishable) key** — safe to embed in
desktop apps distributed to end users.

Security model:
- The anon key is public. It grants access only through RLS policies.
- Each user authenticates via Supabase Auth and receives a JWT.
- The JWT is sent with every request. RLS policies use ``auth.uid()``
  to restrict access to the user's own data.
- No service_role key, no direct DB connection string, no secrets.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class SupabaseClientConfig:
    """Configuration for client-side Supabase access.

    Parameters
    ----------
    url : str
        Your Supabase project URL (e.g. ``"https://abc123.supabase.co"``).
    anon_key : str
        The **publishable** anon key from your Supabase project settings.
        This is safe to embed in client applications.
    schema : str
        The PostgreSQL schema to query. Default ``"public"``.
    timeout : float
        HTTP request timeout in seconds.
    max_retries : int
        Number of retries on transient failures (network errors, 5xx).
    headers : dict
        Additional headers to include on every request.
    """

    url: str
    anon_key: str
    schema: str = "public"
    timeout: float = 30.0
    max_retries: int = 3
    headers: dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.url = self.url.rstrip("/")
        if not self.url.startswith("http"):
            raise ValueError(
                f"SupabaseClientConfig.url must start with http:// or https://, "
                f"got: {self.url!r}"
            )
        if not self.anon_key:
            raise ValueError(
                "SupabaseClientConfig.anon_key is required. "
                "Find it in your Supabase dashboard under Settings > API."
            )

    @property
    def rest_url(self) -> str:
        """The PostgREST base URL."""
        return f"{self.url}/rest/v1"

    @property
    def auth_url(self) -> str:
        """The Supabase Auth (GoTrue) base URL."""
        return f"{self.url}/auth/v1"

    @property
    def default_headers(self) -> dict[str, str]:
        """Headers required on every request."""
        h = {
            "apikey": self.anon_key,
            "Content-Type": "application/json",
        }
        if self.schema != "public":
            h["Accept-Profile"] = self.schema
            h["Content-Profile"] = self.schema
        h.update(self.headers)
        return h
