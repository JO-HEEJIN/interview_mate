-- CLEANUP: Remove AI-generation narrative Q&As
-- Remove questions that mention "AI wrote resume"
-- Update remaining Q&As to align with final consensus strategy

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

    -- DELETE: Questions about AI writing resume (Final consensus: NEVER mention this)
    DELETE FROM public.qa_pairs
    WHERE user_id = heejin_uuid
    AND question IN (
        'Why didn''t you review your resume before submitting?',
        'How do we know you won''t make careless mistakes with customers?',
        'Do you use AI for other work tasks?',
        'What did you learn from the resume mistake?',
        'Isn''t using AI for your resume cheating?',
        'Why OpenAI specifically after this experience?',
        'Aren''t you embarrassed to proceed with this interview?',
        'How would you help customers avoid the mistake you made?'
    );

    -- UPDATE: "How do you handle mistakes?" - Generic lesson, no resume mention
    UPDATE public.qa_pairs
    SET answer = 'I own them immediately and learn from them systematically. In my startup journey, I learned that moving fast without proper verification can create real risks, especially in production systems. That taught me to always build verification layers—not just "trust but verify," but "verify then trust." That''s why I''m interested in OpenAI''s work on process supervision and safety guardrails. I help customers build verification workflows from the start, because I understand the consequences of getting it wrong.'
    WHERE user_id = heejin_uuid
    AND question = 'How do you handle mistakes?';

    -- UPDATE: "Tell me about a time you showed integrity" - Different example
    UPDATE public.qa_pairs
    SET answer = 'When building Birth2Death, I had to choose between shipping faster with potential safety shortcuts or taking more time to build proper guardrails for vulnerable users. I chose safety, even though it meant delaying launch. For a mental health platform, integrity around user safety isn''t negotiable. That principle—putting user wellbeing above growth metrics—is what I''d bring to advising OpenAI customers.'
    WHERE user_id = heejin_uuid
    AND question = 'Tell me about a time you showed integrity';

    -- UPDATE: "Tell me about Birth2Death" - Accurate, no inflated claims
    UPDATE public.qa_pairs
    SET answer = 'It''s a mental health AI platform I''ve been building with a co-founder. We built a visionOS MVP and are planning iOS launch. Built entirely on OpenAI''s API—GPT-4 for complex conversations, model routing for cost efficiency. I''ve designed the production architecture: 80% cost reduction through smart routing, caching for sub-second latency, high-availability design. The platform is fully engineered but hasn''t launched publicly yet. We''re in beta, focusing on getting the safety and clinical aspects right before scaling. The systems engineering I''ve done is exactly what I''d help your customers with.'
    WHERE user_id = heejin_uuid
    AND question = 'Tell me about Birth2Death';

    -- UPDATE: "Why are you leaving your startup?" - Simple and honest
    UPDATE public.qa_pairs
    SET answer = 'I want to scale my impact beyond a single product. Birth2Death taught me how to build production AI systems, but it''s still pre-launch. As an SA at OpenAI, I can help dozens of startups avoid the challenges I faced and ship faster. I speak founder language because I am one—when they say "we''re burning too much on API calls," I''ve felt that pressure and know how to solve it. I can multiply my impact by helping multiple companies succeed.'
    WHERE user_id = heejin_uuid
    AND question = 'Why are you leaving your startup?';

    -- UPDATE: "Why not continue as a founder?" - Honest about challenges
    UPDATE public.qa_pairs
    SET answer = 'Launching a mental health platform is really hard—clinically, legally, operationally. Even with a co-founder, getting it to market safely takes resources we don''t have. Meanwhile, the systems knowledge I''ve gained—cost optimization, latency engineering, safety architecture—that''s immediately valuable to OpenAI''s customers right now. I can help more people sooner by sharing what I''ve learned across multiple companies.'
    WHERE user_id = heejin_uuid
    AND question = 'Why not continue as a founder?';

    -- UPDATE: "What's the status of Birth2Death's launch?" - Crystal clear
    UPDATE public.qa_pairs
    SET answer = 'We''re in pre-launch phase. The platform is fully engineered—visionOS MVP complete, all core features built—but we haven''t launched publicly yet. We''re working through clinical validation and legal compliance before going live. The engineering is production-ready, but launching responsibly with vulnerable users takes time. That experience of building for scale before launch is what I''d bring to advising customers.'
    WHERE user_id = heejin_uuid
    AND question = 'What''s the status of Birth2Death''s launch?';

    -- UPDATE: "So the 1,000 users claim is false?" - Honest, brief, pivot
    UPDATE public.qa_pairs
    SET answer = 'Those numbers were internal targets for our launch capacity, not current users. The platform is fully engineered but hasn''t launched publicly yet. What I can demonstrate is that I''ve solved the exact production engineering challenges your startup customers face—cost optimization, latency, scalability. The architecture is real, documented, and ready to show. I wanted to clarify this rather than have it discovered later.'
    WHERE user_id = heejin_uuid
    AND question = 'So the 1,000 users claim is false?';

    -- UPDATE: "Are these numbers on your resume accurate?" - Already good from 013, just verify
    -- (This should already be updated from migration 013, but ensuring consistency)

    RAISE NOTICE 'Cleanup complete: Removed AI narrative Q&As, updated remaining to final consensus';
END $$;

-- Verify: Show all questions that remain
SELECT
    question,
    LEFT(answer, 100) as answer_preview,
    question_type,
    source
FROM qa_pairs
WHERE user_id = (SELECT id FROM auth.users WHERE email = 'midmost44@gmail.com')
AND (
    answer LIKE '%AI%' OR
    answer LIKE '%resume%' OR
    question LIKE '%mistake%' OR
    question LIKE '%integrity%' OR
    question = 'Tell me about Birth2Death' OR
    question = 'Why are you leaving your startup?'
)
ORDER BY question;
