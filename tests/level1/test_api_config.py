"""Unit tests for matrx_orm.api.config — APIConfig validation.

These tests run without a database connection (level1).
"""

from __future__ import annotations

import warnings

import pytest

from matrx_orm.api.config import APIConfig


class TestAPIConfig:
    def test_defaults(self) -> None:
        config = APIConfig()
        assert config.host == "127.0.0.1"
        assert config.port == 8745
        assert config.token_ttl == 86400
        assert config.enable_websocket is True

    def test_auto_generates_secret(self) -> None:
        config = APIConfig()
        assert len(config.secret) > 20
        assert config._auto_generated_secret is True

    def test_explicit_secret(self) -> None:
        config = APIConfig(secret="my-secret")
        assert config.secret == "my-secret"
        assert config._auto_generated_secret is False

    def test_unique_secrets(self) -> None:
        c1 = APIConfig()
        c2 = APIConfig()
        assert c1.secret != c2.secret

    def test_non_localhost_warning(self) -> None:
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            APIConfig(host="0.0.0.0")
            assert len(w) == 1
            assert "non-local address" in str(w[0].message)

    def test_localhost_no_warning(self) -> None:
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            APIConfig(host="127.0.0.1")
            assert len(w) == 0

    def test_custom_cors_origins(self) -> None:
        config = APIConfig(cors_origins=["http://myapp.local:4000"])
        assert config.cors_origins == ["http://myapp.local:4000"]

    def test_custom_port(self) -> None:
        config = APIConfig(port=9999)
        assert config.port == 9999
