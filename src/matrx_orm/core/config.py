from dataclasses import dataclass, field
from typing import Dict


class DatabaseConfigError(Exception):
    pass


@dataclass
class DatabaseProjectConfig:
    # Basics for project
    name: str
    host: str
    port: str
    database_name: str
    user: str
    password: str

    # Config section related to file saving, manager override : dto , manager creation
    code_basics: Dict = field(default_factory=dict)
    manager_config_overrides: Dict = field(default_factory=dict)


class DatabaseRegistry:
    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseRegistry, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self._configs: Dict[str, DatabaseProjectConfig] = {}
            self._initialized = True

    def register(self, config: DatabaseProjectConfig) -> None:
        if config.name in self._configs:
            raise DatabaseConfigError(f"Database configuration '{config.name}' already registered")

        required_fields = [config.host, config.port, config.database_name, config.user, config.password]
        if not all(required_fields):
            missing = []
            if not config.host: missing.append("host")
            if not config.port: missing.append("port")
            if not config.database_name: missing.append("database_name")
            if not config.user: missing.append("user")
            if not config.password: missing.append("password")
            raise DatabaseConfigError(
                f"Missing required configuration fields for '{config.name}': " f"{', '.join(missing)}. Please check your environment variables.")

        self._configs[config.name] = config

    def get_database_config(self, config_name: str) -> dict:
        if config_name not in self._configs:
            raise DatabaseConfigError(f"Configuration '{config_name}' not found in registered databases")

        config = self._configs[config_name]
        return {
            "host": config.host,
            "port": config.port,
            "database_name": config.database_name,
            "user": config.user,
            "password": config.password
        }

    def get_config_dataclass(self, config_name: str) -> DatabaseProjectConfig:
        if config_name not in self._configs:
            raise DatabaseConfigError(f"Configuration '{config_name}' not found in registered databases")
        return self._configs[config_name]

    def get_code_config_by_project_name(self, config_name):
        if config_name not in self._configs:
            raise DatabaseConfigError(f"Configuration '{config_name}' not found in registered databases")
        config = self._configs[config_name]
        return config.code_basics

    def get_manager_config_by_project_name(self, config_name):
        if config_name not in self._configs:
            raise DatabaseConfigError(f"Configuration '{config_name}' not found in registered databases")
        config = self._configs[config_name]
        return config.manager_config_overrides


registry = DatabaseRegistry()


def get_database_config(config_name: str) -> dict:
    return registry.get_database_config(config_name)


def get_code_config(config_name: str) -> dict:
    return registry.get_code_config_by_project_name(config_name)


def get_manager_config(config_name: str) -> dict:
    return registry.get_manager_config_by_project_name(config_name)


def register_database(config: DatabaseProjectConfig) -> None:
    registry.register(config)


def get_connection_string(config_name: str) -> str:
    config = get_database_config(config_name)
    connection_string = f"postgresql://{config['user']}:{config['password']}@{config['host']}:{config['port']}/{config['database_name']}"
    return connection_string
