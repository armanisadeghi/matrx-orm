"""Unit tests for matrx_orm.client.supabase_auth — AuthSession.

Tests the AuthSession data class and token expiry logic.
Network-dependent tests (sign_in, sign_up) are in level2.
"""

from __future__ import annotations

import time

import pytest

from matrx_orm.client.supabase_auth import AuthSession, SupabaseAuthError


class TestAuthSession:
    def test_from_response(self) -> None:
        data = {
            "access_token": "eyJ.test.token",
            "refresh_token": "refresh-abc",
            "expires_in": 3600,
            "user": {
                "id": "user-123",
                "email": "alice@example.com",
                "user_metadata": {"name": "Alice"},
            },
        }
        session = AuthSession.from_response(data)
        assert session.access_token == "eyJ.test.token"
        assert session.refresh_token == "refresh-abc"
        assert session.user_id == "user-123"
        assert session.email == "alice@example.com"
        assert session.user_metadata == {"name": "Alice"}

    def test_not_expired(self) -> None:
        session = AuthSession(
            access_token="token",
            refresh_token="refresh",
            expires_at=time.time() + 3600,
            user_id="user-123",
            email="test@test.com",
            user_metadata={},
        )
        assert session.is_expired is False

    def test_expired(self) -> None:
        session = AuthSession(
            access_token="token",
            refresh_token="refresh",
            expires_at=time.time() - 100,
            user_id="user-123",
            email="test@test.com",
            user_metadata={},
        )
        assert session.is_expired is True

    def test_expired_within_buffer(self) -> None:
        # 30 seconds from now, but 60s buffer means it's "expired"
        session = AuthSession(
            access_token="token",
            refresh_token="refresh",
            expires_at=time.time() + 30,
            user_id="user-123",
            email="test@test.com",
            user_metadata={},
        )
        assert session.is_expired is True

    def test_from_response_missing_user(self) -> None:
        data = {
            "access_token": "token",
            "expires_in": 3600,
        }
        session = AuthSession.from_response(data)
        assert session.access_token == "token"
        assert session.user_id == ""
        assert session.email == ""


class TestSupabaseAuthError:
    def test_error_message(self) -> None:
        err = SupabaseAuthError("Invalid credentials", status=401)
        assert err.message == "Invalid credentials"
        assert err.status == 401
        assert str(err) == "Invalid credentials"
