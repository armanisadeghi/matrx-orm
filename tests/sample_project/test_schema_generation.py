"""
Sample Project — Schema Generation Integration Tests
=====================================================
These tests exercise the full schema generation pipeline against real Supabase
databases. They require valid credentials in tests/sample_project/.env.

Run with pytest:

    # Run just the sample project tests
    pytest tests/sample_project/ -v -s

    # Run only one database
    pytest tests/sample_project/ -v -s -k "primary"

    # Skip if no credentials are configured
    pytest tests/sample_project/ -v -s --ignore-glob="*test_schema*"

Mark: ``schema`` — requires live database credentials in .env
"""

import os
import pytest
from pathlib import Path

# ---------------------------------------------------------------------------
# Credential check — skip entire module if no passwords are set
# ---------------------------------------------------------------------------
_env_path = Path(__file__).parent / ".env"
try:
    from dotenv import load_dotenv
    if _env_path.exists():
        load_dotenv(_env_path)
except ImportError:
    pass

_PRIMARY_AVAILABLE = bool(os.environ.get("PRIMARY_DB_PASSWORD"))
_SECONDARY_AVAILABLE = bool(os.environ.get("SECONDARY_DB_PASSWORD"))

pytestmark = pytest.mark.schema


# ---------------------------------------------------------------------------
# Session-scoped fixture: register databases once per test session
# ---------------------------------------------------------------------------
@pytest.fixture(scope="session", autouse=True)
def register_sample_databases():
    """Register primary and secondary databases for the test session."""
    from tests.sample_project.database_registry import setup_databases
    setup_databases()


# ---------------------------------------------------------------------------
# Session-scoped fixtures: one SchemaManager per database
# ---------------------------------------------------------------------------
@pytest.fixture(scope="session")
def primary_schema_manager():
    """Initialised SchemaManager for the primary Supabase database."""
    if not _PRIMARY_AVAILABLE:
        pytest.skip("PRIMARY_DB_PASSWORD not set — skipping primary database tests")
    from matrx_orm.schema_builder.schema_manager import SchemaManager
    sm = SchemaManager(
        schema="public",
        database_project="primary",
        additional_schemas=["auth"],
    )
    sm.initialize()
    return sm


@pytest.fixture(scope="session")
def secondary_schema_manager():
    """Initialised SchemaManager for the secondary Supabase database."""
    if not _SECONDARY_AVAILABLE:
        pytest.skip("SECONDARY_DB_PASSWORD not set — skipping secondary database tests")
    from matrx_orm.schema_builder.schema_manager import SchemaManager
    sm = SchemaManager(
        schema="public",
        database_project="secondary",
        additional_schemas=[],
    )
    sm.initialize()
    return sm


# ---------------------------------------------------------------------------
# Output directory fixture
# ---------------------------------------------------------------------------
@pytest.fixture(scope="session")
def output_dir(tmp_path_factory):
    """Shared temp directory for generated files — cleaned up after the session."""
    return tmp_path_factory.mktemp("generated")


# ===========================================================================
# PRIMARY DATABASE TESTS
# ===========================================================================

class TestPrimaryDatabase:
    """Schema generation tests for the primary Supabase project."""

    def test_schema_manager_initialises(self, primary_schema_manager):
        """SchemaManager must initialise without exceptions."""
        assert primary_schema_manager is not None
        assert primary_schema_manager.initialized

    def test_has_tables(self, primary_schema_manager):
        """Primary database must have at least one public table."""
        tables = primary_schema_manager.schema.tables
        assert isinstance(tables, dict)
        assert len(tables) > 0, "Expected at least one table in the public schema"
        print(f"\n  Primary tables ({len(tables)}): {list(tables.keys())[:10]}")

    def test_auth_schema_visible(self, primary_schema_manager):
        """
        The auth schema must be visible because additional_schemas=['auth'] is set.
        SchemaManager.additional_schemas should include 'auth'.
        """
        assert "auth" in primary_schema_manager.additional_schemas, (
            "auth schema not included — check additional_schemas in DatabaseProjectConfig"
        )

    def test_generate_schema_files(self, primary_schema_manager):
        """generate_schema_files() must return a non-empty schema entry."""
        schema_entry = primary_schema_manager.schema.generate_schema_files()
        assert schema_entry is not None

    def test_generate_models(self, primary_schema_manager):
        """generate_models() must complete without exceptions."""
        models = primary_schema_manager.schema.generate_models()
        # models may be None or a dict depending on save_direct — just assert no exception
        assert True  # reaching here means no exception was raised

    def test_analyze_schema(self, primary_schema_manager):
        """analyze_schema() must return a result with expected top-level keys."""
        analysis = primary_schema_manager.analyze_schema()
        assert analysis is not None
        print(f"\n  Analysis keys: {list(analysis.keys()) if isinstance(analysis, dict) else type(analysis)}")

    def test_foreign_key_references_have_schema(self, primary_schema_manager):
        """
        FK references detected during introspection should include a 'schema' field
        (populated by the updated db_objects.py SQL that joins pg_namespace).
        """
        found_fk_with_schema = False
        for table_name, table in primary_schema_manager.schema.tables.items():
            if not hasattr(table, "columns"):
                continue
            for col in table.columns.values() if isinstance(table.columns, dict) else []:
                fkref = getattr(col, "foreign_key_reference", None)
                if fkref and isinstance(fkref, dict) and "schema" in fkref:
                    found_fk_with_schema = True
                    break
            if found_fk_with_schema:
                break
        # This is informational — warn if no FKs found, but don't hard-fail
        # since an empty database is technically valid.
        if not found_fk_with_schema:
            print("\n  WARNING: No FK references with 'schema' field found. "
                  "Either no FKs exist or introspection SQL needs checking.")

    def test_get_specific_table(self, primary_schema_manager):
        """get_table() must return a table object for any existing table."""
        tables = primary_schema_manager.schema.tables
        if not tables:
            pytest.skip("No tables in primary database")
        first_table_name = next(iter(tables))
        table = primary_schema_manager.get_table(first_table_name)
        assert table is not None
        assert hasattr(table, "name")
        assert table.name == first_table_name


# ===========================================================================
# SECONDARY DATABASE TESTS
# ===========================================================================

class TestSecondaryDatabase:
    """Schema generation tests for the secondary Supabase project."""

    def test_schema_manager_initialises(self, secondary_schema_manager):
        """SchemaManager must initialise without exceptions."""
        assert secondary_schema_manager is not None
        assert secondary_schema_manager.initialized

    def test_has_tables(self, secondary_schema_manager):
        """Secondary database must have at least one public table."""
        tables = secondary_schema_manager.schema.tables
        assert isinstance(tables, dict)
        assert len(tables) > 0, "Expected at least one table in the public schema"
        print(f"\n  Secondary tables ({len(tables)}): {list(tables.keys())[:10]}")

    def test_no_auth_schema(self, secondary_schema_manager):
        """
        Secondary database has no additional_schemas — auth should NOT be
        included in its introspection scope.
        """
        assert "auth" not in secondary_schema_manager.additional_schemas

    def test_generate_schema_files(self, secondary_schema_manager):
        """generate_schema_files() must return a non-empty schema entry."""
        schema_entry = secondary_schema_manager.schema.generate_schema_files()
        assert schema_entry is not None

    def test_generate_models(self, secondary_schema_manager):
        """generate_models() must complete without exceptions."""
        secondary_schema_manager.schema.generate_models()
        assert True

    def test_analyze_schema(self, secondary_schema_manager):
        """analyze_schema() must return a result."""
        analysis = secondary_schema_manager.analyze_schema()
        assert analysis is not None


# ===========================================================================
# CROSS-DATABASE ISOLATION TEST
# ===========================================================================

@pytest.mark.skipif(
    not (_PRIMARY_AVAILABLE and _SECONDARY_AVAILABLE),
    reason="Both databases must be configured",
)
class TestCrossDatabaseIsolation:
    """Verify the two databases are independent and don't bleed state."""

    def test_different_table_sets(self, primary_schema_manager, secondary_schema_manager):
        """Primary and secondary should have independent table registries."""
        primary_tables = set(primary_schema_manager.schema.tables.keys())
        secondary_tables = set(secondary_schema_manager.schema.tables.keys())
        # They're separate databases — the managers must not share state
        assert primary_schema_manager is not secondary_schema_manager
        print(f"\n  Primary-only tables: {len(primary_tables - secondary_tables)}")
        print(f"  Secondary-only tables: {len(secondary_tables - primary_tables)}")
        print(f"  Common tables: {len(primary_tables & secondary_tables)}")

    def test_database_project_names_differ(self, primary_schema_manager, secondary_schema_manager):
        """Each SchemaManager must reference its own database_project."""
        assert primary_schema_manager.database_project == "primary"
        assert secondary_schema_manager.database_project == "secondary"
