"""
Subscription and Credit Management API
Handles user subscriptions, credit purchases, and feature access
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from app.core.supabase import get_supabase_client
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/subscriptions", tags=["subscriptions"])


# ============================================================================
# Pydantic Models
# ============================================================================

class PricingPlan(BaseModel):
    id: str
    plan_code: str
    plan_name: str
    plan_type: str  # 'credits', 'one_time', 'subscription'
    description: Optional[str]
    price_usd: float
    credits_amount: int
    features: List[str]
    display_order: int


class UserSubscription(BaseModel):
    id: str
    plan_code: str
    plan_name: str
    plan_type: str
    status: str
    credits_total: Optional[int] = 0
    credits_used: Optional[int] = 0
    credits_remaining: Optional[int] = 0
    usage_count: Optional[int] = 0
    usage_limit: Optional[int] = None
    purchased_at: datetime
    last_used_at: Optional[datetime] = None


class FeaturesSummary(BaseModel):
    interview_credits: int
    ai_generator_available: bool
    qa_management_available: bool
    active_subscriptions: List[Dict[str, Any]]


class CreditUsageLog(BaseModel):
    id: str
    credits_used: int
    action: str
    session_id: Optional[str]
    created_at: datetime


# ============================================================================
# Endpoints
# ============================================================================

@router.get("/plans", response_model=List[PricingPlan])
async def get_pricing_plans():
    """
    Get all available pricing plans.
    Public endpoint - no authentication required.
    """
    try:
        supabase = get_supabase_client()
        result = supabase.table("pricing_plans")\
            .select("*")\
            .eq("is_active", True)\
            .order("display_order")\
            .execute()

        return result.data or []

    except Exception as e:
        logger.error(f"Error fetching pricing plans: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to fetch pricing plans")


@router.get("/{user_id}/summary", response_model=FeaturesSummary)
async def get_user_features_summary(user_id: str):
    """
    Get comprehensive summary of user's features, credits, and subscriptions.
    """
    try:
        supabase = get_supabase_client()

        # Call database function
        result = supabase.rpc('get_user_features_summary', {
            'p_user_id': user_id
        }).execute()

        if not result.data:
            # Return empty summary for new users
            return FeaturesSummary(
                interview_credits=0,
                ai_generator_available=False,
                qa_management_available=False,
                active_subscriptions=[]
            )

        return result.data

    except Exception as e:
        logger.error(f"Error fetching user features summary: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to fetch user summary")


@router.get("/{user_id}/subscriptions", response_model=List[UserSubscription])
async def get_user_subscriptions(user_id: str):
    """
    Get all active and depleted subscriptions for a user.
    """
    try:
        supabase = get_supabase_client()

        result = supabase.table("user_subscriptions")\
            .select("*, pricing_plans(plan_name)")\
            .eq("user_id", user_id)\
            .in_("status", ["active", "depleted"])\
            .order("purchased_at", desc=True)\
            .execute()

        subscriptions = []
        for sub in (result.data or []):
            subscriptions.append(UserSubscription(
                id=sub['id'],
                plan_code=sub['plan_code'],
                plan_name=sub['pricing_plans']['plan_name'],
                plan_type=sub['plan_type'],
                status=sub['status'],
                credits_total=sub.get('credits_total', 0),
                credits_used=sub.get('credits_used', 0),
                credits_remaining=sub.get('credits_remaining', 0),
                usage_count=sub.get('usage_count', 0),
                usage_limit=sub.get('usage_limit'),
                purchased_at=sub['purchased_at'],
                last_used_at=sub.get('last_used_at')
            ))

        return subscriptions

    except Exception as e:
        logger.error(f"Error fetching user subscriptions: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to fetch subscriptions")


@router.get("/{user_id}/credits")
async def get_user_credits(user_id: str):
    """
    Get user's total available interview credits.
    """
    try:
        supabase = get_supabase_client()

        result = supabase.rpc('get_user_interview_credits', {
            'p_user_id': user_id
        }).execute()

        total_credits = result.data if result.data is not None else 0

        return {
            "user_id": user_id,
            "credits_available": total_credits
        }

    except Exception as e:
        logger.error(f"Error fetching user credits: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to fetch credits")


@router.post("/{user_id}/credits/consume")
async def consume_credit(user_id: str, session_id: Optional[str] = None):
    """
    Consume one interview credit.
    Called when an interview session is completed.
    """
    try:
        supabase = get_supabase_client()

        result = supabase.rpc('consume_interview_credit', {
            'p_user_id': user_id,
            'p_session_id': session_id
        }).execute()

        success = result.data if result.data is not None else False

        if not success:
            raise HTTPException(
                status_code=403,
                detail={
                    "error": "insufficient_credits",
                    "message": "No interview credits available. Please purchase more credits.",
                    "upgrade_url": "/pricing"
                }
            )

        # Get updated credit balance
        credits_result = supabase.rpc('get_user_interview_credits', {
            'p_user_id': user_id
        }).execute()

        remaining_credits = credits_result.data if credits_result.data is not None else 0

        return {
            "success": True,
            "credits_remaining": remaining_credits,
            "message": "Credit consumed successfully"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error consuming credit: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to consume credit")


@router.get("/{user_id}/credits/usage-log", response_model=List[CreditUsageLog])
async def get_credit_usage_log(
    user_id: str,
    limit: int = 50,
    offset: int = 0
):
    """
    Get credit usage history for a user.
    """
    try:
        supabase = get_supabase_client()

        result = supabase.table("credit_usage_log")\
            .select("*")\
            .eq("user_id", user_id)\
            .order("created_at", desc=True)\
            .limit(limit)\
            .offset(offset)\
            .execute()

        return result.data or []

    except Exception as e:
        logger.error(f"Error fetching credit usage log: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to fetch usage log")


@router.get("/{user_id}/feature/{feature_code}")
async def check_feature_access(user_id: str, feature_code: str):
    """
    Check if user has access to a specific feature.

    Feature codes:
    - interview_practice
    - ai_qa_generation
    - qa_pairs_crud
    - qa_bulk_upload
    """
    try:
        supabase = get_supabase_client()

        result = supabase.rpc('user_has_feature', {
            'p_user_id': user_id,
            'p_feature_code': feature_code
        }).execute()

        has_access = result.data if result.data is not None else False

        return {
            "user_id": user_id,
            "feature_code": feature_code,
            "has_access": has_access
        }

    except Exception as e:
        logger.error(f"Error checking feature access: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to check feature access")


@router.get("/{user_id}/transactions")
async def get_payment_transactions(
    user_id: str,
    limit: int = 20,
    offset: int = 0
):
    """
    Get payment transaction history for a user.
    """
    try:
        supabase = get_supabase_client()

        result = supabase.table("payment_transactions")\
            .select("*, pricing_plans(plan_name)")\
            .eq("user_id", user_id)\
            .order("created_at", desc=True)\
            .limit(limit)\
            .offset(offset)\
            .execute()

        return {
            "transactions": result.data or [],
            "total_count": len(result.data or [])
        }

    except Exception as e:
        logger.error(f"Error fetching transactions: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to fetch transactions")
