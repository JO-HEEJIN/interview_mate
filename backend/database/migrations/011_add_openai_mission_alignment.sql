-- Add Q&A pairs emphasizing OpenAI mission alignment and hallucination research
-- This completes the narrative arc: mistake → research → mission alignment

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

    -- 1. Update "Why didn't you review resume?" with OpenAI mission alignment
    UPDATE public.qa_pairs
    SET answer = 'Honestly? I was excited and moved too fast. I trusted the AI output because the technical facts it was based on were all real. That was naive. I learned that AI can optimize in ways that cross ethical lines, and verification is non-negotiable. But here''s what that experience taught me: I''m proceeding with this interview despite the embarrassment because this confirmed why I want to work at OpenAI specifically. The more I researched OpenAI''s work on hallucination and accuracy—your process supervision research, the model spec work, your preparedness framework—the more I realized you''re the only company taking this seriously at a fundamental level. I experienced this problem firsthand, saw how dangerous it can be, and found that OpenAI is leading the work to solve it. That''s the mission I want to be part of—helping customers use AI responsibly because I''ve lived the consequences of not doing so.'
    WHERE user_id = heejin_uuid
    AND question = 'Why didn''t you review your resume before submitting?';

    -- 2. Add new: "Why OpenAI specifically after this experience?"
    INSERT INTO public.qa_pairs (user_id, question, answer, question_type, source)
    VALUES (
        heejin_uuid,
        'Why OpenAI specifically after this experience?',
        'The resume experience made me research how companies are addressing AI accuracy and hallucination. I found OpenAI''s process supervision research, your model spec framework, and your preparedness approach. You''re not just building powerful models—you''re building responsible ones. I experienced firsthand how AI can optimize in dangerous ways, and I saw that OpenAI is leading the work to prevent that. I want to help customers avoid the mistake I made, and OpenAI gives me the best tools and mission to do that.',
        'behavioral',
        'manual'
    )
    ON CONFLICT DO NOTHING;

    -- 3. Add new: "What do you know about OpenAI's work on reducing hallucinations?"
    INSERT INTO public.qa_pairs (user_id, question, answer, question_type, source)
    VALUES (
        heejin_uuid,
        'What do you know about OpenAI''s work on reducing hallucinations?',
        'I''ve studied your process supervision research—rewarding reasoning process instead of just outcomes. Your model spec work defines behavioral guidelines for responsible AI. The preparedness framework evaluates safety systematically. What impressed me most is that you''re addressing this at the architecture level, not just with post-hoc filters. I experienced AI hallucination firsthand with my resume, so I understand why this work matters. As an SA, I''d help customers implement these principles—proper prompting, verification workflows, human-in-the-loop systems.',
        'technical',
        'manual'
    )
    ON CONFLICT DO NOTHING;

    -- 4. Add new: "Aren't you embarrassed to proceed with this interview?"
    INSERT INTO public.qa_pairs (user_id, question, answer, question_type, source)
    VALUES (
        heejin_uuid,
        'Aren''t you embarrassed to proceed with this interview?',
        'Yes, I am. But that embarrassment confirmed something important: this is exactly why I need to work at OpenAI. I made a mistake that demonstrates the exact problem OpenAI is working to solve—AI outputs that look credible but aren''t verified. If I walked away, I''d miss the chance to help prevent others from making similar mistakes. The embarrassment is the price of integrity, and it''s worth paying if it means I can help OpenAI''s customers use AI responsibly.',
        'behavioral',
        'manual'
    )
    ON CONFLICT DO NOTHING;

    -- 5. Add new: "What specific OpenAI research influenced you?"
    INSERT INTO public.qa_pairs (user_id, question, answer, question_type, source)
    VALUES (
        heejin_uuid,
        'What specific OpenAI research influenced you?',
        'Three things stood out. One: your process supervision research showing that rewarding reasoning process reduces hallucination better than outcome-based rewards. Two: the model spec framework—I love that you''re defining responsible AI behavior at a fundamental level. Three: your preparedness framework for evaluating model capabilities and risks. These aren''t just papers—they''re a philosophy of responsible AI development. That''s the approach I want to help customers implement.',
        'technical',
        'manual'
    )
    ON CONFLICT DO NOTHING;

    -- 6. Add new: "Why not Anthropic or Google if you care about AI safety?"
    INSERT INTO public.qa_pairs (user_id, question, answer, question_type, source)
    VALUES (
        heejin_uuid,
        'Why not Anthropic or Google if you care about AI safety?',
        'All these companies do important safety work, but OpenAI''s approach resonated most with me. Your process supervision research, model spec framework, and preparedness approach show you''re addressing safety at the architecture level, not just as an add-on. Plus, OpenAI''s API-first model means millions of developers depend on your safety work—the impact is massive. I experienced an AI accuracy problem firsthand, researched who''s leading the solution, and found OpenAI. The mission, the approach, and the scale all align.',
        'general',
        'manual'
    )
    ON CONFLICT DO NOTHING;

    -- 7. Update "Why OpenAI specifically?" to include hallucination experience
    UPDATE public.qa_pairs
    SET answer = 'Honestly, it''s about mission alignment. I''ve spent years building AI for vulnerable users—mental health, healthcare—where you can''t mess around with safety. OpenAI is one of the few companies that actually takes this seriously, not just in marketing but in how you build and deploy systems. I experienced AI hallucination firsthand with my resume—it optimized in ways I didn''t expect. That made me research who''s solving this problem, and I found OpenAI''s process supervision research, model spec work, preparedness framework. You''re leading this. Plus, I''m already your customer—I know the platform inside out. That matters to me.'
    WHERE user_id = heejin_uuid
    AND question = 'Why OpenAI specifically?';

    -- 8. Add new: "How would you help customers avoid the mistake you made?"
    INSERT INTO public.qa_pairs (user_id, question, answer, question_type, source)
    VALUES (
        heejin_uuid,
        'How would you help customers avoid the mistake you made?',
        'I''d teach them what I learned the hard way: AI verification workflows. First, treat every AI output as a first draft. Second, implement human-in-the-loop for high-stakes content. Third, use structured outputs where possible—less hallucination risk. Fourth, build verification into your process, not as an afterthought. I can speak to this from experience, not theory. When a customer says "the AI gave me this output," I''ll know to ask "but did you verify it?" because I didn''t, and I learned why that matters.',
        'technical',
        'manual'
    )
    ON CONFLICT DO NOTHING;

    RAISE NOTICE 'Added 7 Q&A pairs with OpenAI mission alignment narrative';
END $$;

-- Verify new questions
SELECT question, LEFT(answer, 120) as answer_preview
FROM qa_pairs
WHERE user_id = (SELECT id FROM auth.users WHERE email = 'midmost44@gmail.com')
AND (
    question LIKE '%OpenAI%research%' OR
    question LIKE '%embarrassed%' OR
    question LIKE '%hallucination%' OR
    question LIKE '%Anthropic%' OR
    question LIKE '%customers avoid%'
)
ORDER BY question;
