-- Check all STAR stories for inflated claims or inconsistencies

SELECT
    title,
    LEFT(situation, 100) as situation_preview,
    LEFT(task, 100) as task_preview,
    LEFT(action, 100) as action_preview,
    LEFT(result, 100) as result_preview,
    tags
FROM star_stories
WHERE user_id = (SELECT id::text FROM auth.users WHERE email = 'midmost44@gmail.com')
ORDER BY title;

-- Also check for specific red flags in STAR stories
SELECT
    title,
    CASE
        WHEN situation LIKE '%1000%' OR situation LIKE '%1,000%' THEN 'Contains user count in situation'
        WHEN task LIKE '%1000%' OR task LIKE '%1,000%' THEN 'Contains user count in task'
        WHEN action LIKE '%1000%' OR action LIKE '%1,000%' THEN 'Contains user count in action'
        WHEN result LIKE '%1000%' OR result LIKE '%1,000%' THEN 'Contains user count in result'
        WHEN result LIKE '%retention%' THEN 'Contains retention claim'
        WHEN result LIKE '%satisfaction%' THEN 'Contains satisfaction claim'
        WHEN result LIKE '%users%' AND result LIKE '%serving%' THEN 'Contains serving users claim'
        ELSE 'OK'
    END as red_flag
FROM star_stories
WHERE user_id = (SELECT id::text FROM auth.users WHERE email = 'midmost44@gmail.com')
AND (
    situation LIKE '%1000%' OR situation LIKE '%1,000%' OR
    task LIKE '%1000%' OR task LIKE '%1,000%' OR
    action LIKE '%1000%' OR action LIKE '%1,000%' OR
    result LIKE '%1000%' OR result LIKE '%1,000%' OR
    result LIKE '%retention%' OR
    result LIKE '%satisfaction%' OR
    (result LIKE '%users%' AND result LIKE '%serving%')
)
ORDER BY title;
