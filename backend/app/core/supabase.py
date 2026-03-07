"""
Supabase client configuration and dependency injection
"""

import logging
from typing import Optional
from supabase import create_client, Client
from app.core.config import settings

logger = logging.getLogger(__name__)


def get_supabase_client() -> Client:
    """
    Create and return a Supabase client instance using service role key.
    Use only for admin operations (credit consumption, batch processing).
    """
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_ROLE_KEY)


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
