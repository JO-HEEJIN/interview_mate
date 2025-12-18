"""
ZhipuAI GLM-4.6 API integration for answer generation
Ultra-low latency LLM with SSE streaming support

Pricing (as of Dec 2025):
- GLM-4-Flash: ¥0.001/1K tokens (~$0.00014)
- GLM-4-Air: ¥0.001/1K tokens (~$0.00014)
- Average cost: ~2.0원/분 (vs Claude: ~10-15원/분)

Performance:
- First token latency: ~200-300ms
- Streaming speed: ~50 tokens/sec
- Total answer time: 2-3s for 150 tokens
"""

import logging
from typing import Optional, AsyncIterator
from zhipuai import ZhipuAI
from app.core.config import settings

logger = logging.getLogger(__name__)


class GLMService:
    def __init__(self):
        self.client = ZhipuAI(api_key=settings.ZHIPUAI_API_KEY)
        self.model = settings.GLM_MODEL  # "glm-4-flash" or "glm-4-air"
        logger.info(f"GLM service initialized with model: {self.model}")

    async def generate_answer_stream(
        self,
        question: str,
        resume_text: str = "",
        star_stories: list = None,
        talking_points: list = None,
        format: str = "bullet"  # "bullet" or "paragraph"
    ) -> AsyncIterator[str]:
        """
        Generate interview answer with SSE streaming.
        Yields answer text in chunks for real-time display.

        Args:
            question: The interview question
            resume_text: User's resume content
            star_stories: List of STAR stories
            talking_points: List of key talking points
            format: "bullet" for bullet points, "paragraph" for full text

        Yields:
            str: Text chunks as they're generated
        """
        star_stories = star_stories or []
        talking_points = talking_points or []

        logger.info(f"Generating streaming answer for: '{question}' (format: {format})")

        # Build context
        context_parts = []

        if resume_text:
            context_parts.append(f"RESUME:\n{resume_text}")

        if star_stories:
            stories_text = "\n\n".join([
                f"Story: {s.get('title', 'Untitled')}\n"
                f"Situation: {s.get('situation', '')}\n"
                f"Task: {s.get('task', '')}\n"
                f"Action: {s.get('action', '')}\n"
                f"Result: {s.get('result', '')}"
                for s in star_stories
            ])
            context_parts.append(f"STAR STORIES:\n{stories_text}")

        if talking_points:
            points_text = "\n".join([f"- {p.get('content', '')}" for p in talking_points])
            context_parts.append(f"KEY TALKING POINTS:\n{points_text}")

        context = "\n\n---\n\n".join(context_parts) if context_parts else "No specific context provided."

        # System prompt (optimized for GLM-4.6)
        if format == "bullet":
            system_prompt = """You are an interview coach for OpenAI Solutions Architect interviews.

CRITICAL FORMAT REQUIREMENT:
- Output ONLY bullet points (use "-" prefix)
- Each bullet: 1 concise sentence (10-15 words max)
- Total: 3-5 bullets covering key points
- NO introductory text, NO paragraphs
- Start immediately with first bullet

CONTENT REQUIREMENTS (Birth2Death Project):
- Birth2Death has NOT launched - NO real users, NO customers, NO revenue
- Tested with ~20 friends for feedback only
- Resume had inflated "1,000+ users" claim - address upfront if relevant
- Validation suite built Dec 16-18, 2025 (THIS WEEK)
- Cost reduction: 92.6% measured with real OpenAI API calls
- GitHub pushed Dec 18, 2025 (commit and push dates match)

FORBIDDEN PHRASES:
- "We had customers", "users were", "paying customers"
- "Built a month ago", "validated in November"

REQUIRED PHRASES:
- "Tested with friends", "haven't launched yet"
- "Validated this week", "measured with real API calls"
- "Pushed to GitHub yesterday"

Style:
- Direct, confident, no filler
- Metrics-driven (e.g., "92.6% cost reduction measured")
- Action-focused (e.g., "Built validation suite in 3 days")

Example Output Format:
- I'm Heejin Jo, founder building on OpenAI's API for mental health support
- Birth2Death hasn't launched yet, but validated 92.6% cost reduction this week
- Measured with real API calls, pushed proof to GitHub yesterday
- Resume had wrong "1,000+ users" claim - addressed upfront because honesty matters"""
        else:
            # Paragraph format (fallback)
            system_prompt = """You are an interview coach for OpenAI Solutions Architect interviews. Generate concise, professional answers (2-3 sentences, 30-45 seconds spoken).

[Same content requirements as bullet format, but output in paragraph form]"""

        user_prompt = f"""CANDIDATE BACKGROUND:
{context}

INTERVIEW QUESTION:
{question}

Generate suggested answer (bullet point format):"""

        try:
            # Call GLM API with streaming
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=200,  # ~50 words for bullet points
                temperature=0.7,
                stream=True  # Enable SSE streaming
            )

            # Stream chunks
            chunk_count = 0
            for chunk in response:
                if chunk.choices[0].delta.content:
                    text = chunk.choices[0].delta.content
                    chunk_count += 1
                    logger.debug(f"Streaming chunk #{chunk_count}: {len(text)} chars")
                    yield text

            logger.info(f"Streaming complete: {chunk_count} chunks sent")

        except Exception as e:
            logger.error(f"GLM API error: {str(e)}", exc_info=True)
            yield "\n\n⚠️ Error generating answer. Please try again."

    async def generate_answer(
        self,
        question: str,
        resume_text: str = "",
        star_stories: list = None,
        talking_points: list = None,
        format: str = "bullet"
    ) -> str:
        """
        Generate complete answer (non-streaming).
        Use this for backward compatibility or when full answer is needed upfront.

        Args:
            question: The interview question
            resume_text: User's resume content
            star_stories: List of STAR stories
            talking_points: List of key talking points
            format: "bullet" or "paragraph"

        Returns:
            str: Complete generated answer
        """
        chunks = []
        async for chunk in self.generate_answer_stream(
            question, resume_text, star_stories, talking_points, format
        ):
            chunks.append(chunk)

        return "".join(chunks)


# Global GLM service instance
glm_service = GLMService()
