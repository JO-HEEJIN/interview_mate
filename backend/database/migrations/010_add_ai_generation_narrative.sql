-- Add Q&A pairs with the AI-generation narrative
-- This provides the true context for the resume metrics issue

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

    -- 1. Update "Tell me about yourself" with AI-generation context
    UPDATE public.qa_pairs
    SET answer = 'I''m Heejin Jo, and I''ve been building AI systems for startups, with a focus on vulnerable user populations like mental health and agriculture. The project I''ve invested most deeply in is Birth2Death, a mental health AI platform. Built a visionOS MVP with a co-founder, now planning iOS launch. Before we go further, I need to clarify something about my resume. I used AI to help write my resume and cover letter based on my real technical work, and it optimized the metrics—projecting capacity as if they were actual user numbers. I submitted without carefully reviewing, and realized too late that it had inflated claims. That was my mistake. I should have verified every line. The technical architecture is real, but the user metrics aren''t. I''m bringing this up because, one, integrity matters, especially at OpenAI, and two, this taught me a critical lesson about AI outputs that I''d bring to this role: always verify, never blindly trust.'
    WHERE user_id = heejin_uuid
    AND question = 'Tell me about yourself';

    -- 2. Update "How do you handle mistakes?" with AI context
    UPDATE public.qa_pairs
    SET answer = 'I own them immediately. Actually, there''s something I need to clarify about my resume. I used AI to help write it based on my real technical work, and it optimized the metrics—turning capacity projections into what looked like actual user numbers. I submitted without thoroughly reviewing. That was my mistake. The technical work is real and production-ready, but the user metrics aren''t. I''m bringing this up because I believe integrity is non-negotiable, especially at a company like OpenAI where trust matters so much. This taught me a critical lesson about AI verification that I''d bring to this role.'
    WHERE user_id = heejin_uuid
    AND question = 'How do you handle mistakes?';

    -- 3. Update "Tell me about a time you showed integrity"
    UPDATE public.qa_pairs
    SET answer = 'Actually, right now. When I used AI to help write my resume, it optimized the metrics—projecting user capacity as if they were actual numbers. I submitted without carefully verifying, and realized too late. That was wrong. The technical architecture and cost optimizations I describe are real, but the user metrics aren''t validated yet. I''m telling you this because if I''m going to advise OpenAI''s customers on production systems, I need to model the honesty I''d expect from them. This experience taught me that AI outputs always need human verification—a lesson I''d bring to helping your customers.'
    WHERE user_id = heejin_uuid
    AND question = 'Tell me about a time you showed integrity';

    -- 4. Add new: "Why didn't you review your resume before submitting?"
    INSERT INTO public.qa_pairs (user_id, question, answer, question_type, source)
    VALUES (
        heejin_uuid,
        'Why didn''t you review your resume before submitting?',
        'Honestly? I was excited and moved too fast. I trusted the AI output because the technical facts it was based on were all real. That was naive. I learned that AI can optimize in ways that cross ethical lines, and verification is non-negotiable. It''s actually a lesson I''d bring to this role—helping customers understand that AI outputs need human oversight.',
        'behavioral',
        'manual'
    )
    ON CONFLICT DO NOTHING;

    -- 5. Add new: "How do we know you won't make careless mistakes with customers?"
    INSERT INTO public.qa_pairs (user_id, question, answer, question_type, source)
    VALUES (
        heejin_uuid,
        'How do we know you won''t make careless mistakes with customers?',
        'Fair question. This was a wake-up call. I''ve since implemented a personal rule: verify every AI output, every claim, every metric. Ironically, this mistake taught me exactly what OpenAI customers need to learn—how to use AI responsibly. I can speak to that from lived experience now.',
        'behavioral',
        'manual'
    )
    ON CONFLICT DO NOTHING;

    -- 6. Add new: "Do you use AI for other work tasks?"
    INSERT INTO public.qa_pairs (user_id, question, answer, question_type, source)
    VALUES (
        heejin_uuid,
        'Do you use AI for other work tasks?',
        'Yes, extensively. I use AI for writing, research, prototyping, and problem-solving. But the resume experience taught me a critical lesson: AI is a tool, not a replacement for judgment. I now treat every AI output as a first draft that requires careful verification. That''s exactly the mindset I''d help OpenAI customers develop—how to leverage AI productively while maintaining quality and accuracy.',
        'behavioral',
        'manual'
    )
    ON CONFLICT DO NOTHING;

    -- 7. Add new: "What did you learn from the resume mistake?"
    INSERT INTO public.qa_pairs (user_id, question, answer, question_type, source)
    VALUES (
        heejin_uuid,
        'What did you learn from the resume mistake?',
        'Three things. One: AI can optimize in ways that cross ethical lines without you realizing it. Two: excitement and speed can''t override the need for verification. Three: this is exactly the challenge OpenAI customers face—how to use powerful AI tools responsibly. I can now advise them from lived experience, not just theory. The lesson was painful but valuable.',
        'behavioral',
        'manual'
    )
    ON CONFLICT DO NOTHING;

    -- 8. Add new: "Isn't using AI for your resume cheating?"
    INSERT INTO public.qa_pairs (user_id, question, answer, question_type, source)
    VALUES (
        heejin_uuid,
        'Isn''t using AI for your resume cheating?',
        'I used AI as a writing tool, based on my real experience. The problem wasn''t using AI—it was not reviewing its output carefully. That''s the exact challenge your customers face: how to use AI productively while maintaining quality and accuracy. I understand both the promise and the pitfalls firsthand now. The technical work I described is all real; the mistake was trusting AI to represent it accurately without verification.',
        'behavioral',
        'manual'
    )
    ON CONFLICT DO NOTHING;

    -- 9. Update "Why are you leaving your startup?" to mention LLC
    UPDATE public.qa_pairs
    SET answer = 'Honestly, I want to scale my impact beyond a single product. Birth2Death taught me how to build production AI systems, but it''s still pre-launch. I even set up a Wyoming LLC for it, but launching a mental health platform is really hard—clinically, legally, operationally. As an SA at OpenAI, I can help dozens of startups avoid the mistakes I made and ship faster. I speak founder language because I am one—when they say "we''re burning too much on API calls," I know exactly what that panic feels like.'
    WHERE user_id = heejin_uuid
    AND question = 'Why are you leaving your startup?';

    -- 10. Add new: "Tell me about your startup's legal structure"
    INSERT INTO public.qa_pairs (user_id, question, answer, question_type, source)
    VALUES (
        heejin_uuid,
        'Tell me about your startup''s legal structure',
        'We set up a Wyoming LLC for Birth2Death. It''s a real company, properly structured. The challenge has been that launching a mental health platform requires not just technical readiness but clinical validation and legal compliance. We''ve built the technology, but scaling it responsibly takes resources we don''t have as a bootstrapped team. That''s one reason I''m excited about this role—helping other startups navigate these challenges.',
        'general',
        'manual'
    )
    ON CONFLICT DO NOTHING;

    RAISE NOTICE 'Added/updated 10 Q&A pairs with AI-generation narrative';
END $$;

-- Verify updates
SELECT question, LEFT(answer, 120) as answer_preview
FROM qa_pairs
WHERE user_id = (SELECT id FROM auth.users WHERE email = 'midmost44@gmail.com')
AND (
    question = 'Tell me about yourself' OR
    question LIKE '%review%resume%' OR
    question LIKE '%careless mistakes%' OR
    question LIKE '%AI%' OR
    question LIKE '%learned%'
)
ORDER BY question;
