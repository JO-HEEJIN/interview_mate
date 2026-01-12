-- Migration 034: Grant 100 credits and all one-time features to specific user
-- User email: sc.im@mail.utoronto.ca

-- ============================================================================
-- 1. CREATE ADMIN GRANT PLAN (for free credits grant)
-- ============================================================================
INSERT INTO public.pricing_plans (plan_code, plan_name, plan_type, description, price_usd, credits_amount, features, is_active, display_order)
VALUES ('admin_grant', 'Admin Grant', 'credits', 'Administrative credit grant', 0.00, 100, '["interview_practice"]', false, 999)
ON CONFLICT (plan_code) DO NOTHING;

-- ============================================================================
-- 2. GRANT FEATURES TO USER
-- ============================================================================
DO $$
DECLARE
    target_user_id UUID;
    target_email TEXT := 'sc.im@mail.utoronto.ca';
BEGIN
    -- Get user ID from auth.users table
    SELECT id INTO target_user_id
    FROM auth.users
    WHERE email = target_email;

    IF target_user_id IS NULL THEN
        RAISE NOTICE 'User with email % not found. Skipping grants.', target_email;
        RETURN;
    END IF;

    RAISE NOTICE 'Found user % with ID: %', target_email, target_user_id;

    -- Grant 100 interview credits
    INSERT INTO public.user_subscriptions (
        user_id,
        plan_code,
        plan_type,
        status,
        credits_total,
        credits_used,
        credits_remaining,
        metadata
    ) VALUES (
        target_user_id,
        'admin_grant',
        'credits',
        'active',
        100,
        0,
        100,
        '{"granted_by": "admin", "reason": "promotional grant"}'::jsonb
    );

    RAISE NOTICE 'Granted 100 credits to %', target_email;

    -- Grant AI Q&A Generator (if not already owned)
    INSERT INTO public.user_subscriptions (
        user_id,
        plan_code,
        plan_type,
        status,
        usage_count,
        usage_limit,
        metadata
    )
    SELECT
        target_user_id,
        'ai_generator',
        'one_time',
        'active',
        0,
        NULL,  -- unlimited uses
        '{"granted_by": "admin", "reason": "promotional grant"}'::jsonb
    WHERE NOT EXISTS (
        SELECT 1 FROM public.user_subscriptions
        WHERE user_id = target_user_id
        AND plan_code = 'ai_generator'
        AND status IN ('active', 'depleted')
    );

    RAISE NOTICE 'Granted AI Q&A Generator to %', target_email;

    -- Grant Q&A Management (if not already owned)
    INSERT INTO public.user_subscriptions (
        user_id,
        plan_code,
        plan_type,
        status,
        usage_count,
        usage_limit,
        metadata
    )
    SELECT
        target_user_id,
        'qa_management',
        'one_time',
        'active',
        0,
        NULL,  -- unlimited
        '{"granted_by": "admin", "reason": "promotional grant"}'::jsonb
    WHERE NOT EXISTS (
        SELECT 1 FROM public.user_subscriptions
        WHERE user_id = target_user_id
        AND plan_code = 'qa_management'
        AND status IN ('active', 'depleted')
    );

    RAISE NOTICE 'Granted Q&A Management to %', target_email;
    RAISE NOTICE 'Successfully granted all features to %', target_email;

END $$;
