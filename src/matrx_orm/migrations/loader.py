"""Discovers migration files, parses dependencies, and builds a dependency graph."""

from __future__ import annotations

import importlib.util
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Coroutine

from matrx_orm.exceptions import MigrationError
from .state import MigrationState


@dataclass
class MigrationFile:
    name: str
    path: Path
    dependencies: list[str]
    source: str
    checksum: str
    up: Callable[..., Coroutine[Any, Any, None]] | None = None
    down: Callable[..., Coroutine[Any, Any, None]] | None = None


_NAME_RE = re.compile(r"^(\d{4})_.+\.py$")


class MigrationLoader:
    """Discovers and loads migration files from a directory."""

    def __init__(self, migrations_dir: str | Path) -> None:
        self.migrations_dir = Path(migrations_dir)
        self._migrations: dict[str, MigrationFile] = {}

    def discover(self) -> dict[str, MigrationFile]:
        """Scan the migrations directory and load all migration modules."""
        if not self.migrations_dir.exists():
            return {}

        self._migrations = {}
        for filepath in sorted(self.migrations_dir.glob("*.py")):
            if filepath.name.startswith("__"):
                continue
            match = _NAME_RE.match(filepath.name)
            if not match:
                continue

            name = filepath.stem
            source = filepath.read_text(encoding="utf-8")
            checksum = MigrationState.compute_checksum(source)

            module = self._load_module(filepath, name)

            dependencies = getattr(module, "dependencies", [])
            up_fn = getattr(module, "up", None)
            down_fn = getattr(module, "down", None)

            if up_fn is None:
                raise MigrationError(
                    migration=name,
                    original_error="Migration file is missing an 'up' function",
                )

            self._migrations[name] = MigrationFile(
                name=name,
                path=filepath,
                dependencies=list(dependencies),
                source=source,
                checksum=checksum,
                up=up_fn,
                down=down_fn,
            )

        self._validate_graph()
        return self._migrations

    @property
    def migrations(self) -> dict[str, MigrationFile]:
        if not self._migrations:
            self.discover()
        return self._migrations

    def resolve_order(self) -> list[str]:
        """Return migration names in dependency-resolved (topological) order."""
        migrations = self.migrations
        visited: set[str] = set()
        order: list[str] = []
        visiting: set[str] = set()

        def visit(name: str) -> None:
            if name in visited:
                return
            if name in visiting:
                raise MigrationError(
                    migration=name,
                    original_error=f"Circular dependency detected involving '{name}'",
                )
            visiting.add(name)
            mig = migrations.get(name)
            if mig:
                for dep in mig.dependencies:
                    visit(dep)
            visiting.discard(name)
            visited.add(name)
            order.append(name)

        for name in migrations:
            visit(name)

        return order

    def next_number(self) -> int:
        """Return the next sequential migration number."""
        migrations = self.migrations
        if not migrations:
            return 1
        numbers = []
        for name in migrations:
            match = _NAME_RE.match(name + ".py")
            if match:
                numbers.append(int(match.group(1)))
        return max(numbers) + 1 if numbers else 1

    def _load_module(self, filepath: Path, name: str) -> Any:
        """Dynamically import a migration file as a module."""
        spec = importlib.util.spec_from_file_location(f"matrx_migrations.{name}", filepath)
        if spec is None or spec.loader is None:
            raise MigrationError(
                migration=name,
                original_error=f"Could not load migration file: {filepath}",
            )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def _validate_graph(self) -> None:
        """Ensure all declared dependencies exist."""
        all_names = set(self._migrations.keys())
        for name, mig in self._migrations.items():
            for dep in mig.dependencies:
                if dep not in all_names:
                    raise MigrationError(
                        migration=name,
                        original_error=f"Dependency '{dep}' not found (referenced by '{name}')",
                    )
