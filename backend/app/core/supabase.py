"""
Supabase client configuration and dependency injection
"""

from supabase import create_client, Client
from app.core.config import settings


def get_supabase_client() -> Client:
    """
    Create and return a Supabase client instance.

    This function is used as a FastAPI dependency to provide
    Supabase client access to route handlers.

    Returns:
        Client: Configured Supabase client instance
    """
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY)
