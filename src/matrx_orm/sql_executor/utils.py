from .registry import get_registry

def list_available_queries():
    """Return a list of all available query names with short descriptions"""
    registry = get_registry()
    all_queries = registry.get_all()
    return [
        {
            "name": name,
            "description": all_queries[name]["description"],
            "database": all_queries[name]["database"]
        }
        for name in sorted(all_queries.keys())
    ]

def get_query_details(query_name: str):
    """Get detailed information about a specific query"""
    registry = get_registry()
    query_data = registry.get(query_name)
    
    if not query_data:
        available_queries = ", ".join([q["name"] for q in list_available_queries()])
        raise ValueError(f"Query '{query_name}' not found. Available queries: {available_queries}")
    
    # Return a more user-friendly representation
    return {
        "name": query_name,
        "description": query_data["description"],
        "parameters": [
            {
                "name": p["name"],
                "required": p["required"],
                "type": p["type"],
                "description": p["description"],
                "default": p["default"] if not p["required"] else None
            } for p in query_data["params"]
        ],
        "database": query_data["database"],
        "example": query_data.get("example"),
        "query": query_data["query"],  # Include actual SQL for reference
    }

def generate_documentation():
    """Generate markdown documentation for all available queries"""
    registry = get_registry()
    all_queries = registry.get_all()
    
    docs = ["# SQL Query Documentation\n\n"]
    for query_name in sorted(all_queries.keys()):
        query_data = all_queries[query_name]
        docs.append(f"## {query_name}\n")
        docs.append(f"{query_data['description']}\n")
        docs.append("### Parameters\n")
        for param in query_data["params"]:
            required = "Required" if param["required"] else f"Optional (default: {param['default']})"
            docs.append(f"- **{param['name']}** ({param['type']}): {param['description']} - {required}\n")
        docs.append(f"\n### Database\n{query_data['database']}\n")
        if query_data.get("example"):
            docs.append(f"\n### Example\n```python\n{query_data['example']}\n```\n")
        docs.append("\n### SQL Query\n```sql\n" + query_data["query"] + "\n```\n\n")
    return "".join(docs)

def display_help():
    """Display help information about the query system"""
    help_text = """
    SQL Query System
    ----------------
    Available Functions:
    - execute_query(query_name, params, batch_params, batch_size)
      Execute a query using the appropriate executor based on its type
    - execute_standard_query(query_name, params)
      Execute a predefined SQL query with parameters
    - execute_transaction_query(query_name, params)
      Execute a query with transaction handling
    - execute_batch_query(query_name, batch_params, batch_size)
      Execute a query using batch processing
    - register_query(name, query)
      Register a new query in the global registry
    - list_available_queries()
      Get a list of all available queries with descriptions
    - get_query_details(query_name)
      Get detailed information about a specific query
    - generate_documentation()
      Generate markdown documentation for all queries
    - display_help()
      Show this help message
    Example:
    result = execute_query("get_latest_compiled_recipe", {"recipe_id": "15a11c3d-f037-4f2b-9e22-fe88e68d75e1"})
    """
    return help_text