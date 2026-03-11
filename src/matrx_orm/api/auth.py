"""Token-based authentication for localhost API communication.

Uses HMAC-SHA256 signed tokens. Tokens are short-lived, self-contained,
and validated entirely on the server — no external auth service needed.

Typical flow:
1. Desktop app launches the Python backend.
2. Python backend starts the API server, which prints or writes the shared
   secret to a known location.
3. Desktop app reads the secret and calls ``POST /auth/token`` with the
   secret to obtain a signed bearer token.
4. All subsequent requests include ``Authorization: Bearer <token>``.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import secrets
import time
from dataclasses import dataclass


@dataclass
class TokenPayload:
    """Decoded token contents."""

    client_id: str
    issued_at: float
    expires_at: float
    scopes: list[str]


class TokenAuth:
    """HMAC-SHA256 token issuer and validator.

    Parameters
    ----------
    secret : str
        The shared secret for signing tokens.
    ttl : int
        Default token lifetime in seconds.
    """

    def __init__(self, secret: str, ttl: int = 86400) -> None:
        self._secret = secret.encode("utf-8")
        self._ttl = ttl
        self._revoked: set[str] = set()

    def issue_token(
        self,
        client_id: str = "desktop",
        scopes: list[str] | None = None,
        ttl: int | None = None,
    ) -> str:
        """Create a new signed token.

        Parameters
        ----------
        client_id : str
            Identifier for the client (e.g. ``"electron"``, ``"tauri"``).
        scopes : list[str] | None
            Permission scopes. Defaults to ``["*"]`` (full access).
        ttl : int | None
            Override the default TTL for this token.

        Returns
        -------
        str
            ``<base64-payload>.<hex-signature>``
        """
        now = time.time()
        payload = {
            "cid": client_id,
            "iat": now,
            "exp": now + (ttl or self._ttl),
            "scp": scopes or ["*"],
            "jti": secrets.token_hex(8),
        }
        payload_bytes = json.dumps(payload, separators=(",", ":")).encode("utf-8")

        import base64

        payload_b64 = base64.urlsafe_b64encode(payload_bytes).decode("ascii")
        sig = hmac.new(self._secret, payload_bytes, hashlib.sha256).hexdigest()
        return f"{payload_b64}.{sig}"

    def validate_token(self, token: str) -> TokenPayload:
        """Validate a token and return its payload.

        Raises
        ------
        AuthError
            If the token is malformed, expired, revoked, or has an invalid
            signature.
        """
        parts = token.split(".")
        if len(parts) != 2:
            raise AuthError("Malformed token")

        payload_b64, sig = parts

        import base64

        try:
            payload_bytes = base64.urlsafe_b64decode(payload_b64)
        except Exception as exc:
            raise AuthError("Malformed token payload") from exc

        expected_sig = hmac.new(
            self._secret, payload_bytes, hashlib.sha256
        ).hexdigest()
        if not hmac.compare_digest(sig, expected_sig):
            raise AuthError("Invalid token signature")

        try:
            data = json.loads(payload_bytes)
        except json.JSONDecodeError as exc:
            raise AuthError("Corrupt token payload") from exc

        jti = data.get("jti", "")
        if jti in self._revoked:
            raise AuthError("Token has been revoked")

        exp = data.get("exp", 0)
        if time.time() > exp:
            raise AuthError("Token has expired")

        return TokenPayload(
            client_id=data.get("cid", "unknown"),
            issued_at=data.get("iat", 0),
            expires_at=exp,
            scopes=data.get("scp", []),
        )

    def revoke_token(self, token: str) -> None:
        """Revoke a token so it can no longer be used."""
        try:
            parts = token.split(".")
            if len(parts) == 2:
                import base64

                payload_bytes = base64.urlsafe_b64decode(parts[0])
                data = json.loads(payload_bytes)
                jti = data.get("jti", "")
                if jti:
                    self._revoked.add(jti)
        except Exception:
            pass

    def check_scope(self, payload: TokenPayload, required: str) -> bool:
        """Check if a token has a required scope."""
        if "*" in payload.scopes:
            return True
        return required in payload.scopes


class AuthError(Exception):
    """Raised when authentication fails."""

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)
