-- Migration: Add meta Q&A about why staying updated matters for SA role
-- These explain the "why" behind OpenAI's "familiarize yourself with recent updates" requirement
-- Date: 2025-12-18

DO $$
DECLARE
    v_user_id uuid;
BEGIN
    SELECT id INTO v_user_id FROM auth.users WHERE email = 'heejinpark0303@gmail.com';

    IF v_user_id IS NULL THEN
        RAISE EXCEPTION 'User not found';
    END IF;

    -- Q1: Why does OpenAI care about staying updated?
    INSERT INTO qa_pairs (user_id, question, answer, question_type, source, usage_count)
    VALUES (
        v_user_id,
        'Why is it important for Solutions Architects to stay current with OpenAI''s latest releases?',
        'OpenAI explicitly states "familiarize yourself with recent updates" because SA is fundamentally different from typical engineering roles. We''re testing for two core competencies:

1. Technical curiosity - Not just knowing what exists, but understanding why it was built and what problems it solves
2. Customer-centric thinking - Translating new capabilities into business value for startups

For example, when gpt-realtime was released with 20% lower pricing and WebRTC support, an SA should immediately think: "Which of my customers struggling with voice latency could benefit? How does this change my architecture recommendations?"

In my preparation, I track OpenAI''s changelog and blog. When I built Interview Mate, I chose Deepgram + Claude for flexibility. But now with gpt-realtime GA, I''d recommend it for customers who prioritize conversation flow over model routing flexibility.

This mindset - "new release → customer application → architecture adjustment" - is what separates good SAs from great ones.',
        'behavioral',
        'manual',
        0
    );

    -- Q2: Hybrid architecture with o1 vs 4o
    INSERT INTO qa_pairs (user_id, question, answer, question_type, source, usage_count)
    VALUES (
        v_user_id,
        'A startup is struggling with API costs. They''re using GPT-4o for everything. What would you recommend?',
        'I''d recommend a hybrid routing architecture based on task complexity:

Tier 1 (Simple): 4o-mini ($0.15/1M output)
- Customer support FAQs, content generation, basic chat

Tier 2 (Standard): 4o ($2.50/1M output)
- General business logic, document analysis, most use cases

Tier 3 (Complex reasoning): o1-mini or o1
- Code generation, complex decision trees, mathematical reasoning
- Only when accuracy matters more than speed

Tier 4 (Mission-critical): o1-pro ($600/1M output)
- Medical diagnosis, legal analysis, where one correct answer beats 100 cheap attempts

Implementation pattern:
```python
def route_request(query, complexity):
    if complexity == "simple":
        return call_model("gpt-4o-mini")
    elif complexity == "reasoning":
        return call_model("o1-mini")
    else:
        return call_model("gpt-4o")
```

This is exactly what I implemented in my LLM service abstraction (Claude/GLM routing). The pattern applies to OpenAI''s model family too. Combined with prompt caching, this can reduce costs by 70-90% while maintaining quality where it matters.',
        'technical',
        'manual',
        0
    );

    -- Q3: Realtime API vs traditional pipeline
    INSERT INTO qa_pairs (user_id, question, answer, question_type, source, usage_count)
    VALUES (
        v_user_id,
        'When would you recommend Realtime API over the traditional STT → LLM → TTS pipeline?',
        'Realtime API wins when conversation flow matters more than model flexibility:

Choose Realtime API when:
- Zero latency is critical (customer support, language learning)
- Natural interruptions needed (user can cut off mid-sentence)
- Emotion/tone detection matters (mental health, sales coaching)
- Simple architecture preferred (one API vs three services)
- WebRTC integration needed (browser-based apps)

Choose STT → LLM → TTS when:
- Need specific model combinations (Deepgram Flux + Claude Sonnet)
- Complex post-processing required (sentiment analysis, custom filters)
- Cost optimization through caching and routing
- Multi-language with specialized STT models

Real example: In my Interview Mate system, I chose Deepgram + Claude because I needed:
1. Semantic caching for repeated questions (500ms → 1ms)
2. Flexible model routing (Claude for quality, GLM for cost)
3. Custom question detection logic

For a call center startup with straightforward workflows, I''d recommend gpt-realtime for better UX and simpler ops. Trade-off is $32/1M audio input vs Deepgram''s $0.0077/min (different pricing model, need to calculate based on usage).',
        'technical',
        'manual',
        0
    );

    -- Q4: Combining caching strategies
    INSERT INTO qa_pairs (user_id, question, answer, question_type, source, usage_count)
    VALUES (
        v_user_id,
        'How would you help a startup optimize API costs using the latest OpenAI features?',
        'Three-layer cost optimization strategy:

Layer 1 - Application Semantic Cache (my implementation):
- Exact + similar question matching (85% threshold)
- 500ms DB query → 1ms memory lookup
- Cost savings: 100% on cache hits (60-70% hit rate with good Q&A pairs)

Layer 2 - OpenAI Prompt Caching (automatic):
- System prompts, schemas, RAG context cached automatically
- 50% discount on cached tokens (1024+ tokens)
- Best practice: Put static context first, dynamic content last

Layer 3 - Model Routing:
- Route by complexity (4o-mini → 4o → o1)
- 10-100x cost difference between tiers
- Use 4o-mini for 80% of requests, reserve o1 for 5% that need reasoning

Combined impact example (customer support bot):
- Baseline: 1M requests/month with 4o = $2,500
- + Semantic cache (70% hit): $750
- + Prompt caching (30% of misses): $600
- + Model routing (80% → 4o-mini): $180

76% total cost reduction (closer to my measured 92.6% with aggressive caching).

This is production-ready architecture I''d implement on Day 1 with a new customer. I''ve validated every layer in Interview Mate.',
        'technical',
        'manual',
        0
    );

    -- Q5: Structured Outputs for production stability
    INSERT INTO qa_pairs (user_id, question, answer, question_type, source, usage_count)
    VALUES (
        v_user_id,
        'A startup''s LLM integration keeps failing due to JSON parsing errors. What''s your solution?',
        'Use OpenAI''s Structured Outputs to guarantee schema compliance:

The Problem:
- LLM outputs "almost valid" JSON: missing commas, wrong field names, extra text
- Production apps crash on parse errors
- Retry loops waste tokens and time

The Solution:
```python
from pydantic import BaseModel

class InterviewAnswer(BaseModel):
    question: str
    answer: str
    confidence: float
    sources: list[str]

response = client.chat.completions.create(
    model="gpt-4o",
    messages=[...],
    response_format={"type": "json_schema", "json_schema": InterviewAnswer}
)
# Guaranteed to match schema or API fails cleanly
```

Why this matters:
- 100% schema compliance (not 98%, literally 100%)
- Schema itself is cached by prompt caching (cost reduction bonus)
- Eliminates retry logic, reduces latency
- Makes LLM outputs as reliable as traditional APIs

I implemented similar validation in Interview Mate (Q&A pair matching returns structured format). With Structured Outputs, I''d refactor to guarantee format compliance and eliminate defensive parsing code.

This is especially critical for agent systems where one step''s output feeds the next step - schema mismatches break the entire chain.',
        'technical',
        'manual',
        0
    );

    -- Q6: Reverse question about latest updates
    INSERT INTO qa_pairs (user_id, question, answer, question_type, source, usage_count)
    VALUES (
        v_user_id,
        'What question should I ask the interviewer about OpenAI''s latest releases?',
        'Strategic reverse question that shows curiosity and SA mindset:

"I''ve been following OpenAI''s o1 release and its reasoning capabilities are impressive - 77% on the FrontierScience Olympiad benchmark. From your experience working with Korean startups, are you seeing demand for complex reasoning use cases? And what optimization patterns do you typically recommend when customers want to balance o1''s power with cost considerations?"

Why this works:
1. Shows you read latest updates (o1, FrontierScience)
2. Connects to YOUR role (Korean startups)
3. Demonstrates SA thinking (cost vs performance trade-offs)
4. Invites Kenneth to share real customer stories
5. Opens discussion about architecture patterns (your strength)

Alternative if time is short:
"What''s the most exciting customer success story you''ve seen recently using OpenAI''s latest models?"

This lets them brag about their wins and gives you insight into what "good" looks like for this role.

Avoid asking:
- Basic feature questions (you should''ve researched this)
- Roadmap questions (they can''t answer, NDA)
- "What''s your favorite model?" (too generic)

Best questions show you''ve done homework and are thinking about customer impact.',
        'behavioral',
        'manual',
        0
    );

    RAISE NOTICE 'Successfully added 6 meta Q&A pairs about latest OpenAI updates for user %', v_user_id;
END $$;
