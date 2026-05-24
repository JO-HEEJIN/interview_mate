-- Migration 044: Expose feature source ("purchased" vs "first_profile_free")
--                in get_user_features_summary
--
-- Migration 043 collapsed both reasons (purchased OR first_profile_free) into a
-- single boolean per feature, which means the frontend cannot distinguish
-- "user paid" from "user is on the first-profile trial". The pricing page
-- ends up showing "Owned" on the AI Generator / Q&A Management cards for
-- users who haven't actually paid yet — confusing.
--
-- This migration keeps the existing booleans (so old clients still work) and
-- adds three new fields:
--   - ai_generator_source: 'purchased' | 'first_profile_free' | 'locked'
--   - qa_management_source: 'purchased' | 'first_profile_free' | 'locked'
--   - profile_count: INTEGER (for UI transitions, e.g. 1 → 2 paywall toast)

BEGIN;

CREATE OR REPLACE FUNCTION get_user_features_summary(p_user_id UUID)
RETURNS JSONB AS $$
DECLARE
    result             JSONB;
    profile_count      INTEGER;
    first_profile_free BOOLEAN;
    ai_purchased       BOOLEAN;
    qa_purchased       BOOLEAN;
BEGIN
    SELECT COUNT(*) INTO profile_count
    FROM public.user_interview_profiles
    WHERE user_id = p_user_id;

    first_profile_free := profile_count <= 1;
    ai_purchased       := user_has_feature(p_user_id, 'ai_qa_generation');
    qa_purchased       := user_has_feature(p_user_id, 'qa_pairs_crud');

    SELECT jsonb_build_object(
        'interview_credits',       get_user_interview_credits(p_user_id),
        'ai_generator_available',  ai_purchased OR first_profile_free,
        'qa_management_available', qa_purchased OR first_profile_free,
        'ai_generator_source',     CASE
                                      WHEN ai_purchased       THEN 'purchased'
                                      WHEN first_profile_free THEN 'first_profile_free'
                                      ELSE                         'locked'
                                   END,
        'qa_management_source',    CASE
                                      WHEN qa_purchased       THEN 'purchased'
                                      WHEN first_profile_free THEN 'first_profile_free'
                                      ELSE                         'locked'
                                   END,
        'profile_count',           profile_count,
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
    'Summary of user features and credits. Booleans (*_available) are kept for compatibility; new *_source fields distinguish purchased vs first_profile_free vs locked. profile_count enables UI transitions (e.g. paywall toast when 1 → 2).';

COMMIT;
