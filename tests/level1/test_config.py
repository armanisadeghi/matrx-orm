"""Level 1: DatabaseRegistry — registration, validation, missing fields."""

import pytest

from matrx_orm.core.config import (
    DatabaseConfigError,
    DatabaseProjectConfig,
    DatabaseRegistry,
)


@pytest.fixture(autouse=True)
def _fresh_registry():
    """Reset the singleton between tests."""
    reg = DatabaseRegistry()
    reg._configs.clear()
    reg._used_aliases.clear()
    yield reg
    reg._configs.clear()
    reg._used_aliases.clear()


def _config(name="test_project", alias="test_alias", **overrides):
    defaults = {
        "name": name,
        "host": "localhost",
        "port": "5432",
        "database_name": "testdb",
        "user": "admin",
        "password": "secret",
        "alias": alias,
    }
    defaults.update(overrides)
    return DatabaseProjectConfig(**defaults)


class TestRegisterSuccess:
    def test_basic_registration(self, _fresh_registry):
        reg = _fresh_registry
        cfg = _config()
        reg.register(cfg)
        assert "test_project" in reg._configs

    def test_get_database_config(self, _fresh_registry):
        reg = _fresh_registry
        reg.register(_config())
        result = reg.get_database_config("test_project")
        assert result["host"] == "localhost"
        assert result["port"] == "5432"
        assert result["database_name"] == "testdb"
        assert result["user"] == "admin"
        assert result["password"] == "secret"
        assert result["alias"] == "test_alias"

    def test_get_config_dataclass(self, _fresh_registry):
        reg = _fresh_registry
        cfg = _config()
        reg.register(cfg)
        assert reg.get_config_dataclass("test_project") is cfg


class TestRegisterValidation:
    def test_empty_alias_raises(self, _fresh_registry):
        with pytest.raises(DatabaseConfigError, match="alias cannot be empty"):
            _fresh_registry.register(_config(alias=""))

    def test_duplicate_alias_raises(self, _fresh_registry):
        reg = _fresh_registry
        reg.register(_config(name="p1", alias="shared"))
        with pytest.raises(DatabaseConfigError, match="already used"):
            reg.register(_config(name="p2", alias="shared"))

    def test_duplicate_name_ignored(self, _fresh_registry):
        reg = _fresh_registry
        reg.register(_config(name="dup", alias="a1"))
        reg.register(_config(name="dup", alias="a2"))
        assert reg._configs["dup"].alias == "a1"

    def test_missing_host_raises(self, _fresh_registry):
        with pytest.raises(DatabaseConfigError, match="Missing"):
            _fresh_registry.register(_config(host=""))

    def test_missing_password_raises(self, _fresh_registry):
        with pytest.raises(DatabaseConfigError, match="Missing"):
            _fresh_registry.register(_config(password=""))

    def test_missing_port_raises(self, _fresh_registry):
        with pytest.raises(DatabaseConfigError, match="Missing"):
            _fresh_registry.register(_config(port=""))


class TestGetErrors:
    def test_get_nonexistent_config(self, _fresh_registry):
        with pytest.raises(DatabaseConfigError, match="not found"):
            _fresh_registry.get_database_config("ghost")

    def test_get_nonexistent_dataclass(self, _fresh_registry):
        with pytest.raises(DatabaseConfigError, match="not found"):
            _fresh_registry.get_config_dataclass("ghost")


class TestListHelpers:
    def test_get_all_project_names(self, _fresh_registry):
        reg = _fresh_registry
        reg.register(_config(name="a", alias="a1"))
        reg.register(_config(name="b", alias="b1"))
        names = reg.get_all_database_project_names()
        assert set(names) == {"a", "b"}

    def test_get_all_configs(self, _fresh_registry):
        reg = _fresh_registry
        reg.register(_config(name="x", alias="x1"))
        all_cfgs = reg.get_all_database_configs()
        assert "x" in all_cfgs
        assert all_cfgs["x"]["alias"] == "x1"


class TestAlias:
    def test_get_database_alias(self, _fresh_registry):
        reg = _fresh_registry
        reg.register(_config(name="proj", alias="my_alias"))
        assert reg.get_database_alias("proj") == "my_alias"

    def test_get_alias_nonexistent(self, _fresh_registry):
        with pytest.raises(DatabaseConfigError, match="not found"):
            _fresh_registry.get_database_alias("nope")
