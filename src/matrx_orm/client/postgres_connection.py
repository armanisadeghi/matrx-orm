import json
import os
from typing import Any
from urllib.parse import quote_plus

from psycopg_pool import ConnectionPool
from psycopg.rows import dict_row
from matrx_utils import vcprint

from matrx_orm.utils.sql_utils import sql_param_to_psycopg2
from matrx_orm import get_database_config

connection_pools = {}


def init_connection_details(config_name):
    global connection_pools

    if config_name not in connection_pools:
        config = get_database_config(config_name=config_name)
        vcprint(f"\n[Matrx ORM] Using configuration for: {config_name}\n", color="green")

        db_host = config.get("host")
        db_port = config.get("port")
        db_protocol = config.get("protocol", "postgresql")
        db_name = config.get("database_name")
        db_user = config.get("user")
        db_password = config.get("password")

        if not all([db_host, db_port, db_name, db_user, db_password]):
            raise ValueError(
                f"Incomplete database configuration for '{config_name}'. "
                "Please check your environment variables or settings."
            )

        # All values guaranteed non-None after the guard above.
        safe_user: str = db_user  # type: ignore[assignment]
        safe_password: str = db_password  # type: ignore[assignment]
        safe_host: str = db_host  # type: ignore[assignment]
        safe_port: str = db_port  # type: ignore[assignment]
        safe_name: str = db_name  # type: ignore[assignment]

        # URL-encode user and password so special characters (#, $, @, etc.)
        # don't corrupt the URI — this is the root cause of auth failures when
        # passwords contain symbols.
        connection_string = (
            f"{db_protocol}://{quote_plus(safe_user)}:{quote_plus(safe_password)}"
            f"@{safe_host}:{safe_port}/{safe_name}"
        )
        redacted = f"{db_protocol}://{safe_user}:****@{safe_host}:{safe_port}/{safe_name}"

        vcprint(f"\n[Matrx ORM] Connection String:\n{redacted}\n", color="yellow")

        connection_pools[config_name] = ConnectionPool(
            connection_string,
            min_size=1,
            max_size=10,
            kwargs={"sslmode": "require"},
            open=False,
        )
        connection_pools[config_name].open(wait=True)


def get_postgres_connection(
        database_project="this_will_cause_error_specify_the_database",
):
    init_connection_details(database_project)
    conn = connection_pools[database_project].getconn()
    return conn


def execute_sql_query(query, params=None, database_project="this_will_cause_error_specify_the_database"):
    """
    Executes a SQL query and returns the results as a list of dictionaries.
    """
    conn = get_postgres_connection(database_project)
    try:
        with conn.cursor(row_factory=dict_row) as cur:
            if params and isinstance(params, dict):
                query, params = sql_param_to_psycopg2(query, params)
            cur.execute(query, params)
            results = cur.fetchall()
        conn.commit()
        return results
    except Exception:
        conn.rollback()
        raise
    finally:
        connection_pools[database_project].putconn(conn)


def execute_sql_file(filename, params=None, database_project="this_will_cause_error_specify_the_database"):
    """
    Executes a SQL query from a file and returns the results.
    """
    sql_dir = os.path.join(os.path.dirname(__file__), "sql")
    with open(os.path.join(sql_dir, filename), "r") as sql_file:
        query = sql_file.read()

    if params:
        query, params = sql_param_to_psycopg2(query, params)

    vcprint(f"Executing query:\n{query}\n", color="green")
    vcprint(f"With params: {params}\n", color="green")

    return execute_sql_query(query, params, database_project)


def execute_transaction_query(query, params=None, database_project="this_will_cause_error_specify_the_database"):
    """
    Executes a SQL query within a transaction, commits it, and returns any results.
    Suitable for INSERT/UPDATE/DELETE operations that may or may not return values.
    """
    conn = get_postgres_connection(database_project)
    try:
        with conn.cursor(row_factory=dict_row) as cur:
            if params and isinstance(params, dict):
                query, params = sql_param_to_psycopg2(query, params)
            cur.execute(query, params)
            conn.commit()

            # Try to fetch results if any are available
            try:
                return cur.fetchall()
            except Exception:
                return []
    finally:
        connection_pools[database_project].putconn(conn)


def execute_batch_query(query: str, batch_params: list[dict[str, Any]], batch_size: int = 50,
                        database_project: str = ""):
    """
    Executes a SQL query with batched parameters.
    """
    conn = get_postgres_connection(database_project)
    all_results = []

    try:
        # Process in batches
        for i in range(0, len(batch_params), batch_size):
            batch = batch_params[i: i + batch_size]
            vcprint(f"Processing batch {i // batch_size + 1}/{(len(batch_params) + batch_size - 1) // batch_size}",
                    color="blue")

            # Process each row individually within the batch
            for _, row_params in enumerate(batch):
                # Handle JSONB serialization properly
                processed_params = {}
                for key, value in row_params.items():
                    if key == "data" and isinstance(value, dict):
                        # Convert dict to JSONB-compatible string
                        processed_params[key] = json.dumps(value)
                    else:
                        processed_params[key] = value

                # Execute the query for this row
                with conn.cursor(row_factory=dict_row) as cur:
                    if processed_params:
                        query_with_names, params = sql_param_to_psycopg2(query, processed_params)
                        cur.execute(query_with_names, params)
                        conn.commit()
                        try:
                            result = cur.fetchall()
                            if result:
                                all_results.extend(result)
                        except Exception:
                            pass
    finally:
        connection_pools[database_project].putconn(conn)

    return all_results