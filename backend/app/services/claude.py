"""
Anthropic Claude API integration for AI answer generation
"""

import re
import logging
from typing import Optional
from difflib import SequenceMatcher
from anthropic import Anthropic
from app.core.config import settings

# 로거 설정
logger = logging.getLogger(__name__)


def normalize_question(question: str) -> str:
    """
    Normalize question for cache key generation.
    Removes punctuation, extra spaces, and converts to lowercase.
    """
    # Remove punctuation and convert to lowercase
    normalized = re.sub(r'[^\w\s]', '', question.lower())
    # Remove extra spaces
    normalized = ' '.join(normalized.split())
    return normalized


def calculate_similarity(str1: str, str2: str) -> float:
    """
    Calculate similarity ratio between two strings.
    Returns a value between 0 and 1, where 1 is identical.
    """
    return SequenceMatcher(None, str1, str2).ratio()


class ClaudeService:
    def __init__(self):
        self.client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        self.model = "claude-sonnet-4-20250514"
        # Simple in-memory cache for answers
        # Format: {normalized_question: {"question": original, "answer": generated_answer}}
        self._answer_cache = {}
        self._cache_similarity_threshold = 0.85  # 85% similarity to use cached answer
        self._max_cache_size = 50  # Limit cache size to prevent memory issues
        logger.info("Claude service initialized with semantic caching")

    def _get_cached_answer(self, question: str) -> Optional[str]:
        """
        Check cache for similar questions and return cached answer if found.

        Args:
            question: The question to check

        Returns:
            Cached answer if similar question found, None otherwise
        """
        normalized_q = normalize_question(question)

        # First check exact match
        if normalized_q in self._answer_cache:
            logger.info(f"Cache hit (exact): '{question}'")
            return self._answer_cache[normalized_q]["answer"]

        # Check for similar questions
        for cached_q, cached_data in self._answer_cache.items():
            similarity = calculate_similarity(normalized_q, cached_q)
            if similarity >= self._cache_similarity_threshold:
                logger.info(f"Cache hit (similar, {similarity:.2%}): '{question}' ~ '{cached_data['question']}'")
                return cached_data["answer"]

        logger.debug(f"Cache miss: '{question}'")
        return None

    def _cache_answer(self, question: str, answer: str):
        """
        Cache the generated answer for future use.

        Args:
            question: The original question
            answer: The generated answer
        """
        normalized_q = normalize_question(question)

        # Implement simple LRU: remove oldest if cache is full
        if len(self._answer_cache) >= self._max_cache_size:
            # Remove first item (oldest in insertion order for Python 3.7+)
            oldest_key = next(iter(self._answer_cache))
            del self._answer_cache[oldest_key]
            logger.debug(f"Cache full, removed oldest entry: '{oldest_key}'")

        self._answer_cache[normalized_q] = {
            "question": question,
            "answer": answer
        }
        logger.info(f"Cached answer for: '{question}' (cache size: {len(self._answer_cache)})")

    def clear_cache(self):
        """Clear the answer cache."""
        self._answer_cache.clear()
        logger.info("Answer cache cleared")

    async def generate_answer(
        self,
        question: str,
        resume_text: str = "",
        star_stories: list = None,
        talking_points: list = None,
        use_cache: bool = True
    ) -> str:
        """
        Generate an interview answer based on question and user context.

        Args:
            question: The interview question detected
            resume_text: User's resume content
            star_stories: List of STAR stories
            talking_points: List of key talking points

        Returns:
            Generated answer suggestion
        """
        star_stories = star_stories or []
        talking_points = talking_points or []

        # Check cache first if enabled
        if use_cache:
            cached_answer = self._get_cached_answer(question)
            if cached_answer:
                return cached_answer

        logger.info(f"Generating answer for question: '{question}'")
        logger.info(f"Context: resume={len(resume_text)} chars, stories={len(star_stories)}, points={len(talking_points)}")

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

        system_prompt = """You are an interview coaching assistant. Generate CONCISE answers.

Requirements:
1. Keep answers under 100 words (2-3 sentences maximum)
2. Direct and specific - get to the point immediately
3. Use one concrete example if relevant, skip if not
4. Can be delivered in 30-45 seconds
5. Natural and conversational

Be brief and actionable. Avoid long explanations."""

        user_prompt = f"""CANDIDATE BACKGROUND:
{context}

INTERVIEW QUESTION:
{question}

Generate a suggested answer:"""

        try:
            logger.info("Sending request to Claude API")
            response = self.client.messages.create(
                model=self.model,
                max_tokens=300,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": user_prompt}
                ]
            )

            answer = response.content[0].text
            logger.info(f"Generated answer: {len(answer)} chars")

            # Cache the answer for future use
            if use_cache:
                self._cache_answer(question, answer)

            return answer

        except Exception as e:
            logger.error(f"Claude API error: {str(e)}", exc_info=True)
            return "Error generating answer. Please try again."

    async def detect_question(self, transcription: str) -> dict:
        """
        Detect if the transcription contains an interview question.

        Returns:
            {
                "is_question": bool,
                "question": str (extracted question),
                "question_type": str (behavioral/technical/situational)
            }
        """
        logger.info(f"Detecting question in transcription: '{transcription}'")
        
        system_prompt = """Analyze the transcription and determine if it contains an interview question.
Return your analysis in this exact format:
IS_QUESTION: yes/no
QUESTION: [the extracted question, or "none" if no question]
TYPE: behavioral/technical/situational/general/none"""

        try:
            logger.info("Sending question detection request to Claude API")
            response = self.client.messages.create(
                model=self.model,
                max_tokens=256,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": f"Transcription: {transcription}"}
                ]
            )

            result_text = response.content[0].text
            logger.info(f"Question detection raw response: {result_text}")

            # Parse response
            lines = result_text.strip().split("\n")
            is_question = False
            question = ""
            question_type = "none"

            for line in lines:
                if line.startswith("IS_QUESTION:"):
                    is_question = "yes" in line.lower()
                elif line.startswith("QUESTION:"):
                    question = line.replace("QUESTION:", "").strip()
                    if question.lower() == "none":
                        question = ""
                elif line.startswith("TYPE:"):
                    question_type = line.replace("TYPE:", "").strip().lower()

            result = {
                "is_question": is_question,
                "question": question,
                "question_type": question_type
            }
            logger.info(f"Question detection result: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Question detection error: {str(e)}", exc_info=True)
            return {"is_question": False, "question": "", "question_type": "none"}


claude_service = ClaudeService()
