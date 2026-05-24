-- Migration 041: Pricing redesign 2026-05
--
-- Bumps the free trial from 3 → 30 credits and restructures paid tiers to
-- drive lock-in before the paywall (see diary.md 2026-05-24).
--
-- Tier changes (credits_amount @ price_usd):
--   free_starter:     3 @ $0  →  30 @ $0
--   credits_starter: 10 @ $4  →  25 @ $5
--   credits_popular: 25 @ $8  →  60 @ $10
--   credits_pro:     50 @ $15 → 150 @ $20
--
-- Also refactors grant_free_credits_on_signup() to read credits_amount
-- dynamically from pricing_plans, so future trial-size changes only require
-- a single UPDATE on that table.
--
-- IMPORTANT: Lemon Squeezy variant prices must be updated in the dashboard
-- to match the new price_usd values (see diary.md Phase 2 checklist).

BEGIN;

-- ============================================================================
-- 1. Update pricing tiers
-- ============================================================================

UPDATE public.pricing_plans
SET credits_amount = 30,
    description    = '30 free credits for new users',
    updated_at     = NOW()
WHERE plan_code = 'free_starter';

UPDATE public.pricing_plans
SET credits_amount = 25,
    price_usd      = 5.00,
    updated_at     = NOW()
WHERE plan_code = 'credits_starter';

UPDATE public.pricing_plans
SET credits_amount = 60,
    price_usd      = 10.00,
    updated_at     = NOW()
WHERE plan_code = 'credits_popular';

UPDATE public.pricing_plans
SET credits_amount = 150,
    price_usd      = 20.00,
    updated_at     = NOW()
WHERE plan_code = 'credits_pro';

-- ============================================================================
-- 2. Refactor signup trigger to read trial size dynamically from pricing_plans
-- ============================================================================

CREATE OR REPLACE FUNCTION grant_free_credits_on_signup()
RETURNS TRIGGER AS $$
DECLARE
    trial_credits INTEGER;
BEGIN
    -- Skip if user already has any subscription (avoid duplicate grants on
    -- re-runs of the trigger or post-hoc profile inserts).
    IF EXISTS (
        SELECT 1 FROM public.user_subscriptions
        WHERE user_id = NEW.id
    ) THEN
        RETURN NEW;
    END IF;

    -- Single source of truth for trial size: pricing_plans.free_starter
    SELECT credits_amount INTO trial_credits
    FROM public.pricing_plans
    WHERE plan_code = 'free_starter';

    IF trial_credits IS NULL OR trial_credits <= 0 THEN
        RAISE WARNING 'free_starter plan not found or invalid; skipping signup grant for user %', NEW.id;
        RETURN NEW;
    END IF;

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
        NEW.id,
        'free_starter',
        'credits',
        'active',
        trial_credits,
        0,
        trial_credits,
        jsonb_build_object(
            'granted_reason', 'signup_bonus',
            'granted_at',     NOW()
        )
    );

    RAISE NOTICE 'Granted % free credits to new user: %', trial_credits, NEW.id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

COMMENT ON FUNCTION grant_free_credits_on_signup IS
    'Grants free interview credits to new users on signup. Trial size is read dynamically from pricing_plans (free_starter plan).';

-- Trigger definition itself is unchanged — CREATE OR REPLACE FUNCTION keeps
-- the existing trigger pointing at the new function body.

COMMIT;
