from typing import Dict, List, Optional
from .types import SQLQuery

class QueryRegistry:
    """Global registry for SQL queries"""
    
    def __init__(self):
        self._queries: Dict[str, SQLQuery] = {}
    
    def register(self, name: str, query: SQLQuery) -> None:
        """Register a SQL query in the registry"""
        if name in self._queries:
            raise ValueError(f"Query '{name}' is already registered")
        self._queries[name] = query
    
    def get(self, name: str) -> Optional[SQLQuery]:
        """Get a query by name"""
        return self._queries.get(name)
    
    def exists(self, name: str) -> bool:
        """Check if a query exists in the registry"""
        return name in self._queries
    
    def list_names(self) -> List[str]:
        """Get all registered query names"""
        return list(self._queries.keys())
    
    def get_all(self) -> Dict[str, SQLQuery]:
        """Get all registered queries"""
        return self._queries.copy()
    
    def clear(self) -> None:
        """Clear all registered queries"""
        self._queries.clear()
    
    def unregister(self, name: str) -> bool:
        """Remove a query from the registry"""
        if name in self._queries:
            del self._queries[name]
            return True
        return False

# Global registry instance
_global_registry = QueryRegistry()

def get_registry() -> QueryRegistry:
    """Get the global query registry instance"""
    return _global_registry

def register_query(name: str, query: SQLQuery) -> None:
    """Register a query in the global registry"""
    _global_registry.register(name, query)