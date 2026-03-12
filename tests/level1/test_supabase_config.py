"""Unit tests for matrx_orm.client.supabase_config — SupabaseClientConfig.

These tests run without a database connection (level1).
"""

from __future__ import annotations

import pytest

from matrx_orm.client.supabase_config import SupabaseClientConfig


class TestSupabaseClientConfig:
    def test_valid_config(self) -> None:
        config = SupabaseClientConfig(
            url="https://abc123.supabase.co",
            anon_key="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.test",
        )
        assert config.url == "https://abc123.supabase.co"
        assert config.anon_key.startswith("eyJ")
        assert config.schema == "public"

    def test_strips_trailing_slash(self) -> None:
        config = SupabaseClientConfig(
            url="https://abc123.supabase.co/",
            anon_key="test-key",
        )
        assert config.url == "https://abc123.supabase.co"

    def test_rest_url(self) -> None:
        config = SupabaseClientConfig(
            url="https://abc123.supabase.co",
            anon_key="test-key",
        )
        assert config.rest_url == "https://abc123.supabase.co/rest/v1"

    def test_auth_url(self) -> None:
        config = SupabaseClientConfig(
            url="https://abc123.supabase.co",
            anon_key="test-key",
        )
        assert config.auth_url == "https://abc123.supabase.co/auth/v1"

    def test_default_headers(self) -> None:
        config = SupabaseClientConfig(
            url="https://abc123.supabase.co",
            anon_key="my-anon-key",
        )
        headers = config.default_headers
        assert headers["apikey"] == "my-anon-key"
        assert headers["Content-Type"] == "application/json"
        assert "Accept-Profile" not in headers  # public schema

    def test_custom_schema_headers(self) -> None:
        config = SupabaseClientConfig(
            url="https://abc123.supabase.co",
            anon_key="test-key",
            schema="auth",
        )
        headers = config.default_headers
        assert headers["Accept-Profile"] == "auth"
        assert headers["Content-Profile"] == "auth"

    def test_custom_headers_merged(self) -> None:
        config = SupabaseClientConfig(
            url="https://abc123.supabase.co",
            anon_key="test-key",
            headers={"X-Custom": "value"},
        )
        headers = config.default_headers
        assert headers["X-Custom"] == "value"
        assert headers["apikey"] == "test-key"

    def test_invalid_url_raises(self) -> None:
        with pytest.raises(ValueError, match="must start with http"):
            SupabaseClientConfig(url="abc123.supabase.co", anon_key="key")

    def test_empty_anon_key_raises(self) -> None:
        with pytest.raises(ValueError, match="anon_key is required"):
            SupabaseClientConfig(
                url="https://abc123.supabase.co", anon_key=""
            )

    def test_custom_timeout(self) -> None:
        config = SupabaseClientConfig(
            url="https://abc123.supabase.co",
            anon_key="key",
            timeout=60.0,
        )
        assert config.timeout == 60.0

    def test_custom_retries(self) -> None:
        config = SupabaseClientConfig(
            url="https://abc123.supabase.co",
            anon_key="key",
            max_retries=5,
        )
        assert config.max_retries == 5
