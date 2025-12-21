-- Fix 3 STAR stories: Remove inflated metrics
-- Keep technical achievements, remove false user data

DO $$
DECLARE
    heejin_user_id TEXT;
BEGIN
    -- Get user ID as text
    SELECT id::text INTO heejin_user_id
    FROM auth.users
    WHERE email = 'midmost44@gmail.com';

    IF heejin_user_id IS NULL THEN
        RAISE EXCEPTION 'User not found';
    END IF;

    -- 1. Fix "LLM Cost Optimization" - Remove "4.2/5 satisfaction"
    UPDATE star_stories
    SET result = 'Cut costs from $0.45 to $0.09 per user (80% reduction). The architecture validated through testing proved that quality could be maintained while drastically reducing costs. Extended projected runway by 6 months.'
    WHERE user_id = heejin_user_id
    AND title = 'LLM Cost Optimization - 80% Reduction at Birth2Death';

    -- 2. Fix "P95 Latency Reduction" - Remove retention claim and "120K daily requests"
    UPDATE star_stories
    SET result = 'Achieved under 1s P95 latency. The system architecture was designed and tested to handle high-volume traffic efficiently. These optimizations are production-ready and documented.'
    WHERE user_id = heejin_user_id
    AND title = 'P95 Latency Reduction from 3s to under 1s';

    -- 3. Fix "Thriving in Startup Ambiguity" - Remove ALL false claims
    UPDATE star_stories
    SET
        situation = 'At Birth2Death, requirements were constantly changing. No clear roadmap. Limited resources as a bootstrapped startup.',
        result = 'Shipped MVP in 2 weeks with core functionality complete. Built production-ready architecture despite uncertainty. This rapid iteration approach is what startups need when validating ideas quickly.',
        tags = ARRAY['ambiguity', 'startup', 'MVP', 'iteration']
    WHERE user_id = heejin_user_id
    AND title = 'Thriving in Startup Ambiguity';

    RAISE NOTICE 'Fixed 3 STAR stories - removed inflated metrics';
END $$;

-- Verify: Check the fixed stories
SELECT
    title,
    result
FROM star_stories
WHERE user_id = (SELECT id::text FROM auth.users WHERE email = 'midmost44@gmail.com')
AND title IN (
    'LLM Cost Optimization - 80% Reduction at Birth2Death',
    'P95 Latency Reduction from 3s to under 1s',
    'Thriving in Startup Ambiguity'
)
ORDER BY title;
