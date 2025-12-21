-- OpenAI Kenneth Interview Q&A Pairs - Part 2
-- Categories 4-6: Safety, Behavioral, Solutions Architect
-- Date: December 2025

DO $$
DECLARE
    heejin_uuid UUID;
BEGIN
    SELECT id INTO heejin_uuid
    FROM auth.users
    WHERE email = 'midmost44@gmail.com';

    IF heejin_uuid IS NULL THEN
        RAISE EXCEPTION 'User not found';
    END IF;

    -- ========================================
    -- CATEGORY 4: TECHNICAL - SAFETY / HEALTHBENCH
    -- ========================================

    INSERT INTO public.qa_pairs (user_id, question, answer, question_type) VALUES
    (heejin_uuid, 'You mentioned HealthBench. How specifically did it influence your design?',
    'HealthBench emphasizes three things: emergency referral accuracy, communication quality, and responding under uncertainty. I applied these directly. First, crisis detection is Layer 1 in the router - before cost optimization. Second, system prompts in app/services/openai_client.py are tailored for therapeutic conversation. Third, when the AI is uncertain, it says so rather than hallucinating. HealthBench taught me that in healthcare AI, a safe ''I don''t know'' is better than a confident wrong answer.');

    INSERT INTO public.qa_pairs (user_id, question, answer, question_type) VALUES
    (heejin_uuid, 'How do you handle confirmation bias in mental health AI?',
    'This is critical. If a user repeatedly journals about suicidal thoughts, the AI can''t just affirm and deepen that pattern. The THERAPEUTIC_SYSTEM_PROMPT in openai_client.py explicitly instructs the model to gently challenge catastrophic thinking and suggest professional help. The crisis detection layer catches these patterns and routes to the safety-focused GPT-4 prompt. The app would also have a visible ''Talk to a human'' button linking to crisis hotlines.');

    INSERT INTO public.qa_pairs (user_id, question, answer, question_type) VALUES
    (heejin_uuid, 'What if the AI generates harmful advice?',
    'Multi-layer defense. First, system prompt explicitly forbids medical advice, suicide methods, or anything that could cause harm. Second, crisis keywords trigger the CRISIS_SYSTEM_PROMPT which emphasizes professional help resources. Third, in production I''d implement output filtering - responses checked for crisis language with warning overlays. Fourth, I''d log all GPT-4 crisis conversations for manual review. Defense in depth - multiple chances to catch and correct.');

    INSERT INTO public.qa_pairs (user_id, question, answer, question_type) VALUES
    (heejin_uuid, 'How do you balance empathy with not replacing professional therapy?',
    'The THERAPEUTIC_SYSTEM_PROMPT sets clear boundaries: ''I''m a journaling companion, not a therapist. I can listen and reflect, but I can''t diagnose or treat mental health conditions.'' When users ask for clinical advice, the response guides them to licensed professionals. It''s empathetic but boundaried.');

    INSERT INTO public.qa_pairs (user_id, question, answer, question_type) VALUES
    (heejin_uuid, 'What''s your false positive rate for crisis detection?',
    'In testing, about 3% false positive rate - phrases like ''I''m dying to see that movie'' triggering crisis mode. I handle this by showing a gentle check-in rather than alarming the user. The router prioritizes safety over convenience - I''d rather have 3% false positives than miss a real crisis. The CRISIS_KEYWORDS list is deliberately conservative.');

    INSERT INTO public.qa_pairs (user_id, question, answer, question_type) VALUES
    (heejin_uuid, 'How would you implement HealthBench-style evaluation in production?',
    'I''d sample 100 random conversations per week and evaluate them on HealthBench criteria - accurate information, appropriate communication, proper emergency handling. Use GPT-4 as the grader initially, then have human clinicians review a subset to validate. Over time, this builds a quality dataset and catches model drift.');

    -- ========================================
    -- CATEGORY 5: BEHAVIORAL
    -- ========================================

    INSERT INTO public.qa_pairs (user_id, question, answer, question_type) VALUES
    (heejin_uuid, 'Tell me about a time you failed.',
    'This resume situation is the most recent. I failed to communicate accurately the stage of my project. But I learned that in high-stakes environments like OpenAI, precision matters more than impressiveness. I''d rather under-promise and over-deliver. The failure taught me to separate ''what I built'' from ''what I validated'' - and to be crystal clear about the distinction.');

    INSERT INTO public.qa_pairs (user_id, question, answer, question_type) VALUES
    (heejin_uuid, 'Why do you want to work at OpenAI specifically?',
    'Two reasons. First, mission alignment - I''ve been building AI for mental health, which is exactly the kind of ''AI for humanity'' OpenAI prioritizes. I''ve read your HealthBench research, I follow your safety work, and I believe AI should benefit vulnerable populations. Second, Solutions Architect is the perfect intersection of my background - I''m technical enough to debug customer code, but I''ve been a founder so I understand business constraints. I want to help Korean startups succeed with OpenAI, and I can bridge that gap.');

    INSERT INTO public.qa_pairs (user_id, question, answer, question_type) VALUES
    (heejin_uuid, 'What''s your biggest weakness?',
    'I move fast, sometimes too fast. As a co-founder of a startup, I optimized for shipping quickly, which meant I didn''t always document decisions thoroughly or get external review before launch. This resume situation is an example - I should have had someone else review it. At OpenAI, I''d balance that speed with the rigor you need for customer-facing roles - double-checking technical guidance, documenting recommendations, and getting peer review.');

    INSERT INTO public.qa_pairs (user_id, question, answer, question_type) VALUES
    (heejin_uuid, 'How do you handle disagreement with a customer?',
    'I''d first make sure I understand their perspective - ask clarifying questions, restate their position to confirm. Then I''d present my technical recommendation with data - ''Here''s why I think approach A is better than B, based on X, Y, Z.'' But ultimately, it''s their product. If they disagree after hearing the technical tradeoffs, I''d support their decision and help them execute it well. My job is to give them the information to make good choices, not to force my opinion.');

    INSERT INTO public.qa_pairs (user_id, question, answer, question_type) VALUES
    (heejin_uuid, 'Describe a time you had to learn something completely new quickly.',
    'iOS development with Swift for Birth2Death. I had React Native experience, but native iOS was completely new. I had limited time before wanting to launch. I read Apple''s docs, built prototype apps, joined developer forums, and shipped a working mental health journaling app. It wasn''t perfect, but it worked. That ability to ramp up quickly on new tech is critical for Solutions Architect - your customers will be using cutting-edge AI in ways no one''s done before.');

    INSERT INTO public.qa_pairs (user_id, question, answer, question_type) VALUES
    (heejin_uuid, 'How do you prioritize when everything is urgent?',
    'I use impact vs effort matrix. High impact, low effort goes first. But for startups, there''s a third dimension: risk. If something could kill the business if wrong (like safety in mental health AI), it gets priority regardless of effort. When I built Birth2Death, I spent 40% of dev time on safety features that users wouldn''t directly see - because the risk of getting it wrong was too high.');

    INSERT INTO public.qa_pairs (user_id, question, answer, question_type) VALUES
    (heejin_uuid, 'What would you do if a customer asked you to help them build something unethical?',
    'I''d first clarify what they''re trying to achieve and why. Sometimes what sounds unethical is a misunderstanding. If it''s genuinely unethical - like using AI to manipulate users or violate privacy - I''d explain why it violates OpenAI''s usage policies and suggest ethical alternatives. If they insist, I''d escalate to my manager and refuse to help. I won''t compromise on ethics for a customer win.');

    -- ========================================
    -- CATEGORY 6: SOLUTIONS ARCHITECT ROLE
    -- ========================================

    INSERT INTO public.qa_pairs (user_id, question, answer, question_type) VALUES
    (heejin_uuid, 'What does a Solutions Architect do, in your understanding?',
    'A Solutions Architect is a technical advisor who helps customers succeed with OpenAI''s platform. That means: understanding their business problem, designing an architecture that solves it, helping them implement it, troubleshooting when things break, and feeding product feedback back to OpenAI. You''re part consultant, part engineer, part customer advocate. You need to speak both founder language and engineer language fluently.');

    INSERT INTO public.qa_pairs (user_id, question, answer, question_type) VALUES
    (heejin_uuid, 'How would you help a Korean startup that''s never used LLMs before?',
    'I''d start with their business problem, not the technology. What are they trying to achieve? Then I''d show them a simple proof of concept - 20 lines of Python calling the OpenAI API - so they see immediate value. Once they''re excited, I''d help them architect properly: prompt engineering best practices, error handling, cost management, evaluation metrics. I''d also connect them with other Korean startups doing similar things - community building is huge in Korea''s ecosystem.');

    INSERT INTO public.qa_pairs (user_id, question, answer, question_type) VALUES
    (heejin_uuid, 'A customer says GPT-4 is too slow. What do you recommend?',
    'First, I''d measure - what''s their actual P95 latency and what''s their target? If it''s truly too slow, I''d recommend: (1) Streaming responses so users see output immediately, (2) Model routing - use GPT-3.5 for simple queries like I did in Birth2Death, (3) Prompt compression to reduce tokens, (4) Caching for repeated queries. I''d also ask if they need GPT-4 for everything - often 80% of queries can use a faster model. Birth2Death is a case study for exactly this problem.');

    INSERT INTO public.qa_pairs (user_id, question, answer, question_type) VALUES
    (heejin_uuid, 'A customer''s costs are too high. How do you help?',
    'I''d audit their usage - are they using GPT-4 when GPT-3.5 would work? Are they re-sending the same context window repeatedly? Are they using inefficient prompts? Then I''d show them concrete tactics: model routing like I implemented in Birth2Death, semantic caching, prompt optimization, fine-tuning for common queries. I''d build them a cost tracking dashboard so they can see exactly where money is going. My Birth2Death cost optimization architecture reducing costs by 80% is exactly the reference I''d share.');

    INSERT INTO public.qa_pairs (user_id, question, answer, question_type) VALUES
    (heejin_uuid, 'How would you handle a customer who''s frustrated with OpenAI''s rate limits?',
    'Empathy first - rate limits are frustrating when you''re trying to ship. Then solutions: (1) Request a rate limit increase if they have a good use case, (2) Implement request queuing and retry logic to handle limits gracefully, (3) Use batching to reduce request count, (4) Consider upgrading to a higher tier. I''d also help them architect around limits - for example, caching aggressively to reduce total requests.');

    INSERT INTO public.qa_pairs (user_id, question, answer, question_type) VALUES
    (heejin_uuid, 'What would you do if you don''t know the answer to a customer''s technical question?',
    'I''d be honest - ''I don''t know off the top of my head, but let me find out.'' Then I''d consult OpenAI''s internal docs, ask the engineering team, or escalate to product specialists. The key is not pretending to know when you don''t. Customers trust advisors who say ''I don''t know, but I''ll get you the answer'' more than those who bullshit.');

    INSERT INTO public.qa_pairs (user_id, question, answer, question_type) VALUES
    (heejin_uuid, 'How would you measure your success as a Solutions Architect?',
    'Three metrics. First, customer success - are my customers building working products and scaling? Second, NPS - would they recommend me to other founders? Third, product feedback quality - am I surfacing valuable insights to OpenAI''s product team? It''s not about how many calls I take, it''s about whether the customers I work with succeed and whether I help OpenAI build better products.');

    RAISE NOTICE 'Inserted 19 Q&A pairs - Categories 4-6';
END $$;
