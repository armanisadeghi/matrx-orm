"""Level 1: MigrationLoader — discovery, deps, topological sort, checksums."""

import textwrap
from pathlib import Path

import pytest

from matrx_orm.exceptions import MigrationError
from matrx_orm.migrations.loader import MigrationLoader, _NAME_RE
from matrx_orm.migrations.state import MigrationState


@pytest.fixture
def mig_dir(tmp_path):
    return tmp_path / "migrations"


def _write_migration(mig_dir: Path, filename: str, deps: list[str] | None = None, has_down: bool = True):
    mig_dir.mkdir(parents=True, exist_ok=True)
    dep_str = repr(deps or [])
    content = textwrap.dedent(f"""\
        dependencies = {dep_str}

        async def up(db):
            pass

    """)
    if has_down:
        content += textwrap.dedent("""\
        async def down(db):
            pass
        """)
    (mig_dir / filename).write_text(content, encoding="utf-8")


class TestNameRegex:
    def test_valid_names(self):
        assert _NAME_RE.match("0001_init.py")
        assert _NAME_RE.match("0042_add_users.py")
        assert _NAME_RE.match("9999_final.py")

    def test_invalid_names(self):
        assert _NAME_RE.match("init.py") is None
        assert _NAME_RE.match("001_short.py") is None
        assert _NAME_RE.match("__init__.py") is None
        assert _NAME_RE.match("0001_init.txt") is None


class TestDiscover:
    def test_discovers_files(self, mig_dir):
        _write_migration(mig_dir, "0001_init.py")
        _write_migration(mig_dir, "0002_add_users.py", deps=["0001_init"])
        loader = MigrationLoader(mig_dir)
        migs = loader.discover()
        assert "0001_init" in migs
        assert "0002_add_users" in migs

    def test_ignores_dunder_files(self, mig_dir):
        _write_migration(mig_dir, "0001_init.py")
        (mig_dir / "__init__.py").write_text("")
        loader = MigrationLoader(mig_dir)
        migs = loader.discover()
        assert "__init__" not in migs

    def test_empty_dir(self, mig_dir):
        mig_dir.mkdir(parents=True, exist_ok=True)
        loader = MigrationLoader(mig_dir)
        assert loader.discover() == {}

    def test_nonexistent_dir(self, tmp_path):
        loader = MigrationLoader(tmp_path / "nope")
        assert loader.discover() == {}

    def test_missing_up_raises(self, mig_dir):
        mig_dir.mkdir(parents=True, exist_ok=True)
        (mig_dir / "0001_bad.py").write_text("dependencies = []\n", encoding="utf-8")
        loader = MigrationLoader(mig_dir)
        with pytest.raises(MigrationError, match="missing an 'up' function"):
            loader.discover()


class TestDependencyValidation:
    def test_missing_dependency_raises(self, mig_dir):
        _write_migration(mig_dir, "0002_orphan.py", deps=["0001_gone"])
        loader = MigrationLoader(mig_dir)
        with pytest.raises(MigrationError, match="not found"):
            loader.discover()


class TestResolveOrder:
    def test_linear_chain(self, mig_dir):
        _write_migration(mig_dir, "0001_a.py")
        _write_migration(mig_dir, "0002_b.py", deps=["0001_a"])
        _write_migration(mig_dir, "0003_c.py", deps=["0002_b"])
        loader = MigrationLoader(mig_dir)
        loader.discover()
        order = loader.resolve_order()
        assert order == ["0001_a", "0002_b", "0003_c"]

    def test_diamond_deps(self, mig_dir):
        _write_migration(mig_dir, "0001_a.py")
        _write_migration(mig_dir, "0002_b.py", deps=["0001_a"])
        _write_migration(mig_dir, "0003_c.py", deps=["0001_a"])
        _write_migration(mig_dir, "0004_d.py", deps=["0002_b", "0003_c"])
        loader = MigrationLoader(mig_dir)
        loader.discover()
        order = loader.resolve_order()
        assert order.index("0001_a") < order.index("0002_b")
        assert order.index("0001_a") < order.index("0003_c")
        assert order.index("0002_b") < order.index("0004_d")
        assert order.index("0003_c") < order.index("0004_d")

    def test_circular_dependency_raises(self, mig_dir):
        _write_migration(mig_dir, "0001_a.py", deps=["0002_b"])
        _write_migration(mig_dir, "0002_b.py", deps=["0001_a"])
        loader = MigrationLoader(mig_dir)
        loader._migrations = {}
        for filepath in sorted(mig_dir.glob("*.py")):
            name = filepath.stem
            source = filepath.read_text(encoding="utf-8")
            module = loader._load_module(filepath, name)
            from matrx_orm.migrations.loader import MigrationFile
            loader._migrations[name] = MigrationFile(
                name=name,
                path=filepath,
                dependencies=getattr(module, "dependencies", []),
                source=source,
                checksum=MigrationState.compute_checksum(source),
                up=getattr(module, "up", None),
                down=getattr(module, "down", None),
            )
        with pytest.raises(MigrationError, match="Circular"):
            loader.resolve_order()


class TestNextNumber:
    def test_first_migration(self, mig_dir):
        mig_dir.mkdir(parents=True, exist_ok=True)
        loader = MigrationLoader(mig_dir)
        assert loader.next_number() == 1

    def test_after_existing(self, mig_dir):
        _write_migration(mig_dir, "0001_init.py")
        _write_migration(mig_dir, "0002_users.py", deps=["0001_init"])
        loader = MigrationLoader(mig_dir)
        loader.discover()
        assert loader.next_number() == 3


class TestChecksum:
    def test_deterministic(self):
        source = "async def up(db):\n    pass\n"
        c1 = MigrationState.compute_checksum(source)
        c2 = MigrationState.compute_checksum(source)
        assert c1 == c2

    def test_different_content(self):
        c1 = MigrationState.compute_checksum("v1")
        c2 = MigrationState.compute_checksum("v2")
        assert c1 != c2

    def test_sha256_length(self):
        checksum = MigrationState.compute_checksum("test")
        assert len(checksum) == 64
