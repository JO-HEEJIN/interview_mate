-- Migration: Add latest OpenAI updates Q&A pairs (Dec 2025)
-- Priority: High-impact questions for Solutions Architect interview
-- Date: 2025-12-18

-- Get user ID
DO $$
DECLARE
    v_user_id uuid;
BEGIN
    SELECT id INTO v_user_id FROM auth.users WHERE email = 'midmost44@gmail.com';

    IF v_user_id IS NULL THEN
        RAISE EXCEPTION 'User not found';
    END IF;

    -- Q1: Enterprise AI adoption trends
    INSERT INTO qa_pairs (user_id, question, answer, question_type, source, usage_count)
    VALUES (
        v_user_id,
        'What are the latest enterprise AI adoption trends you''re seeing?',
        'Based on OpenAI''s State of Enterprise AI 2025 report, we''re seeing explosive growth. Key metrics: 75% of workers report AI improved their output speed or quality, saving 40-60 minutes daily. Heavy users save 10+ hours per week. Weekly ChatGPT Enterprise messages increased 8x year-over-year, and reasoning token consumption rose 320x.

From a Solutions Architect perspective, this means customers are moving from experimentation to production at scale. The fastest-growing markets are Australia, Brazil, Netherlands, and France (140%+ YoY growth).

When I help customers, I focus on: (1) Identifying high-impact workflows where 40-60min savings compounds across teams, (2) Building hybrid architectures (o1 for complex reasoning, 4o for general tasks) to balance cost and performance, (3) Implementing prompt caching and semantic caching for 90%+ cost reduction at scale.',
        'behavioral',
        'manual',
        0
    );

    -- Q2: ChatGPT Apps ecosystem
    INSERT INTO qa_pairs (user_id, question, answer, question_type, source, usage_count)
    VALUES (
        v_user_id,
        'How would you help a startup build and distribute their AI product using OpenAI''s platform?',
        'I''d leverage OpenAI''s new ChatGPT Apps ecosystem, launched December 2025. Developers can now submit apps to reach 800 million weekly ChatGPT users through the app directory at chatgpt.com/apps.

Technical approach:
1. Use the Apps SDK (beta) built on Model Context Protocol (MCP) to create chat-native experiences
2. Integrate their service as a ChatGPT App with proper context and actions
3. Submit for review via OpenAI Developer Platform with MCP connectivity details, testing guidelines, and directory metadata
4. Ensure compliance with safety, privacy, and transparency guidelines

Business value: Instead of building from scratch, startups get instant distribution to 800M users. This is like the App Store moment for AI applications.

From my experience building Interview Mate with real-time transcription and answer generation, I understand the full stack from API integration to user experience. I''d help them architect the MCP integration, optimize for low latency, and design the submission for maximum discoverability.',
        'technical',
        'manual',
        0
    );

    -- Q3: Realtime API for production use cases
    INSERT INTO qa_pairs (user_id, question, answer, question_type, source, usage_count)
    VALUES (
        v_user_id,
        'When would you recommend the new gpt-realtime model over other solutions?',
        'The gpt-realtime model (GA, December 2025) is ideal for production voice agents that need:

1. Low latency: WebRTC support means browser-native real-time communication
2. Complex function calling: 66.5% accuracy (up from 49.7%), crucial for multi-step workflows
3. Natural conversation: Captures non-verbal cues (laughs), switches languages mid-sentence, adapts tone
4. Long-running functions: Model continues conversation while waiting on API results (huge UX improvement)

Cost: $32/1M audio input (cached: $0.40), $64/1M output (20% cheaper than preview)

Best use cases: Customer support (Intercom, Zendesk), healthcare triage, language learning, sales calls

I''d compare vs alternatives:
- Deepgram STT + Claude: Better for complex reasoning, more flexible model routing
- gpt-realtime: Better for real-time conversational UX, simpler architecture

In my Interview Mate system, I used Deepgram + Claude for flexibility. For a call center startup, I''d likely recommend gpt-realtime for the native conversation flow and WebRTC integration.',
        'technical',
        'manual',
        0
    );

    -- Q4: o1-pro cost justification
    INSERT INTO qa_pairs (user_id, question, answer, question_type, source, usage_count)
    VALUES (
        v_user_id,
        'o1-pro costs $600 per million output tokens. How would you justify this to customers?',
        'o1-pro makes sense when one accurate answer beats hundreds of cheap attempts:

Use cases where cost is justified:
1. Medical diagnosis: One correct diagnosis > 100 failed attempts with 4o
2. Legal document analysis: Accuracy matters more than speed
3. Complex code generation: Single correct implementation > debugging 10 buggy versions
4. Scientific research: PhD-level reasoning (GPT-5.2: 77% on FrontierScience Olympiad benchmark)

Cost comparison example (customer support ticket routing):
- Option A: 4o-mini (10 attempts to get complex routing right): 10M tokens × $0.15 = $1,500
- Option B: o1-pro (1 attempt, correct): 1M tokens × $600 = $600 (60% savings)

Key insight: o1 uses 60% fewer reasoning tokens than o1-preview, so actual cost is lower than it appears.

Architecture strategy: Hybrid routing
- Simple queries: 4o-mini ($0.15/1M)
- Complex reasoning: o1 or o1-mini
- Mission-critical: o1-pro

This is what I implemented in my LLM service abstraction with Claude/GLM routing. Same pattern applies to OpenAI''s model family.',
        'behavioral',
        'manual',
        0
    );

    -- Q5: Prompt caching + semantic caching
    INSERT INTO qa_pairs (user_id, question, answer, question_type, source, usage_count)
    VALUES (
        v_user_id,
        'How would you combine OpenAI''s prompt caching with application-level caching?',
        'Two-layer caching strategy for maximum cost reduction:

Layer 1 - Application Semantic Cache (my implementation):
- Exact match: Hash-based lookup (1ms)
- Similar questions: SequenceMatcher 85% threshold (1-5ms)
- Savings: 500ms → 1ms DB query elimination, 100% cost reduction on cache hits
- Hit rate: 60-70% with 50+ Q&A pairs

Layer 2 - OpenAI Prompt Caching:
- Automatic for 1024+ token prompts
- Caches system prompt + context (STAR stories, schemas, tools)
- Savings: Up to 90% input token cost, 80% latency reduction
- Cache duration: 5-10 minutes (up to 1 hour off-peak)

Combined example (interview coaching):
Request 1: "Tell me about yourself" - Miss both caches - Full cost
Request 2: "Tell me about yourself" - Hit L1 cache - 0ms, $0
Request 3: "Tell me about your leadership experience" - Miss L1, hit L2 (same context) - 200ms, 90% cheaper

Architecture:
```python
async def get_answer(question):
    # L1: Check semantic cache
    cached = find_in_cache(question)
    if cached: return cached

    # L2: API call (prompt caching automatic)
    answer = await openai.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": large_context},  # Auto-cached
            {"role": "user", "content": question}
        ]
    )

    # Update L1 cache
    store_in_cache(question, answer)
    return answer
```

This is exactly what I built in Interview Mate. L1 gave 2.5x speedup, L2 adds 90% cost reduction on top.',
        'technical',
        'manual',
        0
    );

    -- Q6: FrontierScience awareness
    INSERT INTO qa_pairs (user_id, question, answer, question_type, source, usage_count)
    VALUES (
        v_user_id,
        'What do you know about OpenAI''s latest research capabilities?',
        'OpenAI released FrontierScience in December 2025, a benchmark for PhD-level scientific reasoning across physics, chemistry, and biology.

Key results:
- GPT-5.2 scores 77% on Olympiad track (designed by international medalists)
- 25% on Research track (real-world PhD-level tasks, 10-point rubric)
- For context: GPT-4 scored 39% on GPQA in Nov 2023, GPT-5.2 now scores 92%

Real-world impact:
The "Early science acceleration experiments with GPT-5" paper (Nov 2025) shows GPT-5 measurably accelerates research across math, physics, biology, computer science. Examples: novel literature synthesis, tough computations, even resolving open problems like "On Learning-Curve Monotonicity for Maximum Likelihood Estimators."

Solutions Architect implications:
When working with biotech, pharma, or materials science startups, I can now credibly say: "OpenAI''s models are achieving PhD-level reasoning. Let''s design your research workflow to leverage this for literature review (80% time savings) and hypothesis generation."

This is different from typical enterprise use cases, but shows OpenAI''s frontier capabilities - important for credibility when discussing technical depth with technical founders.',
        'general',
        'manual',
        0
    );

    RAISE NOTICE 'Successfully added 6 latest OpenAI updates Q&A pairs for user %', v_user_id;
END $$;
