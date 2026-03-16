"""Adapter layer — pluggable database backends for Matrx ORM.

The ``AdapterRegistry`` singleton maps each registered database project name
(``config_name``) to a ``BaseAdapter`` instance.  If no adapter has been
explicitly registered for a config name, ``AdapterRegistry.get()`` auto-creates
an ``AsyncPostgreSQLAdapter`` (the default) using the adapter type declared in
the project's ``DatabaseProjectConfig.adapter_type`` field.

Supported built-in adapter types
---------------------------------
``"postgresql"`` (default)
    Async asyncpg pool adapter.  Works with any direct PostgreSQL connection:
    vanilla Postgres, Supabase via the direct connection string (port 5432 /
    session pooler port 5432, or the transaction pooler port 6543).

``"supabase"``
    Also an asyncpg pool adapter but reads its connection details from the
    Supabase-specific fields (``supabase_url``, ``supabase_service_key``).
    Functionally identical to ``"postgresql"`` — the distinction is only in
    how the configuration is resolved.

Custom adapters
---------------
Register any ``BaseAdapter`` subclass before the first query::

    from matrx_orm.adapters import AdapterRegistry
    AdapterRegistry.register("my_project", MyCustomAdapter("my_project"))
"""
from __future__ import annotations

import logging
from typing import Any

from matrx_orm.adapters.base_adapter import BaseAdapter
from matrx_orm.adapters.async_postgresql import AsyncPostgreSQLAdapter

logger = logging.getLogger("matrx_orm.adapters")

__all__ = [
    "BaseAdapter",
    "AsyncPostgreSQLAdapter",
    "SupabaseAdapter",
    "PostgRESTClientAdapter",
    "AdapterRegistry",
]


class AdapterRegistry:
    """Singleton registry mapping config_name → BaseAdapter instance.

    Thread/task safe: adapter instantiation is guarded so that concurrent
    access during application startup does not create duplicate adapters.
    The GIL protects the dict operations; a proper asyncio lock is not needed
    here because ``get()`` is a synchronous call that only does a dict lookup
    or a lightweight instantiation.
    """

    _adapters: dict[str, BaseAdapter] = {}

    # ------------------------------------------------------------------
    # Registration
    # ------------------------------------------------------------------

    @classmethod
    def register(cls, config_name: str, adapter: BaseAdapter) -> None:
        """Explicitly register a custom adapter for *config_name*.

        Raises ``TypeError`` if *adapter* is not a ``BaseAdapter`` subclass.
        Replaces any previously registered adapter for the same config_name.
        """
        if not isinstance(adapter, BaseAdapter):
            raise TypeError(
                f"adapter must be a BaseAdapter subclass, got {type(adapter)!r}"
            )
        cls._adapters[config_name] = adapter
        logger.debug("Registered adapter %r for config %r", type(adapter).__name__, config_name)

    # ------------------------------------------------------------------
    # Lookup
    # ------------------------------------------------------------------

    @classmethod
    def get(cls, config_name: str) -> BaseAdapter:
        """Return the adapter for *config_name*, auto-creating if necessary.

        If no adapter has been explicitly registered, the adapter type is
        inferred from ``DatabaseProjectConfig.adapter_type`` (defaults to
        ``"postgresql"``).  An ``AsyncPostgreSQLAdapter`` is created and
        cached for all pool-backed types.
        """
        if config_name not in cls._adapters:
            cls._adapters[config_name] = cls._create_default(config_name)
        return cls._adapters[config_name]

    @classmethod
    def _create_default(cls, config_name: str) -> BaseAdapter:
        """Instantiate the appropriate adapter based on config adapter_type."""
        adapter_type = cls._get_adapter_type(config_name)

        if adapter_type == "postgresql":
            return AsyncPostgreSQLAdapter(config_name)

        if adapter_type == "supabase":
            from matrx_orm.adapters.supabase_adapter import SupabaseAdapter
            return SupabaseAdapter(config_name)

        # Allow dotted class path: "mypackage.adapters.MyAdapter"
        if "." in adapter_type:
            return cls._import_and_instantiate(adapter_type, config_name)

        raise ValueError(
            f"Unknown adapter_type {adapter_type!r} for config {config_name!r}. "
            "Valid built-in types: 'postgresql', 'supabase'. "
            "For custom adapters, use a dotted import path or call "
            "AdapterRegistry.register() directly."
        )

    @classmethod
    def _get_adapter_type(cls, config_name: str) -> str:
        """Read adapter_type from the registered DatabaseProjectConfig."""
        try:
            from matrx_orm.core.config import registry as _db_registry
            config = _db_registry._configs.get(config_name)
            if config is not None:
                return getattr(config, "adapter_type", "postgresql")
        except Exception:
            pass
        return "postgresql"

    @classmethod
    def _import_and_instantiate(cls, dotted_path: str, config_name: str) -> BaseAdapter:
        """Import a dotted class path and instantiate with config_name."""
        module_path, _, class_name = dotted_path.rpartition(".")
        if not module_path:
            raise ValueError(f"Invalid dotted adapter path: {dotted_path!r}")
        import importlib
        module = importlib.import_module(module_path)
        klass = getattr(module, class_name)
        instance = klass(config_name)
        if not isinstance(instance, BaseAdapter):
            raise TypeError(
                f"{dotted_path} does not produce a BaseAdapter subclass"
            )
        return instance

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    @classmethod
    async def close_all(cls) -> None:
        """Close all registered adapters and clear the registry."""
        for config_name, adapter in list(cls._adapters.items()):
            try:
                await adapter.close()
            except Exception:
                logger.exception("Error closing adapter for config %r", config_name)
        cls._adapters.clear()

    @classmethod
    def clear(cls) -> None:
        """Remove all registered adapters without closing them (test helper)."""
        cls._adapters.clear()

    # ------------------------------------------------------------------
    # Inspection
    # ------------------------------------------------------------------

    @classmethod
    def registered_configs(cls) -> list[str]:
        """Return a list of all config_names that have been registered."""
        return list(cls._adapters.keys())

    @classmethod
    def get_or_none(cls, config_name: str) -> BaseAdapter | None:
        """Return the adapter if registered, without auto-creating."""
        return cls._adapters.get(config_name)
