-- Update Q&A answers to be more conversational and natural
-- This makes answers sound like real speech, not formal writing

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

    -- Update key answers to conversational style

    -- 1. Tell me about yourself
    UPDATE public.qa_pairs
    SET answer = 'I''m Heejin Jo, and I''ve been building AI systems for startups—most recently as the founder of Birth2Death, a mental health platform that serves over 1,000 users. I''ve worked extensively with OpenAI''s platform, and honestly, I''ve faced every challenge your startup customers deal with—cutting LLM costs by 80%, getting latency down to under a second, all that stuff. That hands-on experience is what I''d bring to this role.'
    WHERE user_id = heejin_uuid AND question = 'Tell me about yourself';

    -- 2. Why OpenAI specifically?
    UPDATE public.qa_pairs
    SET answer = 'Honestly, it''s about mission alignment. I''ve spent years building AI for vulnerable users—mental health, healthcare—where you can''t mess around with safety. OpenAI is one of the few companies that actually takes this seriously, not just in marketing but in how you build and deploy systems. Plus, I''m already your customer—I know the platform inside out. That matters to me.'
    WHERE user_id = heejin_uuid AND question = 'Why OpenAI specifically?';

    -- 3. Cost optimization challenge
    UPDATE public.qa_pairs
    SET answer = 'So at Birth2Death, we hit this point where we were burning 45 cents per user on LLMs. We just couldn''t scale like that. What I did was build a routing system—GPT-4 for the really complex emotional stuff, maybe 20% of conversations, and GPT-3.5 for everything else. Added some caching, optimized prompts. End result? Cut costs from 45 cents to 9 cents. That bought us six more months of runway.'
    WHERE user_id = heejin_uuid AND question = 'Tell me about a complex technical challenge you solved';

    -- 4. Why Solutions Architect role?
    UPDATE public.qa_pairs
    SET answer = 'I''ve learned that great technology isn''t enough—you need to understand customer problems deeply and translate between tech possibilities and business outcomes. I''ve been on both sides: as a founder needing guidance, and as an engineer building solutions. I know what Korean startups need because I was one of them, and I can help them build what actually works.'
    WHERE user_id = heejin_uuid AND question = 'Why Solutions Architect role?';

    -- 5. Tell me about Birth2Death
    UPDATE public.qa_pairs
    SET answer = 'It''s a mental health AI platform I founded that serves over 1,000 users across Europe and Korea. Built entirely on OpenAI''s API—GPT-4 for complex conversations, fine-tuned models for routine stuff. I''ve solved the hard production challenges: cut costs by 80% through smart routing, got P95 latency under a second with caching, maintained 99.9% uptime. This hands-on experience means I can help your customers avoid the pitfalls I''ve already dealt with.'
    WHERE user_id = heejin_uuid AND question = 'Tell me about Birth2Death';

    -- 6. Korean market trends
    UPDATE public.qa_pairs
    SET answer = 'So here''s what I''m seeing in Korea—startups are getting way more specialized. They expect GPT-level quality as a baseline, but they need domain-specific accuracy. Take WERT INTELLIGENCE. They tried using GPT for patent search, but it kept hallucinating patent numbers. So they built their own model. That''s the risk for OpenAI in Korea—startups will prototype with you, but if they hit accuracy or cost walls, they''ll go build their own. Our job is to keep them in the ecosystem by showing them fine-tuning, RAG, hybrid approaches.'
    WHERE user_id = heejin_uuid AND question = 'What trends do you see in the Korean AI startup ecosystem that OpenAI should be aware of?';

    -- 7. Why leave startup?
    UPDATE public.qa_pairs
    SET answer = 'I''m not leaving the mission behind—I''m scaling my impact. As a solo founder, I can help 1,000 users. As an SA, I can help dozens of startups who each serve millions. Founders trust me because I speak their language. When they say "we have 2 weeks of runway," I don''t give them a textbook answer—I give them a survival strategy because I''ve been there.'
    WHERE user_id = heejin_uuid AND question = 'Why are you leaving your startup?';

    -- 8. Handle ambiguity
    UPDATE public.qa_pairs
    SET answer = 'I actually like it. Startups are messy by nature, right? My approach is basically: build something fast, get it in front of users, see what breaks. At Birth2Death, I could''ve spent six months planning, but I just shipped an MVP in two weeks instead. Learned way more from real users than I ever would''ve from planning.'
    WHERE user_id = heejin_uuid AND question = 'How do you handle ambiguity?';

    -- 9. Tell me about a failure
    UPDATE public.qa_pairs
    SET answer = 'Yeah, so I built this feature I was really excited about, and literally no one used it. That hurt. I had to go talk to users and figure out what happened. Turns out I was solving the problem I thought they had, not the one they actually had. So I rebuilt it based on real feedback, and adoption went way up. Now I always start with user pain, not my assumptions.'
    WHERE user_id = heejin_uuid AND question = 'Tell me about a failure';

    -- 10. Time you disagreed
    UPDATE public.qa_pairs
    SET answer = 'So a founder wanted this complex agent system, and I thought a simpler workflow would be way better. Instead of arguing, I just showed them the numbers—cost, latency, failure rates. They saw it clearly and chose the simpler approach. Shipped way faster that way.'
    WHERE user_id = heejin_uuid AND question = 'Tell me about a time you disagreed with someone';

    -- 11. Time you moved fast
    UPDATE public.qa_pairs
    SET answer = 'I built a full NASA award-winning AI platform in 48 hours—web app, mobile AR, satellite data integration, decision agent, all of it. This rapid prototyping ability is exactly what startups need when they''re trying to validate ideas quickly. I love fast cycles.'
    WHERE user_id = heejin_uuid AND question = 'Tell me about a time you moved fast';

    -- 12. Why not stay an engineer?
    UPDATE public.qa_pairs
    SET answer = 'I love engineering, but I get way more energy from helping multiple teams succeed at once. As an SA, I can multiply my impact. Instead of building one product, I can help dozens of startups ship better products.'
    WHERE user_id = heejin_uuid AND question = 'Why not just stay an engineer?';

    -- 13. Customer prefers Claude
    UPDATE public.qa_pairs
    SET answer = 'I stay objective. I''d acknowledge Claude''s strengths, then guide them toward architecture principles: safety, tool use, consistency, ecosystem maturity, latency, cost tradeoffs. My job isn''t to defend a model—it''s to help them design a system where OpenAI delivers the most value.'
    WHERE user_id = heejin_uuid AND question = 'What if a customer says Claude or Gemini is better?';

    -- 14. Use competitors' models?
    UPDATE public.qa_pairs
    SET answer = 'Yes, I do. I actively test Claude, Gemini, open-source models. That actually helps me understand where OpenAI fits best. As an SA, my job isn''t blind loyalty—it''s helping customers succeed. That requires honesty and system-level thinking.'
    WHERE user_id = heejin_uuid AND question = 'Do you personally use competitors'' models?';

    -- 15. Biggest criticism of OpenAI
    UPDATE public.qa_pairs
    SET answer = 'One challenge is expectation management. Some users think LLMs should be perfect out of the box. I see a big opportunity for better guidance around system design, safety, and evaluation—and that''s exactly where SAs can help.'
    WHERE user_id = heejin_uuid AND question = 'What is your biggest criticism of OpenAI today?';

    -- 16. Working with startup customers
    UPDATE public.qa_pairs
    SET answer = 'I focus on understanding their constraints—limited resources, changing priorities, need for speed. I worked with early-stage companies where requirements shifted constantly. Adopted a prototype-first approach, shipping MVPs in 2 weeks instead of lengthy planning. The key is being flexible while maintaining quality.'
    WHERE user_id = heejin_uuid AND question = 'How do you work with startup customers?';

    -- 17. Why OpenAI over competitors
    UPDATE public.qa_pairs
    SET answer = 'All these companies are doing great work, but OpenAI is where mission and scale meet. My work has always focused on human well-being and responsible deployment, and OpenAI is uniquely committed to studying and improving those aspects, not just pushing benchmarks. Plus, OpenAI''s impact on real developers and startups is unmatched—that''s where I can contribute most.'
    WHERE user_id = heejin_uuid AND question = 'Why OpenAI over Anthropic, Google, or other AI companies?';

    -- 18. Why not continue as founder
    UPDATE public.qa_pairs
    SET answer = 'I still think like a founder, but I want to create impact at a way larger scale. At OpenAI, the tools I help build could reach millions of users, not just thousands. As an SA, I can help dozens of startups avoid the mistakes I made and accelerate their growth.'
    WHERE user_id = heejin_uuid AND question = 'Why not continue as a founder?';

    -- 19. Handle founder who is wrong
    UPDATE public.qa_pairs
    SET answer = 'I don''t say "you''re wrong." I ask questions, show tradeoffs, let data speak. Founders respect clarity, not ego.'
    WHERE user_id = heejin_uuid AND question = 'How do you handle a founder who is wrong but very confident?';

    -- 20. First 90 days
    UPDATE public.qa_pairs
    SET answer = 'Listen first. Learn from customers, sales, existing SAs. Then start codifying patterns and sharing them.'
    WHERE user_id = heejin_uuid AND question = 'What would you do in your first 90 days?';

    RAISE NOTICE 'Updated 20 key answers to conversational style';
END $$;

-- Verify update
SELECT question, LEFT(answer, 100) as answer_preview
FROM qa_pairs
WHERE user_id = (SELECT id FROM auth.users WHERE email = 'midmost44@gmail.com')
AND question IN (
    'Tell me about yourself',
    'Why OpenAI specifically?',
    'Tell me about a complex technical challenge you solved'
)
ORDER BY question;
