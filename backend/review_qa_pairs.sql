-- Review all Q&A pairs for potentially inflated claims
-- Look for these red flags:
-- 1. User numbers/metrics (1000+, 4.1/5, 68%, 99.9%)
-- 2. "Production" claims
-- 3. "Serving users" language
-- 4. Measured retention/satisfaction

SELECT
    question,
    answer,
    question_type,
    source,
    usage_count
FROM public.qa_pairs
WHERE user_id = (SELECT id FROM auth.users WHERE email = 'midmost44@gmail.com')
ORDER BY question;

-- Also check for specific red flag phrases
SELECT
    question,
    answer,
    CASE
        WHEN answer ILIKE '%1000%' OR answer ILIKE '%1,000%' THEN 'Contains user count'
        WHEN answer ILIKE '%serving%users%' THEN 'Claims serving users'
        WHEN answer ILIKE '%production%' THEN 'Claims production'
        WHEN answer ILIKE '%retention%' OR answer ILIKE '%satisfaction%' THEN 'Contains metrics'
        WHEN answer ILIKE '%uptime%' THEN 'Contains uptime claim'
        ELSE 'OK'
    END as red_flag
FROM public.qa_pairs
WHERE user_id = (SELECT id FROM auth.users WHERE email = 'midmost44@gmail.com')
AND (
    answer ILIKE '%1000%' OR
    answer ILIKE '%1,000%' OR
    answer ILIKE '%serving%users%' OR
    answer ILIKE '%production%' OR
    answer ILIKE '%retention%' OR
    answer ILIKE '%satisfaction%' OR
    answer ILIKE '%uptime%'
)
ORDER BY red_flag, question;
