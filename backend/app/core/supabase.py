"""
Supabase client configuration and dependency injection
"""

import logging
from typing import Optional
from supabase import create_client, Client
from app.core.config import settings

logger = logging.getLogger(__name__)


# Module-level singleton. Previously this function returned a NEW client on
# every call — each FastAPI endpoint, every WebSocket auth, every credit
# consume rebuilt the underlying httpx session + redid the SSL handshake +
# re-authenticated. With ~3.7ms SQL function execution but ~1.4s baseline
# end-to-end /summary latency, the overhead was the client construction
# itself, not the database.
#
# Reusing a single client lets httpx keep its connection pool warm across
# requests (HTTP keep-alive to Supabase's PostgREST). supabase-py / httpx
# are thread-safe so a single shared instance is fine across FastAPI's
# worker threads.
_supabase_client: Optional[Client] = None


def get_supabase_client() -> Client:
    """
    Return the process-wide Supabase client (service role).
    Use only for admin operations (credit consumption, batch processing).
    """
    global _supabase_client
    if _supabase_client is None:
        _supabase_client = create_client(
            settings.SUPABASE_URL,
            settings.SUPABASE_SERVICE_ROLE_KEY,
        )
    return _supabase_client


async def verify_access_token(access_token: str) -> Optional[str]:
    """
    Verify a Supabase JWT access token and return the user_id.

    Args:
        access_token: JWT token from Supabase auth session

    Returns:
        user_id (str) if valid, None if invalid
    """
    try:
        client = get_supabase_client()
        user_response = client.auth.get_user(access_token)
        if user_response and user_response.user:
            return user_response.user.id
        return None
    except Exception as e:
        logger.warning(f"Token verification failed: {e}")
        return None
