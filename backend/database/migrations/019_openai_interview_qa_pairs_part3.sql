-- OpenAI Kenneth Interview Q&A Pairs - Part 3
-- Categories 7-10: Korea, Birth2Death, Future, Edge Cases
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
    -- CATEGORY 7: KOREA / LOCALIZATION
    -- ========================================

    INSERT INTO public.qa_pairs (user_id, question, answer, question_type) VALUES
    (heejin_uuid, 'Why is the Seoul Solutions Architect role important?',
    'Korea is transitioning from a ''fast follower'' to a ''first mover'' in AI. Korean startups are incredibly ambitious and well-funded, but many don''t have deep experience with frontier LLMs. They need someone who understands both the technology and the Korean business culture. I can bridge that gap - I''m a native Korean speaker, I''ve worked in Seoul''s startup ecosystem, and I have hands-on OpenAI API experience.');

    INSERT INTO public.qa_pairs (user_id, question, answer, question_type) VALUES
    (heejin_uuid, 'What''s unique about the Korean startup ecosystem?',
    'Three things. First, speed - Korean startups move incredibly fast, often faster than US counterparts. They expect rapid iteration. Second, hierarchy - even in startups, seniority matters. As a Solutions Architect, I need to communicate differently with a CEO versus an engineer. Third, community - Korean founders trust peer recommendations heavily. Building relationships in the ecosystem compounds quickly.');

    INSERT INTO public.qa_pairs (user_id, question, answer, question_type) VALUES
    (heejin_uuid, 'How would you handle language barriers with Korean customers?',
    'I''m a native Korean speaker, so language isn''t a barrier for me. But cultural translation matters too. Korean business culture is more formal and relationship-driven than US culture. I''d invest time building relationships before jumping into technical recommendations. I''d also translate OpenAI''s documentation and best practices into Korean where needed - many developers prefer Korean for learning.');

    INSERT INTO public.qa_pairs (user_id, question, answer, question_type) VALUES
    (heejin_uuid, 'What Korean companies do you think would benefit most from OpenAI''s platform?',
    'I see three categories. First, B2B SaaS companies adding AI features - HR tech, customer support, legal tech. Second, content companies - Naver, Kakao, entertainment companies could use GPT for content generation. Third, healthcare and education startups - Korea has strong digital health and edtech sectors, and they''re underserved by AI solutions. I''d prioritize companies with distribution and funding.');

    INSERT INTO public.qa_pairs (user_id, question, answer, question_type) VALUES
    (heejin_uuid, 'How would you build trust with Korean founders who are skeptical of US tech companies?',
    'I''d emphasize that I''m Korean and I understand their concerns - data sovereignty, latency, pricing. Then I''d show concrete value quickly - a working prototype in their first meeting. Trust in Korea is built through results and relationships, not sales pitches. I''d also connect them with other successful Korean OpenAI customers - social proof is powerful in Korea.');

    INSERT INTO public.qa_pairs (user_id, question, answer, question_type) VALUES
    (heejin_uuid, 'What are the biggest technical challenges for Korean language processing with LLMs?',
    'Two main issues. First, tokenization - Korean text tokenizes less efficiently than English, so costs are higher per character. I''d help Korean customers optimize prompts to reduce tokens. Second, cultural context - idioms, honorifics, and cultural references don''t always translate well. I''d recommend prompt engineering techniques that preserve Korean cultural nuance rather than forcing English mental models.');

    -- ========================================
    -- CATEGORY 8: BIRTH2DEATH
    -- ========================================

    INSERT INTO public.qa_pairs (user_id, question, answer, question_type) VALUES
    (heejin_uuid, 'Tell me more about Birth2Death.',
    'Birth2Death is a mental health journaling platform built entirely on OpenAI''s API. My co-founder Kush and I built it to help people process difficult emotions through AI-assisted journaling. The technical challenge was making it cost-effective and safe - hence the model routing, semantic caching, and crisis detection architecture. The code is on GitHub at github.com/JO-HEEJIN/birth2death-backend.');

    INSERT INTO public.qa_pairs (user_id, question, answer, question_type) VALUES
    (heejin_uuid, 'How many users does Birth2Death have right now?',
    'Birth2Death hasn''t launched publicly. We''ve built the full architecture - the backend is production-ready, we have the iOS app built - but we''re in beta testing with about 20 users (friends and early supporters). The 1,000+ user metrics on my resume were design targets, not actual users. That''s the mistake I''m addressing upfront.');

    INSERT INTO public.qa_pairs (user_id, question, answer, question_type) VALUES
    (heejin_uuid, 'Why haven''t you launched Birth2Death yet?',
    'Two reasons. First, mental health is high-stakes - we wanted to get the safety features absolutely right before public launch. Crisis detection, appropriate boundaries, ethical guardrails. Second, funding - as a bootstrapped startup, we''re being deliberate about launch timing. We''d rather launch with proper support infrastructure than rush and handle a crisis poorly.');

    INSERT INTO public.qa_pairs (user_id, question, answer, question_type) VALUES
    (heejin_uuid, 'What platform is Birth2Death built for?',
    'We''re launching on iOS first. The initial plan was visionOS (Apple Vision Pro) because spatial computing felt natural for introspective journaling, but we pivoted to iOS for broader reach. The backend is platform-agnostic - FastAPI with OpenAI API - so we can expand to other platforms later.');

    INSERT INTO public.qa_pairs (user_id, question, answer, question_type) VALUES
    (heejin_uuid, 'Are you working on Birth2Death full-time?',
    'Not currently. My co-founder Kush and I are both exploring other opportunities while keeping Birth2Death as a side project. The technical infrastructure is complete and validated - we''re at the stage where the next step is either raise funding for proper launch or keep it as a side project. If I join OpenAI, I''d bring all the lessons learned from building it.');

    -- ========================================
    -- CATEGORY 9: FUTURE PLANS
    -- ========================================

    INSERT INTO public.qa_pairs (user_id, question, answer, question_type) VALUES
    (heejin_uuid, 'Where do you see yourself in 5 years?',
    'I see myself as a senior Solutions Architect or SA team lead at OpenAI, having helped dozens of Korean startups build successful AI products. I want to be the person Korean founders call when they''re stuck on a hard technical problem. Longer term, I''d love to contribute to OpenAI''s developer education - creating documentation, tutorials, and best practices for the Korean market.');

    INSERT INTO public.qa_pairs (user_id, question, answer, question_type) VALUES
    (heejin_uuid, 'What would you do in your first 30 days at OpenAI?',
    'First 2 weeks: Learn OpenAI''s internal tools, processes, and product roadmap. Shadow senior Solutions Architects on customer calls. Second 2 weeks: Take on my first customers - probably smaller startups where I can make quick impact. Final 2 weeks: Build relationships in the Korean startup ecosystem - attend meetups, reach out to accelerators, start building my network. By day 30, I want to have helped at least 3 customers ship something.');

    INSERT INTO public.qa_pairs (user_id, question, answer, question_type) VALUES
    (heejin_uuid, 'What type of customers would you want to work with?',
    'Early-stage startups that are technical and ambitious. I''m most valuable when they''re trying to push the boundaries - complex use cases, novel applications, technical challenges. I''d also love to work with companies in healthcare, education, or mental health - areas where AI can have real social impact. But honestly, I''d work with any customer who''s excited about building great products.');

    INSERT INTO public.qa_pairs (user_id, question, answer, question_type) VALUES
    (heejin_uuid, 'How would you contribute to OpenAI beyond customer work?',
    'I''d want to contribute to three areas. First, developer documentation - I''d write guides, tutorials, and case studies for the Korean market. Second, product feedback - I''d synthesize customer pain points and feature requests and feed them to the product team. Third, community building - I''d help build the Korean OpenAI developer community through meetups, workshops, and online content.');

    INSERT INTO public.qa_pairs (user_id, question, answer, question_type) VALUES
    (heejin_uuid, 'What''s one thing you''d change about OpenAI''s platform if you could?',
    'I''d add more granular cost controls and budgeting features. As a founder, I want to set a hard cap on API spending per user or per day and get alerted before I hit it. Right now, it''s too easy to accidentally spend $1000 on a bug. Better cost visibility and controls would make OpenAI more accessible to bootstrapped startups who are cost-conscious.');

    -- ========================================
    -- CATEGORY 10: EDGE CASES / DIFFICULT
    -- ========================================

    INSERT INTO public.qa_pairs (user_id, question, answer, question_type) VALUES
    (heejin_uuid, 'What if a customer asks you to help them build a competitor to OpenAI?',
    'I''d be transparent - ''I can''t help you build a direct OpenAI competitor since I work here. But if you''re building a product that uses LLMs and could use multiple providers, I can still help you integrate OpenAI as one of your options.'' I''d set clear boundaries while still being helpful where appropriate.');

    INSERT INTO public.qa_pairs (user_id, question, answer, question_type) VALUES
    (heejin_uuid, 'A customer is unhappy with GPT-4''s performance on their use case. What do you do?',
    'I''d first understand what ''unhappy'' means - is it accuracy, cost, latency? Then I''d debug - can I see their prompts? Their eval set? Their expected vs actual outputs? Often the issue is prompt engineering or evaluation methodology. If it''s genuinely a model limitation, I''d either help them work around it (fine-tuning, RAG, ensemble approaches) or escalate to the research team for feedback.');

    INSERT INTO public.qa_pairs (user_id, question, answer, question_type) VALUES
    (heejin_uuid, 'How would you handle a customer who''s aggressive or rude on a call?',
    'I''d stay professional and try to understand what''s driving the frustration - usually it''s a technical blocker causing business pain. I''d say ''I hear you''re frustrated. Let''s focus on solving the problem. What specifically isn''t working?'' If they continue being abusive, I''d politely end the call and escalate to my manager. My job is to help customers, not to accept abuse.');

    INSERT INTO public.qa_pairs (user_id, question, answer, question_type) VALUES
    (heejin_uuid, 'What would you do if you accidentally shared confidential customer information with another customer?',
    'I''d immediately notify both customers, apologize, and notify my manager and legal team. I''d be completely transparent about what was shared and what the impact could be. Then I''d work with our security team to ensure it doesn''t happen again - better access controls, clearer protocols. Mistakes happen, but how you handle them defines your integrity.');

    INSERT INTO public.qa_pairs (user_id, question, answer, question_type) VALUES
    (heejin_uuid, 'A customer wants a feature that OpenAI doesn''t offer and won''t build. What do you say?',
    'I''d empathize - ''I understand why you''d want that.'' Then I''d offer alternatives - ''While we don''t offer that directly, here are three ways to achieve similar functionality.'' I''d also document the request and share it with the product team. Even if we can''t build every feature, hearing what customers need helps prioritize the roadmap.');

    INSERT INTO public.qa_pairs (user_id, question, answer, question_type) VALUES
    (heejin_uuid, 'How would you handle a situation where your technical recommendation conflicts with your sales team''s promises?',
    'I''d first talk to the sales rep privately to understand what was promised and why. Often there''s a miscommunication. Then I''d talk to the customer and clarify - ''Here''s what''s technically feasible, here''s the timeline, here''s the complexity.'' If sales promised something unrealistic, I''d work with them to set proper expectations with the customer. Technical credibility is more important than a short-term sales win.');

    INSERT INTO public.qa_pairs (user_id, question, answer, question_type) VALUES
    (heejin_uuid, 'What if you realize mid-call that you gave a customer wrong technical advice?',
    'I''d immediately correct it - ''Actually, I need to revise what I said earlier. I was wrong about X, the correct answer is Y.'' Then I''d explain why I was wrong and what the right approach is. Customers respect someone who admits mistakes quickly more than someone who doubles down on being wrong. Then I''d document it so I don''t make the same mistake again.');

    INSERT INTO public.qa_pairs (user_id, question, answer, question_type) VALUES
    (heejin_uuid, 'A customer asks about OpenAI''s future product roadmap. What do you share?',
    'I''d only share what''s publicly announced. If they''re asking about unannounced features, I''d say ''I can''t comment on future plans, but I can help you solve your problem with what''s available today.'' If they''re a strategic customer and there''s an NDA in place, I might be able to share more, but I''d check with product leadership first.');

    RAISE NOTICE 'Inserted 27 Q&A pairs - Categories 7-10';
    RAISE NOTICE 'Total Q&A pairs for OpenAI interview: 68';
END $$;
