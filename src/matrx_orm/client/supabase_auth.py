"""Supabase Auth client for desktop applications.

Handles user authentication (sign up, sign in, token refresh, sign out)
against the Supabase GoTrue API. The resulting JWT is used to authorize
all subsequent PostgREST requests, and RLS policies enforce per-user
data access.

Usage::

    from matrx_orm.client import SupabaseClientConfig, SupabaseAuth

    config = SupabaseClientConfig(
        url="https://abc123.supabase.co",
        anon_key="eyJ...",
    )
    auth = SupabaseAuth(config)

    # Sign in
    session = await auth.sign_in_with_password("user@example.com", "password")
    print(session.access_token)  # JWT for PostgREST requests
    print(session.user_id)       # auth.uid() value used by RLS

    # Refresh when expired
    session = await auth.refresh_session(session.refresh_token)

    # Sign out
    await auth.sign_out(session.access_token)
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass
from typing import Any

from matrx_orm.client.supabase_config import SupabaseClientConfig


@dataclass
class AuthSession:
    """Represents an authenticated user session."""

    access_token: str
    refresh_token: str
    expires_at: float
    user_id: str
    email: str
    user_metadata: dict[str, Any]

    @property
    def is_expired(self) -> bool:
        """Check if the access token has expired (with 60s buffer)."""
        return time.time() > (self.expires_at - 60)

    @classmethod
    def from_response(cls, data: dict[str, Any]) -> AuthSession:
        """Parse a GoTrue auth response into an AuthSession."""
        user = data.get("user", {})
        return cls(
            access_token=data["access_token"],
            refresh_token=data.get("refresh_token", ""),
            expires_at=time.time() + data.get("expires_in", 3600),
            user_id=user.get("id", ""),
            email=user.get("email", ""),
            user_metadata=user.get("user_metadata", {}),
        )


class SupabaseAuthError(Exception):
    """Raised when a Supabase Auth operation fails."""

    def __init__(self, message: str, status: int = 0) -> None:
        self.message = message
        self.status = status
        super().__init__(message)


class SupabaseAuth:
    """Client for Supabase GoTrue authentication.

    Parameters
    ----------
    config : SupabaseClientConfig
        The Supabase project configuration (URL + anon key).
    """

    def __init__(self, config: SupabaseClientConfig) -> None:
        self._config = config
        self._session: AuthSession | None = None

    @property
    def session(self) -> AuthSession | None:
        """The current session, or None if not signed in."""
        return self._session

    @property
    def access_token(self) -> str | None:
        """The current access token, or None."""
        return self._session.access_token if self._session else None

    async def sign_up(
        self,
        email: str,
        password: str,
        user_metadata: dict[str, Any] | None = None,
    ) -> AuthSession:
        """Create a new user account.

        Parameters
        ----------
        email : str
            The user's email address.
        password : str
            The user's password (min 6 characters by default).
        user_metadata : dict | None
            Optional metadata to attach to the user profile.

        Returns
        -------
        AuthSession
            The new session with access/refresh tokens.
        """
        body: dict[str, Any] = {"email": email, "password": password}
        if user_metadata:
            body["data"] = user_metadata

        data = await self._auth_request("POST", "/signup", body)
        self._session = AuthSession.from_response(data)
        return self._session

    async def sign_in_with_password(
        self, email: str, password: str
    ) -> AuthSession:
        """Sign in with email and password.

        Returns
        -------
        AuthSession
            The session with access/refresh tokens.
        """
        data = await self._auth_request(
            "POST",
            "/token?grant_type=password",
            {"email": email, "password": password},
        )
        self._session = AuthSession.from_response(data)
        return self._session

    async def sign_in_with_otp(self, email: str) -> dict[str, Any]:
        """Send a magic link / OTP to the user's email.

        The user clicks the link or enters the OTP to complete sign-in.
        Returns the GoTrue response (typically just a confirmation).
        """
        return await self._auth_request(
            "POST", "/otp", {"email": email}
        )

    async def verify_otp(
        self, email: str, token: str, type: str = "email"
    ) -> AuthSession:
        """Verify an OTP code to complete sign-in.

        Parameters
        ----------
        email : str
            The email the OTP was sent to.
        token : str
            The OTP code.
        type : str
            OTP type. Default ``"email"``.
        """
        data = await self._auth_request(
            "POST",
            "/verify",
            {"email": email, "token": token, "type": type},
        )
        self._session = AuthSession.from_response(data)
        return self._session

    async def refresh_session(
        self, refresh_token: str | None = None
    ) -> AuthSession:
        """Refresh an expired access token.

        Parameters
        ----------
        refresh_token : str | None
            The refresh token. If None, uses the current session's token.

        Returns
        -------
        AuthSession
            A new session with fresh tokens.
        """
        rt = refresh_token or (
            self._session.refresh_token if self._session else None
        )
        if not rt:
            raise SupabaseAuthError("No refresh token available")

        data = await self._auth_request(
            "POST",
            "/token?grant_type=refresh_token",
            {"refresh_token": rt},
        )
        self._session = AuthSession.from_response(data)
        return self._session

    async def sign_out(self, access_token: str | None = None) -> None:
        """Sign out and invalidate the session."""
        token = access_token or (
            self._session.access_token if self._session else None
        )
        if token:
            try:
                await self._auth_request(
                    "POST", "/logout", {}, access_token=token
                )
            except SupabaseAuthError:
                pass  # Sign-out failures are not critical
        self._session = None

    async def get_user(
        self, access_token: str | None = None
    ) -> dict[str, Any]:
        """Fetch the current user's profile from Supabase Auth."""
        token = access_token or (
            self._session.access_token if self._session else None
        )
        if not token:
            raise SupabaseAuthError("No access token available")

        return await self._auth_request(
            "GET", "/user", access_token=token
        )

    async def ensure_valid_session(self) -> AuthSession:
        """Return a valid session, refreshing if expired.

        Raises SupabaseAuthError if no session exists.
        """
        if not self._session:
            raise SupabaseAuthError("Not signed in")
        if self._session.is_expired:
            return await self.refresh_session()
        return self._session

    # ── Internal ───────────────────────────────────────────────────────

    async def _auth_request(
        self,
        method: str,
        path: str,
        body: dict[str, Any] | None = None,
        access_token: str | None = None,
    ) -> dict[str, Any]:
        """Make a request to the GoTrue API."""
        import aiohttp

        url = f"{self._config.auth_url}{path}"
        headers = {
            "apikey": self._config.anon_key,
            "Content-Type": "application/json",
        }
        if access_token:
            headers["Authorization"] = f"Bearer {access_token}"

        async with aiohttp.ClientSession() as session:
            kwargs: dict[str, Any] = {
                "headers": headers,
                "timeout": aiohttp.ClientTimeout(total=self._config.timeout),
            }
            if body is not None and method != "GET":
                kwargs["json"] = body

            async with session.request(method, url, **kwargs) as resp:
                text = await resp.text()

                if resp.status >= 400:
                    try:
                        error_data = json.loads(text)
                        msg = error_data.get(
                            "error_description",
                            error_data.get("msg", error_data.get("message", text)),
                        )
                    except (json.JSONDecodeError, KeyError):
                        msg = text
                    raise SupabaseAuthError(msg, status=resp.status)

                if not text:
                    return {}
                return json.loads(text)
