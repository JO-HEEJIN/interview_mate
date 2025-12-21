-- Fix remaining AI+resume mentions in 2 Q&A pairs
-- Remove "AI hallucination with my resume" narrative

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

    -- 1. UPDATE "Why OpenAI specifically?" - Remove AI hallucination mention
    UPDATE public.qa_pairs
    SET answer = 'Honestly, it''s about mission alignment. I''ve spent years building AI for vulnerable users—mental health, healthcare—where you can''t mess around with safety. OpenAI is one of the few companies that actually takes this seriously, not just in marketing but in how you build and deploy systems. The more I researched your work on hallucination and accuracy—your process supervision research, model spec work, preparedness framework—the more I realized you''re leading this work at a fundamental level. Plus, I''m already your customer—I know the platform inside out. That experience matters.'
    WHERE user_id = heejin_uuid
    AND question = 'Why OpenAI specifically?';

    -- 2. UPDATE "What do you know about OpenAI's work on reducing hallucinations?" - Remove resume mention
    UPDATE public.qa_pairs
    SET answer = 'I''ve studied your process supervision research—rewarding reasoning process instead of just outcomes. Your model spec work defines behavioral guidelines for responsible AI. The preparedness framework evaluates safety systematically. What impressed me most is that you''re addressing this at the architecture level, not just with post-hoc filters. This work is critical for production systems. As an SA, I''d help customers implement these principles—proper prompting, verification workflows, human-in-the-loop systems—to build reliable AI applications.'
    WHERE user_id = heejin_uuid
    AND question = 'What do you know about OpenAI''s work on reducing hallucinations?';

    RAISE NOTICE 'Fixed 2 remaining AI+resume mentions';
END $$;

-- Verify: Should return 1 row (only "Tell me about yourself" which is correct)
SELECT question, answer
FROM qa_pairs
WHERE user_id = (SELECT id FROM auth.users WHERE email = 'midmost44@gmail.com')
AND answer LIKE '%resume%'
ORDER BY question;
