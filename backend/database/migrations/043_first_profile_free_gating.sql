-- Migration 043: First-profile-free gating for one-time features
--
-- Policy (see diary.md 2026-05-24): every user gets the ai_generator and
-- qa_management features FREE while their profile count is ≤ 1. From the
-- second profile onward they need to purchase those features as before.
--
-- Rationale: users who just signed up and built their first profile are at
-- the moment of strongest "wow, this is useful" perception. Paywalling the
-- resume → Q&A generation flow at that moment is the biggest conversion
-- killer in the current funnel. By the time they create a SECOND profile
-- (e.g. for a different company or role), the value is clear and the
-- purchase friction is justified — duplicating a profile does not copy Q&A
-- pairs anyway, so the feature is genuinely needed again.
--
-- Implementation: a single OR added to get_user_features_summary(). All
-- frontend gating already reads from this summary, so no other code touches
-- are required for the boolean to flip.
--
-- Backend endpoint enforcement (context_upload.py, qa_pairs.py) is OUT OF
-- SCOPE for this migration — those endpoints currently trust the frontend
-- gating. Tightening them is tracked separately.

BEGIN;

CREATE OR REPLACE FUNCTION get_user_features_summary(p_user_id UUID)
RETURNS JSONB AS $$
DECLARE
    result             JSONB;
    profile_count      INTEGER;
    first_profile_free BOOLEAN;
BEGIN
    -- ≤ 1 profile means the user is still on their "first profile" and
    -- therefore qualifies for the free one-time-feature trial.
    SELECT COUNT(*) INTO profile_count
    FROM public.user_interview_profiles
    WHERE user_id = p_user_id;

    first_profile_free := profile_count <= 1;

    SELECT jsonb_build_object(
        'interview_credits',       get_user_interview_credits(p_user_id),
        'ai_generator_available',  user_has_feature(p_user_id, 'ai_qa_generation') OR first_profile_free,
        'qa_management_available', user_has_feature(p_user_id, 'qa_pairs_crud')    OR first_profile_free,
        'active_subscriptions', (
            SELECT jsonb_agg(
                jsonb_build_object(
                    'plan_code',         us.plan_code,
                    'plan_name',         pp.plan_name,
                    'plan_type',         us.plan_type,
                    'credits_remaining', us.credits_remaining,
                    'status',            us.status
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

COMMENT ON FUNCTION get_user_features_summary IS
    'Summary of user features and credits. ai_generator and qa_management are granted for free while the user has ≤ 1 interview profile (first-profile-free trial, diary.md 2026-05-24).';

COMMIT;
