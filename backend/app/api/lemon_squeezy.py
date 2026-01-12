"""
Lemon Squeezy Payment Integration API
Handles credit purchases and feature unlocks via Lemon Squeezy
"""

from fastapi import APIRouter, HTTPException, Request, Header
from pydantic import BaseModel
from typing import Optional
import hmac
import hashlib
import httpx
import logging
from datetime import datetime
from app.core.config import settings
from app.core.supabase import get_supabase_client

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/lemon-squeezy", tags=["lemon-squeezy"])


# ============================================================================
# Pydantic Models
# ============================================================================

class CreateCheckoutRequest(BaseModel):
    user_id: str
    plan_code: str
    success_url: str
    cancel_url: str


class CheckoutSessionResponse(BaseModel):
    checkout_url: str
    order_id: str


# ============================================================================
# Endpoints
# ============================================================================

@router.post("/create-checkout-session", response_model=CheckoutSessionResponse)
async def create_checkout_session(request: CreateCheckoutRequest):
    """
    Create a Lemon Squeezy checkout session for purchasing credits or features.
    """
    try:
        # Verify API configuration
        if not settings.LEMON_SQUEEZY_API_KEY:
            logger.error("LEMON_SQUEEZY_API_KEY is not configured")
            raise HTTPException(status_code=500, detail="Payment service not configured")

        if not settings.LEMON_SQUEEZY_STORE_ID:
            logger.error("LEMON_SQUEEZY_STORE_ID is not configured")
            raise HTTPException(status_code=500, detail="Payment service not configured")

        supabase = get_supabase_client()

        # Get plan details
        plan_result = supabase.table("pricing_plans")\
            .select("*")\
            .eq("plan_code", request.plan_code)\
            .eq("is_active", True)\
            .execute()

        if not plan_result.data:
            raise HTTPException(status_code=404, detail="Pricing plan not found")

        plan = plan_result.data[0]

        # Get Lemon Squeezy product variant ID for this plan
        # You'll need to create products in Lemon Squeezy dashboard and store variant IDs
        variant_id = get_variant_id_for_plan(request.plan_code)

        if not variant_id:
            raise HTTPException(
                status_code=500,
                detail=f"Lemon Squeezy product not configured for plan: {request.plan_code}"
            )

        logger.info(f"Creating checkout for plan: {request.plan_code}, variant: {variant_id}, store: {settings.LEMON_SQUEEZY_STORE_ID}")

        # Create Lemon Squeezy checkout
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.lemonsqueezy.com/v1/checkouts",
                headers={
                    "Accept": "application/vnd.api+json",
                    "Content-Type": "application/vnd.api+json",
                    "Authorization": f"Bearer {settings.LEMON_SQUEEZY_API_KEY}"
                },
                json={
                    "data": {
                        "type": "checkouts",
                        "attributes": {
                            "product_options": {
                                "redirect_url": request.success_url
                            },
                            "checkout_data": {
                                "custom": {
                                    "user_id": request.user_id,
                                    "plan_code": request.plan_code,
                                    "plan_type": plan['plan_type'],
                                    "credits_amount": str(plan['credits_amount']) if plan['credits_amount'] else "0"
                                }
                            }
                        },
                        "relationships": {
                            "store": {
                                "data": {
                                    "type": "stores",
                                    "id": settings.LEMON_SQUEEZY_STORE_ID
                                }
                            },
                            "variant": {
                                "data": {
                                    "type": "variants",
                                    "id": variant_id
                                }
                            }
                        }
                    }
                }
            )

        if response.status_code not in [200, 201]:
            logger.error(f"Lemon Squeezy API error (status {response.status_code}): {response.text}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to create checkout session: {response.status_code}"
            )

        checkout_data = response.json()
        checkout_url = checkout_data['data']['attributes']['url']
        order_id = checkout_data['data']['id']

        logger.info(f"Created Lemon Squeezy checkout: {order_id} for user {request.user_id}")

        return CheckoutSessionResponse(
            checkout_url=checkout_url,
            order_id=order_id
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating checkout session: {type(e).__name__}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to create checkout session: {str(e)}")


@router.post("/webhook")
async def lemon_squeezy_webhook(
    request: Request,
    x_signature: str = Header(None, alias="x-signature")
):
    """
    Handle Lemon Squeezy webhook events.
    Called by Lemon Squeezy when payment events occur.
    """
    try:
        payload = await request.body()

        # Verify webhook signature
        if not verify_webhook_signature(payload, x_signature):
            logger.error("Invalid webhook signature")
            raise HTTPException(status_code=400, detail="Invalid signature")

        event_data = await request.json()
        event_name = event_data.get('meta', {}).get('event_name')

        logger.info(f"Received Lemon Squeezy webhook: {event_name}")

        # Handle different event types
        if event_name == 'order_created':
            await handle_order_created(event_data)

        elif event_name == 'order_refunded':
            await handle_order_refunded(event_data)

        elif event_name == 'subscription_created':
            # For future subscription support
            pass

        return {"status": "success"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing webhook: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Webhook processing failed")


# ============================================================================
# Helper Functions
# ============================================================================

def verify_webhook_signature(payload: bytes, signature: str) -> bool:
    """
    Verify Lemon Squeezy webhook signature.
    """
    if not signature or not settings.LEMON_SQUEEZY_WEBHOOK_SECRET:
        return False

    expected_signature = hmac.new(
        settings.LEMON_SQUEEZY_WEBHOOK_SECRET.encode('utf-8'),
        payload,
        hashlib.sha256
    ).hexdigest()

    return hmac.compare_digest(signature, expected_signature)


def get_variant_id_for_plan(plan_code: str) -> Optional[str]:
    """
    Map plan codes to Lemon Squeezy variant IDs.
    These need to be configured after creating products in Lemon Squeezy dashboard.
    """
    variant_mapping = {
        # Credit packs (matching pricing_plans table)
        'credits_starter': settings.LEMON_SQUEEZY_VARIANT_CREDITS_STARTER,
        'credits_popular': settings.LEMON_SQUEEZY_VARIANT_CREDITS_POPULAR,
        'credits_pro': settings.LEMON_SQUEEZY_VARIANT_CREDITS_PRO,
        # One-time features
        'ai_generator': settings.LEMON_SQUEEZY_VARIANT_AI_GENERATOR,
        'qa_management': settings.LEMON_SQUEEZY_VARIANT_QA_MANAGEMENT,
    }

    return variant_mapping.get(plan_code)


# ============================================================================
# Webhook Handlers
# ============================================================================

async def handle_order_created(event_data: dict):
    """
    Handle successful order creation (payment completed).
    Grant access to purchased features/credits.
    """
    try:
        supabase = get_supabase_client()

        order = event_data['data']['attributes']
        # Custom data is in meta.custom_data, not in order attributes
        custom_data = event_data.get('meta', {}).get('custom_data', {})

        user_id = custom_data.get('user_id')
        plan_code = custom_data.get('plan_code')
        plan_type = custom_data.get('plan_type')
        credits_amount = int(custom_data.get('credits_amount', 0))

        logger.info(f"Webhook custom_data: {custom_data}")

        if not user_id or not plan_code:
            logger.error(f"Missing required custom data in webhook. user_id={user_id}, plan_code={plan_code}, full_meta={event_data.get('meta', {})}")
            return

        # Get plan details
        plan_result = supabase.table("pricing_plans")\
            .select("*")\
            .eq("plan_code", plan_code)\
            .execute()

        if not plan_result.data:
            logger.error(f"Plan not found: {plan_code}")
            return

        plan = plan_result.data[0]

        # Create subscription record
        subscription_data = {
            "user_id": user_id,
            "plan_code": plan_code,
            "plan_type": plan_type,
            "status": "active",
            "lemon_squeezy_order_id": order['order_number'],
            "lemon_squeezy_customer_id": order.get('customer_id'),
            "metadata": {
                "order_id": event_data['data']['id'],
                "amount_paid": order['total'] / 100
            }
        }

        # Add credit-specific fields
        if plan_type == 'credits':
            subscription_data.update({
                "credits_total": credits_amount,
                "credits_used": 0,
                "credits_remaining": credits_amount
            })

        # Add one-time purchase specific fields
        elif plan_type == 'one_time':
            # Check if already purchased
            existing = supabase.table("user_subscriptions")\
                .select("id")\
                .eq("user_id", user_id)\
                .eq("plan_code", plan_code)\
                .eq("status", "active")\
                .execute()

            if existing.data:
                logger.warning(f"User {user_id} already has {plan_code}, skipping duplicate")
                return

            # Set usage limits
            if plan_code == 'ai_generator':
                subscription_data["usage_limit"] = 1

        # Insert subscription
        sub_result = supabase.table("user_subscriptions")\
            .insert(subscription_data)\
            .execute()

        subscription_id = sub_result.data[0]['id'] if sub_result.data else None

        # Record transaction
        transaction_data = {
            "user_id": user_id,
            "subscription_id": subscription_id,
            "plan_code": plan_code,
            "amount_usd": order['total'] / 100,
            "currency": order['currency'].upper(),
            "payment_method": "lemon_squeezy",
            "payment_status": "completed",
            "lemon_squeezy_order_id": order['order_number'],
            "lemon_squeezy_customer_id": order.get('customer_id'),
            "completed_at": datetime.now().isoformat(),
            "metadata": {
                "order_id": event_data['data']['id'],
                "receipt_email": order.get('user_email')
            }
        }

        supabase.table("payment_transactions")\
            .insert(transaction_data)\
            .execute()

        logger.info(f"✅ Granted {plan_code} to user {user_id} via Lemon Squeezy")

    except Exception as e:
        logger.error(f"Error handling order creation: {e}", exc_info=True)


async def handle_order_refunded(event_data: dict):
    """
    Handle refunded order.
    Revoke access to features/credits.
    """
    try:
        supabase = get_supabase_client()

        order = event_data['data']['attributes']
        order_number = order['order_number']

        # Update transaction status
        supabase.table("payment_transactions")\
            .update({
                "payment_status": "refunded",
                "refunded_at": datetime.now().isoformat()
            })\
            .eq("lemon_squeezy_order_id", order_number)\
            .execute()

        # Revoke subscription
        supabase.table("user_subscriptions")\
            .update({
                "status": "refunded",
                "credits_remaining": 0
            })\
            .eq("lemon_squeezy_order_id", order_number)\
            .execute()

        logger.info(f"♻️ Order refunded: {order_number}")

    except Exception as e:
        logger.error(f"Error handling refund: {e}", exc_info=True)
