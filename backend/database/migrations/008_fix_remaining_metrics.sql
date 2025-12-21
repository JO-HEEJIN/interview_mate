-- Fix remaining inflated metrics in Q&A pairs
-- Remove false satisfaction scores, retention claims, and user counts

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

    -- 1. Fix cross-functional communication (REMOVE 4.2/5 SCORE)
    UPDATE public.qa_pairs
    SET answer = 'At Birth2Death, I had to work closely with our product team when our LLM costs hit $0.45 per user—completely unsustainable. The product team was worried any cost reduction would hurt our mental health app''s quality, while engineering needed immediate action. I created a detailed analysis showing we could route 80% of routine conversations to GPT-3.5 while keeping GPT-4 for complex emotional support. I presented clear trade-offs and suggested A/B testing to validate the approach. The architecture worked—we achieved 80% cost reduction while maintaining response quality. Both teams got what they needed.'
    WHERE user_id = heejin_uuid
    AND question = 'Can you share an example of how you have successfully navigated cross-functional communication in the past?';

    -- 2. Fix user feedback example (REMOVE SATISFACTION SCORE AND RETENTION CLAIMS)
    UPDATE public.qa_pairs
    SET answer = 'At Birth2Death, early testers were saying our AI responses felt generic and weren''t helpful for mental health conversations. I analyzed the feedback and found people wanted more empathetic, personalized responses. I implemented intelligent model routing—using GPT-4 for complex emotional conversations and GPT-3.5 for routine ones. We also optimized prompts to be more contextually aware. The result was better response quality while actually cutting costs by 80%. The architecture proved that you can optimize for both quality and cost.'
    WHERE user_id = heejin_uuid
    AND question = 'Could you share an example of a time when you took feedback from users or customers and then turned that feedback into an actionable improvement?';

    -- 3. Fix "What is unique" answer (REMOVE 1000+ USERS AND 99.9% UPTIME)
    UPDATE public.qa_pairs
    SET answer = 'I''m not just an advisor—I''m a founder who has built production AI systems on your platform. I''ve designed architectures that reduce LLM costs by 80%, optimized RAG pipelines for sub-second latency, and architected systems for high availability. I can prototype alongside customers, not just advise, because I''ve solved these exact problems. Plus, I bring deep Korean market knowledge—I know what Korean founders need because I am one.'
    WHERE user_id = heejin_uuid
    AND question = 'What is something unique you bring to this role?';

    RAISE NOTICE 'Fixed 3 Q&A pairs with inflated metrics';
END $$;

-- Verify updates
SELECT question, LEFT(answer, 120) as answer_preview
FROM qa_pairs
WHERE user_id = (SELECT id FROM auth.users WHERE email = 'midmost44@gmail.com')
AND question IN (
    'Can you share an example of how you have successfully navigated cross-functional communication in the past?',
    'Could you share an example of a time when you took feedback from users or customers and then turned that feedback into an actionable improvement?',
    'What is something unique you bring to this role?'
)
ORDER BY question;
