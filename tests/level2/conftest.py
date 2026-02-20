"""Level 2 fixtures: DB connection, model registration, seed data, cleanup."""

import asyncio
import os
from uuid import uuid4

import pytest

from matrx_orm.core.config import (
    DatabaseProjectConfig,
    DatabaseRegistry,
    register_database,
)
from matrx_orm.core.fields import (
    BooleanField,
    CharField,
    DateTimeField,
    ForeignKey,
    IntegerField,
    JSONField,
    TextField,
    UUIDField,
)
from matrx_orm.core.base import Model, ModelMeta
from matrx_orm.core.registry import ModelRegistry
from matrx_orm.core.async_db_manager import AsyncDatabaseManager
from matrx_orm.core.relations import ManyToManyReference
from matrx_orm.migrations.operations import MigrationDB
from matrx_orm.state import CachePolicy, StateManager


DB_PROJECT_NAME = "matrx_test"


def _env(key: str, default: str = "") -> str:
    return os.environ.get(key, default)


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def db_config():
    """Register a test database from environment variables."""
    reg = DatabaseRegistry()
    if DB_PROJECT_NAME in reg._configs:
        return DB_PROJECT_NAME

    config = DatabaseProjectConfig(
        name=DB_PROJECT_NAME,
        host=_env("MATRX_TEST_DB_HOST", "localhost"),
        port=_env("MATRX_TEST_DB_PORT", "5432"),
        database_name=_env("MATRX_TEST_DB_NAME", "matrx_test"),
        user=_env("MATRX_TEST_DB_USER", "postgres"),
        password=_env("MATRX_TEST_DB_PASSWORD", "postgres"),
        alias=_env("MATRX_TEST_DB_ALIAS", "matrx_test"),
    )
    register_database(config)
    return DB_PROJECT_NAME


@pytest.fixture(scope="session")
def migration_db(db_config):
    return MigrationDB(db_config)


# ---------------------------------------------------------------------------
# Test models — created dynamically so they don't pollute the global registry
# ---------------------------------------------------------------------------

_MODELS_CREATED = False


def _create_test_models():
    global _MODELS_CREATED
    if _MODELS_CREATED:
        return
    _MODELS_CREATED = True

    ModelMeta("TestUser", (Model,), {
        "id": UUIDField(primary_key=True),
        "username": CharField(max_length=100, unique=True),
        "email": CharField(max_length=255),
        "bio": TextField(null=True),
        "is_active": BooleanField(default=True),
        "age": IntegerField(null=True),
        "_database": DB_PROJECT_NAME,
        "_table_name": "test_user",
    })

    ModelMeta("TestPost", (Model,), {
        "id": UUIDField(primary_key=True),
        "title": CharField(max_length=200),
        "body": TextField(null=True),
        "author_id": ForeignKey(to_model="TestUser", to_column="id"),
        "metadata": JSONField(null=True),
        "is_published": BooleanField(default=False),
        "_database": DB_PROJECT_NAME,
        "_table_name": "test_post",
    })

    ModelMeta("TestTag", (Model,), {
        "id": UUIDField(primary_key=True),
        "name": CharField(max_length=50, unique=True),
        "_database": DB_PROJECT_NAME,
        "_table_name": "test_tag",
    })

    ModelMeta("TestCategory", (Model,), {
        "id": UUIDField(primary_key=True),
        "name": CharField(max_length=100),
        "parent_id": ForeignKey(to_model="TestCategory", to_column="id", null=True),
        "_database": DB_PROJECT_NAME,
        "_table_name": "test_category",
    })

    ModelMeta("TestProfile", (Model,), {
        "id": UUIDField(primary_key=True),
        "user_id": ForeignKey(to_model="TestUser", to_column="id"),
        "display_name": CharField(max_length=100, null=True),
        "settings": JSONField(null=True),
        "_database": DB_PROJECT_NAME,
        "_table_name": "test_profile",
    })


SEED_SCHEMA_SQL = """
DROP TABLE IF EXISTS test_post_tag CASCADE;
DROP TABLE IF EXISTS test_profile CASCADE;
DROP TABLE IF EXISTS test_post CASCADE;
DROP TABLE IF EXISTS test_category CASCADE;
DROP TABLE IF EXISTS test_tag CASCADE;
DROP TABLE IF EXISTS test_user CASCADE;
DROP TABLE IF EXISTS _matrx_migrations CASCADE;

CREATE TABLE test_user (
    id UUID PRIMARY KEY,
    username VARCHAR(100) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL,
    bio TEXT,
    is_active BOOLEAN DEFAULT true,
    age INTEGER
);

CREATE TABLE test_post (
    id UUID PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    body TEXT,
    author_id UUID NOT NULL REFERENCES test_user(id) ON DELETE CASCADE,
    metadata JSONB,
    is_published BOOLEAN DEFAULT false
);

CREATE TABLE test_tag (
    id UUID PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE
);

CREATE TABLE test_post_tag (
    post_id UUID NOT NULL REFERENCES test_post(id) ON DELETE CASCADE,
    tag_id UUID NOT NULL REFERENCES test_tag(id) ON DELETE CASCADE,
    PRIMARY KEY (post_id, tag_id)
);

CREATE TABLE test_category (
    id UUID PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    parent_id UUID REFERENCES test_category(id) ON DELETE SET NULL
);

CREATE TABLE test_profile (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL UNIQUE REFERENCES test_user(id) ON DELETE CASCADE,
    display_name VARCHAR(100),
    settings JSONB
);
"""


SEED_USER_IDS = [str(uuid4()) for _ in range(5)]
SEED_TAG_IDS = [str(uuid4()) for _ in range(3)]
SEED_POST_IDS = [str(uuid4()) for _ in range(5)]
SEED_CATEGORY_IDS = [str(uuid4()) for _ in range(3)]
SEED_PROFILE_IDS = [str(uuid4()) for _ in range(3)]


SEED_DATA_SQL = f"""
INSERT INTO test_user (id, username, email, bio, is_active, age) VALUES
    ('{SEED_USER_IDS[0]}', 'alice', 'alice@test.com', 'Alice bio', true, 30),
    ('{SEED_USER_IDS[1]}', 'bob', 'bob@test.com', 'Bob bio', true, 25),
    ('{SEED_USER_IDS[2]}', 'charlie', 'charlie@test.com', NULL, true, 40),
    ('{SEED_USER_IDS[3]}', 'diana', 'diana@test.com', 'Diana bio', false, 35),
    ('{SEED_USER_IDS[4]}', 'eve', 'eve@test.com', 'Eve bio', true, 28);

INSERT INTO test_tag (id, name) VALUES
    ('{SEED_TAG_IDS[0]}', 'python'),
    ('{SEED_TAG_IDS[1]}', 'orm'),
    ('{SEED_TAG_IDS[2]}', 'testing');

INSERT INTO test_post (id, title, body, author_id, metadata, is_published) VALUES
    ('{SEED_POST_IDS[0]}', 'First Post', 'Hello world', '{SEED_USER_IDS[0]}', '{{"views": 100}}', true),
    ('{SEED_POST_IDS[1]}', 'Second Post', 'Another post', '{SEED_USER_IDS[0]}', NULL, false),
    ('{SEED_POST_IDS[2]}', 'Bobs Post', 'Content here', '{SEED_USER_IDS[1]}', '{{"views": 50}}', true),
    ('{SEED_POST_IDS[3]}', 'Draft Post', NULL, '{SEED_USER_IDS[2]}', NULL, false),
    ('{SEED_POST_IDS[4]}', 'Published', 'Great content', '{SEED_USER_IDS[3]}', '{{"views": 200}}', true);

INSERT INTO test_post_tag (post_id, tag_id) VALUES
    ('{SEED_POST_IDS[0]}', '{SEED_TAG_IDS[0]}'),
    ('{SEED_POST_IDS[0]}', '{SEED_TAG_IDS[1]}'),
    ('{SEED_POST_IDS[2]}', '{SEED_TAG_IDS[2]}');

INSERT INTO test_category (id, name, parent_id) VALUES
    ('{SEED_CATEGORY_IDS[0]}', 'Tech', NULL),
    ('{SEED_CATEGORY_IDS[1]}', 'Python', '{SEED_CATEGORY_IDS[0]}'),
    ('{SEED_CATEGORY_IDS[2]}', 'Web', '{SEED_CATEGORY_IDS[0]}');

INSERT INTO test_profile (id, user_id, display_name, settings) VALUES
    ('{SEED_PROFILE_IDS[0]}', '{SEED_USER_IDS[0]}', 'Alice D', '{{"theme": "dark"}}'),
    ('{SEED_PROFILE_IDS[1]}', '{SEED_USER_IDS[1]}', 'Bob M', NULL),
    ('{SEED_PROFILE_IDS[2]}', '{SEED_USER_IDS[2]}', NULL, '{{"theme": "light"}}');
"""


CLEANUP_SQL = """
DROP TABLE IF EXISTS test_post_tag CASCADE;
DROP TABLE IF EXISTS test_profile CASCADE;
DROP TABLE IF EXISTS test_post CASCADE;
DROP TABLE IF EXISTS test_category CASCADE;
DROP TABLE IF EXISTS test_tag CASCADE;
DROP TABLE IF EXISTS test_user CASCADE;
DROP TABLE IF EXISTS _matrx_migrations CASCADE;
DROP TABLE IF EXISTS _test_migration_table CASCADE;
"""


@pytest.fixture(scope="session", autouse=True)
async def seed_database(db_config, migration_db):
    """Create schema, register models, seed data; tear down at session end."""
    _create_test_models()

    for stmt in SEED_SCHEMA_SQL.strip().split(";"):
        stmt = stmt.strip()
        if stmt:
            await migration_db.execute(stmt)

    for stmt in SEED_DATA_SQL.strip().split(";"):
        stmt = stmt.strip()
        if stmt:
            await migration_db.execute(stmt)

    yield

    for stmt in CLEANUP_SQL.strip().split(";"):
        stmt = stmt.strip()
        if stmt:
            try:
                await migration_db.execute(stmt)
            except Exception:
                pass

    await AsyncDatabaseManager.close_all_pools()


@pytest.fixture
def user_model():
    return ModelRegistry.get_model("TestUser")


@pytest.fixture
def post_model():
    return ModelRegistry.get_model("TestPost")


@pytest.fixture
def tag_model():
    return ModelRegistry.get_model("TestTag")


@pytest.fixture
def category_model():
    return ModelRegistry.get_model("TestCategory")


@pytest.fixture
def profile_model():
    return ModelRegistry.get_model("TestProfile")


@pytest.fixture
def user_ids():
    return SEED_USER_IDS


@pytest.fixture
def post_ids():
    return SEED_POST_IDS


@pytest.fixture
def tag_ids():
    return SEED_TAG_IDS
