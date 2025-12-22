"""
Unified LLM service with multi-provider support and failover
Supports Claude (Anthropic) and GLM-4.6 (ZhipuAI) with intelligent routing

Strategy options:
- "claude": Use only Claude (high quality, higher cost)
- "glm": Use only GLM (ultra-low cost, good quality)
- "hybrid": Try GLM first, fallback to Claude if error (best of both worlds)
"""

import logging
from typing import Optional, AsyncIterator
from app.core.config import settings
from app.services.claude import claude_service
from app.services.glm_service import glm_service

logger = logging.getLogger(__name__)


class LLMService:
    def __init__(self):
        self.strategy = settings.LLM_SERVICE  # "claude" or "glm" or "hybrid"
        self.primary_service = None
        self.fallback_service = None

        # Configure based on strategy
        if self.strategy == "claude":
            self.primary_service = claude_service
            self.fallback_service = None
            logger.info("LLM strategy: Claude only")
        elif self.strategy == "glm":
            self.primary_service = glm_service
            self.fallback_service = None
            logger.info("LLM strategy: GLM only")
        elif self.strategy == "hybrid":
            self.primary_service = glm_service
            self.fallback_service = claude_service
            logger.info("LLM strategy: Hybrid (GLM → Claude fallback)")
        else:
            logger.warning(f"Unknown LLM strategy: {self.strategy}, defaulting to Claude")
            self.primary_service = claude_service
            self.fallback_service = None

    async def generate_answer_stream(
        self,
        question: str,
        resume_text: str = "",
        star_stories: list = None,
        talking_points: list = None,
        qa_pairs: list = None,
        format: str = "bullet",
        user_profile: Optional[dict] = None,
        session_history: list = None,
        examples_used: list = None
    ) -> AsyncIterator[str]:
        """
        Generate streaming answer with automatic failover.

        Args:
            question: The interview question
            resume_text: User's resume content
            star_stories: List of STAR stories
            talking_points: List of key talking points
            qa_pairs: List of Q&A pairs for RAG
            format: "bullet" for bullet points, "paragraph" for full text
            user_profile: User's interview profile settings
            session_history: Previous Q&A in this session for context
            examples_used: Examples already used in session to avoid repetition

        Yields:
            str: Text chunks as they're generated
        """
        try:
            # Try primary service
            if hasattr(self.primary_service, 'generate_answer_stream'):
                logger.warning(f"RAG_DEBUG: Using primary service: {self.primary_service.__class__.__name__}")
                logger.warning(f"RAG_DEBUG: Passing {len(qa_pairs or [])} Q&A pairs to service")
                logger.warning(f"RAG_DEBUG: user_profile exists: {user_profile is not None}")

                # Build kwargs dynamically to support services with different signatures
                kwargs = {
                    "question": question,
                    "resume_text": resume_text,
                    "star_stories": star_stories,
                    "talking_points": talking_points,
                    "qa_pairs": qa_pairs,
                    "format": format,
                    "user_profile": user_profile
                }

                # Add session parameters only if the service supports them (Claude does, GLM doesn't)
                import inspect
                sig = inspect.signature(self.primary_service.generate_answer_stream)
                if "session_history" in sig.parameters:
                    kwargs["session_history"] = session_history
                if "examples_used" in sig.parameters:
                    kwargs["examples_used"] = examples_used

                async for chunk in self.primary_service.generate_answer_stream(**kwargs):
                    yield chunk
            else:
                # Primary service doesn't support streaming, use non-streaming method
                logger.info(f"Primary service doesn't support streaming, using non-streaming")
                answer = await self.primary_service.generate_answer(
                    question, resume_text, star_stories, talking_points, qa_pairs, user_profile=user_profile
                )
                yield answer

        except Exception as e:
            logger.error(f"Primary service error: {str(e)}")

            # Try fallback if available
            if self.fallback_service:
                logger.info(f"Falling back to: {self.fallback_service.__class__.__name__}")
                try:
                    # Silently switch to backup service (no user-facing message)
                    answer = await self.fallback_service.generate_answer(
                        question, resume_text, star_stories, talking_points, qa_pairs, user_profile=user_profile
                    )
                    yield answer

                except Exception as fallback_error:
                    logger.error(f"Fallback service also failed: {str(fallback_error)}")
                    yield "\n\n⚠️ Error generating answer. Please try again."
            else:
                # No fallback available
                yield "\n\n⚠️ Error generating answer. Please try again."

    async def generate_answer(
        self,
        question: str,
        resume_text: str = "",
        star_stories: list = None,
        talking_points: list = None,
        qa_pairs: list = None,
        format: str = "bullet",
        user_profile: Optional[dict] = None
    ) -> str:
        """
        Generate complete answer (non-streaming) with automatic failover.

        Args:
            question: The interview question
            resume_text: User's resume content
            star_stories: List of STAR stories
            talking_points: List of key talking points
            format: "bullet" or "paragraph"
            user_profile: User's interview profile settings

        Returns:
            str: Complete generated answer
        """
        try:
            # Try primary service
            logger.info(f"Using primary service: {self.primary_service.__class__.__name__}")

            if hasattr(self.primary_service, 'generate_answer'):
                if format == "bullet" and hasattr(self.primary_service, 'generate_answer_stream'):
                    # GLM service - use format parameter
                    chunks = []
                    async for chunk in self.primary_service.generate_answer_stream(
                        question, resume_text, star_stories, talking_points, qa_pairs, format, user_profile=user_profile
                    ):
                        chunks.append(chunk)
                    return "".join(chunks)
                else:
                    # Claude service - no format parameter
                    return await self.primary_service.generate_answer(
                        question, resume_text, star_stories, talking_points, qa_pairs, user_profile=user_profile
                    )
            else:
                raise Exception("Primary service doesn't support generate_answer")

        except Exception as e:
            logger.error(f"Primary service error: {str(e)}")

            # Try fallback if available
            if self.fallback_service:
                logger.info(f"Falling back to: {self.fallback_service.__class__.__name__}")
                try:
                    return await self.fallback_service.generate_answer(
                        question, resume_text, star_stories, talking_points, qa_pairs, user_profile=user_profile
                    )
                except Exception as fallback_error:
                    logger.error(f"Fallback service also failed: {str(fallback_error)}")
                    return "⚠️ Error generating answer. Please try again."
            else:
                return "⚠️ Error generating answer. Please try again."


# Global LLM service instance
llm_service = LLMService()
