from typing import List, Optional, Any, TypedDict

class QueryParam(TypedDict):
    """Type definition for a query parameter"""
    name: str
    required: bool
    description: str
    type: str  # 'string', 'integer', 'float', 'boolean', 'uuid', etc.
    default: Optional[Any]  # Default value if optional

class SQLQuery(TypedDict):
    """Type definition for a SQL query"""
    query: str
    params: List[QueryParam]
    database: str
    description: str
    example: Optional[str]  # Example usage
    executor_type: Optional[str]  # 'standard', 'transaction', or 'batch'