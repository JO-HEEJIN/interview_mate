"""
HTTP authentication dependency — Supabase JWT verification.

Pattern: FastAPI `Depends(get_current_user_id)` extracts and verifies the
bearer token, returning the authenticated user_id. Endpoints that take
a `user_id` path parameter then compare it with the verified id and
raise 403 on mismatch.

Why endpoint-side comparison instead of a fused guard:
  - Comparison logic is visible in each endpoint signature — easier to
    audit when reviewing the file
  - Leaves room for future admin/service overrides without changing
    the auth dependency itself
  - 403 message can be customized per endpoint if needed
"""

import logging
from typing import Optional

from fastapi import Header, HTTPException, status

from app.core.supabase import verify_access_token

logger = logging.getLogger(__name__)


async def get_current_user_id(
    authorization: Optional[str] = Header(None),
) -> str:
    """
    Verify the Authorization header and return the authenticated user_id.

    Raises 401 if the header is missing, malformed, or the token is
    invalid/expired. Never returns None — endpoints can rely on the
    return value being a real user_id.
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or malformed Authorization header",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = authorization[len("Bearer "):].strip()
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Empty bearer token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = await verify_access_token(token)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user_id


def require_user_match(path_user_id: str, current_user_id: str) -> None:
    """
    Raise 403 if the path user_id doesn't match the authenticated user.

    Use after `get_current_user_id` in endpoints that take `{user_id}`
    in their URL path.
    """
    if path_user_id != current_user_id:
        logger.warning(
            f"User mismatch: token user_id={current_user_id} tried to access path user_id={path_user_id}"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this user's data",
        )
