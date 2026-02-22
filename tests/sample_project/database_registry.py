from dotenv import load_dotenv

load_dotenv()

from matrx_utils.conf import settings, NotConfiguredError
from matrx_utils import vcprint
from matrx_orm import DatabaseProjectConfig, register_database
from matrx_orm.core.config import DatabaseConfigError

# ---------------------------------------------------------------------------
# Primary database — Supabase (MY_MATRX project: viyklljfdhtidwecakwx)
#
# additional_schemas=["auth"] makes the ORM and schema builder aware of the
# auth schema — auth.users FKs resolve via fetch_fk() without _unfetchable.
# ---------------------------------------------------------------------------
try:
    primary_config = DatabaseProjectConfig(
        name="primary",
        alias="primary",
        host=settings.PRIMARY_DB_HOST,
        port=settings.PRIMARY_DB_PORT,
        protocol=settings.PRIMARY_DB_PROTOCOL,
        database_name=settings.PRIMARY_DB_NAME,
        user=settings.PRIMARY_DB_USER,
        password=settings.PRIMARY_DB_PASSWORD,
        additional_schemas=["auth"],
    )
    register_database(primary_config)
except (AttributeError, NotConfiguredError, DatabaseConfigError) as e:
    vcprint(f"[sample_project] primary database not registered — missing env vars: {e}", color="yellow")

# ---------------------------------------------------------------------------
# Secondary database — Supabase (MATRX_DM project: deayzgwvqfdeskkdwudy)
#
# No cross-database FK relationships configured yet.
# To add one later: ForeignKey(Users, to_column="id", to_db="primary")
# ---------------------------------------------------------------------------
try:
    secondary_config = DatabaseProjectConfig(
        name="secondary",
        alias="secondary",
        host=settings.SECONDARY_DB_HOST,
        port=settings.SECONDARY_DB_PORT,
        protocol=settings.SECONDARY_DB_PROTOCOL,
        database_name=settings.SECONDARY_DB_NAME,
        user=settings.SECONDARY_DB_USER,
        password=settings.SECONDARY_DB_PASSWORD,
        additional_schemas=[],
    )
    register_database(secondary_config)
except (AttributeError, NotConfiguredError, DatabaseConfigError) as e:
    vcprint(f"[sample_project] secondary database not registered — missing env vars: {e}", color="yellow")
