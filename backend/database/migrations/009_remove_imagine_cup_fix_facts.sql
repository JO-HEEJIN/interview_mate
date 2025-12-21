-- CRITICAL: Remove all Microsoft Imagine Cup references (FALSE CLAIM)
-- Fix NASA award terminology and other factual errors

DO $$
DECLARE
    heejin_uuid UUID;
BEGIN
    -- Get user ID
    SELECT id INTO heejin_uuid
    FROM auth.users
    WHERE email = 'midmost44@gmail.com';

    IF heejin_uuid IS NULL THEN
        RAISE EXCEPTION 'User not found';
    END IF;

    -- 1. Remove ALL Imagine Cup references (THIS WAS FALSE!)
    UPDATE public.qa_pairs
    SET answer = REPLACE(answer, 'Microsoft Imagine Cup 2026 acceptance', '')
    WHERE user_id = heejin_uuid
    AND answer LIKE '%Imagine Cup%';

    UPDATE public.qa_pairs
    SET answer = REPLACE(answer, 'Microsoft Imagine Cup 2026 submission (accepted to competition)', '')
    WHERE user_id = heejin_uuid
    AND answer LIKE '%Imagine Cup%';

    UPDATE public.qa_pairs
    SET answer = REPLACE(answer, ', Microsoft Imagine Cup', '')
    WHERE user_id = heejin_uuid
    AND answer LIKE '%Imagine Cup%';

    -- Clean up any remaining Imagine Cup text
    UPDATE public.qa_pairs
    SET answer = REGEXP_REPLACE(answer, 'Microsoft Imagine Cup[^.]*\.?\s*', '', 'g')
    WHERE user_id = heejin_uuid
    AND answer LIKE '%Imagine Cup%';

    -- 2. Fix NASA award terminology (Local Award, not Local Impact Award)
    UPDATE public.qa_pairs
    SET answer = REPLACE(answer, 'Local Impact Award', 'Local Award')
    WHERE user_id = heejin_uuid
    AND answer LIKE '%Local Impact Award%';

    UPDATE public.qa_pairs
    SET answer = REPLACE(answer, 'local impact award', 'local award')
    WHERE user_id = heejin_uuid
    AND answer LIKE '%local impact award%';

    -- 3. Update "Tell me about yourself" with correct facts
    UPDATE public.qa_pairs
    SET answer = 'I''m Heejin Jo, and I''ve been building AI systems for startups, with a focus on vulnerable user populations. The project I''ve invested most deeply in is Birth2Death, a mental health AI platform. I want to be upfront: my resume cited user projections, but we haven''t launched yet. I built a visionOS MVP, and we''re now planning an iOS launch. The technical architecture is production-ready, but we''re still in testing. I''m bringing this up because integrity matters, especially at OpenAI.'
    WHERE user_id = heejin_uuid
    AND question = 'Tell me about yourself';

    -- 4. Update "Tell me about Birth2Death" with correct facts
    UPDATE public.qa_pairs
    SET answer = 'It''s a mental health AI platform I''ve been developing with a co-founder—we built a visionOS MVP that''s production-ready but not yet launched. We''re planning an iOS launch first. Built on OpenAI''s API—GPT-4 for complex conversations, optimized routing system. I''ve designed the production engineering architecture: 80% cost reduction through smart routing, caching for sub-second latency, high availability design. These architectures are stress-tested, not validated at scale yet, but the engineering is sound.'
    WHERE user_id = heejin_uuid
    AND question = 'Tell me about Birth2Death';

    -- 5. Update "Why leave startup" - not solo founder
    UPDATE public.qa_pairs
    SET answer = 'Honestly, I want to scale my impact beyond a single product. Birth2Death taught me how to build production AI systems, but it''s still pre-launch. As an SA at OpenAI, I can help dozens of startups avoid the mistakes I made and ship faster. I speak founder language because I am one—when they say "we''re burning too much on API calls," I know exactly what that panic feels like and how to solve it.'
    WHERE user_id = heejin_uuid
    AND question = 'Why are you leaving your startup?';

    -- 6. Update "Why not continue as founder" - mention co-founder context
    UPDATE public.qa_pairs
    SET answer = 'I love building, but I''ve learned that launching a mental health platform is really hard—clinically, legally, operationally. Even with a co-founder, getting it to market safely takes resources we don''t have. Meanwhile, the systems knowledge I''ve gained—cost optimization, latency engineering, safety architecture—that''s immediately valuable to OpenAI''s customers right now. I can help more people sooner this way.'
    WHERE user_id = heejin_uuid
    AND question = 'Why not continue as a founder?';

    -- 7. Update "Time you moved fast" - fix NASA award name
    UPDATE public.qa_pairs
    SET answer = 'I built a NASA Space Apps Challenge award-winning AI platform in 48 hours—web app, mobile AR, satellite data integration, decision agent, all of it. Won the Houston Local Award, judged by Zein who was a local mentor. This rapid prototyping ability is exactly what startups need when they''re trying to validate ideas quickly. I love fast cycles.'
    WHERE user_id = heejin_uuid
    AND question = 'Tell me about a time you moved fast';

    RAISE NOTICE 'Removed all Imagine Cup references and fixed factual errors';
END $$;

-- Verify: Check for any remaining Imagine Cup references (should be 0)
SELECT question, answer
FROM qa_pairs
WHERE user_id = (SELECT id FROM auth.users WHERE email = 'midmost44@gmail.com')
AND answer LIKE '%Imagine Cup%';

-- Verify: Check NASA award is corrected
SELECT question, LEFT(answer, 150) as answer_preview
FROM qa_pairs
WHERE user_id = (SELECT id FROM auth.users WHERE email = 'midmost44@gmail.com')
AND answer LIKE '%NASA%';
