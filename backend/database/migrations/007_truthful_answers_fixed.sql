-- Update key answers to be truthful while maintaining strength
-- This addresses the Birth2Death launch status issue

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

    -- 1. Tell me about yourself (TRUTHFUL VERSION)
    UPDATE public.qa_pairs
    SET answer = 'I''m Heejin Jo, and I''ve been building AI systems for vulnerable user populations. Most recently, I built Birth2Death, a mental health AI platform—currently in late-stage MVP on visionOS. I want to be upfront: my resume cited user projections, but we haven''t launched to production yet. The system is production-ready with sub-second latency and all the core features, but I''m still in the testing phase. That hands-on experience building a real production system is what I''d bring to this role.'
    WHERE user_id = heejin_uuid AND question = 'Tell me about yourself';

    -- 2. Tell me about Birth2Death (TRUTHFUL VERSION)
    UPDATE public.qa_pairs
    SET answer = 'It''s a mental health AI platform I''ve been building—currently a visionOS MVP that''s production-ready but not yet launched. Built entirely on OpenAI''s API—GPT-4 for complex conversations, optimized routing system. I''ve solved the production engineering challenges: designed an 80% cost reduction architecture through smart routing, built caching for sub-second latency, architected for 99.9% uptime. These are proven architectures I''ve implemented, not measured against live users yet, but I know they work because I''ve stress-tested them. This systems thinking is what I''d bring to help your customers.'
    WHERE user_id = heejin_uuid AND question = 'Tell me about Birth2Death';

    -- 3. Complex technical challenge (FOCUS ON ARCHITECTURE, NOT USER METRICS)
    UPDATE public.qa_pairs
    SET answer = 'At Birth2Death, I needed to architect a system that could handle emotional AI conversations cost-effectively. I designed a routing system—GPT-4 for complex emotional analysis, maybe 20% of conversations, and GPT-3.5 for routine interactions. Added prompt optimization and caching layers. The architecture reduced projected costs from 45 cents to 9 cents per conversation. I haven''t validated this at scale yet, but the engineering is sound and the unit economics work.'
    WHERE user_id = heejin_uuid AND question = 'Tell me about a complex technical challenge you solved';

    -- 4. Why leave startup (HONEST VERSION)
    UPDATE public.qa_pairs
    SET answer = 'Honestly, I''ve realized I want to scale my impact beyond a single product. Birth2Death taught me how to build production AI systems, but it''s still pre-launch. As an SA at OpenAI, I can help dozens of startups avoid the mistakes I made and ship faster. I speak founder language because I am one—when they say "we''re burning too much on API calls," I know exactly what that panic feels like and how to solve it.'
    WHERE user_id = heejin_uuid AND question = 'Why are you leaving your startup?';

    -- 5. Why not continue as founder (HONEST VERSION)
    UPDATE public.qa_pairs
    SET answer = 'I love building, but I''ve learned that launching a mental health platform solo is really hard—clinically, legally, operationally. I''ve built something production-ready, but getting it to market safely takes resources I don''t have. Meanwhile, the systems knowledge I''ve gained—cost optimization, latency engineering, safety architecture—that''s immediately valuable to OpenAI''s customers right now. I can help more people sooner this way.'
    WHERE user_id = heejin_uuid AND question = 'Why not continue as a founder?';

    -- 6. Check if "How do you handle mistakes?" exists, if not insert, otherwise update
    IF EXISTS (SELECT 1 FROM public.qa_pairs WHERE user_id = heejin_uuid AND question = 'How do you handle mistakes?') THEN
        UPDATE public.qa_pairs
        SET answer = 'I own them immediately. Actually, there''s something I need to clarify about my resume—I cited user projections for Birth2Death, but we haven''t launched yet. That was poor judgment on my part. The technical work is real and production-ready, but I should''ve been clearer about our launch status. I''m bringing this up because I believe integrity is non-negotiable, especially at a company like OpenAI where trust matters so much.'
        WHERE user_id = heejin_uuid AND question = 'How do you handle mistakes?';
    ELSE
        INSERT INTO public.qa_pairs (user_id, question, answer, question_type, source)
        VALUES (
            heejin_uuid,
            'How do you handle mistakes?',
            'I own them immediately. Actually, there''s something I need to clarify about my resume—I cited user projections for Birth2Death, but we haven''t launched yet. That was poor judgment on my part. The technical work is real and production-ready, but I should''ve been clearer about our launch status. I''m bringing this up because I believe integrity is non-negotiable, especially at a company like OpenAI where trust matters so much.',
            'behavioral',
            'manual'
        );
    END IF;

    -- 7. Check if "Tell me about a time you showed integrity" exists
    IF EXISTS (SELECT 1 FROM public.qa_pairs WHERE user_id = heejin_uuid AND question = 'Tell me about a time you showed integrity') THEN
        UPDATE public.qa_pairs
        SET answer = 'Actually, right now. When I submitted my resume, I cited projected user numbers for Birth2Death without clarifying they were projections, not actuals. That was wrong. The technical architecture and cost optimizations I describe are real, but the user metrics aren''t validated yet. I''m telling you this because if I''m going to advise OpenAI''s customers on production systems, I need to model the honesty I''d expect from them.'
        WHERE user_id = heejin_uuid AND question = 'Tell me about a time you showed integrity';
    ELSE
        INSERT INTO public.qa_pairs (user_id, question, answer, question_type, source)
        VALUES (
            heejin_uuid,
            'Tell me about a time you showed integrity',
            'Actually, right now. When I submitted my resume, I cited projected user numbers for Birth2Death without clarifying they were projections, not actuals. That was wrong. The technical architecture and cost optimizations I describe are real, but the user metrics aren''t validated yet. I''m telling you this because if I''m going to advise OpenAI''s customers on production systems, I need to model the honesty I''d expect from them.',
            'behavioral',
            'manual'
        );
    END IF;

    -- 8. Update any Imagine Cup references (CLARIFY STATUS)
    UPDATE public.qa_pairs
    SET answer = REPLACE(
        answer,
        'Microsoft Imagine Cup 2026 acceptance',
        'Microsoft Imagine Cup 2026 submission (accepted to competition)'
    )
    WHERE user_id = heejin_uuid
    AND answer LIKE '%Imagine Cup%';

    RAISE NOTICE 'Updated key answers to truthful versions';
END $$;

-- Verify updates
SELECT question, LEFT(answer, 100) as answer_preview
FROM qa_pairs
WHERE user_id = (SELECT id FROM auth.users WHERE email = 'midmost44@gmail.com')
AND question IN (
    'Tell me about yourself',
    'Tell me about Birth2Death',
    'How do you handle mistakes?',
    'Tell me about a time you showed integrity'
)
ORDER BY question;
