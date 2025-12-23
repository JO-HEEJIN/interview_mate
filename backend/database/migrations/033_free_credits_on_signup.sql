-- Migration 033: Grant free credits to new users on signup
-- Gives 3 free interview credits when a new user profile is created

-- First, create a pricing plan for free credits (if not exists)
INSERT INTO public.pricing_plans (plan_code, plan_name, plan_type, description, price_usd, credits_amount, features, display_order, is_active)
VALUES (
    'free_starter',
    'Welcome Credits',
    'credits',
    'Free starter credits for new users',
    0.00,
    3,
    '["interview_practice"]',
    0,
    false  -- Hidden from pricing page
)
ON CONFLICT (plan_code) DO NOTHING;

-- Function to grant free credits to new users
CREATE OR REPLACE FUNCTION grant_free_credits_on_signup()
RETURNS TRIGGER AS $$
BEGIN
    -- Check if user already has any subscriptions (avoid duplicate grants)
    IF NOT EXISTS (
        SELECT 1 FROM public.user_subscriptions
        WHERE user_id = NEW.id
    ) THEN
        -- Grant 3 free interview credits
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
            3,
            0,
            3,
            jsonb_build_object(
                'granted_reason', 'signup_bonus',
                'granted_at', NOW()
            )
        );

        RAISE NOTICE 'Granted 3 free credits to new user: %', NEW.id;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Create trigger on profiles table
DROP TRIGGER IF EXISTS trigger_grant_free_credits ON public.profiles;

CREATE TRIGGER trigger_grant_free_credits
    AFTER INSERT ON public.profiles
    FOR EACH ROW
    EXECUTE FUNCTION grant_free_credits_on_signup();

-- Comment
COMMENT ON FUNCTION grant_free_credits_on_signup IS 'Automatically grants 3 free interview credits when a new user signs up';
