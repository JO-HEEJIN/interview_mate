-- Insert Q&A pairs for heejin user
-- Interview preparation data for OpenAI Solutions Architect position

-- Note: Replace 'USER_ID_HERE' with actual heejin user UUID from profiles table

INSERT INTO public.qa_pairs (user_id, question, answer, question_type, source) VALUES

-- Self Introduction & Background
('heejin', 'Tell me about yourself',
'I am Heejin Jo, a startup founder and AI engineer who has built production applications on OpenAI''s platform. I founded Birth2Death, a mental health AI platform serving 1,000+ users using GPT-4 and fine-tuned models. I have navigated every challenge your startup customers face - from cutting LLM costs by 80% to achieving sub-second latency. As a native Korean with deep ties to Seoul''s startup ecosystem, I am uniquely positioned to help Korean founders succeed with OpenAI''s technology.',
'general', 'manual'),

-- Why OpenAI
('heejin', 'Why OpenAI specifically?',
'Three reasons: First, I am already your customer - I have built on your platform and know its strengths firsthand. Second, I deeply respect OpenAI''s research on AI safety, specifically HealthBench and Affective Use studies. As someone building mental health AI, I align with OpenAI''s philosophy that safety is a core product feature, not an afterthought. Third, I want to help shape Korea''s AI future by bringing OpenAI''s best practices to Korean startups who need this technology most.',
'general', 'manual'),

-- Why Solutions Architect
('heejin', 'Why Solutions Architect role?',
'As a founder, I have learned that great technology is not enough - you need to understand customer problems deeply and translate between technical possibilities and business outcomes. I have been on both sides: as a startup founder needing guidance, and as an engineer building solutions. I know what Korean startups need because I was one of them, and I can help them build what actually works.',
'general', 'manual'),

-- Technical Challenge - Cost Optimization
('heejin', 'Tell me about a complex technical challenge you solved',
'Cost vs. Quality Optimization for my startup. Problem: GPT-4 was costing $0.45 per user, which was unsustainable for our Wyoming-based LLC. Solution: I built a Model Routing System routing 80% of routine queries to GPT-3.5 Turbo and complex 20% to GPT-4. I also implemented semantic caching with embeddings. Result: Reduced costs by 80% to $0.09 per user while maintaining 99.9% uptime and sub-second latency. I do not just advise on these tradeoffs - I have lived them.',
'technical', 'manual'),

-- Birth2Death Project
('heejin', 'Tell me about Birth2Death',
'It is a mental health AI platform I founded that serves 1,000+ users across Europe and Korea. Built entirely on OpenAI''s API, it uses GPT-4 for complex conversations and fine-tuned Llama3 for routine queries. I have solved key production challenges: cutting costs from $0.45 to $0.09 per user through model routing, achieving sub-second P95 latency with caching strategies, and maintaining 99.9% uptime. This hands-on experience with your platform means I can help your customers avoid the pitfalls I have already overcome.',
'technical', 'manual'),

-- Korea Market Insight
('heejin', 'Why Seoul? What is your view on the Korean market?',
'Korea is at a turning point. We are moving from a Fast Follower to a First Mover aiming to become a G3 AI powerhouse alongside the US and China. We already dominate the hardware side with HBM (High Bandwidth Memory), but now there is a massive national push for Sovereign AI - building independent, competitive AI capabilities. However, Korean startups often struggle to apply these global LLMs to local vertical problems. I want to be the bridge. I can help Korean founders leverage OpenAI''s platform to build world-class applications that support this national ambition.',
'general', 'manual'),

-- Unique Value Proposition
('heejin', 'What is something unique you bring to this role?',
'I am not just an advisor - I am a founder who has built production AI systems on your platform. I have reduced LLM costs by 80%, optimized RAG pipelines for sub-second latency, and scaled to 1,000+ users while maintaining 99.9% uptime. I can prototype alongside customers, not just advise, because I have solved these exact problems in production.',
'behavioral', 'manual'),

-- Why Leave Startup
('heejin', 'Why are you leaving your startup?',
'I am not leaving my passion behind - I am scaling my impact. As a solo founder, I can help 1,000 users. As a Solutions Architect, I can help 100 startups who each serve millions. Founders trust me because I speak their language. When they say we have 2 weeks of runway and need to ship MVP, I do not give them a textbook answer. I give them a survival strategy because I have been there. That empathy is my unique edge.',
'behavioral', 'manual'),

-- Handling Ambiguity
('heejin', 'How do you handle ambiguity?',
'I thrive in it. Startups are ambiguous by nature. My approach is: prototype fast, gather feedback, iterate. For example, with Birth2Death, I did not spend 6 months planning - I shipped an MVP in 2 weeks and learned from real users. That is how I would work with startup customers too - moving quickly from idea to working prototype to production.',
'behavioral', 'manual'),

-- Fast Execution
('heejin', 'Tell me about a time you moved fast',
'I built a full NASA award-winning AI agent platform in 48 hours - web app, mobile AR, satellite data integration, and decision agent. This rapid prototyping ability is exactly what startups need when they are trying to validate ideas quickly. I enjoy fast cycles and helping founders move from concept to working prototype.',
'behavioral', 'manual'),

-- Working with Customers
('heejin', 'What is your philosophy for working with customers?',
'I listen first. I ask questions. I never assume. My role is to understand their real needs and guide them to a solution that is simple, safe, and scalable. I do not just advise - I prototype alongside them, debug their code, and help them make the tough tradeoffs between cost, quality, and speed.',
'behavioral', 'manual'),

-- Ecosystem Knowledge
('heejin', 'How are you connected to the startup ecosystem in Korea?',
'I am deeply connected both as a builder and someone who understands Korea''s innovation system. I have launched products in Korea, worked with local businesses at GetNShow, and participated in programs like 예창패. I understand how funding flows through organizations like 신보 and 기보, and I am following Korea''s AI strategy initiatives like 초격차 스타트업 1000+. This ecosystem knowledge, combined with my technical depth, allows me to help Korean founders navigate both technical and business challenges.',
'general', 'manual'),

-- Why Founders Trust You
('heejin', 'Why do founders trust you?',
'Because I understand their reality. I have bootstrapped products, worked with small businesses, and dealt with all the constraints myself. Founders do not need a model - they need a partner who can help them make tough tradeoffs between cost and quality, speed and perfection. I can be that partner because I have lived their journey.',
'behavioral', 'manual'),

-- Staying Updated
('heejin', 'How do you stay updated with LLM trends?',
'I regularly implement new models, read papers, build prototypes, and deploy real systems. For me, learning is not just reading - it is shipping. I have worked with GPT-4, fine-tuned Llama3, implemented RAG pipelines, and deployed on-device models - staying current by actually building with these technologies.',
'technical', 'manual'),

-- Use Case Identification
('heejin', 'How would you help a startup identify use cases?',
'I always start with problem decomposition. Instead of asking What do you want to build I ask: What takes your team the most time? What decisions require expertise? Where do users feel the most friction? Then I map these to automation, agent workflows, and retrieval systems that deliver real business value.',
'technical', 'manual'),

-- Handling Competitor Comparisons
('heejin', 'How would you handle a customer who compares OpenAI unfavorably to competitors?',
'I stay honest and constructive. I acknowledge the strengths of other models, and then show customers how to design a system where OpenAI brings unique value - for example: agent workflows, tool usage, safety, consistency, or ecosystem maturity. I help them choose the right architecture for their product, where OpenAI becomes a core component.',
'situational', 'manual'),

-- Availability
('heejin', 'What is your availability?',
'I can relocate to Seoul within 2-4 weeks. Birth2Death is stable with operational processes in place, so I am ready to move quickly and start contributing immediately.',
'general', 'manual'),

-- What Excites You
('heejin', 'What excites you about working with startups?',
'Startups move fast, and I do too. I have built complete products alone - backend, frontend, mobile, AI, deployment - so I understand the pressure and speed they need. I want to help founders turn ideas into working products as quickly and safely as possible, helping them avoid the technical pitfalls I have already overcome.',
'behavioral', 'manual');
