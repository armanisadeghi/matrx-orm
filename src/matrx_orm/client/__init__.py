from .postgres_connection import get_postgres_connection

# Supabase client-side components (for desktop/client apps)
from .supabase_config import SupabaseClientConfig
from .supabase_auth import SupabaseAuth, AuthSession, SupabaseAuthError
from .supabase_manager import SupabaseManager
from .postgrest import PostgRESTClient, PostgRESTError

__all__ = [
    "get_postgres_connection",
    "SupabaseClientConfig",
    "SupabaseAuth",
    "AuthSession",
    "SupabaseAuthError",
    "SupabaseManager",
    "PostgRESTClient",
    "PostgRESTError",
]