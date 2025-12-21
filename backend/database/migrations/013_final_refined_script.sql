-- Final refined script with ChatGPT's micro-adjustments
-- "internal targets" + immediate recovery + specific language

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

    -- 1. UPDATE "Tell me about yourself" - FINAL REFINED VERSION
    UPDATE public.qa_pairs
    SET answer = 'I''m Heejin Jo, and I''m a startup founder and AI engineer motivated by technology for human benefit. I''ve been building AI systems for vulnerable populations, particularly in mental health. I built Birth2Death entirely on OpenAI''s API and solved the exact production challenges your customers face—implementing model routing to reduce unit costs by 80%, maintaining sub-second latency, and designing the system to scale. Before we dive deeper, I need to clarify something important about my resume. The Birth2Death metrics—specifically the user count and retention data—were phrased in a way that implies live production usage. To be completely transparent: the platform is fully engineered and production-ready, but it hasn''t launched publicly yet. Those were internal targets, not current production metrics. I should have been clearer about our stage. That''s on me. What I can stand behind confidently is the engineering work itself. I wanted to address this upfront because I know how much OpenAI values accuracy and integrity. The architecture, the OpenAI API integration, and the optimization decisions are all real and documented. I can walk you through the architecture and the specific tradeoffs I made, if that''s helpful. Now I want to help dozens of startups succeed with OpenAI, bringing both the technical depth and the cultural bridge that Korea''s ''First Mover'' AI ecosystem needs.'
    WHERE user_id = heejin_uuid
    AND question = 'Tell me about yourself';

    -- 2. UPDATE "Are these numbers accurate?" - REFINED
    UPDATE public.qa_pairs
    SET answer = 'That''s a great question, and I want to be precise. The cost reduction—from 45 cents to 9 cents—and the architecture design are validated through load testing. However, I need to clarify: those user numbers were internal targets for our launch capacity, not current production metrics. The platform is fully engineered but hasn''t launched publicly yet. What I can stand behind confidently is all the technical work—the architecture, the tradeoffs, the engineering decisions. I can walk you through any of it.'
    WHERE user_id = heejin_uuid
    AND question = 'Are these numbers on your resume accurate?';

    RAISE NOTICE 'Updated to final refined version with micro-adjustments';
END $$;

-- Verify
SELECT question, LEFT(answer, 150) as answer_preview
FROM qa_pairs
WHERE user_id = (SELECT id FROM auth.users WHERE email = 'midmost44@gmail.com')
AND question = 'Tell me about yourself';
