"""
Anthropic Claude API integration for AI answer generation
"""

import logging
from anthropic import Anthropic
from app.core.config import settings

# 로거 설정
logger = logging.getLogger(__name__)

class ClaudeService:
    def __init__(self):
        self.client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        self.model = "claude-sonnet-4-20250514"
        logger.info("Claude service initialized")

    async def generate_answer(
        self,
        question: str,
        resume_text: str = "",
        star_stories: list = None,
        talking_points: list = None
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

        system_prompt = """You are an interview coaching assistant. Your job is to help the candidate answer interview questions effectively.

Based on the candidate's background information (resume, STAR stories, talking points), generate a concise, natural-sounding answer that:
1. Directly addresses the question
2. Uses specific examples from their experience when relevant
3. Follows the STAR format for behavioral questions
4. Is conversational and authentic, not robotic
5. Can be delivered in about 1-2 minutes

Keep the answer focused and avoid unnecessary filler. The candidate will use this as a guide, not read it verbatim."""

        user_prompt = f"""CANDIDATE BACKGROUND:
{context}

INTERVIEW QUESTION:
{question}

Generate a suggested answer:"""

        try:
            logger.info("Sending request to Claude API")
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1024,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": user_prompt}
                ]
            )

            answer = response.content[0].text
            logger.info(f"Generated answer: {len(answer)} chars")
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
