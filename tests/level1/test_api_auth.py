"""Unit tests for matrx_orm.api.auth — Token issuance and validation.

These tests run without a database connection (level1).
"""

from __future__ import annotations

import time

import pytest

from matrx_orm.api.auth import AuthError, TokenAuth, TokenPayload


@pytest.fixture
def auth() -> TokenAuth:
    return TokenAuth(secret="test-secret-key", ttl=3600)


class TestTokenIssuance:
    def test_issue_token_returns_string(self, auth: TokenAuth) -> None:
        token = auth.issue_token()
        assert isinstance(token, str)
        assert "." in token

    def test_token_format(self, auth: TokenAuth) -> None:
        token = auth.issue_token()
        parts = token.split(".")
        assert len(parts) == 2
        # First part is base64, second is hex signature
        assert len(parts[1]) == 64  # SHA-256 hex digest

    def test_custom_client_id(self, auth: TokenAuth) -> None:
        token = auth.issue_token(client_id="electron")
        payload = auth.validate_token(token)
        assert payload.client_id == "electron"

    def test_custom_scopes(self, auth: TokenAuth) -> None:
        token = auth.issue_token(scopes=["users.read", "notes.write"])
        payload = auth.validate_token(token)
        assert payload.scopes == ["users.read", "notes.write"]

    def test_default_scopes_wildcard(self, auth: TokenAuth) -> None:
        token = auth.issue_token()
        payload = auth.validate_token(token)
        assert payload.scopes == ["*"]

    def test_custom_ttl(self, auth: TokenAuth) -> None:
        token = auth.issue_token(ttl=60)
        payload = auth.validate_token(token)
        assert payload.expires_at - payload.issued_at == pytest.approx(60, abs=1)


class TestTokenValidation:
    def test_valid_token(self, auth: TokenAuth) -> None:
        token = auth.issue_token()
        payload = auth.validate_token(token)
        assert isinstance(payload, TokenPayload)
        assert payload.client_id == "desktop"

    def test_malformed_token_no_dot(self, auth: TokenAuth) -> None:
        with pytest.raises(AuthError, match="Malformed token"):
            auth.validate_token("nodothere")

    def test_malformed_token_too_many_dots(self, auth: TokenAuth) -> None:
        with pytest.raises(AuthError, match="Malformed token"):
            auth.validate_token("a.b.c")

    def test_invalid_signature(self, auth: TokenAuth) -> None:
        token = auth.issue_token()
        payload_b64, _ = token.split(".")
        bad_token = f"{payload_b64}.{'0' * 64}"
        with pytest.raises(AuthError, match="Invalid token signature"):
            auth.validate_token(bad_token)

    def test_wrong_secret_fails(self) -> None:
        auth1 = TokenAuth(secret="secret-one", ttl=3600)
        auth2 = TokenAuth(secret="secret-two", ttl=3600)
        token = auth1.issue_token()
        with pytest.raises(AuthError, match="Invalid token signature"):
            auth2.validate_token(token)

    def test_expired_token(self) -> None:
        auth = TokenAuth(secret="test", ttl=0)
        token = auth.issue_token(ttl=0)
        # Token expires immediately
        time.sleep(0.01)
        with pytest.raises(AuthError, match="Token has expired"):
            auth.validate_token(token)

    def test_corrupt_payload(self, auth: TokenAuth) -> None:
        import base64
        import hashlib
        import hmac

        bad_payload = b"not-json"
        payload_b64 = base64.urlsafe_b64encode(bad_payload).decode()
        sig = hmac.new(
            b"test-secret-key", bad_payload, hashlib.sha256
        ).hexdigest()
        with pytest.raises(AuthError, match="Corrupt token payload"):
            auth.validate_token(f"{payload_b64}.{sig}")


class TestTokenRevocation:
    def test_revoke_token(self, auth: TokenAuth) -> None:
        token = auth.issue_token()
        # Valid before revocation
        auth.validate_token(token)
        # Revoke
        auth.revoke_token(token)
        # Invalid after revocation
        with pytest.raises(AuthError, match="revoked"):
            auth.validate_token(token)

    def test_revoke_invalid_token_no_error(self, auth: TokenAuth) -> None:
        # Should not raise
        auth.revoke_token("garbage-token")


class TestScopeChecking:
    def test_wildcard_scope_allows_all(self, auth: TokenAuth) -> None:
        token = auth.issue_token(scopes=["*"])
        payload = auth.validate_token(token)
        assert auth.check_scope(payload, "users.read") is True
        assert auth.check_scope(payload, "anything") is True

    def test_specific_scope(self, auth: TokenAuth) -> None:
        token = auth.issue_token(scopes=["users.read", "notes.write"])
        payload = auth.validate_token(token)
        assert auth.check_scope(payload, "users.read") is True
        assert auth.check_scope(payload, "notes.write") is True
        assert auth.check_scope(payload, "users.delete") is False
