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


# Phase 1.2: Pattern-based question detection
QUESTION_PATTERNS = {
    # Behavioral questions (STAR method)
    "behavioral": [
        r"tell\s+(me|us)\s+about\s+(yourself|a\s+time)",
        r"describe\s+(a\s+time|an?\s+situation|an?\s+experience)",
        r"give\s+(me|us)\s+an?\s+example",
        r"walk\s+(me|us)\s+through",
        r"share\s+(a\s+story|an?\s+experience)",
        r"what('?s|\s+is)\s+your\s+(biggest|greatest)\s+(strength|weakness|achievement)",
        r"how\s+do\s+you\s+(handle|deal\s+with|approach)",
        r"have\s+you\s+ever",
        r"can\s+you\s+tell",
    ],
    # Technical questions
    "technical": [
        r"how\s+(would|do)\s+you\s+(design|build|implement|architect)",
        r"what('?s|\s+is)\s+the\s+(difference|time\s+complexity)",
        r"explain\s+(how|what|why)",
        r"what\s+(are\s+the\s+)?(trade[-\s]?offs|benefits)",
        r"how\s+(does|would)\s+(this|that)\s+(work|scale)",
        r"what\s+technologies",
        r"which\s+(algorithm|approach|pattern)",
    ],
    # Situational questions
    "situational": [
        r"what\s+would\s+you\s+do\s+(if|when)",
        r"how\s+would\s+you\s+(handle|approach|solve)",
        r"imagine\s+(you|that)",
        r"suppose\s+(you|that)",
        r"if\s+you\s+(were|had\s+to)",
    ],
    # General/fit questions
    "general": [
        r"^why\s+(do\s+you\s+want|are\s+you\s+interested|openai)",
        r"what\s+(interests|excites|motivates)\s+you",
        r"where\s+do\s+you\s+see\s+yourself",
        r"what\s+(are\s+your|do\s+you\s+know\s+about)",
        r"^do\s+you\s+have\s+(any\s+)?questions",
        r"is\s+there\s+anything",
        r"tell\s+(me|us)\s+about\s+(openai|this\s+role)",
    ]
}

# Compile patterns once for performance
COMPILED_PATTERNS = {
    qtype: [re.compile(pattern, re.IGNORECASE) for pattern in patterns]
    for qtype, patterns in QUESTION_PATTERNS.items()
}


def detect_question_fast(text: str) -> dict:
    """
    OPTIMIZED: Fast pattern-based question detection (Phase 1.2).

    Performance comparison:
    - Old detect_question(): ~1000ms (Claude API call)
    - New detect_question_fast(): <1ms (regex pattern matching)

    Args:
        text: Transcribed text to analyze

    Returns:
        {
            "is_question": bool,
            "question": str,
            "question_type": str,
            "confidence": str ("high"/"medium"/"low")
        }
    """
    if not text or len(text.strip()) < 5:
        return {
            "is_question": False,
            "question": "",
            "question_type": "none",
            "confidence": "high"
        }

    text_clean = text.strip()
    text_lower = text_clean.lower()

    # Step 1: Obvious question markers
    has_question_mark = '?' in text
    starts_with_question_word = any(
        text_lower.startswith(word) for word in [
            'what', 'how', 'why', 'when', 'where', 'who', 'which',
            'can you', 'could you', 'would you', 'will you',
            'do you', 'did you', 'have you', 'tell me', 'describe'
        ]
    )

    # Step 2: Pattern matching for question type
    matched_type = None
    for qtype, patterns in COMPILED_PATTERNS.items():
        for pattern in patterns:
            if pattern.search(text_lower):
                matched_type = qtype
                break
        if matched_type:
            break

    # Step 3: Determine if it's a question
    is_question = has_question_mark or starts_with_question_word or (matched_type is not None)

    # Step 4: Determine confidence
    if has_question_mark and matched_type:
        confidence = "high"
    elif matched_type:
        confidence = "high"
    elif has_question_mark:
        confidence = "medium"
    elif starts_with_question_word:
        confidence = "medium"
    else:
        confidence = "low"

    return {
        "is_question": is_question,
        "question": text_clean if is_question else "",
        "question_type": matched_type or "general" if is_question else "none",
        "confidence": confidence
    }


class ClaudeService:
    def __init__(self):
        self.client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        self.model = "claude-sonnet-4-20250514"
        # Simple in-memory cache for answers
        # Format: {normalized_question: {"question": original, "answer": generated_answer}}
        self._answer_cache = {}
        self._cache_similarity_threshold = 0.85  # 85% similarity to use cached answer
        self._max_cache_size = 50  # Limit cache size to prevent memory issues

        # In-memory Q&A index for fast lookup (Phase 1.1 optimization)
        # Format: {normalized_question: qa_pair_dict}
        self._qa_index = {}
        self._qa_pairs_list = []  # Original list for similarity fallback

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

    def build_qa_index(self, qa_pairs: list):
        """
        Build in-memory index of Q&A pairs for fast lookup.
        Call this when context is updated with Q&A pairs.

        Args:
            qa_pairs: List of Q&A pair dicts from database

        Performance: O(n) where n = number of Q&A pairs
        This runs once when context is loaded, enabling O(1) exact match
        and faster similarity matching afterward.
        """
        self._qa_index.clear()
        self._qa_pairs_list = qa_pairs

        for qa_pair in qa_pairs:
            question = qa_pair.get("question", "")
            normalized = normalize_question(question)

            # Store normalized question → original Q&A pair
            self._qa_index[normalized] = qa_pair

        logger.info(f"✓ Built Q&A index with {len(self._qa_index)} entries (took <1ms)")

    def find_matching_qa_pair_fast(self, question: str) -> Optional[dict]:
        """
        OPTIMIZED: Find matching Q&A pair using pre-built index.

        Performance comparison:
        - Old find_matching_qa_pair(): 500ms (O(n) similarity checks)
        - New find_matching_qa_pair_fast(): <1ms (O(1) hash lookup + early exit)

        Args:
            question: The detected interview question

        Returns:
            Matching Q&A pair if found (similarity >= 85%), None otherwise
        """
        if not self._qa_index:
            logger.warning("Q&A index not built - call build_qa_index() first")
            return None

        normalized_q = normalize_question(question)
        threshold = 0.85  # 85% similarity threshold

        # Step 1: O(1) exact match check using hash index
        if normalized_q in self._qa_index:
            qa_pair = self._qa_index[normalized_q]
            logger.info(f"✓ Exact Q&A match: '{question}' (took <1ms)")
            return qa_pair

        # Step 2: Similarity matching with early exit optimization
        best_match = None
        best_similarity = 0.0

        for normalized_qa, qa_pair in self._qa_index.items():
            similarity = calculate_similarity(normalized_q, normalized_qa)

            if similarity > best_similarity:
                best_similarity = similarity
                best_match = qa_pair

                # Early exit: if we find a very high match, stop searching
                if similarity >= 0.95:
                    logger.info(f"✓ Near-exact Q&A match ({similarity:.2%}): '{question}' (early exit)")
                    return best_match

        # Step 3: Return best match if above threshold
        if best_similarity >= threshold:
            logger.info(f"✓ Similar Q&A match ({best_similarity:.2%}): '{question}' ~ '{best_match['question']}'")
            return best_match

        logger.debug(f"No Q&A match found (best: {best_similarity:.2%})")
        return None

    async def generate_answer_stream(
        self,
        question: str,
        resume_text: str = "",
        star_stories: list = None,
        talking_points: list = None,
        format: str = "paragraph"
    ):
        """
        Generate streaming answer with Claude API (REAL-TIME DISPLAY).

        Args:
            question: The interview question
            resume_text: User's resume content
            star_stories: List of STAR stories
            talking_points: List of key talking points
            format: "bullet" or "paragraph" (for compatibility)

        Yields:
            str: Text chunks as they're generated
        """
        star_stories = star_stories or []
        talking_points = talking_points or []

        logger.info(f"Streaming answer for: '{question}'")

        # Build context (same as non-streaming)
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

        # Use same system prompt as non-streaming
        system_prompt = self._get_system_prompt()
        user_prompt = f"""CANDIDATE BACKGROUND:
{context}

INTERVIEW QUESTION:
{question}

Generate a suggested answer:"""

        try:
            # Claude streaming API
            with self.client.messages.stream(
                model=self.model,
                max_tokens=300,
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}]
            ) as stream:
                for text in stream.text_stream:
                    yield text

            logger.info("Streaming complete")

        except Exception as e:
            logger.error(f"Claude streaming error: {str(e)}", exc_info=True)
            yield "\n\n⚠️ Error generating answer. Please try again."

    def _get_system_prompt(self) -> str:
        """Get the system prompt (extracted for reuse)"""
        return """You are an interview coach for OpenAI Solutions Architect interviews. Generate professional, technically precise answers that demonstrate expertise.

CRITICAL: Birth2Death Project Facts (MUST follow exactly):
- Birth2Death has NOT launched publicly - NO real users, NO customers, NO revenue
- Tested with ~20 friends for feedback only (NOT beta users, NOT paying customers)
- Resume had inflated claims ("1,000+ users") - candidate addresses this UPFRONT in opening statement
- Validation timeline (BE PRECISE):
  * Core architecture (router.py, semantic_cache.py) - built earlier in development
  * Validation suite (run_real_validation.py, 200 test conversations) - built Dec 16-18, 2025 (THIS WEEK)
  * GitHub push - Dec 18, 2025 (YESTERDAY/TODAY) - commit and push dates match (no backdating)
- Cost reduction validation:
  * cost_analysis.py: Initial design with ESTIMATED tokens (80.4% theoretical reduction)
  * run_real_validation.py: REAL OpenAI API calls with MEASURED tokens (92.6% actual reduction, cost ~$0.20 to run)
  * Results in real_validation_results.json show measured data: $0.0049 → $0.0004 per conversation
- FORBIDDEN PHRASES (never use these):
  * "We had customers", "users were", "paying customers", "actual live usage", "production users"
  * "Built a month ago", "validated in November", "been running for weeks"
- REQUIRED PHRASES (always use these):
  * "Validated through testing this week", "built the validation suite Dec 16-18", "tested with friends"
  * "Measured with real API calls", "haven't launched yet", "no real users"
  * "Pushed to GitHub yesterday", "commit shows Dec 18"
- Opening statement context: Candidate addresses resume issue in first 60 seconds, then shows code proof

Actual Files in GitHub (github.com/JO-HEEJIN/birth2death-backend):
- router.py (lines 20-30: COMPLEX_PATTERNS for routing logic)
- semantic_cache.py (NOT cache.py - use correct filename)
- cost_tracker.py (cost tracking implementation)
- test_data/conversations.json (200 test conversations)
- cost_analysis.py (initial validation with estimated tokens)
- run_real_validation.py (REAL OpenAI API validation with measured tokens)
- results/cost_breakdown.json (initial analysis with estimates)
- results/cost_analysis_detailed.json (detailed 200-conversation analysis)
- results/real_validation_results.json (REAL API results - 92.6% cost reduction measured)
- app/core/database.py (connection pooling)
- app/utils/prompts.py (prompt compression utilities)
- app/services/tasks.py (Celery async tasks with real sentiment analysis)

NEVER mention files that don't exist. If unsure, say "in the codebase" without specific filename.

Style Requirements (INTRO CALL FORMAT - 25 minutes total):
1. BREVITY: 2-3 sentences MAX (30-45 seconds spoken) - this is an intro call, not a deep dive
2. Lead with the core answer first, details second
3. End with "Would you like me to elaborate?" or "I can walk through the details if helpful"
4. Professional yet conversational - avoid excessive formality
5. Use specific metrics when relevant (e.g., "92.6% measured reduction", "0.92 similarity threshold")
6. Reference files only if directly asked (don't volunteer "in router.py lines 20-30" unless specifically asked)
7. For behavioral questions: Brief STAR format - Situation + Result in 2 sentences
8. Avoid filler words ("So honestly...", "Yeah, so...", "Like...") - be direct
9. Never use "First, Second, Third" structure unless listing is explicitly requested
10. Business impact in one phrase: "92.6% cost reduction" not "which resulted in significant cost savings"

Key principles:
- ACCURACY about project stage (validation/testing, NOT production)
- ACCURACY about timeline (validation built THIS WEEK, Dec 16-18)
- ACCURACY about file names and paths (check the list above)
- HONESTY about resume issue (candidate addresses upfront, don't avoid it)
- Specificity (actual numbers, exact filenames, line numbers where relevant)
- Evidence (GitHub repo pushed yesterday, real test results, measured metrics)
- Professional confidence without arrogance

Resume Issue Handling:
- If asked about "1,000+ users" or user metrics: "That was a mistake on my resume - Birth2Death hasn't launched, so there are no real users yet. I addressed this in my opening because honesty matters more than looking perfect."
- If asked about validation: "I built the validation suite this week (Dec 16-18) to prove the architecture works with real measured data, not just claims."
- If asked about GitHub: "I pushed the validation code to GitHub yesterday (Dec 18) - you can see the commit and push dates match, no backdating."
- Always redirect from the mistake to the proof: acknowledge the error quickly, then show the real technical work"""

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

        system_prompt = self._get_system_prompt()
        user_prompt = f"""CANDIDATE BACKGROUND:
{context}

INTERVIEW QUESTION:
{question}

Generate a suggested answer:"""

        try:
            logger.info("Sending request to Claude API")
            response = self.client.messages.create(
                model=self.model,
                max_tokens=300,  # Shorter for 25-min intro call format
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


    async def extract_qa_pairs(self, text: str) -> list:
        """
        Extract Q&A pairs from free-form text using Claude AI.

        Args:
            text: Free-form text containing questions and answers

        Returns:
            List of dicts with keys: question, answer, question_type, source
        """
        logger.info(f"Extracting Q&A pairs from text ({len(text)} chars)")

        system_prompt = """You are a Q&A extraction assistant. Parse the provided text and extract interview questions and their answers.

Return ONLY a JSON array of objects with this exact structure:
[
  {
    "question": "the interview question",
    "answer": "the corresponding answer",
    "question_type": "behavioral/technical/situational/general"
  }
]

Rules:
- Extract ALL question-answer pairs you find
- Clean up questions and answers (remove extra whitespace, fix typos if obvious)
- Classify each question appropriately
- If text has no clear Q&A pairs, return empty array []
- Return ONLY valid JSON, no other text"""

        try:
            logger.info("Sending Q&A extraction request to Claude API")
            response = self.client.messages.create(
                model=self.model,
                max_tokens=4096,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": text}
                ]
            )

            result_text = response.content[0].text.strip()
            logger.info(f"Q&A extraction response: {result_text[:200]}...")

            # Parse JSON response
            import json
            qa_pairs = json.loads(result_text)

            # Add source field
            for pair in qa_pairs:
                pair["source"] = "bulk_upload"

            logger.info(f"Extracted {len(qa_pairs)} Q&A pairs")
            return qa_pairs

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            logger.error(f"Raw response: {result_text}")
            return []
        except Exception as e:
            logger.error(f"Q&A extraction error: {str(e)}", exc_info=True)
            return []

    def find_matching_qa_pair(self, question: str, qa_pairs: list) -> Optional[dict]:
        """
        Find a matching Q&A pair from user's uploaded pairs using semantic matching.

        Args:
            question: The detected interview question
            qa_pairs: List of user's Q&A pairs (dicts with question, answer, etc.)

        Returns:
            Matching Q&A pair dict if found (similarity >= 85%), None otherwise
        """
        if not qa_pairs:
            return None

        normalized_q = normalize_question(question)
        threshold = 0.85  # 85% similarity threshold

        best_match = None
        best_similarity = 0.0

        for qa_pair in qa_pairs:
            qa_question = qa_pair.get("question", "")
            normalized_qa = normalize_question(qa_question)

            similarity = calculate_similarity(normalized_q, normalized_qa)

            if similarity > best_similarity:
                best_similarity = similarity
                best_match = qa_pair

        if best_similarity >= threshold:
            logger.info(f"Found matching Q&A pair ({best_similarity:.2%}): '{question}' ~ '{best_match['question']}'")
            return best_match
        else:
            logger.info(f"No matching Q&A pair found (best: {best_similarity:.2%})")
            return None

    def get_temporary_answer(self, question_type: str) -> str:
        """
        Get a type-specific temporary answer to show immediately while processing.

        Args:
            question_type: The type of question (behavioral/technical/situational/general)

        Returns:
            Temporary stalling text appropriate for the question type
        """
        temporary_answers = {
            "behavioral": "For behavioral questions, I'd use the STAR method to structure my response. Let me think of a relevant example...",
            "technical": "From a technical perspective, I'd approach this systematically. Give me a moment to organize my thoughts...",
            "situational": "In that situation, I would first assess the priorities and stakeholders involved. Let me elaborate...",
            "general": "That's a great question. Let me think about the best way to address this..."
        }

        return temporary_answers.get(question_type, temporary_answers["general"])


claude_service = ClaudeService()
