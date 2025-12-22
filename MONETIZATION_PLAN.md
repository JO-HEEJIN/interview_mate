# Interview Mate - Monetization Plan

## Pricing Strategy (Credit-Based + One-Time)

### Free Tier
- **Profile Management**: Unlimited access
  - Basic profile info
  - Interview settings (including custom instructions)
  - STAR stories
  - Resume upload
- **Purpose**: User onboarding and data collection

### Paid Features

#### 🎫 Interview Credits (Pay-as-you-go)
Credit-based system to align with COGS (Deepgram + OpenAI API costs)

| Pack | Price | Sessions | Per Session | Discount |
|------|-------|----------|-------------|----------|
| **Starter** | $4 | 10 | $0.40 | - |
| **Popular** | $8 | 25 | $0.32 | 20% off ⭐ |
| **Pro** | $15 | 50 | $0.30 | 25% off ⭐ |

**COGS Analysis:**
- Deepgram (30min): $0.18
- Claude API: $0.05
- Total COGS: ~$0.23/session
- **Margin: 74% on Starter pack**

#### 🤖 One-Time Purchases
Low/no API costs → Lifetime access model

| Feature | Price | Description | COGS |
|---------|-------|-------------|------|
| **AI Q&A Generator** | $10 | Generate 30 Q&A pairs once from resume/JD | ~$0.05 |
| **Q&A Management** | $25 | Unlimited create/edit/bulk upload Q&A pairs | ~$0 |

**Pricing Examples:**
- Profile only: **Free**
- 10 interviews: **$4**
- 10 interviews + AI Generator: **$14**
- 25 interviews + AI Gen + Q&A: **$43**

---

## Feature Access Matrix

| Feature | Free | Credits ($4-15) | +AI Gen ($10) | +Q&A Mgmt ($25) |
|---------|------|-----------------|---------------|-----------------|
| Profile Management | ✅ | ✅ | ✅ | ✅ |
| Interview Settings | ✅ | ✅ | ✅ | ✅ |
| STAR Stories | ✅ | ✅ | ✅ | ✅ |
| Resume Upload | ✅ | ✅ | ✅ | ✅ |
| **Interview Practice** | ❌ | ✅ (credit-based) | ✅ | ✅ |
| **AI Q&A Generator** | ❌ | ❌ | ✅ (1x use) | ✅ |
| **Q&A Pairs CRUD** | ❌ Read-only | ❌ Read-only | ❌ Read-only | ✅ Unlimited |
| **Bulk Upload Q&A** | ❌ | ❌ | ❌ | ✅ |

---

## Database Schema

### 1. `pricing_plans` Table
Defines available features and prices.

```sql
CREATE TABLE public.pricing_plans (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    plan_code VARCHAR(50) UNIQUE NOT NULL, -- 'interview', 'ai_generator', 'qa_pairs'
    plan_name VARCHAR(100) NOT NULL,
    description TEXT,
    price_usd DECIMAL(10, 2) NOT NULL,
    features JSONB NOT NULL, -- Array of feature flags
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Seed data
INSERT INTO public.pricing_plans (plan_code, plan_name, description, price_usd, features) VALUES
('interview', 'Interview Practice', 'Real-time AI mock interviews', 5.00, '["interview_practice"]'),
('ai_generator', 'AI Q&A Generator', 'Auto-generate interview Q&A pairs', 10.00, '["ai_qa_generation"]'),
('qa_pairs', 'Q&A Pairs Management', 'Create and manage custom Q&A pairs', 25.00, '["qa_pairs_crud", "qa_bulk_upload"]');
```

### 2. `user_subscriptions` Table
Tracks which features each user has purchased.

```sql
CREATE TABLE public.user_subscriptions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
    plan_code VARCHAR(50) NOT NULL REFERENCES public.pricing_plans(plan_code),
    status VARCHAR(50) NOT NULL DEFAULT 'active' CHECK (
        status IN ('active', 'cancelled', 'expired', 'refunded')
    ),
    purchased_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE, -- NULL = lifetime access
    stripe_subscription_id VARCHAR(255), -- For Stripe integration
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    UNIQUE(user_id, plan_code) -- User can only have one subscription per feature
);

CREATE INDEX idx_user_subscriptions_user ON public.user_subscriptions(user_id);
CREATE INDEX idx_user_subscriptions_status ON public.user_subscriptions(user_id, status);
```

### 3. `payment_transactions` Table
Audit log of all payments.

```sql
CREATE TABLE public.payment_transactions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
    plan_code VARCHAR(50) NOT NULL REFERENCES public.pricing_plans(plan_code),
    amount_usd DECIMAL(10, 2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD',
    payment_method VARCHAR(50) NOT NULL, -- 'stripe', 'paypal', etc.
    payment_status VARCHAR(50) NOT NULL CHECK (
        payment_status IN ('pending', 'completed', 'failed', 'refunded')
    ),
    stripe_payment_intent_id VARCHAR(255),
    stripe_charge_id VARCHAR(255),
    metadata JSONB DEFAULT '{}', -- Additional payment info
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_payment_transactions_user ON public.payment_transactions(user_id);
CREATE INDEX idx_payment_transactions_status ON public.payment_transactions(payment_status);
```

### 4. Helper Functions

```sql
-- Check if user has access to a specific feature
CREATE OR REPLACE FUNCTION user_has_feature(p_user_id UUID, p_feature_code VARCHAR)
RETURNS BOOLEAN AS $$
BEGIN
    RETURN EXISTS (
        SELECT 1
        FROM user_subscriptions us
        JOIN pricing_plans pp ON us.plan_code = pp.plan_code
        WHERE us.user_id = p_user_id
          AND us.status = 'active'
          AND pp.features @> to_jsonb(ARRAY[p_feature_code])
          AND (us.expires_at IS NULL OR us.expires_at > NOW())
    );
END;
$$ LANGUAGE plpgsql;

-- Get all active features for a user
CREATE OR REPLACE FUNCTION get_user_features(p_user_id UUID)
RETURNS JSONB AS $$
DECLARE
    features JSONB;
BEGIN
    SELECT jsonb_agg(DISTINCT feature)
    INTO features
    FROM (
        SELECT jsonb_array_elements_text(pp.features) AS feature
        FROM user_subscriptions us
        JOIN pricing_plans pp ON us.plan_code = pp.plan_code
        WHERE us.user_id = p_user_id
          AND us.status = 'active'
          AND (us.expires_at IS NULL OR us.expires_at > NOW())
    ) sub;

    RETURN COALESCE(features, '[]'::jsonb);
END;
$$ LANGUAGE plpgsql;
```

---

## Backend Implementation

### 1. Feature Gate Middleware
**File:** `backend/app/middleware/feature_gate.py` (NEW)

```python
from fastapi import HTTPException, Request
from functools import wraps
from app.core.supabase import get_supabase_client

FEATURE_FLAGS = {
    'interview_practice': 'Interview Practice',
    'ai_qa_generation': 'AI Q&A Generator',
    'qa_pairs_crud': 'Q&A Pairs Management',
    'qa_bulk_upload': 'Bulk Upload Q&A Pairs',
}

def require_feature(feature_code: str):
    """
    Decorator to protect endpoints that require paid features.

    Usage:
        @router.get("/interview")
        @require_feature("interview_practice")
        async def start_interview(user_id: str):
            ...
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract user_id from request
            # This depends on your auth system
            request: Request = kwargs.get('request') or args[0]
            user_id = getattr(request.state, 'user_id', None)

            if not user_id:
                raise HTTPException(status_code=401, detail="Unauthorized")

            # Check feature access
            supabase = get_supabase_client()
            result = supabase.rpc('user_has_feature', {
                'p_user_id': user_id,
                'p_feature_code': feature_code
            }).execute()

            has_access = result.data if result.data else False

            if not has_access:
                feature_name = FEATURE_FLAGS.get(feature_code, feature_code)
                raise HTTPException(
                    status_code=403,
                    detail={
                        "error": "feature_locked",
                        "message": f"This feature requires: {feature_name}",
                        "feature_code": feature_code,
                        "upgrade_url": "/pricing"
                    }
                )

            return await func(*args, **kwargs)
        return wrapper
    return decorator
```

### 2. Subscription API
**File:** `backend/app/api/subscriptions.py` (NEW)

```python
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from app.core.supabase import get_supabase_client

router = APIRouter(prefix="/api/subscriptions", tags=["subscriptions"])

class SubscriptionResponse(BaseModel):
    active_features: List[str]
    active_plans: List[dict]
    total_spent_usd: float

@router.get("/{user_id}")
async def get_user_subscriptions(user_id: str) -> SubscriptionResponse:
    """Get user's active subscriptions and features"""
    supabase = get_supabase_client()

    # Get active features
    features_result = supabase.rpc('get_user_features', {
        'p_user_id': user_id
    }).execute()
    active_features = features_result.data or []

    # Get active subscriptions
    subs_result = supabase.table("user_subscriptions")\
        .select("*, pricing_plans(*)")\
        .eq("user_id", user_id)\
        .eq("status", "active")\
        .execute()

    active_plans = subs_result.data or []

    # Calculate total spent
    total_result = supabase.table("payment_transactions")\
        .select("amount_usd")\
        .eq("user_id", user_id)\
        .eq("payment_status", "completed")\
        .execute()

    total_spent = sum(t['amount_usd'] for t in (total_result.data or []))

    return SubscriptionResponse(
        active_features=active_features,
        active_plans=active_plans,
        total_spent_usd=total_spent
    )

@router.get("/plans/available")
async def get_available_plans():
    """Get all available pricing plans"""
    supabase = get_supabase_client()
    result = supabase.table("pricing_plans")\
        .select("*")\
        .eq("is_active", True)\
        .execute()

    return {"plans": result.data or []}
```

### 3. Stripe Integration
**File:** `backend/app/api/payments.py` (NEW)

```python
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import stripe
from app.core.config import settings
from app.core.supabase import get_supabase_client

stripe.api_key = settings.STRIPE_SECRET_KEY
router = APIRouter(prefix="/api/payments", tags=["payments"])

class CreateCheckoutRequest(BaseModel):
    user_id: str
    plan_code: str
    success_url: str
    cancel_url: str

@router.post("/create-checkout-session")
async def create_checkout_session(request: CreateCheckoutRequest):
    """Create Stripe checkout session for a plan"""
    supabase = get_supabase_client()

    # Get plan details
    plan_result = supabase.table("pricing_plans")\
        .select("*")\
        .eq("plan_code", request.plan_code)\
        .execute()

    if not plan_result.data:
        raise HTTPException(status_code=404, detail="Plan not found")

    plan = plan_result.data[0]

    # Create Stripe checkout session
    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'unit_amount': int(plan['price_usd'] * 100),  # Convert to cents
                    'product_data': {
                        'name': plan['plan_name'],
                        'description': plan['description'],
                    },
                },
                'quantity': 1,
            }],
            mode='payment',  # One-time payment
            success_url=request.success_url,
            cancel_url=request.cancel_url,
            metadata={
                'user_id': request.user_id,
                'plan_code': request.plan_code,
            }
        )

        return {"checkout_url": checkout_session.url}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/webhook")
async def stripe_webhook(request: Request):
    """Handle Stripe webhook events"""
    payload = await request.body()
    sig_header = request.headers.get('stripe-signature')

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Handle successful payment
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        user_id = session['metadata']['user_id']
        plan_code = session['metadata']['plan_code']

        # Grant feature access
        supabase = get_supabase_client()

        # Create subscription
        supabase.table("user_subscriptions").insert({
            "user_id": user_id,
            "plan_code": plan_code,
            "status": "active",
            "stripe_subscription_id": session['id']
        }).execute()

        # Record transaction
        supabase.table("payment_transactions").insert({
            "user_id": user_id,
            "plan_code": plan_code,
            "amount_usd": session['amount_total'] / 100,
            "payment_method": "stripe",
            "payment_status": "completed",
            "stripe_payment_intent_id": session['payment_intent']
        }).execute()

    return {"status": "success"}
```

---

## Frontend Implementation

### 1. Pricing Page
**File:** `frontend/src/app/pricing/page.tsx` (NEW)

Shows all available plans with clear feature comparison and CTA buttons.

### 2. Feature Lock Components
**File:** `frontend/src/components/FeatureLock.tsx` (NEW)

Shows upgrade prompt when user tries to access locked features.

### 3. Update Navigation
Add "Pricing" link to header and show upgrade prompts on locked pages.

---

## Feature Gate Locations

### Interview Practice ($5)
- **Frontend:** `/app/interview/page.tsx` - Show upgrade prompt if not subscribed
- **Backend:** `/api/websocket.py` - Block WebSocket if not subscribed

### AI Q&A Generator ($10)
- **Frontend:** `/app/profile/qa-pairs/page.tsx` - Hide "AI Generate" button
- **Backend:** `/api/context_upload.py` - Block generation endpoints

### Q&A Pairs CRUD ($25)
- **Frontend:** `/app/profile/qa-pairs/page.tsx` - Show read-only view
- **Backend:** `/api/qa_pairs.py` - Block create/update/delete/bulk_upload

---

## Migration Plan

### Phase 1: Database Setup
1. Create `pricing_plans`, `user_subscriptions`, `payment_transactions` tables
2. Add helper functions
3. Seed initial pricing data

### Phase 2: Backend
1. Implement feature gate middleware
2. Add subscription API endpoints
3. Integrate Stripe payment flow
4. Add feature checks to protected endpoints

### Phase 3: Frontend
1. Create pricing page
2. Add FeatureLock components
3. Update navigation
4. Add upgrade prompts

### Phase 4: Testing
1. Test payment flow end-to-end
2. Verify feature gates work correctly
3. Test webhook handling

---

## Environment Variables

Add to `.env`:
```bash
STRIPE_SECRET_KEY=sk_test_...
STRIPE_PUBLISHABLE_KEY=pk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
```

---

## Future Enhancements

1. **Subscription Plans**: Monthly/annual recurring payments
2. **Team Plans**: Multi-user access
3. **Usage-based Pricing**: Pay per interview session
4. **Promotional Codes**: Discounts and referrals
5. **Localization**: Support KRW, EUR, etc.
6. **Alternative Payment Methods**: PayPal, Korean gateways (Toss, KakaoPay)
