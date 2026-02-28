from __future__ import annotations

import os
import asyncio
import traceback
from typing import Any

import asyncpg
from contextlib import asynccontextmanager
from matrx_orm.core.config import get_database_config, DatabaseConfigError
from matrx_orm.exceptions import (
    DatabaseError,
    ConnectionError,
    ConfigurationError,
    IntegrityError,
    ParameterError,
    QueryError,
    StateError,
    AdapterError,
    UnknownDatabaseError,
)
from matrx_orm.error_handling import handle_orm_operation


async def _init_vector_codec(conn: asyncpg.Connection) -> None:
    """Register a text codec for pgvector's ``vector`` type on each new connection.

    Without this, asyncpg returns vector columns as raw strings like
    ``[0.1,0.2,...]``.  With it, they arrive as ``list[float]`` so
    ``VectorField.to_python`` receives an already-parsed value.

    The encoder is a passthrough — ``VectorField.get_db_prep_value`` converts
    Python lists to the ``[x,y,...]`` string before writing to the DB.

    This is a no-op when pgvector is not installed (the type simply won't exist
    and asyncpg will raise ``UndefinedTypeError`` which we silently swallow).
    """
    try:
        await conn.set_type_codec(
            "vector",
            encoder=lambda v: v,
            decoder=lambda v: [float(x) for x in v.strip("[]").split(",")],
            schema="pg_catalog",
            format="text",
        )
    except Exception:
        # pgvector not installed on this database — silently skip
        pass


class AsyncDatabaseManager:
    _instance = None
    _pools = {}
    _pool_loops = {}  # Track which event loop each pool belongs to
    _locks = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    async def get_pool(cls, config_name):
        """Get or create a connection pool for the specified database with error handling.
        
        Automatically detects event loop changes and recreates pools as needed.
        This allows sync methods (using asyncio.run()) to work correctly in scripts/tests
        where multiple sequential event loops may be created.
        """
        if config_name not in cls._locks:
            cls._locks[config_name] = asyncio.Lock()

        async with cls._locks[config_name]:
            # Get the current event loop
            try:
                current_loop = asyncio.get_running_loop()
                current_loop_id = id(current_loop)
            except RuntimeError:
                # No running loop (shouldn't happen in async context, but be safe)
                current_loop_id = None

            # Check if pool exists and belongs to a different event loop
            if config_name in cls._pools and current_loop_id is not None:
                pool_loop_id = cls._pool_loops.get(config_name)
                
                if pool_loop_id != current_loop_id:
                    # Pool is from a different event loop - close and recreate
                    # This happens when using sync methods that create new loops via asyncio.run()
                    try:
                        old_pool = cls._pools[config_name]
                        await old_pool.close()
                    except Exception:
                        # Ignore errors closing old pool (it might already be closed)
                        pass
                    
                    # Remove the old pool so we can create a new one
                    del cls._pools[config_name]
                    if config_name in cls._pool_loops:
                        del cls._pool_loops[config_name]

            if config_name not in cls._pools:
                async with handle_orm_operation(
                    operation_name="create_connection_pool",
                    model=None,
                    config_name=config_name,
                ):
                    config = get_database_config(config_name)
                    try:
                        pool = await asyncpg.create_pool(
                            host=config["host"],
                            port=config["port"],
                            database=config["database_name"],
                            user=config["user"],
                            password=config["password"],
                            min_size=5,
                            max_size=20,
                            command_timeout=10,
                            ssl="require",
                            statement_cache_size=0,
                            init=_init_vector_codec,
                        )
                        cls._pools[config_name] = pool
                        
                        try:
                            current_loop = asyncio.get_running_loop()
                            cls._pool_loops[config_name] = id(current_loop)
                        except RuntimeError:
                            cls._pool_loops[config_name] = None
                    except DatabaseConfigError as e:
                        raise ConfigurationError(
                            model=None,
                            config_key=config_name,
                            reason=f"Invalid or missing configuration: {str(e)}",
                        ) from e
                    except asyncpg.exceptions.ConnectionFailureError as e:
                        raise ConnectionError(
                            model=None,
                            db_url=f"{config.get('host')}:{config.get('port')}/{config.get('database_name')}",
                            original_error=e,
                        ) from e
                    except asyncpg.exceptions.InvalidAuthorizationSpecificationError as e:
                        raise ConnectionError(
                            model=None,
                            db_url=f"{config.get('host')}:{config.get('port')}/{config.get('database_name')}",
                            original_error=e,
                        ) from e
                    except Exception as e:
                        raise AdapterError(model=None, adapter_name="asyncpg", original_error=e) from e
            return cls._pools[config_name]

    @classmethod
    @asynccontextmanager
    async def get_connection(cls, config_name, timeout=10.0):
        """Get a connection from the pool with a timeout and error handling."""
        pool = await cls.get_pool(config_name)
        try:
            async with asyncio.timeout(timeout):
                conn = await pool.acquire()
                try:
                    yield conn
                finally:
                    await pool.release(conn)
        except asyncio.TimeoutError:
            async with handle_orm_operation(
                operation_name="acquire_connection",
                model=None,
                config_name=config_name,
                timeout=timeout,
            ):
                raise DatabaseError(
                    model=None,
                    message=f"Timeout acquiring connection after {timeout}s",
                    details={"config_name": config_name, "timeout": timeout},
                ) from None
        except asyncpg.exceptions.InterfaceError as e:
            async with handle_orm_operation(
                operation_name="acquire_connection",
                model=None,
                config_name=config_name,
                timeout=timeout,
            ):
                raise StateError(
                    model=None,
                    operation="acquire_connection",
                    reason="Connection pool issue",
                    details={"config_name": config_name},
                    original_error=e,
                ) from e

    @classmethod
    async def execute_query(cls, config_name: str, query: str, *args: Any, timeout: float = 10.0) -> list[dict[str, Any]]:
        """Execute a query and return results with error handling.

        When a transaction is active for the current task (set via the
        ``transaction()`` context manager), the transaction's connection is
        reused so that all queries participate in the same atomic block.
        """
        # Reuse the active transaction connection when available
        try:
            from matrx_orm.core.transaction import get_active_connection
            tx_conn = get_active_connection()
        except ImportError:
            tx_conn = None

        if tx_conn is not None:
            try:
                results = await tx_conn.fetch(query, *args)
                return [dict(r) for r in results]
            except asyncpg.exceptions.PostgresSyntaxError as e:
                raise QueryError(
                    model=None,
                    message=f"Invalid SQL syntax: {str(e)}",
                    details={"query": query, "args": args, "config_name": config_name},
                ) from e
            except asyncpg.exceptions.UniqueViolationError as e:
                raise IntegrityError(model=None, constraint="unknown", original_error=e) from e
            except asyncpg.exceptions.DataError as e:
                raise ParameterError(model=None, query=query, args=args, reason=str(e)) from e
            except Exception as e:
                raise UnknownDatabaseError(
                    model=None,
                    operation="execute_query",
                    query=query,
                    args=args,
                    traceback="",
                    original_error=e,
                ) from e

        async with handle_orm_operation(
            operation_name="execute_query",
            model=None,
            config_name=config_name,
            query=query,
            args=args,
            timeout=timeout,
        ):
            async with cls.get_connection(config_name, timeout) as conn:
                try:
                    results = await conn.fetch(query, *args)
                    return [dict(r) for r in results]
                except asyncpg.exceptions.PostgresSyntaxError as e:
                    raise QueryError(
                        model=None,
                        message=f"Invalid SQL syntax: {str(e)}",
                        details={
                            "query": query,
                            "args": args,
                            "config_name": config_name,
                        },
                    ) from e
                except asyncpg.exceptions.UniqueViolationError as e:
                    raise IntegrityError(
                        model=None,
                        constraint="unknown",
                        original_error=e,
                    ) from e
                except asyncpg.exceptions.ConnectionDoesNotExistError as e:
                    raise ConnectionError(
                        model=None,
                        db_url=config_name,
                        original_error=e,
                    ) from e
                except asyncpg.exceptions.DataError as e:
                    raise ParameterError(model=None, query=query, args=args, reason=str(e)) from e
                except Exception as e:
                    tb = traceback.format_exc()
                    raise UnknownDatabaseError(
                        model=None,
                        operation="execute_query",
                        query=query,
                        args=args,
                        traceback=tb,
                        original_error=e,
                    ) from e

    @classmethod
    async def cleanup(cls):
        """Close all connection pools with error handling."""
        async with handle_orm_operation(operation_name="cleanup_pools", model=None, active_pools=len(cls._pools)):
            for config_name, pool in list(cls._pools.items()):
                try:
                    await pool.close()
                except Exception as e:
                    raise StateError(
                        model=None,
                        operation="cleanup_pools",
                        reason=f"Failed to close pool for {config_name}",
                        details={"config_name": config_name},
                        original_error=e,
                    ) from e
            cls._pools.clear()
            cls._pool_loops.clear()
            cls._locks.clear()


def run_sync(coro):
    """Run an async coroutine synchronously, ensuring all connection pools are
    closed before the event loop shuts down.

    Every call to asyncio.run() creates a fresh event loop. asyncpg pools are
    bound to the loop they were created on; when the loop is torn down without
    first closing the pool, Python emits ResourceWarning: unclosed connection
    for every idle connection in the pool (min_size=5 by default means at least
    5 warnings per call).

    This helper wraps the caller's coroutine so that AsyncDatabaseManager.cleanup()
    is always awaited at the end of the same event loop, regardless of whether the
    coroutine succeeded or raised.
    """

    async def _wrapped():
        try:
            return await coro
        finally:
            await AsyncDatabaseManager.cleanup()

    return asyncio.run(_wrapped())


async def main():
    db = AsyncDatabaseManager()
    try:
        results = await db.execute_query(
            "your_database_project",  # replace with your registered project name
            "SELECT * FROM your_table WHERE id = $1",
            "your-record-uuid",
        )
        print(results)
    except DatabaseError as e:
        print(f"Database error: {e}")
    finally:
        await db.cleanup()


async def cause_error():
    db = AsyncDatabaseManager()
    try:
        results = await db.execute_query(
            "your_database_project",  # replace with your registered project name
            "SELECT * FROM your_table WHERE id = $1",
            "invalid-uuid",
        )
        print(results)
    except DatabaseError as e:
        print(f"Database error: {e}")
    finally:
        await db.cleanup()


if __name__ == "__main__":
    os.system("cls")
    asyncio.run(cause_error())
