-- Setup complete profile for Heejin Jo (midmost44@gmail.com)
-- This script will:
-- 1. Add unique constraint on email (if not exists)
-- 2. Create profile
-- 3. Add STAR story
-- 4. Add Q&A pairs

-- Step 1: Add unique constraint on email if it doesn't exist
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'profiles_email_key'
    ) THEN
        ALTER TABLE public.profiles ADD CONSTRAINT profiles_email_key UNIQUE (email);
    END IF;
END $$;

-- Step 2: Get or create profile for existing auth user
DO $$
DECLARE
    heejin_uuid UUID;
    auth_user_id UUID;
BEGIN
    -- First, check if user exists in auth.users
    SELECT id INTO auth_user_id
    FROM auth.users
    WHERE email = 'midmost44@gmail.com';

    -- If no auth user exists, raise an error
    IF auth_user_id IS NULL THEN
        RAISE EXCEPTION 'No authenticated user found with email midmost44@gmail.com. Please sign up first.';
    END IF;

    -- Check if profile exists, if not create it
    SELECT id INTO heejin_uuid
    FROM public.profiles
    WHERE id = auth_user_id;

    IF heejin_uuid IS NULL THEN
        -- Create profile using the auth user's ID
        INSERT INTO public.profiles (id, email, full_name)
        VALUES (auth_user_id, 'midmost44@gmail.com', 'Heejin Jo')
        RETURNING id INTO heejin_uuid;
    ELSE
        -- Update existing profile
        UPDATE public.profiles
        SET full_name = 'Heejin Jo'
        WHERE id = auth_user_id;
        heejin_uuid := auth_user_id;
    END IF;

    -- Delete old data with 'heejin' string (if any)
    DELETE FROM public.star_stories WHERE user_id::text = 'heejin';
    DELETE FROM public.qa_pairs WHERE user_id::text = 'heejin';

    -- Insert STAR Stories (8 stories)
    INSERT INTO public.star_stories (user_id, title, situation, task, action, result, tags) VALUES

    (heejin_uuid,
     'LLM Cost Optimization - 80% Reduction at Birth2Death',
     'Birth2Death LLM costs were unsustainable at $0.45 per user. We could not scale the business.',
     'Cut costs by at least 60% without degrading quality of AI responses for mental health conversations.',
     'Implemented intelligent model routing - GPT-4 for 20% complex emotional conversations, GPT-3.5 Turbo for 80% routine. Added semantic caching and optimized prompts to reduce token usage.',
     'Cut costs from $0.45 to $0.09 per user (80% reduction) while maintaining 4.2/5 satisfaction. Extended runway by 6 months.',
     ARRAY['cost-optimization', 'LLM', 'startup', 'production']),

    (heejin_uuid,
     'P95 Latency Reduction from 3s to under 1s',
     'Birth2Death P95 latency was 3+ seconds causing poor user experience. Users were abandoning conversations.',
     'Reduce latency to under 1 second while maintaining response quality.',
     'Implemented Redis caching for common queries, prompt compression to reduce tokens, async processing with Celery for heavy tasks, and connection pooling with pgbouncer.',
     'Achieved under 1s P95 latency. User retention improved significantly. System handles 120K daily requests at peak.',
     ARRAY['latency', 'performance', 'infrastructure', 'production']),

    (heejin_uuid,
     'NASA Space Apps - Award-Winning AI in 48 Hours',
     'NASA Space Apps Challenge 2025. Had 48 hours to build something from scratch.',
     'Build a complete AI application that solves a real problem using NASA data.',
     'Built agricultural AI agent with real-time NASA satellite data integration (SMAP, MODIS, Landsat). Created web app with React/Next.js and mobile AR with React Native.',
     'Won Local Impact Award. Proved ability to go from concept to working demo in 48 hours.',
     ARRAY['rapid-prototyping', 'hackathon', 'AI-agent', 'full-stack']),

    (heejin_uuid,
     'Multi-Agent AI System for Business Operations',
     'Cafe owners needed help with complex operations - sales analysis, inventory, customer service.',
     'Build an AI system that could handle multiple business functions and drive real decisions.',
     'Built multi-agent system using GPT-4: sales analysis agent, inventory management agent, customer service agent. Created mobile app for managers.',
     '25% inventory waste reduction. 40% faster customer response time. Cafe owners using daily.',
     ARRAY['multi-agent', 'business-operations', 'GPT-4', 'production']),

    (heejin_uuid,
     'Database Query Optimization - 10x Improvement',
     'Query to fetch user conversations was taking 500ms. Table had 10M rows with no proper indexing.',
     'Reduce query time significantly without major architecture changes.',
     'Added composite index on (user_id, updated_at DESC). Implemented materialized view for top 20 conversations per user.',
     'Query time dropped from 500ms to 50ms. 4x reduction in database CPU usage.',
     ARRAY['database', 'optimization', 'PostgreSQL', 'performance']),

    (heejin_uuid,
     'Thriving in Startup Ambiguity',
     'At Birth2Death, requirements were constantly changing. No clear roadmap. Limited resources.',
     'Ship product despite uncertainty and constraints.',
     'Adopted prototype-first approach. Shipped MVP in 2 weeks instead of 6-month planning. Gathered real user feedback.',
     'Launched to 1000+ users. 68% D7 retention. Microsoft Imagine Cup 2026 acceptance.',
     ARRAY['ambiguity', 'startup', 'MVP', 'iteration']),

    (heejin_uuid,
     'Resolving Technical Disagreement Constructively',
     'Disagreed with team lead about technology choice for a critical system.',
     'Voice concerns without being dismissive while finding best solution.',
     'Prepared document with trade-offs analysis. Presented alternatives with data. Suggested prototyping both approaches.',
     'Ended up with hybrid solution better than either original proposal.',
     ARRAY['collaboration', 'conflict-resolution', 'leadership']),

    (heejin_uuid,
     'Privacy-First LLM in Healthcare at Lime Friends',
     'Healthcare chatbot needed to handle sensitive patient data. Could not use external APIs due to privacy.',
     'Build production-quality NLP system without relying on cloud LLM APIs.',
     'Deployed on-premise LLM. Built custom NLP pipeline achieving 90% intent classification accuracy.',
     'Handled 100K+ daily requests. Maintained compliance with healthcare regulations.',
     ARRAY['healthcare', 'privacy', 'on-premise', 'compliance']);

    -- Insert Q&A Pairs (Interview Preparation)
    INSERT INTO public.qa_pairs (user_id, question, answer, question_type, source) VALUES

    (heejin_uuid, 'Tell me about yourself',
    'I am Heejin Jo, a startup founder and AI engineer who has built production applications on OpenAI''s platform. I founded Birth2Death, a mental health AI platform serving 1,000+ users using GPT-4 and fine-tuned models. I have navigated every challenge your startup customers face - from cutting LLM costs by 80% to achieving sub-second latency. As a native Korean with deep ties to Seoul''s startup ecosystem, I am uniquely positioned to help Korean founders succeed with OpenAI''s technology.',
    'general', 'manual'),

    (heejin_uuid, 'Why OpenAI specifically?',
    'Three reasons: First, I am already your customer - I have built on your platform and know its strengths firsthand. Second, I deeply respect OpenAI''s research on AI safety, specifically HealthBench and Affective Use studies. As someone building mental health AI, I align with OpenAI''s philosophy that safety is a core product feature, not an afterthought. Third, I want to help shape Korea''s AI future by bringing OpenAI''s best practices to Korean startups who need this technology most.',
    'general', 'manual'),

    (heejin_uuid, 'Why Solutions Architect role?',
    'As a founder, I have learned that great technology is not enough - you need to understand customer problems deeply and translate between technical possibilities and business outcomes. I have been on both sides: as a startup founder needing guidance, and as an engineer building solutions. I know what Korean startups need because I was one of them, and I can help them build what actually works.',
    'general', 'manual'),

    (heejin_uuid, 'Tell me about a complex technical challenge you solved',
    'Cost vs. Quality Optimization for my startup. Problem: GPT-4 was costing $0.45 per user, which was unsustainable for our Wyoming-based LLC. Solution: I built a Model Routing System routing 80% of routine queries to GPT-3.5 Turbo and complex 20% to GPT-4. I also implemented semantic caching with embeddings. Result: Reduced costs by 80% to $0.09 per user while maintaining 99.9% uptime and sub-second latency. I do not just advise on these tradeoffs - I have lived them.',
    'technical', 'manual'),

    (heejin_uuid, 'Tell me about Birth2Death',
    'It is a mental health AI platform I founded that serves 1,000+ users across Europe and Korea. Built entirely on OpenAI''s API, it uses GPT-4 for complex conversations and fine-tuned Llama3 for routine queries. I have solved key production challenges: cutting costs from $0.45 to $0.09 per user through model routing, achieving sub-second P95 latency with caching strategies, and maintaining 99.9% uptime. This hands-on experience with your platform means I can help your customers avoid the pitfalls I have already overcome.',
    'technical', 'manual'),

    (heejin_uuid, 'Why Seoul? What is your view on the Korean market?',
    'Korea is at a turning point. We are moving from a Fast Follower to a First Mover aiming to become a G3 AI powerhouse alongside the US and China. We already dominate the hardware side with HBM (High Bandwidth Memory), but now there is a massive national push for Sovereign AI - building independent, competitive AI capabilities. However, Korean startups often struggle to apply these global LLMs to local vertical problems. I want to be the bridge. I can help Korean founders leverage OpenAI''s platform to build world-class applications that support this national ambition.',
    'general', 'manual'),

    (heejin_uuid, 'What is something unique you bring to this role?',
    'I am not just an advisor - I am a founder who has built production AI systems on your platform. I have reduced LLM costs by 80%, optimized RAG pipelines for sub-second latency, and scaled to 1,000+ users while maintaining 99.9% uptime. I can prototype alongside customers, not just advise, because I have solved these exact problems in production.',
    'behavioral', 'manual'),

    (heejin_uuid, 'Why are you leaving your startup?',
    'I am not leaving my passion behind - I am scaling my impact. As a solo founder, I can help 1,000 users. As a Solutions Architect, I can help 100 startups who each serve millions. Founders trust me because I speak their language. When they say we have 2 weeks of runway and need to ship MVP, I do not give them a textbook answer. I give them a survival strategy because I have been there. That empathy is my unique edge.',
    'behavioral', 'manual'),

    (heejin_uuid, 'How do you handle ambiguity?',
    'I thrive in it. Startups are ambiguous by nature. My approach is: prototype fast, gather feedback, iterate. For example, with Birth2Death, I did not spend 6 months planning - I shipped an MVP in 2 weeks and learned from real users. That is how I would work with startup customers too - moving quickly from idea to working prototype to production.',
    'behavioral', 'manual'),

    (heejin_uuid, 'Tell me about a time you moved fast',
    'I built a full NASA award-winning AI agent platform in 48 hours - web app, mobile AR, satellite data integration, and decision agent. This rapid prototyping ability is exactly what startups need when they are trying to validate ideas quickly. I enjoy fast cycles and helping founders move from concept to working prototype.',
    'behavioral', 'manual'),

    (heejin_uuid, 'What is your philosophy for working with customers?',
    'I listen first. I ask questions. I never assume. My role is to understand their real needs and guide them to a solution that is simple, safe, and scalable. I do not just advise - I prototype alongside them, debug their code, and help them make the tough tradeoffs between cost, quality, and speed.',
    'behavioral', 'manual'),

    (heejin_uuid, 'How are you connected to the startup ecosystem in Korea?',
    'I am deeply connected both as a builder and someone who understands Korea''s innovation system. I have launched products in Korea, worked with local businesses at GetNShow, and participated in programs like 예창패. I understand how funding flows through organizations like 신보 and 기보, and I am following Korea''s AI strategy initiatives like 초격차 스타트업 1000+. This ecosystem knowledge, combined with my technical depth, allows me to help Korean founders navigate both technical and business challenges.',
    'general', 'manual'),

    (heejin_uuid, 'Why do founders trust you?',
    'Because I understand their reality. I have bootstrapped products, worked with small businesses, and dealt with all the constraints myself. Founders do not need a model - they need a partner who can help them make tough tradeoffs between cost and quality, speed and perfection. I can be that partner because I have lived their journey.',
    'behavioral', 'manual'),

    (heejin_uuid, 'How do you stay updated with LLM trends?',
    'I regularly implement new models, read papers, build prototypes, and deploy real systems. For me, learning is not just reading - it is shipping. I have worked with GPT-4, fine-tuned Llama3, implemented RAG pipelines, and deployed on-device models - staying current by actually building with these technologies.',
    'technical', 'manual'),

    (heejin_uuid, 'How would you help a startup identify use cases?',
    'I always start with problem decomposition. Instead of asking What do you want to build I ask: What takes your team the most time? What decisions require expertise? Where do users feel the most friction? Then I map these to automation, agent workflows, and retrieval systems that deliver real business value.',
    'technical', 'manual'),

    (heejin_uuid, 'How would you handle a customer who compares OpenAI unfavorably to competitors?',
    'I stay honest and constructive. I acknowledge the strengths of other models, and then show customers how to design a system where OpenAI brings unique value - for example: agent workflows, tool usage, safety, consistency, or ecosystem maturity. I help them choose the right architecture for their product, where OpenAI becomes a core component.',
    'situational', 'manual'),

    (heejin_uuid, 'What is your availability?',
    'I can relocate to Seoul within 2-4 weeks. Birth2Death is stable with operational processes in place, so I am ready to move quickly and start contributing immediately.',
    'general', 'manual'),

    (heejin_uuid, 'What excites you about working with startups?',
    'Startups move fast, and I do too. I have built complete products alone - backend, frontend, mobile, AI, deployment - so I understand the pressure and speed they need. I want to help founders turn ideas into working products as quickly and safely as possible, helping them avoid the technical pitfalls I have already overcome.',
    'behavioral', 'manual'),

    (heejin_uuid, 'Can you share an example of removing a feature you wanted but wasn''t best for users?',
    'I was eager to implement a 3D AR feature in our mental health application to enhance user interaction. However, I realized this feature was too resource-heavy for older iOS devices, particularly those running iOS 16 or earlier. It would have excluded a portion of our user base who relied on those devices. Balancing inclusivity and performance, I made the decision to remove the 3D AR feature from the iOS version to ensure broader accessibility and a smoother user experience. We retained that feature for visionOS where it was more suitable. This decision exemplified my willingness to put user accessibility and product stability first, even if it meant stepping back from a feature I was personally excited about.',
    'behavioral', 'manual'),

    (heejin_uuid, 'Walk me through your model routing logic - which signals, where in pipeline, quality assurance?',
    'In our model routing strategy, about 80% of user queries were relatively repetitive or semantically similar - for example, common questions with similar intent. For these, I used semantic embeddings and a caching mechanism to recognize that the question had been effectively answered before. Thus, I routed these queries to GPT-3.5 Turbo or Llama3 without sacrificing quality. This allowed us to reduce costs significantly. For the remaining 20% of more complex or unique queries - such as those involving nuanced medical details - I routed them to GPT-4 to ensure we maintained high response quality. The criteria for routing were based on semantic similarity and complexity, and the logic was embedded in our preprocessing pipeline. This approach ensured that we balanced cost efficiency with maintaining quality of responses.',
    'technical', 'manual'),

    (heejin_uuid, 'Are you making clinical/diagnostic claims with your mental health AI? How does this affect design?',
    'Our platform does not make any clinical or diagnostic claims. We operate purely as an assistive layer. While we do use certain internal metrics - such as tracking user interaction patterns like hand movements or attention shifts - these are not presented as medical diagnoses. Instead, they are simply used to tailor the user experience or to offer supportive feedback. We ensure that our prompts and system messaging clearly state that we are providing guidance and not medical advice. This approach helps us avoid any liability issues and keeps our role strictly supportive rather than diagnostic.',
    'technical', 'manual'),

    (heejin_uuid, 'How would you handle a customer wanting to use an experimental OpenAI feature not ready for production?',
    'If a customer is interested in integrating a highly experimental feature that I believe is not mature enough for production, my approach is to set realistic expectations through clear and data-driven communication. I would explain that while the idea is innovative, the current stability and performance of that feature might not yet meet production standards. I would share relevant metrics or examples - such as explaining how a model like DeepSeek might handle a few queries well but may not be reliable at scale. Then I would suggest a phased approach: we could test it on a small scale initially, but for a consistent user experience, we should rely on more stable models like the GPT series or Claude. This way, the customer understands that we are aiming to balance innovation with reliability, ensuring a good user experience.',
    'situational', 'manual'),

    (heejin_uuid, 'How have you managed multiple high-priority projects simultaneously?',
    'When managing multiple high-priority projects, I use a structured approach to stay organized and ensure each project gets the attention it needs. First, I deconstruct each project into its core components and key priorities. By identifying the essential tasks and understanding the main objectives, I can create a clear structure and timeline for each one. Next, I prioritize these tasks based on deadlines and the impact on overall project goals. This allows me to allocate my time efficiently and ensure that each project progresses smoothly. I also use tools to track progress and maintain regular communication with stakeholders to keep everyone aligned. By breaking down complex projects into manageable parts and setting clear priorities, I can handle multiple projects simultaneously without compromising on quality or deadlines.',
    'behavioral', 'manual'),

    (heejin_uuid, 'How would you handle mid-project requirement changes while maintaining good customer relationships?',
    'When a customer changes their requirements mid-project, my priority is to maintain clear communication and adapt efficiently. First, I break down the new requirements into their core components and reassess the priorities. This helps me understand the main objectives of the pivot and create a revised timeline that aligns with the new goals. Next, I prioritize tasks based on deadlines and overall impact, ensuring that we stay on track and deliver quality results. I also maintain regular communication with the customer to manage expectations and ensure they are informed of any adjustments to the project scope or timeline. By structuring the new requirements into manageable parts and setting clear priorities, I can smoothly handle changes while keeping the project on course and preserving a positive client relationship.',
    'behavioral', 'manual'),

    (heejin_uuid, 'A Korean startup wants GPT-4 quality, GPT-3.5 cost, real-time responses in 3 weeks. What would you NOT let them build?',
    'In a scenario where a customer wants GPT-4-level quality, GPT-3.5-level cost, and real-time responses all within a very short timeframe, the first thing I would do is focus on education and realistic expectation-setting. Rather than outright saying no, I would explain the concept of model routing and the trade-offs involved. If they are unfamiliar, I would take a few minutes to help them understand what is feasible within the given constraints. By doing so, I can guide them toward a more realistic approach, such as starting with a phased implementation or adjusting certain expectations. This way, they understand the realistic possibilities without feeling dismissed, and we can find a balanced solution together.',
    'situational', 'manual'),

    (heejin_uuid, 'What excites you most about working with startups as a Solutions Architect?',
    'One of the aspects I am most excited about is aligning with OpenAI''s safety philosophy and helping startups understand the importance of ethical AI use. As someone who has worked in mental health AI, I deeply respect that OpenAI is not just focused on performance benchmarks, but also on measuring how AI impacts human well-being. I have closely followed research about ensuring AI is used for human benefit, and I think it is crucial to instill that mindset in the startups we work with. In introductory discussions, I would emphasize to founders that while we can help them leverage AI effectively, we also need to consider the ethical implications - like how to handle sensitive situations or protect users from potential harm. My background helps me connect with them on that level and guide them toward building not just innovative, but also responsible AI applications.',
    'general', 'manual'),

    (heejin_uuid, 'How do you explain complex AI concepts to non-technical stakeholders?',
    'When a request is complex or mixes multiple asks, I start by clarifying the objective, success criteria, and constraints such as deadlines, resources, and risks. I then decompose the work into manageable subtasks and set priorities based on time sensitivity and business impact. During execution, I maintain lightweight tracking and regular communication to keep alignment and visibility. This ensures that everyone stays on the same page regardless of their technical background.',
    'behavioral', 'manual'),

    (heejin_uuid, 'What trends do you see in the Korean AI startup ecosystem that OpenAI should be aware of?',
    'I see a critical trend emerging in Korea: startups are moving toward hyper-specialized, domain-specific AI that goes far beyond general document processing. They expect GPT-level capabilities as a baseline, but what they really need are models fine-tuned for their vertical. A great example is WERT INTELLIGENCE. They started with a patent search tool using GPT, but quickly hit a wall—the model hallucinated patent numbers and failed on domain-specific accuracy. So they pivoted to building their own model that not only searches patents but also identifies companies behind them, predicts their next research directions, and even generates new patent documents. This shift from OpenAI to custom models is the biggest risk for OpenAI Seoul. Korean startups will start with GPT for prototyping, but if they hit accuracy or cost issues at scale, they will build their own. Our job is to help them architect solutions where OpenAI remains the foundation—whether through fine-tuning, embeddings, or hybrid approaches—so they do not feel the need to leave the ecosystem entirely.',
    'general', 'manual'),

    (heejin_uuid, 'What is the biggest challenge or risk for OpenAI in the Korean market?',
    'The biggest risk is losing customers to in-house model development. Korean startups are highly technical and cost-conscious. They will prototype with GPT, but the moment they encounter hallucinations in domain-specific tasks or unsustainable costs at scale, they will consider building their own models. I have seen this firsthand with companies like WERT INTELLIGENCE, who moved from GPT to a custom patent model because GPT could not handle the precision required for patent numbers and legal language. To counter this, OpenAI Seoul needs to position itself not just as an API provider, but as a long-term partner. We need to show them how fine-tuning, RAG, and hybrid architectures can solve their problems while staying in the OpenAI ecosystem. If we can help them achieve domain-specific accuracy without leaving our platform, we keep them as customers. Otherwise, we risk becoming just a prototyping tool.',
    'general', 'manual');

    -- Show created UUID
    RAISE NOTICE 'Profile created with UUID: %', heejin_uuid;

END $$;

-- Verify the data was inserted
SELECT 'Profile created:' as status, id, email, full_name FROM profiles WHERE email = 'midmost44@gmail.com';
SELECT 'STAR stories count:' as status, COUNT(*) as count FROM star_stories WHERE user_id::uuid = (SELECT id FROM profiles WHERE email = 'midmost44@gmail.com');
SELECT 'Q&A pairs count:' as status, COUNT(*) as count FROM qa_pairs WHERE user_id::uuid = (SELECT id FROM profiles WHERE email = 'midmost44@gmail.com');
