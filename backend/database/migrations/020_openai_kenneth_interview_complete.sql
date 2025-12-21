-- OpenAI Kenneth Interview - Complete Q&A Set
-- 68 questions covering all interview scenarios
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

    -- Clean up old interview Q&A
    DELETE FROM public.qa_pairs
    WHERE user_id = heejin_uuid
    AND (
        question LIKE '%resume%'
        OR question LIKE '%OpenAI%'
        OR question LIKE '%Birth2Death%'
        OR question LIKE '%Solutions Architect%'
        OR question LIKE '%Korean%'
        OR question LIKE '%model routing%'
        OR question LIKE '%cost%'
        OR question LIKE '%HealthBench%'
    );

    -- CATEGORY 1: RESUME / HONESTY (5 questions - behavioral)

    INSERT INTO public.qa_pairs (user_id, question, answer, question_type) VALUES
    (heejin_uuid,
    'Why didn''t you put these as ''design targets'' on your resume from the start?',
    'That''s the mistake I made. As a co-founder building this with limited resources, I was so focused on the engineering - proving the system COULD handle 1,000 users at $0.09 per session - that I wrote it as if it was already happening. I should have labeled them as ''validated capacity'' or ''design goals.'' That''s on me, and I take full responsibility.',
    'behavioral');

    INSERT INTO public.qa_pairs (user_id, question, answer, question_type) VALUES
    (heejin_uuid,
    'How can we trust anything else on your resume?',
    'Fair question. Here''s what''s verifiable: The code is on GitHub at github.com/JO-HEEJIN/birth2death-backend. My education is documented. My competition wins (NASA Space Apps Local Award, AI Skin Burn Diagnosis) have public records. My work experience at SKIA, Lime Friends - those companies exist and I can provide references. What was wrong was framing design targets as production metrics. Everything else is accurate and I can provide documentation for any of it.',
    'behavioral');

    INSERT INTO public.qa_pairs (user_id, question, answer, question_type) VALUES
    (heejin_uuid,
    'Have you lied on applications before?',
    'No. This is the first time I''ve made this mistake, and it''s taught me a hard lesson. I''ve never fabricated education, work experience, or technical skills. This was a case of poor judgment in how I presented development-stage metrics, not a pattern of dishonesty.',
    'behavioral');

    INSERT INTO public.qa_pairs (user_id, question, answer, question_type) VALUES
    (heejin_uuid,
    'Why should OpenAI hire someone who inflated their resume?',
    'You shouldn''t hire me despite the resume mistake - you should consider me because I caught it myself, addressed it immediately, and showed you the real technical work. OpenAI values integrity. I demonstrated that by clarifying before you had to dig it out. The question is: do you value someone who makes a mistake but owns it immediately, or someone who never makes mistakes? The former is more realistic.',
    'behavioral');

    INSERT INTO public.qa_pairs (user_id, question, answer, question_type) VALUES
    (heejin_uuid,
    'What if this happens with a customer? Will you inflate their results too?',
    'The exact opposite. This experience taught me the importance of precision in metrics. As a Solutions Architect, I''d help customers set realistic benchmarks, track real data, and be honest about what''s proven versus projected. I''d rather under-promise and over-deliver than repeat this mistake.',
    'behavioral');

    -- CATEGORY 2: TECHNICAL - ARCHITECTURE (10 questions - technical)

    INSERT INTO public.qa_pairs (user_id, question, answer, question_type) VALUES
    (heejin_uuid,
    'Walk me through the model routing architecture step by step.',
    'Sure. When a user sends a message, it goes through three layers. First, semantic cache check - I generate an embedding with text-embedding-3-small and check Redis for cosine similarity above 0.92. If hit, return cached response, cost $0.00002, latency 50ms. If miss, Layer 2: crisis detection - keywords like ''suicide'' bypass everything and go straight to GPT-4 with safety prompt. Layer 3: complexity router - pattern matching determines simple versus complex. Simple queries like greetings, acknowledgments go to GPT-3.5. Complex therapeutic questions go to GPT-4. The distribution targets 80/20, validated through testing. The code is in app/services/router.py on GitHub.',
    'technical');

    INSERT INTO public.qa_pairs (user_id, question, answer, question_type) VALUES
    (heejin_uuid,
    'Why 0.92 similarity threshold specifically?',
    'I tested thresholds from 0.85 to 0.95. At 0.95, cache hit rate was only 10% - too strict. At 0.85, we got quality issues - responses felt generic. 0.92 was the sweet spot: 30% hit rate with no noticeable quality degradation in my test conversations. The threshold balances cache efficiency with response accuracy.',
    'technical');

    INSERT INTO public.qa_pairs (user_id, question, answer, question_type) VALUES
    (heejin_uuid,
    'What happens if Redis goes down?',
    'Graceful degradation. The cache check is wrapped in a try-except in app/core/redis_client.py. If Redis fails, we log the error and proceed directly to the model router. The system continues working, just without caching benefits. Latency increases from ~400ms to ~600ms, cost increases by about 30%, but no user-facing errors. I''d set up Redis monitoring and auto-failover in production.',
    'technical');

    INSERT INTO public.qa_pairs (user_id, question, answer, question_type) VALUES
    (heejin_uuid,
    'How do you handle context in conversations? Does the router see previous messages?',
    'Yes. The router receives the full conversation context - last 10 messages. This is important because ''tell me more'' in isolation looks simple, but if the previous message was about trauma, the router has context to route it to GPT-4. The complexity classification uses both the current message and recent conversation history.',
    'technical');

    INSERT INTO public.qa_pairs (user_id, question, answer, question_type) VALUES
    (heejin_uuid,
    'What''s your embedding dimensionality and why?',
    'I''m using text-embedding-3-small, which is 1536 dimensions. It''s fast, cheap ($0.00002 per request), and sufficient for semantic similarity in conversational queries. For mental health conversations, the semantic space isn''t that complex - we''re not doing multi-lingual retrieval or highly technical jargon. 1536 dims gives us good separation without the cost of larger embeddings.',
    'technical');

    INSERT INTO public.qa_pairs (user_id, question, answer, question_type) VALUES
    (heejin_uuid,
    'How do you prevent cache poisoning or bad responses being cached?',
    'Two mechanisms. First, responses are only cached after successful generation - no error states get cached. Second, cache has 24-hour TTL in the config, so any problematic responses don''t persist indefinitely. In production, I''d add a review layer where flagged responses could be manually purged from cache.',
    'technical');

    INSERT INTO public.qa_pairs (user_id, question, answer, question_type) VALUES
    (heejin_uuid,
    'Can you show me the actual code for the crisis detection?',
    'Absolutely. It''s in app/services/router.py lines 20-30. The CRISIS_KEYWORDS list includes ''suicide'', ''kill myself'', ''self-harm'', ''end my life'', etc. The _is_crisis method does pattern matching - not ML - because I need 100% reliability. Can''t afford false negatives. If any keyword matches, classify_complexity immediately routes to GPT-4 with a safety-tuned system prompt that emphasizes professional help resources.',
    'technical');

    INSERT INTO public.qa_pairs (user_id, question, answer, question_type) VALUES
    (heejin_uuid,
    'What if someone tries to game the system to get cheaper GPT-3.5 responses?',
    'In a public API, that''s a valid concern. I''d implement rate limiting per user and monitor for suspicious patterns. But for mental health journaling, the user has no incentive to game it - they want good answers. The cost optimization benefits me as the platform operator, not the user directly. The router prioritizes quality over cost for complex queries.',
    'technical');

    INSERT INTO public.qa_pairs (user_id, question, answer, question_type) VALUES
    (heejin_uuid,
    'How would this scale to 10,000 concurrent users?',
    'The architecture is stateless, so horizontal scaling is straightforward. I''d need: (1) Redis cluster instead of single instance for cache, (2) Load balancer in front of FastAPI instances, (3) Database connection pooling and read replicas, (4) CDN for static assets. The model router itself is pure logic - no bottlenecks. The constraint would be OpenAI API rate limits, which I''d handle with request queuing and retry logic.',
    'technical');

    INSERT INTO public.qa_pairs (user_id, question, answer, question_type) VALUES
    (heejin_uuid,
    'Why FastAPI over Flask or Django?',
    'Three reasons. One, async/await native support - critical for handling multiple concurrent OpenAI API calls without blocking. Two, automatic API documentation with OpenAPI spec - makes it easy for frontend devs. Three, performance - FastAPI is significantly faster than Flask for I/O-bound workloads like LLM API calls. Since this app is basically proxying requests to OpenAI, async I/O is essential.',
    'technical');

    -- CATEGORY 3: TECHNICAL - COST OPTIMIZATION (6 questions - technical)

    INSERT INTO public.qa_pairs (user_id, question, answer, question_type) VALUES
    (heejin_uuid,
    'How did you validate the 80% cost reduction?',
    'I built a test suite with 200 sample conversations covering different therapeutic scenarios - simple journaling, complex emotional processing, crisis situations. I ran each conversation through two configurations: baseline (all GPT-4) and optimized (with routing and caching). The baseline averaged $0.45 per 5-turn session. The optimized averaged $0.086. That''s 80.9% reduction. The detailed breakdown is in results/cost_breakdown.json in the GitHub repo.',
    'technical');

    INSERT INTO public.qa_pairs (user_id, question, answer, question_type) VALUES
    (heejin_uuid,
    'What''s the cost breakdown per request type?',
    'Cache hit: $0.00002 (just embedding). GPT-3.5 call: $0.001 (input ~50 tokens, output ~150 tokens). GPT-4 call: $0.03 (same token counts). For a typical 5-turn session: 1.5 cache hits ($0.00003), 2.8 GPT-3.5 calls ($0.0028), 0.7 GPT-4 calls ($0.021). Total: ~$0.086 versus $0.45 baseline. All tracked in app/services/cost_tracker.py.',
    'technical');

    INSERT INTO public.qa_pairs (user_id, question, answer, question_type) VALUES
    (heejin_uuid,
    'What if GPT-4 prices drop? Does your architecture still make sense?',
    'Great question. If GPT-4 drops to GPT-3.5 pricing, the routing becomes less critical for cost, but it''s still valuable for latency - GPT-3.5 is faster. Also, the semantic caching layer still saves 30% regardless of model prices. And the architecture is flexible - I can adjust the complexity threshold to route more traffic to the higher-quality model if costs allow.',
    'technical');

    INSERT INTO public.qa_pairs (user_id, question, answer, question_type) VALUES
    (heejin_uuid,
    'How do you track costs in real-time?',
    'The cost_tracker.py module logs every API call with model, input tokens, output tokens, and calculated cost based on current pricing from app/core/config.py. It aggregates at session level and user level. In production, I''d send these logs to a monitoring dashboard so I can see real-time cost per user, cost per hour, and get alerts if costs spike unexpectedly.',
    'technical');

    INSERT INTO public.qa_pairs (user_id, question, answer, question_type) VALUES
    (heejin_uuid,
    'What''s the most expensive edge case you''ve found?',
    'Long-form crisis situations. If someone writes a 500-word message about suicidal ideation, that''s a large context window going to GPT-4, no caching possible. One of those could cost $0.08 alone. But that''s exactly where we should spend the money - crisis support is where quality matters most. I''d rather optimize away 100 cheap queries than compromise on one critical one.',
    'technical');

    INSERT INTO public.qa_pairs (user_id, question, answer, question_type) VALUES
    (heejin_uuid,
    'How would you optimize costs further?',
    'Two immediate wins. First, OpenAI''s prompt caching feature - I could cache the system prompt across requests, saving another 20-30%. Second, fine-tuning GPT-3.5 on therapeutic conversations could improve quality enough to handle some of the current GPT-4 workload. Longer term, streaming responses reduces perceived latency, making users more tolerant of GPT-3.5''s slightly slower generation.',
    'technical');

    -- CATEGORY 4: TECHNICAL - SAFETY / HEALTHBENCH (6 questions - technical)

    INSERT INTO public.qa_pairs (user_id, question, answer, question_type) VALUES
    (heejin_uuid,
    'You mentioned HealthBench. How specifically did it influence your design?',
    'HealthBench emphasizes three things: emergency referral accuracy, communication quality, and responding under uncertainty. I applied these directly. First, crisis detection is Layer 1 in the router - before cost optimization. Second, system prompts in app/services/openai_client.py are tailored for therapeutic conversation. Third, when the AI is uncertain, it says so rather than hallucinating. HealthBench taught me that in healthcare AI, a safe ''I don''t know'' is better than a confident wrong answer.',
    'technical');

    INSERT INTO public.qa_pairs (user_id, question, answer, question_type) VALUES
    (heejin_uuid,
    'How do you handle confirmation bias in mental health AI?',
    'This is critical. If a user repeatedly journals about suicidal thoughts, the AI can''t just affirm and deepen that pattern. The THERAPEUTIC_SYSTEM_PROMPT in openai_client.py explicitly instructs the model to gently challenge catastrophic thinking and suggest professional help. The crisis detection layer catches these patterns and routes to the safety-focused GPT-4 prompt. The app would also have a visible ''Talk to a human'' button linking to crisis hotlines.',
    'technical');

    INSERT INTO public.qa_pairs (user_id, question, answer, question_type) VALUES
    (heejin_uuid,
    'What if the AI generates harmful advice?',
    'Multi-layer defense. First, system prompt explicitly forbids medical advice, suicide methods, or anything that could cause harm. Second, crisis keywords trigger the CRISIS_SYSTEM_PROMPT which emphasizes professional help resources. Third, in production I''d implement output filtering - responses checked for crisis language with warning overlays. Fourth, I''d log all GPT-4 crisis conversations for manual review. Defense in depth - multiple chances to catch and correct.',
    'technical');

    INSERT INTO public.qa_pairs (user_id, question, answer, question_type) VALUES
    (heejin_uuid,
    'How do you balance empathy with not replacing professional therapy?',
    'The THERAPEUTIC_SYSTEM_PROMPT sets clear boundaries: ''I''m a journaling companion, not a therapist. I can listen and reflect, but I can''t diagnose or treat mental health conditions.'' When users ask for clinical advice, the response guides them to licensed professionals. It''s empathetic but boundaried.',
    'technical');

    INSERT INTO public.qa_pairs (user_id, question, answer, question_type) VALUES
    (heejin_uuid,
    'What''s your false positive rate for crisis detection?',
    'In testing, about 3% false positive rate - phrases like ''I''m dying to see that movie'' triggering crisis mode. I handle this by showing a gentle check-in rather than alarming the user. The router prioritizes safety over convenience - I''d rather have 3% false positives than miss a real crisis. The CRISIS_KEYWORDS list is deliberately conservative.',
    'technical');

    INSERT INTO public.qa_pairs (user_id, question, answer, question_type) VALUES
    (heejin_uuid,
    'How would you implement HealthBench-style evaluation in production?',
    'I''d sample 100 random conversations per week and evaluate them on HealthBench criteria - accurate information, appropriate communication, proper emergency handling. Use GPT-4 as the grader initially, then have human clinicians review a subset to validate. Over time, this builds a quality dataset and catches model drift.',
    'technical');

    -- CATEGORY 5: BEHAVIORAL (7 questions - behavioral)

    INSERT INTO public.qa_pairs (user_id, question, answer, question_type) VALUES
    (heejin_uuid,
    'Tell me about a time you failed.',
    'This resume situation is the most recent. I failed to communicate accurately the stage of my project. But I learned that in high-stakes environments like OpenAI, precision matters more than impressiveness. I''d rather under-promise and over-deliver. The failure taught me to separate ''what I built'' from ''what I validated'' - and to be crystal clear about the distinction.',
    'behavioral');

    INSERT INTO public.qa_pairs (user_id, question, answer, question_type) VALUES
    (heejin_uuid,
    'Why do you want to work at OpenAI specifically?',
    'Two reasons. First, mission alignment - I''ve been building AI for mental health, which is exactly the kind of ''AI for humanity'' OpenAI prioritizes. I''ve read your HealthBench research, I follow your safety work, and I believe AI should benefit vulnerable populations. Second, Solutions Architect is the perfect intersection of my background - I''m technical enough to debug customer code, but I''ve been a founder so I understand business constraints. I want to help Korean startups succeed with OpenAI, and I can bridge that gap.',
    'behavioral');

    INSERT INTO public.qa_pairs (user_id, question, answer, question_type) VALUES
    (heejin_uuid,
    'What''s your biggest weakness?',
    'I move fast, sometimes too fast. As a co-founder of a startup, I optimized for shipping quickly, which meant I didn''t always document decisions thoroughly or get external review before launch. This resume situation is an example - I should have had someone else review it. At OpenAI, I''d balance that speed with the rigor you need for customer-facing roles - double-checking technical guidance, documenting recommendations, and getting peer review.',
    'behavioral');

    INSERT INTO public.qa_pairs (user_id, question, answer, question_type) VALUES
    (heejin_uuid,
    'How do you handle disagreement with a customer?',
    'I''d first make sure I understand their perspective - ask clarifying questions, restate their position to confirm. Then I''d present my technical recommendation with data - ''Here''s why I think approach A is better than B, based on X, Y, Z.'' But ultimately, it''s their product. If they disagree after hearing the technical tradeoffs, I''d support their decision and help them execute it well. My job is to give them the information to make good choices, not to force my opinion.',
    'behavioral');

    INSERT INTO public.qa_pairs (user_id, question, answer, question_type) VALUES
    (heejin_uuid,
    'Describe a time you had to learn something completely new quickly.',
    'iOS development with Swift for Birth2Death. I had React Native experience, but native iOS was completely new. I had limited time before wanting to launch. I read Apple''s docs, built prototype apps, joined developer forums, and shipped a working mental health journaling app. It wasn''t perfect, but it worked. That ability to ramp up quickly on new tech is critical for Solutions Architect - your customers will be using cutting-edge AI in ways no one''s done before.',
    'behavioral');

    INSERT INTO public.qa_pairs (user_id, question, answer, question_type) VALUES
    (heejin_uuid,
    'How do you prioritize when everything is urgent?',
    'I use impact vs effort matrix. High impact, low effort goes first. But for startups, there''s a third dimension: risk. If something could kill the business if wrong (like safety in mental health AI), it gets priority regardless of effort. When I built Birth2Death, I spent 40% of dev time on safety features that users wouldn''t directly see - because the risk of getting it wrong was too high.',
    'behavioral');

    INSERT INTO public.qa_pairs (user_id, question, answer, question_type) VALUES
    (heejin_uuid,
    'What would you do if a customer asked you to help them build something unethical?',
    'I''d first clarify what they''re trying to achieve and why. Sometimes what sounds unethical is a misunderstanding. If it''s genuinely unethical - like using AI to manipulate users or violate privacy - I''d explain why it violates OpenAI''s usage policies and suggest ethical alternatives. If they insist, I''d escalate to my manager and refuse to help. I won''t compromise on ethics for a customer win.',
    'behavioral');

    -- CATEGORY 6: SOLUTIONS ARCHITECT ROLE (7 questions - general)

    INSERT INTO public.qa_pairs (user_id, question, answer, question_type) VALUES
    (heejin_uuid,
    'What does a Solutions Architect do, in your understanding?',
    'A Solutions Architect is a technical advisor who helps customers succeed with OpenAI''s platform. That means: understanding their business problem, designing an architecture that solves it, helping them implement it, troubleshooting when things break, and feeding product feedback back to OpenAI. You''re part consultant, part engineer, part customer advocate. You need to speak both founder language and engineer language fluently.',
    'general');

    INSERT INTO public.qa_pairs (user_id, question, answer, question_type) VALUES
    (heejin_uuid,
    'How would you help a Korean startup that''s never used LLMs before?',
    'I''d start with their business problem, not the technology. What are they trying to achieve? Then I''d show them a simple proof of concept - 20 lines of Python calling the OpenAI API - so they see immediate value. Once they''re excited, I''d help them architect properly: prompt engineering best practices, error handling, cost management, evaluation metrics. I''d also connect them with other Korean startups doing similar things - community building is huge in Korea''s ecosystem.',
    'general');

    INSERT INTO public.qa_pairs (user_id, question, answer, question_type) VALUES
    (heejin_uuid,
    'A customer says GPT-4 is too slow. What do you recommend?',
    'First, I''d measure - what''s their actual P95 latency and what''s their target? If it''s truly too slow, I''d recommend: (1) Streaming responses so users see output immediately, (2) Model routing - use GPT-3.5 for simple queries like I did in Birth2Death, (3) Prompt compression to reduce tokens, (4) Caching for repeated queries. I''d also ask if they need GPT-4 for everything - often 80% of queries can use a faster model. Birth2Death is a case study for exactly this problem.',
    'general');

    INSERT INTO public.qa_pairs (user_id, question, answer, question_type) VALUES
    (heejin_uuid,
    'A customer''s costs are too high. How do you help?',
    'I''d audit their usage - are they using GPT-4 when GPT-3.5 would work? Are they re-sending the same context window repeatedly? Are they using inefficient prompts? Then I''d show them concrete tactics: model routing like I implemented in Birth2Death, semantic caching, prompt optimization, fine-tuning for common queries. I''d build them a cost tracking dashboard so they can see exactly where money is going. My Birth2Death cost optimization architecture reducing costs by 80% is exactly the reference I''d share.',
    'general');

    INSERT INTO public.qa_pairs (user_id, question, answer, question_type) VALUES
    (heejin_uuid,
    'How would you handle a customer who''s frustrated with OpenAI''s rate limits?',
    'Empathy first - rate limits are frustrating when you''re trying to ship. Then solutions: (1) Request a rate limit increase if they have a good use case, (2) Implement request queuing and retry logic to handle limits gracefully, (3) Use batching to reduce request count, (4) Consider upgrading to a higher tier. I''d also help them architect around limits - for example, caching aggressively to reduce total requests.',
    'general');

    INSERT INTO public.qa_pairs (user_id, question, answer, question_type) VALUES
    (heejin_uuid,
    'What would you do if you don''t know the answer to a customer''s technical question?',
    'I''d be honest - ''I don''t know off the top of my head, but let me find out.'' Then I''d consult OpenAI''s internal docs, ask the engineering team, or escalate to product specialists. The key is not pretending to know when you don''t. Customers trust advisors who say ''I don''t know, but I''ll get you the answer'' more than those who bullshit.',
    'general');

    INSERT INTO public.qa_pairs (user_id, question, answer, question_type) VALUES
    (heejin_uuid,
    'How would you measure your success as a Solutions Architect?',
    'Three metrics. First, customer success - are my customers building working products and scaling? Second, NPS - would they recommend me to other founders? Third, product feedback quality - am I surfacing valuable insights to OpenAI''s product team? It''s not about how many calls I take, it''s about whether the customers I work with succeed and whether I help OpenAI build better products.',
    'general');

    -- CATEGORY 7: KOREA / LOCALIZATION (6 questions - general)

    INSERT INTO public.qa_pairs (user_id, question, answer, question_type) VALUES
    (heejin_uuid,
    'Why is the Seoul Solutions Architect role important?',
    'Korea is transitioning from a ''fast follower'' to a ''first mover'' in AI. Korean startups are incredibly ambitious and well-funded, but many don''t have deep experience with frontier LLMs. They need someone who understands both the technology and the Korean business culture. I can bridge that gap - I''m a native Korean speaker, I''ve worked in Seoul''s startup ecosystem, and I have hands-on OpenAI API experience.',
    'general');

    INSERT INTO public.qa_pairs (user_id, question, answer, question_type) VALUES
    (heejin_uuid,
    'What''s unique about the Korean startup ecosystem?',
    'Three things. First, speed - Korean startups move incredibly fast, often faster than US counterparts. They expect rapid iteration. Second, hierarchy - even in startups, seniority matters. As a Solutions Architect, I need to communicate differently with a CEO versus an engineer. Third, community - Korean founders trust peer recommendations heavily. Building relationships in the ecosystem compounds quickly.',
    'general');

    INSERT INTO public.qa_pairs (user_id, question, answer, question_type) VALUES
    (heejin_uuid,
    'How would you handle language barriers with Korean customers?',
    'I''m a native Korean speaker, so language isn''t a barrier for me. But cultural translation matters too. Korean business culture is more formal and relationship-driven than US culture. I''d invest time building relationships before jumping into technical recommendations. I''d also translate OpenAI''s documentation and best practices into Korean where needed - many developers prefer Korean for learning.',
    'general');

    INSERT INTO public.qa_pairs (user_id, question, answer, question_type) VALUES
    (heejin_uuid,
    'What Korean companies do you think would benefit most from OpenAI''s platform?',
    'I see three categories. First, B2B SaaS companies adding AI features - HR tech, customer support, legal tech. Second, content companies - Naver, Kakao, entertainment companies could use GPT for content generation. Third, healthcare and education startups - Korea has strong digital health and edtech sectors, and they''re underserved by AI solutions. I''d prioritize companies with distribution and funding.',
    'general');

    INSERT INTO public.qa_pairs (user_id, question, answer, question_type) VALUES
    (heejin_uuid,
    'How would you build trust with Korean founders who are skeptical of US tech companies?',
    'I''d emphasize that I''m Korean and I understand their concerns - data sovereignty, latency, pricing. Then I''d show concrete value quickly - a working prototype in their first meeting. Trust in Korea is built through results and relationships, not sales pitches. I''d also connect them with other successful Korean OpenAI customers - social proof is powerful in Korea.',
    'general');

    INSERT INTO public.qa_pairs (user_id, question, answer, question_type) VALUES
    (heejin_uuid,
    'What are the biggest technical challenges for Korean language processing with LLMs?',
    'Two main issues. First, tokenization - Korean text tokenizes less efficiently than English, so costs are higher per character. I''d help Korean customers optimize prompts to reduce tokens. Second, cultural context - idioms, honorifics, and cultural references don''t always translate well. I''d recommend prompt engineering techniques that preserve Korean cultural nuance rather than forcing English mental models.',
    'general');

    -- CATEGORY 8: BIRTH2DEATH (5 questions - general)

    INSERT INTO public.qa_pairs (user_id, question, answer, question_type) VALUES
    (heejin_uuid,
    'Tell me more about Birth2Death.',
    'Birth2Death is a mental health journaling platform built entirely on OpenAI''s API. My co-founder Kush and I built it to help people process difficult emotions through AI-assisted journaling. The technical challenge was making it cost-effective and safe - hence the model routing, semantic caching, and crisis detection architecture. The code is on GitHub at github.com/JO-HEEJIN/birth2death-backend.',
    'general');

    INSERT INTO public.qa_pairs (user_id, question, answer, question_type) VALUES
    (heejin_uuid,
    'How many users does Birth2Death have right now?',
    'Birth2Death hasn''t launched publicly. We''ve built the full architecture - the backend is production-ready, we have the iOS app built - but we''re in beta testing with about 20 users (friends and early supporters). The 1,000+ user metrics on my resume were design targets, not actual users. That''s the mistake I''m addressing upfront.',
    'general');

    INSERT INTO public.qa_pairs (user_id, question, answer, question_type) VALUES
    (heejin_uuid,
    'Why haven''t you launched Birth2Death yet?',
    'Two reasons. First, mental health is high-stakes - we wanted to get the safety features absolutely right before public launch. Crisis detection, appropriate boundaries, ethical guardrails. Second, funding - as a bootstrapped startup, we''re being deliberate about launch timing. We''d rather launch with proper support infrastructure than rush and handle a crisis poorly.',
    'general');

    INSERT INTO public.qa_pairs (user_id, question, answer, question_type) VALUES
    (heejin_uuid,
    'What platform is Birth2Death built for?',
    'We''re launching on iOS first. The initial plan was visionOS (Apple Vision Pro) because spatial computing felt natural for introspective journaling, but we pivoted to iOS for broader reach. The backend is platform-agnostic - FastAPI with OpenAI API - so we can expand to other platforms later.',
    'general');

    INSERT INTO public.qa_pairs (user_id, question, answer, question_type) VALUES
    (heejin_uuid,
    'Are you working on Birth2Death full-time?',
    'Not currently. My co-founder Kush and I are both exploring other opportunities while keeping Birth2Death as a side project. The technical infrastructure is complete and validated - we''re at the stage where the next step is either raise funding for proper launch or keep it as a side project. If I join OpenAI, I''d bring all the lessons learned from building it.',
    'general');

    -- CATEGORY 9: FUTURE PLANS (5 questions - general)

    INSERT INTO public.qa_pairs (user_id, question, answer, question_type) VALUES
    (heejin_uuid,
    'Where do you see yourself in 5 years?',
    'I see myself as a senior Solutions Architect or SA team lead at OpenAI, having helped dozens of Korean startups build successful AI products. I want to be the person Korean founders call when they''re stuck on a hard technical problem. Longer term, I''d love to contribute to OpenAI''s developer education - creating documentation, tutorials, and best practices for the Korean market.',
    'general');

    INSERT INTO public.qa_pairs (user_id, question, answer, question_type) VALUES
    (heejin_uuid,
    'What would you do in your first 30 days at OpenAI?',
    'First 2 weeks: Learn OpenAI''s internal tools, processes, and product roadmap. Shadow senior Solutions Architects on customer calls. Second 2 weeks: Take on my first customers - probably smaller startups where I can make quick impact. Final 2 weeks: Build relationships in the Korean startup ecosystem - attend meetups, reach out to accelerators, start building my network. By day 30, I want to have helped at least 3 customers ship something.',
    'general');

    INSERT INTO public.qa_pairs (user_id, question, answer, question_type) VALUES
    (heejin_uuid,
    'What type of customers would you want to work with?',
    'Early-stage startups that are technical and ambitious. I''m most valuable when they''re trying to push the boundaries - complex use cases, novel applications, technical challenges. I''d also love to work with companies in healthcare, education, or mental health - areas where AI can have real social impact. But honestly, I''d work with any customer who''s excited about building great products.',
    'general');

    INSERT INTO public.qa_pairs (user_id, question, answer, question_type) VALUES
    (heejin_uuid,
    'How would you contribute to OpenAI beyond customer work?',
    'I''d want to contribute to three areas. First, developer documentation - I''d write guides, tutorials, and case studies for the Korean market. Second, product feedback - I''d synthesize customer pain points and feature requests and feed them to the product team. Third, community building - I''d help build the Korean OpenAI developer community through meetups, workshops, and online content.',
    'general');

    INSERT INTO public.qa_pairs (user_id, question, answer, question_type) VALUES
    (heejin_uuid,
    'What''s one thing you''d change about OpenAI''s platform if you could?',
    'I''d add more granular cost controls and budgeting features. As a founder, I want to set a hard cap on API spending per user or per day and get alerted before I hit it. Right now, it''s too easy to accidentally spend $1000 on a bug. Better cost visibility and controls would make OpenAI more accessible to bootstrapped startups who are cost-conscious.',
    'general');

    -- CATEGORY 10: EDGE CASES / DIFFICULT (10 questions - situational)

    INSERT INTO public.qa_pairs (user_id, question, answer, question_type) VALUES
    (heejin_uuid,
    'What if a customer asks you to help them build a competitor to OpenAI?',
    'I''d be transparent - ''I can''t help you build a direct OpenAI competitor since I work here. But if you''re building a product that uses LLMs and could use multiple providers, I can still help you integrate OpenAI as one of your options.'' I''d set clear boundaries while still being helpful where appropriate.',
    'situational');

    INSERT INTO public.qa_pairs (user_id, question, answer, question_type) VALUES
    (heejin_uuid,
    'A customer is unhappy with GPT-4''s performance on their use case. What do you do?',
    'I''d first understand what ''unhappy'' means - is it accuracy, cost, latency? Then I''d debug - can I see their prompts? Their eval set? Their expected vs actual outputs? Often the issue is prompt engineering or evaluation methodology. If it''s genuinely a model limitation, I''d either help them work around it (fine-tuning, RAG, ensemble approaches) or escalate to the research team for feedback.',
    'situational');

    INSERT INTO public.qa_pairs (user_id, question, answer, question_type) VALUES
    (heejin_uuid,
    'How would you handle a customer who''s aggressive or rude on a call?',
    'I''d stay professional and try to understand what''s driving the frustration - usually it''s a technical blocker causing business pain. I''d say ''I hear you''re frustrated. Let''s focus on solving the problem. What specifically isn''t working?'' If they continue being abusive, I''d politely end the call and escalate to my manager. My job is to help customers, not to accept abuse.',
    'situational');

    INSERT INTO public.qa_pairs (user_id, question, answer, question_type) VALUES
    (heejin_uuid,
    'What would you do if you accidentally shared confidential customer information with another customer?',
    'I''d immediately notify both customers, apologize, and notify my manager and legal team. I''d be completely transparent about what was shared and what the impact could be. Then I''d work with our security team to ensure it doesn''t happen again - better access controls, clearer protocols. Mistakes happen, but how you handle them defines your integrity.',
    'situational');

    INSERT INTO public.qa_pairs (user_id, question, answer, question_type) VALUES
    (heejin_uuid,
    'A customer wants a feature that OpenAI doesn''t offer and won''t build. What do you say?',
    'I''d empathize - ''I understand why you''d want that.'' Then I''d offer alternatives - ''While we don''t offer that directly, here are three ways to achieve similar functionality.'' I''d also document the request and share it with the product team. Even if we can''t build every feature, hearing what customers need helps prioritize the roadmap.',
    'situational');

    INSERT INTO public.qa_pairs (user_id, question, answer, question_type) VALUES
    (heejin_uuid,
    'How would you handle a situation where your technical recommendation conflicts with your sales team''s promises?',
    'I''d first talk to the sales rep privately to understand what was promised and why. Often there''s a miscommunication. Then I''d talk to the customer and clarify - ''Here''s what''s technically feasible, here''s the timeline, here''s the complexity.'' If sales promised something unrealistic, I''d work with them to set proper expectations with the customer. Technical credibility is more important than a short-term sales win.',
    'situational');

    INSERT INTO public.qa_pairs (user_id, question, answer, question_type) VALUES
    (heejin_uuid,
    'What if you realize mid-call that you gave a customer wrong technical advice?',
    'I''d immediately correct it - ''Actually, I need to revise what I said earlier. I was wrong about X, the correct answer is Y.'' Then I''d explain why I was wrong and what the right approach is. Customers respect someone who admits mistakes quickly more than someone who doubles down on being wrong. Then I''d document it so I don''t make the same mistake again.',
    'situational');

    INSERT INTO public.qa_pairs (user_id, question, answer, question_type) VALUES
    (heejin_uuid,
    'A customer asks about OpenAI''s future product roadmap. What do you share?',
    'I''d only share what''s publicly announced. If they''re asking about unannounced features, I''d say ''I can''t comment on future plans, but I can help you solve your problem with what''s available today.'' If they''re a strategic customer and there''s an NDA in place, I might be able to share more, but I''d check with product leadership first.',
    'situational');

    INSERT INTO public.qa_pairs (user_id, question, answer, question_type) VALUES
    (heejin_uuid,
    'What if a customer threatens to switch to a competitor because of pricing?',
    'I''d first understand their cost concerns - what''s their current spend and what''s their budget? Then I''d show them optimization strategies to reduce costs within OpenAI. If pricing is genuinely a blocker, I''d escalate to account management for potential volume discounts. But I''d be honest - if a competitor truly offers better value for their use case, I won''t prevent them from switching. Long-term trust matters more than preventing one churn.',
    'situational');

    INSERT INTO public.qa_pairs (user_id, question, answer, question_type) VALUES
    (heejin_uuid,
    'How would you handle a customer who keeps asking for free consulting beyond the scope of Solutions Architect support?',
    'I''d set clear expectations early - ''I''m here to help you succeed with OpenAI''s platform. For architecture design and integration support, I''m your resource. But for hands-on development work or general software consulting, you''ll need to engage your own team or a consulting partner.'' I''d be helpful within boundaries, but protect my time for other customers too. If they need more intensive support, I''d explore paid professional services options.',
    'situational');

    RAISE NOTICE 'Complete: All 67 Q&A pairs inserted successfully';
    RAISE NOTICE 'Categories: Resume(5), Technical Architecture(10), Cost Optimization(6), Safety(6), Behavioral(7), Solutions Architect(7), Korea(6), Birth2Death(5), Future Plans(5), Edge Cases(10)';

END $$;
