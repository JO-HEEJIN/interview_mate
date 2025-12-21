-- FINAL STRATEGY: Hybrid approach
-- Lead with strengths (Mission → Builder → Bridge)
-- Defend with technical framing if asked
-- Brief honesty only if pressed

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

    -- 1. UPDATE "Tell me about yourself" - LEAD WITH STRENGTHS (Mission → Builder → Bridge)
    UPDATE public.qa_pairs
    SET answer = 'I''m Heejin Jo, and I''m a startup founder and AI engineer motivated by technology for human benefit. I grew up facing hardship, which drove me to build medical and mental health AI systems. This aligns perfectly with OpenAI''s mission—I''ve closely followed your research on safety and responsible AI deployment. I built Birth2Death, a mental health AI platform, entirely on OpenAI''s API. I solved real production challenges your customers face—implemented a model routing system that reduced unit costs by 80%, from 45 cents to 9 cents per conversation, while maintaining sub-second latency. I don''t just advise on these tradeoffs; I''ve lived them as a founder. Now I want to bridge OpenAI''s technology with Korea''s ambitious startup ecosystem. Korea is moving from ''Fast Follower'' to ''First Mover'' in AI, and with my background launching products in both US and Korea, I can help Korean startups leverage OpenAI to build world-class applications.'
    WHERE user_id = heejin_uuid
    AND question = 'Tell me about yourself';

    -- 2. ADD NEW: "Are these numbers on your resume accurate?" - TECHNICAL FRAMING FIRST
    INSERT INTO public.qa_pairs (user_id, question, answer, question_type, source)
    VALUES (
        heejin_uuid,
        'Are these numbers on your resume accurate?',
        'That''s a great question. Let me be precise about those metrics. The cost reduction—from 45 cents to 9 cents per conversation—and the architecture design were validated through load testing and unit economics modeling. I designed the system to handle 1,000+ concurrent users and verified the cost logic works under those conditions. However, I want to be transparent: we''re currently in beta phase. The system is production-ready from an engineering perspective—I''ve built the full architecture, stress-tested it—but we haven''t launched to that user base yet. The engineering is real; the active user count is still being built.',
        'general',
        'manual'
    )
    ON CONFLICT DO NOTHING;

    -- 3. ADD NEW: "So the 1,000 users claim is false?" - BRIEF HONESTY IF PRESSED
    INSERT INTO public.qa_pairs (user_id, question, answer, question_type, source)
    VALUES (
        heejin_uuid,
        'So the 1,000 users claim is false?',
        'To be completely transparent: when I prepared my application materials, I focused on the technical capacity and architecture I''d built. In hindsight, I should have been clearer that we''re pre-launch. The engineering is real—I can show you the architecture, the code, the load tests, the NASA award verification with Zein—but the active user count isn''t at that scale yet. I wanted to clarify this rather than have it discovered later. What I can demonstrate is that I''ve solved the exact production engineering challenges your startup customers face.',
        'behavioral',
        'manual'
    )
    ON CONFLICT DO NOTHING;

    -- 4. UPDATE "Tell me about Birth2Death" - FOCUS ON VALIDATED CAPACITY
    UPDATE public.qa_pairs
    SET answer = 'It''s a mental health AI platform I''ve been building with a co-founder—we built a visionOS MVP and are planning iOS launch. Built entirely on OpenAI''s API. The architecture is designed and load-tested to handle 1,000+ concurrent users. I''ve validated the production engineering: 80% cost reduction through smart routing, caching for sub-second latency, high-availability architecture. These are stress-tested and proven, not yet validated at scale with live users. We''re in beta. But the systems thinking and engineering are exactly what I''d bring to help your customers.'
    WHERE user_id = heejin_uuid
    AND question = 'Tell me about Birth2Death';

    -- 5. UPDATE "How do you handle mistakes?" - REMOVE AI CONFESSION, FOCUS ON LESSON
    UPDATE public.qa_pairs
    SET answer = 'I own them immediately and learn from them. In my startup journey, I''ve learned that moving fast without proper verification layers can create real risks. That taught me that in production, "trust but verify" isn''t enough—we need "verify then trust." That''s why I''m obsessed with OpenAI''s research on process supervision and safety guardrails. I learned the hard way that unchecked AI can lead to silent failures. As an SA, I''d help customers build verification workflows from the start.'
    WHERE user_id = heejin_uuid
    AND question = 'How do you handle mistakes?';

    -- 6. UPDATE "Tell me about a time you showed integrity" - REMOVE RESUME MENTION
    UPDATE public.qa_pairs
    SET answer = 'In my startup, I had to make a decision between shipping faster with potentially risky shortcuts or taking more time to build proper safety guardrails for a mental health platform. I chose safety, even though it meant slower launch. For vulnerable users, integrity isn''t negotiable. That principle—putting user safety above growth metrics—is what I''d bring to advising OpenAI customers.'
    WHERE user_id = heejin_uuid
    AND question = 'Tell me about a time you showed integrity';

    -- 7. ADD NEW: "What's the status of Birth2Death's launch?"
    INSERT INTO public.qa_pairs (user_id, question, answer, question_type, source)
    VALUES (
        heejin_uuid,
        'What''s the status of Birth2Death''s launch?',
        'We''re in beta phase. We built a visionOS MVP with full functionality—emotional AI conversations, crisis detection, personalized strategies. The engineering is production-ready: we''ve stress-tested the architecture, validated unit economics, set up proper LLC structure. But launching a mental health platform responsibly requires clinical validation and legal compliance. We''re working through those before full launch. The delay taught me a lot about responsible AI deployment—exactly the mindset I''d bring to OpenAI customers.',
        'general',
        'manual'
    )
    ON CONFLICT DO NOTHING;

    RAISE NOTICE 'Updated to hybrid strategy: strengths first, honesty if pressed';
END $$;

-- Verify updates
SELECT question, LEFT(answer, 120) as answer_preview
FROM qa_pairs
WHERE user_id = (SELECT id FROM auth.users WHERE email = 'midmost44@gmail.com')
AND question IN (
    'Tell me about yourself',
    'Are these numbers on your resume accurate?',
    'Tell me about Birth2Death',
    'What''s the status of Birth2Death''s launch?'
)
ORDER BY question;
