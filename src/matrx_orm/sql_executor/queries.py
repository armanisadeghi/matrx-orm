from typing import Dict, List, Optional, Any, TypedDict


class QueryParam(TypedDict):
    """Type definition for a query parameter."""
    name: str
    required: bool
    description: str
    type: str  # 'string', 'integer', 'float', 'boolean', 'uuid', etc.
    default: Optional[Any]


class SQLQuery(TypedDict):
    """Type definition for a SQL query."""
    query: str
    params: List[QueryParam]
    database: str
    description: str
    example: Optional[str]
    executor_type: Optional[str]  # 'standard', 'transaction', or 'batch'


# Registry of named SQL queries.  Populate this dict in your application by
# calling register_query() or by assigning directly:
#
#   from matrx_orm.sql_executor.queries import SQL_QUERIES, SQLQuery
#
#   SQL_QUERIES["get_active_users"] = SQLQuery(
#       query="SELECT * FROM users WHERE is_active = true",
#       params=[],
#       database="my_project",
#       description="Fetch all active users",
#       example=None,
#       executor_type="standard",
#   )
SQL_QUERIES: Dict[str, SQLQuery] = {}


def register_query(name: str, query: SQLQuery) -> None:
    """Register a named SQL query into the global registry."""
    SQL_QUERIES[name] = query
