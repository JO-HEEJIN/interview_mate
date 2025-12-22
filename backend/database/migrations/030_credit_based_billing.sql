-- Migration 030: Credit-Based Billing System
-- Implements pay-as-you-go interview credits and one-time feature purchases

-- ============================================================================
-- 1. PRICING PLANS TABLE
-- ============================================================================
CREATE TABLE public.pricing_plans (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    plan_code VARCHAR(50) UNIQUE NOT NULL,
    plan_name VARCHAR(100) NOT NULL,
    plan_type VARCHAR(50) NOT NULL CHECK (
        plan_type IN ('credits', 'one_time', 'subscription')
    ),
    description TEXT,
    price_usd DECIMAL(10, 2) NOT NULL,
    credits_amount INTEGER DEFAULT 0, -- For credit packs only
    features JSONB NOT NULL DEFAULT '[]', -- Array of feature codes
    metadata JSONB DEFAULT '{}',
    is_active BOOLEAN DEFAULT true,
    display_order INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Seed pricing plans
INSERT INTO public.pricing_plans (plan_code, plan_name, plan_type, description, price_usd, credits_amount, features, display_order) VALUES
-- Interview Credit Packs
('credits_starter', 'Starter Pack', 'credits', '10 interview practice sessions', 4.00, 10, '["interview_practice"]', 1),
('credits_popular', 'Popular Pack', 'credits', '25 interview practice sessions (20% off)', 8.00, 25, '["interview_practice"]', 2),
('credits_pro', 'Pro Pack', 'credits', '50 interview practice sessions (25% off)', 15.00, 50, '["interview_practice"]', 3),

-- One-time Feature Purchases
('ai_generator', 'AI Q&A Generator', 'one_time', 'Auto-generate 30 Q&A pairs from your resume (one-time use)', 10.00, 0, '["ai_qa_generation"]', 4),
('qa_management', 'Q&A Management', 'one_time', 'Create, edit, and bulk upload unlimited Q&A pairs', 25.00, 0, '["qa_pairs_crud", "qa_bulk_upload"]', 5);

-- ============================================================================
-- 2. USER SUBSCRIPTIONS TABLE (Modified for Credits)
-- ============================================================================
CREATE TABLE public.user_subscriptions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
    plan_code VARCHAR(50) NOT NULL REFERENCES public.pricing_plans(plan_code),
    plan_type VARCHAR(50) NOT NULL CHECK (
        plan_type IN ('credits', 'one_time', 'subscription')
    ),
    status VARCHAR(50) NOT NULL DEFAULT 'active' CHECK (
        status IN ('active', 'depleted', 'cancelled', 'expired', 'refunded')
    ),

    -- Credit tracking (for credit packs only)
    credits_total INTEGER DEFAULT 0, -- Total credits purchased
    credits_used INTEGER DEFAULT 0, -- Credits consumed
    credits_remaining INTEGER DEFAULT 0, -- Available credits

    -- Usage tracking (for one-time purchases)
    usage_count INTEGER DEFAULT 0, -- Times feature has been used
    usage_limit INTEGER, -- Max uses allowed (NULL = unlimited)

    -- Timestamps
    purchased_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_used_at TIMESTAMP WITH TIME ZONE,
    expires_at TIMESTAMP WITH TIME ZONE, -- NULL = never expires

    -- Payment integration
    stripe_payment_intent_id VARCHAR(255),
    stripe_customer_id VARCHAR(255),

    -- Metadata
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_user_subscriptions_user ON public.user_subscriptions(user_id);
CREATE INDEX idx_user_subscriptions_status ON public.user_subscriptions(user_id, status);
CREATE INDEX idx_user_subscriptions_plan ON public.user_subscriptions(plan_code);
CREATE INDEX idx_user_subscriptions_credits ON public.user_subscriptions(user_id, credits_remaining) WHERE plan_type = 'credits';

-- ============================================================================
-- 3. PAYMENT TRANSACTIONS TABLE
-- ============================================================================
CREATE TABLE public.payment_transactions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
    subscription_id UUID REFERENCES public.user_subscriptions(id) ON DELETE SET NULL,
    plan_code VARCHAR(50) NOT NULL REFERENCES public.pricing_plans(plan_code),

    -- Payment details
    amount_usd DECIMAL(10, 2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD',
    payment_method VARCHAR(50) NOT NULL, -- 'stripe', 'paypal', etc.
    payment_status VARCHAR(50) NOT NULL DEFAULT 'pending' CHECK (
        payment_status IN ('pending', 'processing', 'completed', 'failed', 'refunded', 'disputed')
    ),

    -- Stripe integration
    stripe_payment_intent_id VARCHAR(255) UNIQUE,
    stripe_charge_id VARCHAR(255),
    stripe_customer_id VARCHAR(255),
    stripe_receipt_url TEXT,

    -- Metadata
    failure_reason TEXT,
    metadata JSONB DEFAULT '{}',

    -- Timestamps
    completed_at TIMESTAMP WITH TIME ZONE,
    refunded_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_payment_transactions_user ON public.payment_transactions(user_id);
CREATE INDEX idx_payment_transactions_status ON public.payment_transactions(payment_status);
CREATE INDEX idx_payment_transactions_stripe_pi ON public.payment_transactions(stripe_payment_intent_id);
CREATE INDEX idx_payment_transactions_created ON public.payment_transactions(created_at DESC);

-- ============================================================================
-- 4. CREDIT USAGE LOG TABLE
-- ============================================================================
CREATE TABLE public.credit_usage_log (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
    subscription_id UUID NOT NULL REFERENCES public.user_subscriptions(id) ON DELETE CASCADE,

    -- Usage details
    credits_used INTEGER NOT NULL DEFAULT 1,
    action VARCHAR(100) NOT NULL, -- 'interview_started', 'interview_completed'

    -- Context
    session_id UUID, -- Link to interview session if applicable
    metadata JSONB DEFAULT '{}',

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_credit_usage_user ON public.credit_usage_log(user_id);
CREATE INDEX idx_credit_usage_subscription ON public.credit_usage_log(subscription_id);
CREATE INDEX idx_credit_usage_created ON public.credit_usage_log(created_at DESC);

-- ============================================================================
-- 5. HELPER FUNCTIONS
-- ============================================================================

-- Get total available interview credits for a user
CREATE OR REPLACE FUNCTION get_user_interview_credits(p_user_id UUID)
RETURNS INTEGER AS $$
DECLARE
    total_credits INTEGER;
BEGIN
    SELECT COALESCE(SUM(credits_remaining), 0)
    INTO total_credits
    FROM user_subscriptions
    WHERE user_id = p_user_id
      AND plan_type = 'credits'
      AND status = 'active'
      AND (expires_at IS NULL OR expires_at > NOW());

    RETURN total_credits;
END;
$$ LANGUAGE plpgsql;

-- Consume one interview credit
CREATE OR REPLACE FUNCTION consume_interview_credit(
    p_user_id UUID,
    p_session_id UUID DEFAULT NULL
)
RETURNS BOOLEAN AS $$
DECLARE
    v_subscription_id UUID;
    v_credits_remaining INTEGER;
BEGIN
    -- Find active subscription with credits (FIFO - oldest first)
    SELECT id, credits_remaining
    INTO v_subscription_id, v_credits_remaining
    FROM user_subscriptions
    WHERE user_id = p_user_id
      AND plan_type = 'credits'
      AND status = 'active'
      AND credits_remaining > 0
      AND (expires_at IS NULL OR expires_at > NOW())
    ORDER BY purchased_at ASC
    LIMIT 1
    FOR UPDATE;

    IF v_subscription_id IS NULL THEN
        RETURN FALSE; -- No credits available
    END IF;

    -- Decrement credit
    UPDATE user_subscriptions
    SET credits_remaining = credits_remaining - 1,
        credits_used = credits_used + 1,
        last_used_at = NOW(),
        status = CASE
            WHEN credits_remaining - 1 = 0 THEN 'depleted'
            ELSE 'active'
        END,
        updated_at = NOW()
    WHERE id = v_subscription_id;

    -- Log usage
    INSERT INTO credit_usage_log (user_id, subscription_id, credits_used, action, session_id)
    VALUES (p_user_id, v_subscription_id, 1, 'interview_completed', p_session_id);

    RETURN TRUE;
END;
$$ LANGUAGE plpgsql;

-- Check if user has access to a feature
CREATE OR REPLACE FUNCTION user_has_feature(p_user_id UUID, p_feature_code VARCHAR)
RETURNS BOOLEAN AS $$
BEGIN
    RETURN EXISTS (
        SELECT 1
        FROM user_subscriptions us
        JOIN pricing_plans pp ON us.plan_code = pp.plan_code
        WHERE us.user_id = p_user_id
          AND us.status IN ('active', 'depleted') -- Allow depleted for one-time purchases
          AND pp.features @> to_jsonb(ARRAY[p_feature_code])
          AND (us.expires_at IS NULL OR us.expires_at > NOW())
          AND (
              -- Credits: Must have remaining credits
              (us.plan_type = 'credits' AND us.credits_remaining > 0)
              OR
              -- One-time: Always accessible once purchased
              (us.plan_type = 'one_time')
              OR
              -- Subscription: Must be active
              (us.plan_type = 'subscription' AND us.status = 'active')
          )
    );
END;
$$ LANGUAGE plpgsql;

-- Get user's active features summary
CREATE OR REPLACE FUNCTION get_user_features_summary(p_user_id UUID)
RETURNS JSONB AS $$
DECLARE
    result JSONB;
BEGIN
    SELECT jsonb_build_object(
        'interview_credits', get_user_interview_credits(p_user_id),
        'ai_generator_available', user_has_feature(p_user_id, 'ai_qa_generation'),
        'qa_management_available', user_has_feature(p_user_id, 'qa_pairs_crud'),
        'active_subscriptions', (
            SELECT jsonb_agg(
                jsonb_build_object(
                    'plan_code', us.plan_code,
                    'plan_name', pp.plan_name,
                    'plan_type', us.plan_type,
                    'credits_remaining', us.credits_remaining,
                    'status', us.status
                )
            )
            FROM user_subscriptions us
            JOIN pricing_plans pp ON us.plan_code = pp.plan_code
            WHERE us.user_id = p_user_id
              AND us.status IN ('active', 'depleted')
        )
    ) INTO result;

    RETURN result;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- 6. TRIGGERS
-- ============================================================================

-- Auto-update updated_at timestamp
CREATE TRIGGER update_pricing_plans_updated_at
    BEFORE UPDATE ON public.pricing_plans
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_user_subscriptions_updated_at
    BEFORE UPDATE ON public.user_subscriptions
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_payment_transactions_updated_at
    BEFORE UPDATE ON public.payment_transactions
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- 7. ROW LEVEL SECURITY (RLS)
-- ============================================================================

ALTER TABLE public.pricing_plans ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.user_subscriptions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.payment_transactions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.credit_usage_log ENABLE ROW LEVEL SECURITY;

-- Pricing plans: Public read
CREATE POLICY "Anyone can view active pricing plans"
    ON public.pricing_plans FOR SELECT
    USING (is_active = true);

-- User subscriptions: Users can view own
CREATE POLICY "Users can view own subscriptions"
    ON public.user_subscriptions FOR SELECT
    USING (auth.uid() = user_id);

-- Payment transactions: Users can view own
CREATE POLICY "Users can view own transactions"
    ON public.payment_transactions FOR SELECT
    USING (auth.uid() = user_id);

-- Credit usage log: Users can view own
CREATE POLICY "Users can view own credit usage"
    ON public.credit_usage_log FOR SELECT
    USING (auth.uid() = user_id);

-- ============================================================================
-- 8. COMMENTS
-- ============================================================================

COMMENT ON TABLE public.pricing_plans IS 'Available pricing plans (credit packs and one-time purchases)';
COMMENT ON TABLE public.user_subscriptions IS 'User purchased features and credit balances';
COMMENT ON TABLE public.payment_transactions IS 'Payment history and audit log';
COMMENT ON TABLE public.credit_usage_log IS 'Detailed log of credit consumption';

COMMENT ON FUNCTION get_user_interview_credits IS 'Get total available interview credits across all active subscriptions';
COMMENT ON FUNCTION consume_interview_credit IS 'Consume one interview credit (FIFO) and log usage';
COMMENT ON FUNCTION user_has_feature IS 'Check if user has access to a specific feature';
COMMENT ON FUNCTION get_user_features_summary IS 'Get comprehensive summary of user features and credits';
