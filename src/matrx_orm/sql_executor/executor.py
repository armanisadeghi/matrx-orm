import os
from typing import Dict, Any, List, Optional
from matrx_utils import vcprint
from matrx_orm.client.postgres_connection import execute_sql_query as db_execute_query
from matrx_orm.client.postgres_connection import execute_transaction_query as db_execute_transaction_query
from matrx_orm.client.postgres_connection import execute_batch_query as db_execute_batch_query
from .registry import get_registry
from .utils import list_available_queries



def validate_params(query_name: str, params: Dict[str, Any]):
    """
    Validate parameters and return a clean parameter dictionary with defaults applied.
    Instead of raising errors for non-critical issues, this attempts to fix or adapt the input.
    """
    registry = get_registry()
    query_data = registry.get(query_name)
    
    if not query_data:
        available_queries = ", ".join([q["name"] for q in list_available_queries()])
        raise ValueError(f"Query '{query_name}' not found. Available queries: {available_queries}")
    
    cleaned_params = {}
    # Apply default values for all parameters
    for param_def in query_data["params"]:
        param_name = param_def["name"]
        # If parameter is provided, use it
        if param_name in params:
            param_value = params[param_name]
            # Basic type conversion attempts when reasonable
            if param_def["type"] == "uuid" and not isinstance(param_value, str) and param_value is not None:
                try:
                    # Try to convert to string if possible
                    param_value = str(param_value)
                except:
                    # If we can't convert and it's required, we have to raise an error
                    if param_def["required"]:
                        raise TypeError(f"Parameter '{param_name}' must be convertible to a string for UUID")
                    else:
                        # Use default for optional params if conversion fails
                        param_value = param_def["default"]
            cleaned_params[param_name] = param_value
        # If parameter is not provided but required, raise error
        elif param_def["required"]:
            raise ValueError(f"Missing required parameter '{param_name}' for query '{query_name}'")
        # If parameter is not provided and optional, use default
        elif param_def["default"] is not None:
            cleaned_params[param_name] = param_def["default"]
    return cleaned_params

def execute_query(query_name: str, params: Optional[Dict[str, Any]] = None, batch_params: Optional[List[Dict[str, Any]]] = None, batch_size: int = 50):
    """
    Central function to execute a query using the appropriate executor based on its type.

    Args:
        query_name: Name of the query in registry
        params: Parameters for standard/transaction execution (single row)
        batch_params: Parameters for batch execution (multiple rows)
        batch_size: Number of rows to process in each batch (for batch execution)
    """
    registry = get_registry()
    query_data = registry.get(query_name)
    
    if not query_data:
        available_queries = ", ".join([q["name"] for q in list_available_queries()])
        raise ValueError(f"Query '{query_name}' not found. Available queries: {available_queries}")

    # Determine which executor to use
    executor_type = query_data.get("executor_type", "standard")

    # If batch_params is provided, use batch execution regardless of executor_type
    if batch_params and len(batch_params) > 0:
        return execute_batch_query(query_name, batch_params, batch_size)

    # Otherwise, use the specified executor type
    params = params or {}
    cleaned_params = validate_params(query_name, params)

    if executor_type == "transaction":
        return db_execute_transaction_query(
            query_data["query"],
            cleaned_params,
            query_data["database"]
        )
    elif executor_type == "batch":
        # If batch is specified but no batch_params, wrap the single params in a list
        return execute_batch_query(query_name, [cleaned_params], batch_size)
    else:  # Default to standard
        return db_execute_query(
            query_data["query"],
            cleaned_params,
            query_data["database"]
        )

def execute_standard_query(query_name: str, params: Optional[Dict[str, Any]] = None):
    """Execute a predefined SQL query by name with the given parameters."""
    params = params or {}
    registry = get_registry()
    query_data = registry.get(query_name)
    
    if not query_data:
        available_queries = ", ".join([q["name"] for q in list_available_queries()])
        raise ValueError(f"Query '{query_name}' not found. Available queries: {available_queries}")
    
    # Clean and validate parameters
    cleaned_params = validate_params(query_name, params)
    # Execute the query
    return db_execute_query(
        query_data["query"],
        cleaned_params,
        query_data["database"]
    )

def execute_transaction_query(query_name: str, params: Optional[Dict[str, Any]] = None):
    """Execute a predefined SQL query that requires transaction handling."""
    params = params or {}
    registry = get_registry()
    query_data = registry.get(query_name)
    
    if not query_data:
        available_queries = ", ".join([q["name"] for q in list_available_queries()])
        raise ValueError(f"Query '{query_name}' not found. Available queries: {available_queries}")

    # Clean and validate parameters
    cleaned_params = validate_params(query_name, params)
    # Execute the query with transaction handling
    return db_execute_transaction_query(
        query_data["query"],
        cleaned_params,
        query_data["database"]
    )

def execute_batch_query(query_name: str, batch_params: List[Dict[str, Any]], batch_size: int = 50):
    """
    Execute a predefined SQL query using batch processing.

    Args:
        query_name: Name of the query in registry
        batch_params: List of parameter dictionaries, one per row
        batch_size: Number of rows to process in each batch

    Returns:
        Combined results from all batches
    """
    registry = get_registry()
    query_data = registry.get(query_name)
    
    if not query_data:
        available_queries = ", ".join([q["name"] for q in list_available_queries()])
        raise ValueError(f"Query '{query_name}' not found. Available queries: {available_queries}")

    # Validate each set of parameters in the batch
    validated_params = []
    for params in batch_params:
        validated_params.append(validate_params(query_name, params))

    # Execute the batch query
    return db_execute_batch_query(
        query_data["query"],
        validated_params,
        batch_size,
        query_data["database"]
    )