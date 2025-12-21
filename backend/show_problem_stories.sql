-- Show full content of the 3 problem STAR stories

SELECT
    title,
    situation,
    task,
    action,
    result,
    tags
FROM star_stories
WHERE user_id = (SELECT id::text FROM auth.users WHERE email = 'midmost44@gmail.com')
AND title IN (
    'LLM Cost Optimization - 80% Reduction at Birth2Death',
    'P95 Latency Reduction from 3s to under 1s',
    'Thriving in Startup Ambiguity'
)
ORDER BY title;
