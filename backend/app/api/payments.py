"""
Stripe Payment Integration API
Handles credit purchases and feature unlocks via Stripe
"""

from fastapi import APIRouter, HTTPException, Request, Header
from pydantic import BaseModel
from typing import Optional
import stripe
import logging
from datetime import datetime
from app.core.config import settings
from app.core.supabase import get_supabase_client

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/payments", tags=["payments"])

# Initialize Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY


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
    session_id: str


# ============================================================================
# Endpoints
# ============================================================================

@router.post("/create-checkout-session", response_model=CheckoutSessionResponse)
async def create_checkout_session(request: CreateCheckoutRequest):
    """
    Create a Stripe Checkout session for purchasing credits or features.
    """
    try:
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

        # Create Stripe checkout session
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'unit_amount': int(plan['price_usd'] * 100),  # Convert to cents
                    'product_data': {
                        'name': plan['plan_name'],
                        'description': plan['description'],
                        'metadata': {
                            'plan_code': plan['plan_code'],
                            'plan_type': plan['plan_type'],
                            'credits_amount': str(plan['credits_amount'])
                        }
                    },
                },
                'quantity': 1,
            }],
            mode='payment',  # One-time payment
            success_url=request.success_url + '?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=request.cancel_url,
            metadata={
                'user_id': request.user_id,
                'plan_code': request.plan_code,
                'plan_type': plan['plan_type'],
                'credits_amount': str(plan['credits_amount']),
            },
            client_reference_id=request.user_id,
        )

        logger.info(f"Created Stripe checkout session: {checkout_session.id} for user {request.user_id}")

        return CheckoutSessionResponse(
            checkout_url=checkout_session.url,
            session_id=checkout_session.id
        )

    except stripe.error.StripeError as e:
        logger.error(f"Stripe error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Payment service error: {str(e)}")
    except Exception as e:
        logger.error(f"Error creating checkout session: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to create checkout session")


@router.post("/webhook")
async def stripe_webhook(
    request: Request,
    stripe_signature: str = Header(None, alias="stripe-signature")
):
    """
    Handle Stripe webhook events.
    Called by Stripe when payment events occur.
    """
    try:
        payload = await request.body()

        # Verify webhook signature
        try:
            event = stripe.Webhook.construct_event(
                payload, stripe_signature, settings.STRIPE_WEBHOOK_SECRET
            )
        except stripe.error.SignatureVerificationError as e:
            logger.error(f"Invalid webhook signature: {e}")
            raise HTTPException(status_code=400, detail="Invalid signature")

        logger.info(f"Received Stripe webhook: {event['type']}")

        # Handle different event types
        if event['type'] == 'checkout.session.completed':
            await handle_checkout_completed(event['data']['object'])

        elif event['type'] == 'payment_intent.succeeded':
            await handle_payment_succeeded(event['data']['object'])

        elif event['type'] == 'payment_intent.payment_failed':
            await handle_payment_failed(event['data']['object'])

        elif event['type'] == 'charge.refunded':
            await handle_charge_refunded(event['data']['object'])

        return {"status": "success"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing webhook: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Webhook processing failed")


# ============================================================================
# Webhook Handlers
# ============================================================================

async def handle_checkout_completed(session: dict):
    """
    Handle successful checkout session completion.
    Grant access to purchased features/credits.
    """
    try:
        supabase = get_supabase_client()

        user_id = session['metadata']['user_id']
        plan_code = session['metadata']['plan_code']
        plan_type = session['metadata']['plan_type']
        credits_amount = int(session['metadata'].get('credits_amount', 0))

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
            "stripe_payment_intent_id": session.get('payment_intent'),
            "stripe_customer_id": session.get('customer'),
            "metadata": {
                "session_id": session['id'],
                "amount_paid": session['amount_total'] / 100
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

            # Set usage limits based on feature
            if plan_code == 'ai_generator':
                subscription_data["usage_limit"] = 1  # Can generate once
            # qa_management has no usage limit (unlimited)

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
            "amount_usd": session['amount_total'] / 100,
            "currency": session['currency'].upper(),
            "payment_method": "stripe",
            "payment_status": "completed",
            "stripe_payment_intent_id": session.get('payment_intent'),
            "stripe_charge_id": session.get('charges', {}).get('data', [{}])[0].get('id'),
            "stripe_customer_id": session.get('customer'),
            "completed_at": datetime.now().isoformat(),
            "metadata": {
                "session_id": session['id'],
                "receipt_email": session.get('customer_details', {}).get('email')
            }
        }

        supabase.table("payment_transactions")\
            .insert(transaction_data)\
            .execute()

        logger.info(f"✅ Granted {plan_code} to user {user_id}")

    except Exception as e:
        logger.error(f"Error handling checkout completion: {e}", exc_info=True)


async def handle_payment_succeeded(payment_intent: dict):
    """
    Handle successful payment intent.
    Additional confirmation after checkout.
    """
    try:
        supabase = get_supabase_client()

        # Update transaction status
        supabase.table("payment_transactions")\
            .update({
                "payment_status": "completed",
                "completed_at": datetime.now().isoformat()
            })\
            .eq("stripe_payment_intent_id", payment_intent['id'])\
            .execute()

        logger.info(f"✅ Payment succeeded: {payment_intent['id']}")

    except Exception as e:
        logger.error(f"Error handling payment success: {e}", exc_info=True)


async def handle_payment_failed(payment_intent: dict):
    """
    Handle failed payment.
    """
    try:
        supabase = get_supabase_client()

        failure_reason = payment_intent.get('last_payment_error', {}).get('message', 'Unknown error')

        # Update transaction status
        supabase.table("payment_transactions")\
            .update({
                "payment_status": "failed",
                "failure_reason": failure_reason
            })\
            .eq("stripe_payment_intent_id", payment_intent['id'])\
            .execute()

        logger.warning(f"❌ Payment failed: {payment_intent['id']} - {failure_reason}")

    except Exception as e:
        logger.error(f"Error handling payment failure: {e}", exc_info=True)


async def handle_charge_refunded(charge: dict):
    """
    Handle refunded charge.
    Revoke access to features/credits.
    """
    try:
        supabase = get_supabase_client()

        # Update transaction status
        supabase.table("payment_transactions")\
            .update({
                "payment_status": "refunded",
                "refunded_at": datetime.now().isoformat()
            })\
            .eq("stripe_charge_id", charge['id'])\
            .execute()

        # Revoke subscription
        supabase.table("user_subscriptions")\
            .update({
                "status": "refunded",
                "credits_remaining": 0  # Remove remaining credits
            })\
            .eq("stripe_payment_intent_id", charge['payment_intent'])\
            .execute()

        logger.info(f"♻️ Charge refunded: {charge['id']}")

    except Exception as e:
        logger.error(f"Error handling refund: {e}", exc_info=True)


@router.get("/session/{session_id}")
async def get_session_details(session_id: str):
    """
    Get Stripe session details after successful checkout.
    Used for displaying confirmation to user.
    """
    try:
        session = stripe.checkout.Session.retrieve(session_id)

        return {
            "status": session['status'],
            "payment_status": session['payment_status'],
            "amount_total": session['amount_total'] / 100,
            "currency": session['currency'],
            "customer_email": session.get('customer_details', {}).get('email'),
            "plan_code": session['metadata'].get('plan_code'),
            "plan_type": session['metadata'].get('plan_type'),
            "credits_amount": session['metadata'].get('credits_amount')
        }

    except stripe.error.StripeError as e:
        logger.error(f"Stripe error: {e}")
        raise HTTPException(status_code=404, detail="Session not found")
