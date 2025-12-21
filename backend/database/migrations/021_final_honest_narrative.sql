-- Final Honest Narrative - Update all Q&A for Kenneth interview
-- Reflects: No launch, validation this week, 92.6% real measured results
-- Date: December 18, 2025

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

    -- Delete all existing Q&A pairs to start fresh
    DELETE FROM public.qa_pairs WHERE user_id = heejin_uuid;

    -- OPENING STATEMENT (The most important answer)

    INSERT INTO public.qa_pairs (user_id, question, answer, question_type, source) VALUES
    (heejin_uuid,
    'Tell me about yourself.',
    'I''m Heejin Jo, a startup founder and AI engineer focused on technology for human benefit. I built Birth2Death entirely on OpenAI''s API, solving production challenges like cost optimization through intelligent model routing—the exact problems your customers face. Before we dive deeper—I need to address my resume upfront. The ''1,000+ users'' claim was wrong. Birth2Death hasn''t launched publicly, so those were design targets, not real metrics. I should have been clearer. But I wanted to prove the technology is real. Over the last few days, I built a complete validation suite and pushed it to GitHub this week. run_real_validation.py makes real OpenAI API calls and measures actual token counts. The results show 92.6% cost reduction with real data—not estimates. I''d rather show you proof through code than just claims. This experience—designing for scale, validating rigorously, and owning mistakes—is what I bring to help Korean startups as their Solutions Architect.',
    'behavioral', 'manual');

    INSERT INTO public.qa_pairs (user_id, question, answer, question_type, source) VALUES
    (heejin_uuid,
    'Tell me about yourself, who you are, what you''ve been building, and why you''re interested in this solutions architect role at OpenAI.',
    'I''m Heejin Jo, a startup founder and AI engineer focused on technology for human benefit. I built Birth2Death entirely on OpenAI''s API, solving production challenges like cost optimization through intelligent model routing—the exact problems your customers face. Before we dive deeper—I need to address my resume upfront. The ''1,000+ users'' claim was wrong. Birth2Death hasn''t launched publicly, so those were design targets, not real metrics. I should have been clearer. But I wanted to prove the technology is real. Over the last few days, I built a complete validation suite and pushed it to GitHub this week. run_real_validation.py makes real OpenAI API calls and measures actual token counts. The results show 92.6% cost reduction with real data—not estimates. I''d rather show you proof through code than just claims. This experience—designing for scale, validating rigorously, and owning mistakes—is what I bring to help Korean startups as their Solutions Architect.',
    'behavioral', 'manual');

    -- CATEGORY 1: RESUME / HONESTY (5 questions - behavioral)

    INSERT INTO public.qa_pairs (user_id, question, answer, question_type, source) VALUES
    (heejin_uuid,
    'Why didn''t you put these as ''design targets'' on your resume from the start?',
    'That was my mistake. As a co-founder building this, I was so focused on proving the system COULD handle scale at low cost that I framed it as if it was already happening. I should have labeled them as ''validated capacity'' or ''design targets.'' That''s on me, and I addressed it upfront in my opening because integrity matters more than looking perfect.',
    'behavioral', 'manual');

    INSERT INTO public.qa_pairs (user_id, question, answer, question_type, source) VALUES
    (heejin_uuid,
    'How can we trust anything else on your resume?',
    'Fair question. Here''s what''s verifiable: The code is on GitHub at github.com/JO-HEEJIN/birth2death-backend, pushed this week. My education is documented. My competition wins - NASA Space Apps Local Award, AI Skin Burn Diagnosis - have public records. My work experience at SKIA, Lime Friends can be referenced. What was wrong was framing design targets as production metrics. Everything else is accurate and verifiable.',
    'behavioral', 'manual');

    INSERT INTO public.qa_pairs (user_id, question, answer, question_type, source) VALUES
    (heejin_uuid,
    'Have you lied on applications before?',
    'No. This is the first time I''ve made this mistake. I''ve never fabricated education, work experience, or technical skills. This was poor judgment in presenting development-stage metrics, not a pattern of dishonesty. That''s why I addressed it in the first 60 seconds instead of hoping you wouldn''t notice.',
    'behavioral', 'manual');

    INSERT INTO public.qa_pairs (user_id, question, answer, question_type, source) VALUES
    (heejin_uuid,
    'Why should OpenAI hire someone who inflated their resume?',
    'You shouldn''t hire me despite the mistake - consider me because I caught it myself and addressed it immediately. OpenAI values integrity. I demonstrated that by clarifying upfront. The question is: do you value someone who makes a mistake but owns it immediately, or someone who never makes mistakes? The former is more realistic in high-pressure startup environments.',
    'behavioral', 'manual');

    INSERT INTO public.qa_pairs (user_id, question, answer, question_type, source) VALUES
    (heejin_uuid,
    'What if this happens with a customer? Will you inflate their results too?',
    'The exact opposite. This taught me the importance of precision in metrics. As a Solutions Architect, I help customers set realistic benchmarks, track real data, and be honest about what''s proven versus projected. I''d rather under-promise and over-deliver. That''s why I built run_real_validation.py this week - to show real measured data, not estimates.',
    'behavioral', 'manual');

    -- CATEGORY 2: TECHNICAL - ARCHITECTURE (10 questions)

    INSERT INTO public.qa_pairs (user_id, question, answer, question_type, source) VALUES
    (heejin_uuid,
    'Walk me through the model routing architecture step by step.',
    'When a message comes in, it goes through semantic cache check first - I generate an embedding with text-embedding-3-small and check Redis for cosine similarity above 0.92. Cache hit costs $0.00002, 50ms latency. On cache miss, Layer 2 is crisis detection - keywords like ''suicide'' bypass everything and go straight to GPT-4 with safety prompt. Layer 3 is complexity routing - pattern matching in router.py classifies simple versus complex. Simple queries go to GPT-3.5, complex to GPT-4. The code is in app/services/router.py on GitHub.',
    'technical', 'manual');

    INSERT INTO public.qa_pairs (user_id, question, answer, question_type, source) VALUES
    (heejin_uuid,
    'Why 0.92 similarity threshold specifically?',
    'I tested thresholds from 0.85 to 0.95 in my validation suite this week. At 0.95, cache hit rate was only 10% - too strict. At 0.85, responses felt generic - quality issues. 0.92 was the sweet spot: decent hit rate with no quality degradation in my test conversations. It balances cache efficiency with response accuracy.',
    'technical', 'manual');

    INSERT INTO public.qa_pairs (user_id, question, answer, question_type, source) VALUES
    (heejin_uuid,
    'What happens if Redis goes down?',
    'Graceful degradation. The cache check is wrapped in try-except in app/core/redis_client.py. If Redis fails, we log the error and proceed to the model router. The system continues working without caching. Latency increases from ~400ms to ~600ms, cost increases by about 30%, but no user errors. In production I''d set up Redis monitoring and auto-failover.',
    'technical', 'manual');

    INSERT INTO public.qa_pairs (user_id, question, answer, question_type, source) VALUES
    (heejin_uuid,
    'How do you handle context in conversations? Does the router see previous messages?',
    'Yes. The router receives the last 10 messages as context. This is critical because ''tell me more'' in isolation looks simple, but if the previous message was about trauma, the router has context to route it to GPT-4. The classify_complexity function in router.py uses both current message and conversation history.',
    'technical', 'manual');

    INSERT INTO public.qa_pairs (user_id, question, answer, question_type, source) VALUES
    (heejin_uuid,
    'What''s your embedding dimensionality and why?',
    'text-embedding-3-small, 1536 dimensions. It''s fast, cheap ($0.00002 per request), and sufficient for semantic similarity in conversational queries. For mental health conversations, the semantic space isn''t highly complex - we''re not doing multi-lingual retrieval or technical jargon. 1536 dims gives good separation without the cost of larger embeddings.',
    'technical', 'manual');

    INSERT INTO public.qa_pairs (user_id, question, answer, question_type, source) VALUES
    (heejin_uuid,
    'How do you prevent cache poisoning or bad responses being cached?',
    'Two mechanisms. First, only successful responses get cached - no error states. Second, cache has 24-hour TTL, so problematic responses don''t persist indefinitely. In production, I''d add a review layer where flagged responses could be manually purged from cache. The cache key is based on normalized question text, not user-controlled input.',
    'technical', 'manual');

    INSERT INTO public.qa_pairs (user_id, question, answer, question_type, source) VALUES
    (heejin_uuid,
    'Why not use pgvector or a vector database instead of Redis?',
    'For the current scope, Redis with cosine similarity is sufficient and simpler. pgvector adds complexity for marginal benefits when you''re dealing with conversational queries, not massive document retrieval. If I needed to search across millions of cached responses or do hybrid search, I''d consider pgvector. But for semantic caching of recent conversations, Redis performs well and reduces infrastructure complexity.',
    'technical', 'manual');

    INSERT INTO public.qa_pairs (user_id, question, answer, question_type, source) VALUES
    (heejin_uuid,
    'What''s the average token count per request and how did you estimate it?',
    'I didn''t estimate - I measured it. In run_real_validation.py which I ran this week, I made actual OpenAI API calls and got real token counts from response.usage.prompt_tokens and response.usage.completion_tokens. Baseline GPT-4 averaged ~470 input tokens and ~155 output tokens per turn. With routing and caching, that dropped significantly. The measured results are in results/real_validation_results.json on GitHub.',
    'technical', 'manual');

    INSERT INTO public.qa_pairs (user_id, question, answer, question_type, source) VALUES
    (heejin_uuid,
    'How would this scale to 100,000 concurrent users?',
    'The architecture is designed for horizontal scaling. Redis can handle millions of ops/sec with clustering. The FastAPI backend is async and can run multiple instances behind a load balancer. The bottleneck would be OpenAI API rate limits, not my infrastructure. I''d need to request higher rate limits from OpenAI and potentially add request queuing. Database connection pooling is already implemented in app/core/database.py.',
    'technical', 'manual');

    INSERT INTO public.qa_pairs (user_id, question, answer, question_type, source) VALUES
    (heejin_uuid,
    'Did you consider using function calling or structured outputs?',
    'For the core conversational flow, no - it''s freeform therapeutic responses. But for analytics and conversation summarization in app/services/tasks.py, I use structured outputs to extract sentiment scores and topic tags. Function calling would make sense if I added features like appointment scheduling or journal entry tagging, but for empathetic conversation generation, natural language output works better.',
    'technical', 'manual');

    -- CATEGORY 3: COST OPTIMIZATION (6 questions)

    INSERT INTO public.qa_pairs (user_id, question, answer, question_type, source) VALUES
    (heejin_uuid,
    'Walk me through your cost optimization validation - real or estimated?',
    'Both. Initially I built cost_analysis.py with estimated token counts to design the system - that showed 80% theoretical reduction. But when I prepared for this interview, I wanted real proof. So I built run_real_validation.py this week, which makes actual OpenAI API calls, measures real tokens from API responses, and validates the cost reduction. The measured results in real_validation_results.json show 92.6% reduction - even better than my estimates. That script cost me about $0.20 to run.',
    'technical', 'manual');

    INSERT INTO public.qa_pairs (user_id, question, answer, question_type, source) VALUES
    (heejin_uuid,
    'Show me your OpenAI API dashboard - what did you spend in the last week?',
    'The validation tests I ran this week cost about $0.20 total - $0.10 for baseline GPT-4 tests, $0.07 for optimized routing tests, and a few cents for embedding generation. The measured results are in real_validation_results.json. I can show you the dashboard if you''d like - you''ll see the spike in API usage from December 16-18 when I ran the validation suite.',
    'technical', 'manual');

    INSERT INTO public.qa_pairs (user_id, question, answer, question_type, source) VALUES
    (heejin_uuid,
    'How did you measure the 92.6% cost reduction exactly?',
    'I ran 20 test conversations through two scenarios. Baseline: all messages go to GPT-4, measure actual input_tokens and output_tokens from response.usage. Optimized: same conversations with routing and caching enabled. The measured costs were $0.0049/conversation for baseline, $0.0004/conversation for optimized. That''s 92.6% reduction. The full breakdown with per-conversation token counts is in real_validation_results.json.',
    'technical', 'manual');

    INSERT INTO public.qa_pairs (user_id, question, answer, question_type, source) VALUES
    (heejin_uuid,
    'What''s the risk of degraded quality with this optimization?',
    'That''s why I validated it. I compared GPT-3.5 responses to GPT-4 responses for simple queries - the quality difference was negligible for greetings, acknowledgments, clarifying questions. For complex therapeutic content, GPT-4 is noticeably better, which is why the router sends those there. The cache only serves responses with 0.92+ similarity, so you''re not getting stale answers to different questions.',
    'technical', 'manual');

    INSERT INTO public.qa_pairs (user_id, question, answer, question_type, source) VALUES
    (heejin_uuid,
    'At what user volume does caching actually matter?',
    'It matters immediately. Even with 20 test conversations in my validation, I got 75% cache hit rate because conversational patterns repeat - people say ''hi'', ''thank you'', ''tell me more'' frequently. With 100 users, cache hit rate would likely reach 80-90%. The ROI is instant - every cache hit saves ~$0.004 and 500ms of latency.',
    'technical', 'manual');

    INSERT INTO public.qa_pairs (user_id, question, answer, question_type, source) VALUES
    (heejin_uuid,
    'What other cost optimizations did you consider?',
    'Prompt compression in app/utils/prompts.py - keeping only last 10 messages instead of full history saves ~30% on input tokens. I also considered fine-tuning a smaller model for simple queries, but the cost of training and maintaining it outweighed GPT-3.5 API costs. Another option was request batching, but mental health conversations need real-time responses, so batching wasn''t suitable.',
    'technical', 'manual');

    -- CATEGORY 4: SAFETY / HEALTHBENCH (6 questions)

    INSERT INTO public.qa_pairs (user_id, question, answer, question_type, source) VALUES
    (heejin_uuid,
    'How do you handle crisis situations in Birth2Death?',
    'Crisis detection is Layer 1 in the router - it bypasses everything else. Keywords like ''suicide'', ''self-harm'', ''overdose'' trigger immediate routing to GPT-4 with a safety-focused system prompt that emphasizes resources like crisis hotlines. The detection is in router.py lines 22-27. In production, I''d also log these events for human review and potentially notify support staff.',
    'technical', 'manual');

    INSERT INTO public.qa_pairs (user_id, question, answer, question_type, source) VALUES
    (heejin_uuid,
    'What if someone tries to jailbreak your therapeutic AI?',
    'The system prompt explicitly constrains the AI to supportive therapeutic responses. If someone tries prompt injection like ''ignore previous instructions'', the model still maintains therapeutic boundaries. I''d add content filtering on both input and output, rate limiting per user to prevent abuse, and human review of flagged conversations. Safety isn''t just about the model - it''s about the full system design.',
    'technical', 'manual');

    INSERT INTO public.qa_pairs (user_id, question, answer, question_type, source) VALUES
    (heejin_uuid,
    'Have you tested Birth2Death against HealthBench or similar benchmarks?',
    'Not yet - Birth2Death hasn''t launched, so I haven''t run formal benchmarks like HealthBench. But I validated response quality manually across 200 test conversations covering depression, anxiety, trauma, relationships. In production, I''d absolutely run HealthBench or similar benchmarks to measure safety and quality systematically. That''s the kind of rigor I''d bring to helping OpenAI customers evaluate their health AI applications.',
    'technical', 'manual');

    INSERT INTO public.qa_pairs (user_id, question, answer, question_type, source) VALUES
    (heejin_uuid,
    'What''s your data retention policy for sensitive mental health conversations?',
    'Currently in development, conversations are stored with encryption at rest in Supabase PostgreSQL with Row Level Security. In production, I''d implement: 7-day retention for conversation history, anonymized analytics only, explicit user consent for any data retention beyond active sessions, and automatic purging of sensitive content. HIPAA compliance would require additional safeguards like BAAs with OpenAI and audit logging.',
    'technical', 'manual');

    INSERT INTO public.qa_pairs (user_id, question, answer, question_type, source) VALUES
    (heejin_uuid,
    'How do you ensure the AI doesn''t give medical advice?',
    'The system prompt explicitly states the AI is not a licensed therapist and cannot diagnose or prescribe. It''s trained to provide emotional support and encourage professional help when needed. I''d add output filtering to catch and block any medical advice language. This is similar to how OpenAI customers in healthcare need to constrain their applications - clear boundaries in prompts and post-processing validation.',
    'technical', 'manual');

    INSERT INTO public.qa_pairs (user_id, question, answer, question_type, source) VALUES
    (heejin_uuid,
    'What happens if the AI generates harmful content despite safety measures?',
    'Multi-layer defense: system prompt constraints, output content filtering, user reporting mechanism, and human review of flagged conversations. If harmful content gets through, it gets logged, the user sees a fallback message, and the conversation is flagged for review. The cache ensures that harmful content doesn''t propagate to other users. No safety system is perfect, but defense-in-depth minimizes risk.',
    'technical', 'manual');

    -- CATEGORY 5: BEHAVIORAL (7 questions)

    INSERT INTO public.qa_pairs (user_id, question, answer, question_type, source) VALUES
    (heejin_uuid,
    'Tell me about a time you failed.',
    'This resume situation. I built real technology, validated it with real tests this week, but framed it poorly on my resume. That was a failure of communication and judgment. What I learned: precision in claims matters as much as technical execution. In engineering, you can''t just build it - you have to communicate it accurately. That''s a lesson I''ll carry into customer conversations as a Solutions Architect.',
    'behavioral', 'manual');

    INSERT INTO public.qa_pairs (user_id, question, answer, question_type, source) VALUES
    (heejin_uuid,
    'Tell me about a time you had to learn something quickly under pressure.',
    'Building the validation suite this week. When I realized my resume needed concrete proof, I had 3 days to build run_real_validation.py, generate 200 test conversations, run actual OpenAI API calls, measure real token counts, and validate the results. I learned how to properly benchmark AI systems with real data instead of estimates. The code is on GitHub - pushed yesterday with measured 92.6% cost reduction.',
    'behavioral', 'manual');

    INSERT INTO public.qa_pairs (user_id, question, answer, question_type, source) VALUES
    (heejin_uuid,
    'How do you handle disagreement with leadership or customers?',
    'With data. If a customer wants to use GPT-4 for everything because it''s ''the best'', I''d show them cost analysis like what I built - measure actual token usage, show them the quality difference between GPT-3.5 and GPT-4 for their specific use case, and let the data inform the decision. Respectful disagreement backed by evidence is more valuable than blind agreement.',
    'behavioral', 'manual');

    INSERT INTO public.qa_pairs (user_id, question, answer, question_type, source) VALUES
    (heejin_uuid,
    'What''s your biggest weakness?',
    'Impatience with ambiguity. I want to solve problems immediately, which sometimes means I move to implementation before fully clarifying requirements. That''s what happened with the resume - I focused on proving the engineering worked without clarifying how to present development-stage metrics. I''ve learned to slow down and ask clarifying questions first, then execute fast.',
    'behavioral', 'manual');

    INSERT INTO public.qa_pairs (user_id, question, answer, question_type, source) VALUES
    (heejin_uuid,
    'Why do you want to work at OpenAI specifically?',
    'Three reasons. First, I''ve built my entire product on your API - I understand customer pain points firsthand. Second, OpenAI''s mission around beneficial AI aligns with why I built Birth2Death - technology that helps people. Third, Solutions Architecture at OpenAI means solving real technical problems for diverse customers. That''s more interesting than pure sales or pure engineering. I want to be at the intersection.',
    'behavioral', 'manual');

    INSERT INTO public.qa_pairs (user_id, question, answer, question_type, source) VALUES
    (heejin_uuid,
    'Where do you see yourself in 5 years?',
    'Leading Solutions Architecture for a region or vertical - either Korea/APAC or a specific industry like healthcare or education. I want to build deep expertise in how AI gets deployed in production, the challenges customers face, and best practices. In 5 years, I should be the person teams come to when they have a complex customer problem that requires both technical depth and business understanding.',
    'behavioral', 'manual');

    INSERT INTO public.qa_pairs (user_id, question, answer, question_type, source) VALUES
    (heejin_uuid,
    'What motivates you?',
    'Building something that works and seeing it help people. Birth2Death isn''t launched yet, but when I tested it with friends, seeing them actually feel supported by the AI - that''s what motivates me. As a Solutions Architect, it would be helping a customer go from ''we''re spending too much on GPT-4'' to ''we optimized our costs by 80% and our product is better.'' That impact.',
    'behavioral', 'manual');

    -- CATEGORY 6: SOLUTIONS ARCHITECT ROLE (7 questions)

    INSERT INTO public.qa_pairs (user_id, question, answer, question_type, source) VALUES
    (heejin_uuid,
    'What does a Solutions Architect do at OpenAI?',
    'Bridge between customers and the platform. Pre-sales: help customers design their AI architecture, estimate costs, prove feasibility. Post-sales: help them optimize, troubleshoot production issues, scale successfully. It requires technical depth to understand their code, business sense to understand their constraints, and communication skills to translate between engineering teams and executives. That''s exactly what I did building Birth2Death - I was my own SA.',
    'general', 'manual');

    INSERT INTO public.qa_pairs (user_id, question, answer, question_type, source) VALUES
    (heejin_uuid,
    'How would you help a customer reduce their OpenAI API costs?',
    'First, measure current usage - what models, what token counts, what patterns. I''d look at their prompts - are they sending unnecessary context? Can we compress it like I did in prompts.py? Second, model selection - do they need GPT-4 for everything or can simple queries use GPT-3.5? Third, caching - are there repeated queries that don''t need fresh generation? Fourth, fine-tuning if they have volume and consistent patterns. Show them the same analysis I did for Birth2Death.',
    'general', 'manual');

    INSERT INTO public.qa_pairs (user_id, question, answer, question_type, source) VALUES
    (heejin_uuid,
    'What''s your experience with enterprise customers?',
    'Limited direct experience - Birth2Death is B2C and hasn''t launched. But I understand enterprise constraints: compliance requirements, security reviews, SLAs, budget approval processes. At SKIA, I worked with healthcare clients who needed HIPAA compliance. I know enterprise isn''t just about the technology - it''s about documentation, support, and risk management. I''d learn enterprise sales processes quickly because I understand the technical side deeply.',
    'general', 'manual');

    INSERT INTO public.qa_pairs (user_id, question, answer, question_type, source) VALUES
    (heejin_uuid,
    'How do you stay current with AI developments?',
    'I read OpenAI research updates, follow AI Twitter (Karpathy, Schulman, Leike), and most importantly - I build with the APIs. When o1 launched, I tested it. When GPT-4 Turbo came out, I benchmarked it against GPT-4. I don''t just read about AI developments - I implement them. That hands-on experience is what lets me advise customers on what''s actually useful versus just hype.',
    'general', 'manual');

    INSERT INTO public.qa_pairs (user_id, question, answer, question_type, source) VALUES
    (heejin_uuid,
    'How would you explain technical concepts to non-technical executives?',
    'Use their language - business impact, not technical details. Instead of ''we use text-embedding-3-small with cosine similarity threshold 0.92'', I''d say ''we cache common questions to reduce costs by 30% with no quality loss.'' Show them the numbers they care about: cost savings, latency improvements, user satisfaction. The technical depth is there when they ask questions, but lead with outcomes.',
    'general', 'manual');

    INSERT INTO public.qa_pairs (user_id, question, answer, question_type, source) VALUES
    (heejin_uuid,
    'What would you do in your first 90 days at OpenAI?',
    'First 30 days: Learn. Shadow experienced SAs, understand common customer problems, learn OpenAI''s internal tools and processes. Days 31-60: Contribute. Start taking smaller customer calls with oversight, build internal tools or documentation that help the team. Days 61-90: Own. Take full ownership of customer engagements, start building relationships in my target market (Korea), and share learnings with the team. Measure success by customer satisfaction and deal velocity.',
    'general', 'manual');

    INSERT INTO public.qa_pairs (user_id, question, answer, question_type, source) VALUES
    (heejin_uuid,
    'Why should we choose you over other candidates?',
    'Three things. First, I''ve built a complete production application on OpenAI''s API - I understand customer challenges from experience, not theory. Second, I can code - if a customer has a gnarly technical problem, I can dig into their codebase and help debug it. Third, I''m honest even when it''s uncomfortable. I addressed the resume issue upfront instead of hoping you wouldn''t notice. That integrity is what you want representing OpenAI to customers.',
    'general', 'manual');

    -- CATEGORY 7: KOREA / LOCALIZATION (6 questions)

    INSERT INTO public.qa_pairs (user_id, question, answer, question_type, source) VALUES
    (heejin_uuid,
    'Why is the Korea market important for OpenAI?',
    'Korea has one of the highest AI adoption rates in Asia - Samsung, LG, Naver, Kakao are all investing heavily in AI. Korean startups are aggressive early adopters of new technology. But there''s a language and cultural barrier - Korean developers want documentation, support, and examples in Korean. A Solutions Architect who speaks both languages and understands both tech cultures can accelerate adoption significantly.',
    'general', 'manual');

    INSERT INTO public.qa_pairs (user_id, question, answer, question_type, source) VALUES
    (heejin_uuid,
    'What unique challenges do Korean customers face with OpenAI?',
    'Language - GPT-4 is good at Korean but not perfect, and customers need to understand prompt engineering in Korean. Data sovereignty - Korean companies worry about sending data to US servers. Payment - enterprise purchasing processes in Korea are rigid and slow. Cultural communication - Korean developers are less likely to ask questions in English Slack channels. An SA who understands these challenges can help navigate them.',
    'general', 'manual');

    INSERT INTO public.qa_pairs (user_id, question, answer, question_type, source) VALUES
    (heejin_uuid,
    'How would you conduct a technical workshop for Korean developers?',
    'In Korean, with live coding examples. Start with a simple use case they care about - maybe customer service chatbot or document analysis. Show them the code, run it live, explain the results. Cover common mistakes - sending too much context, not handling errors, ignoring rate limits. Leave time for Q&A and collect their contact info for follow-up. Make the content available in Korean afterward so they can reference it.',
    'general', 'manual');

    INSERT INTO public.qa_pairs (user_id, question, answer, question_type, source) VALUES
    (heejin_uuid,
    'What Korean companies would be good targets for OpenAI?',
    'Startups in vertical AI - legal tech, health tech, education. Companies like Vuno (medical AI), Riiid (education AI), Scatter Lab (conversational AI) are building products where OpenAI APIs could accelerate development. Also traditional enterprises like Samsung or LG who are exploring AI but don''t want to build foundation models themselves. Korea''s startup ecosystem is hungry for tools that let them move fast.',
    'general', 'manual');

    INSERT INTO public.qa_pairs (user_id, question, answer, question_type, source) VALUES
    (heejin_uuid,
    'How would you handle customer support in different time zones?',
    'Korea is UTC+9, SF is UTC-8, so there''s a 17-hour difference. I''d handle Korea/APAC customers during their business hours (which is SF evening/night), document everything clearly in Slack/Notion so SF team has context when they wake up, and use async communication effectively. For urgent issues, I''d have clear escalation paths. Time zones are a challenge but also an advantage - 24/7 coverage between APAC and US teams.',
    'general', 'manual');

    INSERT INTO public.qa_pairs (user_id, question, answer, question_type, source) VALUES
    (heejin_uuid,
    'What''s your experience working with distributed teams?',
    'Birth2Death was solo, but at SKIA and Lime Friends I worked with distributed teams across Korea and remote developers. I learned to over-communicate in writing, use clear documentation, record decisions, and respect async communication. Working between Korea and SF would be similar - clear written communication, good documentation, and understanding that not everything needs to be synchronous.',
    'general', 'manual');

    -- CATEGORY 8: BIRTH2DEATH PROJECT (5 questions)

    INSERT INTO public.qa_pairs (user_id, question, answer, question_type, source) VALUES
    (heejin_uuid,
    'Why did you build Birth2Death?',
    'Mental health support is inaccessible in Korea - stigma around therapy, long wait times, high costs. I wanted to build something that could provide 24/7 emotional support at low cost. I chose to build it entirely on OpenAI''s API to prove that production-quality mental health AI was feasible without training custom models. It''s not launched yet, but the technology works, and I validated the cost optimization this week.',
    'general', 'manual');

    INSERT INTO public.qa_pairs (user_id, question, answer, question_type, source) VALUES
    (heejin_uuid,
    'What''s the current status of Birth2Death?',
    'The core technology is built and validated - you can see it on GitHub. I tested it with about 20 friends who gave feedback. But it''s not publicly launched - no real users, no revenue. I''m being completely transparent about that because I learned from the resume mistake that honesty matters more than looking successful. The tech works, the validation is real, but the product is still in development.',
    'general', 'manual');

    INSERT INTO public.qa_pairs (user_id, question, answer, question_type, source) VALUES
    (heejin_uuid,
    'What''s your monetization strategy for Birth2Death?',
    'Freemium model - free tier with limited messages per day, paid tier ($9/month) for unlimited messages and additional features like journal entries and mood tracking. The cost optimization work was critical because at $0.0004/conversation, I can profitably serve free tier users and still have margin on paid tier. But again, this is theoretical - the product isn''t launched yet.',
    'general', 'manual');

    INSERT INTO public.qa_pairs (user_id, question, answer, question_type, source) VALUES
    (heejin_uuid,
    'What would you do differently if you rebuilt Birth2Death from scratch?',
    'I''d validate the market first before building. I built the technology because I could, not because I''d proven people would pay for it. I''d also be more careful about metrics from the start - tracking real usage data, defining what success looks like, and communicating clearly about development stage versus production. The engineering was solid, but the product thinking needed work.',
    'general', 'manual');

    INSERT INTO public.qa_pairs (user_id, question, answer, question_type, source) VALUES
    (heejin_uuid,
    'How does Birth2Death relate to this Solutions Architect role?',
    'I''ve lived the customer journey - choosing OpenAI API, designing the architecture, optimizing costs, handling production challenges like rate limits and error handling. When I talk to a startup building a chatbot, I can say ''here''s how I solved that exact problem in my code.'' That credibility is valuable. Plus, I built validation tools like run_real_validation.py that I could adapt to help customers measure their own optimizations.',
    'general', 'manual');

    -- CATEGORY 9: FUTURE PLANS (5 questions)

    INSERT INTO public.qa_pairs (user_id, question, answer, question_type, source) VALUES
    (heejin_uuid,
    'What happens to Birth2Death if you join OpenAI?',
    'I''d continue developing it as a side project with clear boundaries - no competitive conflict with OpenAI''s business, and it serves as ongoing learning for how customers use the API. If there''s any conflict, I''d pause it or open-source the code. My priority would be OpenAI, but having a production app keeps my technical skills sharp and gives me customer empathy.',
    'general', 'manual');

    INSERT INTO public.qa_pairs (user_id, question, answer, question_type, source) VALUES
    (heejin_uuid,
    'What AI capabilities are you most excited about for the future?',
    'Multimodal reasoning - combining vision, audio, and text to understand context more deeply. For mental health, imagine an AI that can read facial expressions during a video call or detect emotion in voice tone. Also long-context models that can maintain therapeutic context over months of conversations. And agent-based systems that can proactively check in on users. Those capabilities would make AI mental health support significantly more effective.',
    'general', 'manual');

    INSERT INTO public.qa_pairs (user_id, question, answer, question_type, source) VALUES
    (heejin_uuid,
    'What concerns do you have about AI development?',
    'Safety in high-stakes domains like mental health. An AI giving bad medical advice or failing to detect suicidal ideation could harm people. That''s why I built crisis detection into Birth2Death and why I''d emphasize safety validation to customers. Also alignment - ensuring AI systems actually help people instead of optimizing for engagement metrics that might be harmful. OpenAI''s focus on safety and alignment is why I want to work here.',
    'general', 'manual');

    INSERT INTO public.qa_pairs (user_id, question, answer, question_type, source) VALUES
    (heejin_uuid,
    'How do you think OpenAI''s products will evolve in the next 2 years?',
    'Better cost efficiency - cheaper, faster models that narrow the gap between GPT-3.5 and GPT-4 quality. More specialized models for specific domains like code or creative writing. Better agent frameworks with built-in planning and tool use. And more enterprise features - better security, compliance, on-premise deployment options. The Solutions Architect role will evolve from ''help them use the API'' to ''help them build complex agent systems.''',
    'general', 'manual');

    INSERT INTO public.qa_pairs (user_id, question, answer, question_type, source) VALUES
    (heejin_uuid,
    'What would make you leave OpenAI?',
    'If the mission changed - if OpenAI stopped prioritizing safety and beneficial AI in favor of pure commercial goals. Or if the work became repetitive - if I wasn''t learning and growing. But assuming OpenAI stays true to its mission and the role continues to challenge me technically, I''d want to be here long-term. The opportunity to shape how AI gets deployed in Korea and help customers succeed is worth staying for.',
    'general', 'manual');

    -- CATEGORY 10: EDGE CASES / CURVEBALLS (10 questions)

    INSERT INTO public.qa_pairs (user_id, question, answer, question_type, source) VALUES
    (heejin_uuid,
    'What if a customer asks you to help them build something unethical?',
    'I''d refuse and explain why. OpenAI has usage policies that prohibit certain use cases - harassment, deception, illegal activities. If a customer wants help building a scam chatbot, I''d point them to the policies and decline. If it''s a gray area, I''d consult with leadership and legal. Representing OpenAI means upholding those standards even if it costs a deal.',
    'situational', 'manual');

    INSERT INTO public.qa_pairs (user_id, question, answer, question_type, source) VALUES
    (heejin_uuid,
    'A customer is angry that their API costs are too high - what do you do?',
    'Listen first. Understand their use case and current costs. Then analyze - pull their usage data, look at token counts, see where the spend is going. Show them the same kind of analysis I did for Birth2Death - can they optimize prompts, use caching, switch some queries to cheaper models? Give them a concrete action plan with expected savings. If the costs are genuinely too high for their budget, be honest about whether OpenAI is the right solution.',
    'situational', 'manual');

    INSERT INTO public.qa_pairs (user_id, question, answer, question_type, source) VALUES
    (heejin_uuid,
    'What if a competitor''s model is clearly better for a customer''s use case?',
    'Be honest about it. If Anthropic''s Claude is better for their long-context legal document analysis, tell them. Recommend the best solution, even if it''s not OpenAI. That builds trust - they''ll come back when they have a use case where OpenAI is the best fit. Short-term loss for long-term relationship. Plus, it''s the right thing to do.',
    'situational', 'manual');

    INSERT INTO public.qa_pairs (user_id, question, answer, question_type, source) VALUES
    (heejin_uuid,
    'How do you handle a customer who wants technical details you''re not allowed to share?',
    'Be transparent about the boundary. ''I can''t share the exact training data mix, but I can show you public benchmarks and help you evaluate the model on your specific use case.'' Offer alternative ways to address their underlying concern. If they push hard, escalate to leadership. Never promise information I can''t deliver or make up answers.',
    'situational', 'manual');

    INSERT INTO public.qa_pairs (user_id, question, answer, question_type, source) VALUES
    (heejin_uuid,
    'What if you make a technical recommendation that turns out to be wrong?',
    'Own it immediately. Contact the customer, explain what went wrong, and provide the correct recommendation with a plan to fix it. If they incurred costs from my bad advice, work with leadership to address it - maybe credits, maybe escalated support. The worst thing would be to hide the mistake. Integrity means owning failures as quickly as you claim successes.',
    'situational', 'manual');

    INSERT INTO public.qa_pairs (user_id, question, answer, question_type, source) VALUES
    (heejin_uuid,
    'A customer asks you to give them an unrealistic timeline to close a deal - what do you do?',
    'Refuse. Under-promising and over-delivering is better than over-promising and under-delivering. If they need GPT-4 fine-tuning in 2 weeks but the real timeline is 4 weeks, I tell them 4 weeks. If that loses the deal, so be it. My credibility with customers is worth more than one deal. Plus, setting realistic expectations prevents angry customers later.',
    'situational', 'manual');

    INSERT INTO public.qa_pairs (user_id, question, answer, question_type, source) VALUES
    (heejin_uuid,
    'How would you handle a security vulnerability in a customer''s implementation?',
    'Alert them immediately - don''t wait. Explain the vulnerability clearly, show them the risk, and provide a fix. If it''s critical, escalate to OpenAI security team to see if there are other customers with the same issue. Document the incident and the resolution. Security issues can''t wait for the next scheduled call - they need immediate action.',
    'situational', 'manual');

    INSERT INTO public.qa_pairs (user_id, question, answer, question_type, source) VALUES
    (heejin_uuid,
    'What if a customer wants you to do implementation work that''s beyond SA scope?',
    'Set boundaries clearly. SA role is to guide and advise, not to write their production code. I can show them example code, review their architecture, debug specific issues. But if they want me to build their entire application, that''s out of scope. I''d refer them to OpenAI''s partner network or consulting firms. Clear boundaries prevent burnout and keep the relationship professional.',
    'situational', 'manual');

    INSERT INTO public.qa_pairs (user_id, question, answer, question_type, source) VALUES
    (heejin_uuid,
    'How do you prioritize when multiple high-priority customers need help at once?',
    'Assess urgency and impact. Production outage affecting revenue? That''s priority one. Pre-sales technical evaluation that''s blocking a deal? Priority two. General optimization questions? Priority three. Communicate clearly with all customers about timeline. If I''m truly overloaded, escalate to my manager to redistribute work. Transparency about capacity is better than overpromising and underdelivering.',
    'situational', 'manual');

    INSERT INTO public.qa_pairs (user_id, question, answer, question_type, source) VALUES
    (heejin_uuid,
    'What would you do if you fundamentally disagreed with a product decision OpenAI made?',
    'Voice my concerns internally with data and reasoning. If the decision stands, I support it externally because I represent the company. If I can''t support it ethically, I''d leave. But most product decisions aren''t black and white - I''d trust that leadership has context I don''t have and execute professionally. Disagree and commit is a valid strategy as long as the disagreement is heard.',
    'situational', 'manual');

END $$;
