import json
import os
from typing import Any, Dict, List

from psycopg2 import pool
from psycopg2.extras import RealDictCursor
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
        db_name = config.get("database_name")
        db_user = config.get("user")
        db_password = config.get("password")

        if not all([db_host, db_port, db_name, db_user, db_password]):
            raise ValueError(
                f"Incomplete database configuration for '{config_name}'. " "Please check your environment variables or settings.")

        connection_string = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

        vcprint(f"\n[Matrx ORM] Connection String:\n{connection_string}\n", color="green")

        connection_pools[config_name] = pool.SimpleConnectionPool(1, 10, dsn=connection_string, sslmode="require")


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
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            if params and isinstance(params, dict):
                query, params = sql_param_to_psycopg2(query, params)
            cur.execute(query, params)
            return cur.fetchall()
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
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            if params and isinstance(params, dict):
                query, params = sql_param_to_psycopg2(query, params)
            cur.execute(query, params)
            conn.commit()  # Explicitly commit the transaction

            # Try to fetch results if any are available
            try:
                return cur.fetchall()
            except:
                # If no results to fetch, return an empty list instead of raising an error
                return []
    finally:
        connection_pools[database_project].putconn(conn)


def execute_batch_query(query: str, batch_params: List[Dict[str, Any]], batch_size: int = 50,
                        database_project="supabase_automation_matrix"):
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
            for idx, row_params in enumerate(batch):
                # Handle JSONB serialization properly
                processed_params = {}
                for key, value in row_params.items():
                    if key == "data" and isinstance(value, dict):
                        # Convert dict to JSONB-compatible string
                        processed_params[key] = json.dumps(value)
                    else:
                        processed_params[key] = value

                # Execute the query for this row
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    if processed_params:
                        query_with_names, params = sql_param_to_psycopg2(query, processed_params)
                        cur.execute(query_with_names, params)
                        conn.commit()
                        try:
                            result = cur.fetchall()
                            if result:
                                all_results.extend(result)
                        except:
                            # No results to fetch
                            pass
    finally:
        connection_pools[database_project].putconn(conn)

    return all_results