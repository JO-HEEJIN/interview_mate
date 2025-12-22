"""
Anthropic Claude API integration for AI answer generation with semantic similarity matching
"""

import re
import logging
from typing import Optional, List
from difflib import SequenceMatcher
from anthropic import Anthropic
from openai import AsyncOpenAI
from pydantic import BaseModel, Field
from app.core.config import settings
from app.services.embedding_service import EmbeddingService, get_embedding_service
from supabase import Client

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
    Calculate similarity ratio between two strings with intelligent matching.

    Uses multiple strategies:
    1. Exact substring matching (if shorter string is in longer string)
    2. Token-based overlap (shared words / total words)
    3. Sequence matching (difflib)

    Returns a value between 0 and 1, where 1 is identical.
    """
    # Strategy 1: Check if one is a substring of the other
    if str1 in str2 or str2 in str1:
        return 0.95  # Very high match if one contains the other

    # Strategy 2: Token-based overlap (good for "tell me about yourself" vs "tell me a bit about yourself")
    tokens1 = set(str1.split())
    tokens2 = set(str2.split())

    if tokens1 and tokens2:
        intersection = tokens1 & tokens2
        union = tokens1 | tokens2
        jaccard = len(intersection) / len(union)

        # Also calculate containment (smaller set contained in larger)
        smaller = min(tokens1, tokens2, key=len)
        larger = max(tokens1, tokens2, key=len)
        containment = len(smaller & larger) / len(smaller) if smaller else 0

        # Use max of jaccard and containment
        token_similarity = max(jaccard, containment)
    else:
        token_similarity = 0.0

    # Strategy 3: Sequence matching (original approach)
    sequence_similarity = SequenceMatcher(None, str1, str2).ratio()

    # Return the maximum similarity from all strategies
    return max(token_similarity, sequence_similarity)


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


# Pydantic schemas for OpenAI Structured Outputs
class QAPairItem(BaseModel):
    question: str = Field(description="The interview question")
    answer: str = Field(description="The corresponding answer")
    question_type: str = Field(description="Type: behavioral, technical, situational, or general")


class QAPairList(BaseModel):
    qa_pairs: List[QAPairItem] = Field(description="List of Q&A pairs extracted from text")


class ClaudeService:
    def __init__(self, supabase: Optional[Client] = None):
        self.client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        self.openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = "claude-sonnet-4-20250514"

        # Initialize embedding service for semantic similarity (proper implementation)
        self.embedding_service = get_embedding_service(supabase) if supabase else None
        self.semantic_threshold = 0.80  # 80% cosine similarity threshold

        # Simple in-memory cache for answers
        # Format: {normalized_question: {"question": original, "answer": generated_answer}}
        self._answer_cache = {}
        self._cache_similarity_threshold = 0.85  # 85% similarity to use cached answer
        self._max_cache_size = 50  # Limit cache size to prevent memory issues

        # In-memory Q&A index for fast lookup (Phase 1.1 optimization)
        # Format: {normalized_question: qa_pair_dict}
        self._qa_index = {}
        self._qa_pairs_list = []  # Original list for similarity fallback

        logger.info("Claude service initialized with OpenAI Embeddings and Anthropic Prompt Caching")

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

        Performance: O(n*m) where n = number of Q&A pairs, m = avg variations per pair
        This runs once when context is loaded, enabling O(1) exact match
        and faster similarity matching afterward.
        """
        self._qa_index.clear()
        self._qa_pairs_list = qa_pairs

        total_entries = 0
        for qa_pair in qa_pairs:
            # Index main question
            question = qa_pair.get("question", "")
            normalized = normalize_question(question)
            self._qa_index[normalized] = qa_pair
            total_entries += 1

            # Index all question variations
            variations = qa_pair.get("question_variations", [])
            if variations:
                for variation in variations:
                    if variation and variation.strip():
                        normalized_var = normalize_question(variation)
                        self._qa_index[normalized_var] = qa_pair
                        total_entries += 1

        logger.info(f"Built Q&A index with {total_entries} entries from {len(qa_pairs)} Q&A pairs (including variations)")

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
        qa_pairs: list = None,
        format: str = "paragraph",
        user_profile: Optional[dict] = None
    ):
        """
        Generate streaming answer with Claude API (REAL-TIME DISPLAY).

        Args:
            question: The interview question
            resume_text: User's resume content
            star_stories: List of STAR stories
            talking_points: List of key talking points
            qa_pairs: List of prepared Q&A pairs
            format: "bullet" or "paragraph" (for compatibility)

        Yields:
            str: Text chunks as they're generated
        """
        star_stories = star_stories or []
        talking_points = talking_points or []
        qa_pairs = qa_pairs or []

        # Check for matching Q&A pair first (using semantic similarity with OpenAI Embeddings)
        matching_qa = await self.find_matching_qa_pair(question, qa_pairs, user_profile.get('id') if user_profile else None)
        if matching_qa:
            logger.info(f"Using prepared Q&A pair for streaming question: '{question}'")
            # Yield the prepared answer directly (simulate streaming)
            yield matching_qa['answer']
            return

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

        # Add Q&A pairs as reference
        if qa_pairs:
            qa_text = "\n\n".join([
                f"Q: {qa.get('question', '')}\nA: {qa.get('answer', '')}"
                for qa in qa_pairs[:5]  # Include top 5 Q&A pairs as reference
            ])
            context_parts.append(f"PREPARED Q&A PAIRS (use as reference if relevant):\n{qa_text}")

        context = "\n\n---\n\n".join(context_parts) if context_parts else "No specific context provided."

        # Use same system prompt as non-streaming
        system_prompt = self._get_system_prompt(user_profile)

        # Detect question type and frustration level
        context_info = self._detect_question_context(question)
        qtype = context_info["type"]
        frustrated = context_info["frustrated"]
        max_tokens = context_info["max_tokens"]
        instruction = context_info["instruction"]

        user_prompt = f"""CANDIDATE BACKGROUND:
{context}

INTERVIEW QUESTION:
{question}

Generate a suggested answer ({instruction}):"""

        try:
            # Claude streaming API with prompt caching
            with self.client.messages.stream(
                model=self.model,
                max_tokens=max_tokens,
                system=[
                    {
                        "type": "text",
                        "text": system_prompt,
                        "cache_control": {"type": "ephemeral"}  # Enable prompt caching
                    }
                ],
                messages=[{"role": "user", "content": user_prompt}]
            ) as stream:
                for text in stream.text_stream:
                    yield text

            logger.info("Streaming complete")

        except Exception as e:
            logger.error(f"Claude streaming error: {str(e)}", exc_info=True)
            yield "\n\n⚠️ Error generating answer. Please try again."

    def _detect_question_context(self, question: str) -> dict:
        """
        Detect question type and interviewer frustration level.

        Returns:
            {
                "type": "yes_no" | "direct" | "deep_dive" | "clarification" | "general",
                "frustrated": bool,
                "max_tokens": int,
                "instruction": str
            }
        """
        question_lower = question.lower()

        # Detect frustration signals
        frustration_phrases = [
            "stop", "hold on", "whoa",
            "that's not what i asked", "i didn't ask",
            "you're doing it again", "answer the question",
            "i just told you", "i asked you", "listen"
        ]
        is_frustrated = any(phrase in question_lower for phrase in frustration_phrases)

        # Detect question type
        yes_no_phrases = ["yes or no", "correct?", "is this", "is that", "would you tell"]
        direct_phrases = ["what is", "what would", "when did", "where is", "how much", "how many"]
        deep_dive_phrases = ["walk me through", "explain how", "tell me about", "describe", "talk about"]
        clarification_phrases = ["what do you mean", "can you clarify", "i don't understand"]

        if any(phrase in question_lower for phrase in yes_no_phrases):
            qtype = "yes_no"
            max_tokens = 20 if is_frustrated else 30
            instruction = "CRITICAL: YES/NO question - Answer in MAXIMUM 5-10 WORDS"
        elif any(phrase in question_lower for phrase in direct_phrases):
            qtype = "direct"
            max_tokens = 40 if is_frustrated else 80
            instruction = "CRITICAL: Direct question - Answer in MAXIMUM 20 WORDS"
        elif any(phrase in question_lower for phrase in deep_dive_phrases):
            qtype = "deep_dive"
            max_tokens = 80 if is_frustrated else 150
            instruction = "Deep-dive question - Answer in MAXIMUM 60 WORDS (30 seconds)"
        elif any(phrase in question_lower for phrase in clarification_phrases):
            qtype = "clarification"
            max_tokens = 50 if is_frustrated else 100
            instruction = "Clarification - Answer in MAXIMUM 30 WORDS"
        else:
            qtype = "general"
            max_tokens = 100 if is_frustrated else 150
            instruction = "Answer in MAXIMUM 60 WORDS (30 seconds)"

        # If frustrated, add explicit warning
        if is_frustrated:
            instruction = f"🚨 INTERVIEWER IS FRUSTRATED - BE ULTRA BRIEF! {instruction}"

        return {
            "type": qtype,
            "frustrated": is_frustrated,
            "max_tokens": max_tokens,
            "instruction": instruction
        }

    def _get_system_prompt(self, user_profile: Optional[dict] = None) -> str:
        """
        Generate system prompt from user profile.

        Args:
            user_profile: Dict with keys: full_name, target_role, target_company,
                         projects_summary, answer_style, custom_instructions, etc.

        Returns:
            System prompt string combining base prompt + user's custom instructions
        """
        # Extract profile data with defaults
        if user_profile:
            name = user_profile.get('full_name') or 'the candidate'
            role = user_profile.get('target_role') or 'your target role'
            company = user_profile.get('target_company') or 'the company'
            projects = user_profile.get('projects_summary') or ''
            style = user_profile.get('answer_style', 'balanced')
            strengths = user_profile.get('key_strengths', [])
        else:
            # Default fallback (for backward compatibility)
            name = 'the candidate'
            role = 'your target role'
            company = 'the company'
            projects = ''
            style = 'balanced'
            strengths = []

        # Build strengths section
        strengths_text = ''
        if strengths:
            strengths_list = '\n'.join([f"- {s}" for s in strengths])
            strengths_text = f"\n\n**Key Strengths to Emphasize:**\n{strengths_list}"

        # Style-specific instructions
        style_instructions = {
            'concise': '- Be extremely concise and direct\n- Prefer bullet points over paragraphs\n- Maximum 30 words for most answers',
            'balanced': '- Balance detail with brevity\n- Use 30-60 words for most answers\n- Provide context but stay focused',
            'detailed': '- Provide comprehensive explanations\n- Use 60-100 words when appropriate\n- Include relevant context and examples'
        }
        style_guide = style_instructions.get(style, style_instructions['balanced'])

        base_prompt = f"""You are {name}, interviewing for {role} at {company}.

# Your Background

{projects if projects else 'Use the candidate background provided in the context below.'}{strengths_text}

# Your Interview Style

**Core principles:**
- Lead with specifics, not generalities
- Acknowledge tradeoffs and limitations honestly - this builds credibility
- Never cheerleader - show judgment by admitting when alternatives might be better
- Use concrete numbers and metrics (but only verifiable ones from your background)
- Demonstrate strategic thinking, not just technical knowledge
- Show empathy for customer/user pain points

**Answer structure (PREP):**
- Point: State your conclusion first
- Reason: One clear reason why
- Example: Concrete, specific evidence from your background
- Point: Restate or add nuance if needed

# Communication Style

**Match the question type:**
- Yes/no → "Yes" or "No, [1-sentence correction]" (under 10 words)
- Direct question → Answer directly using PREP structure (30-60 words)
- Behavioral → Use STAR: Situation + Action + Result (50-60 words)

**Answer style: {style}**
{style_guide}

**Core rules:**
1. Answer ONLY what's asked - don't volunteer extra info
2. CRITICAL: Use EXACT numbers and details from your background - NEVER round, simplify, or change them
3. If your background has specific metrics (e.g., "92.6% reduction"), use those EXACT numbers
4. If your background provides context (e.g., "test vs production"), include that nuance
5. If caught in error, admit it briefly and move on
6. Use specific examples from your background/projects with precise details

# Example Answer Format

**For yes/no questions:**
Keep it under 10 words. If correcting, add one brief sentence.

**For direct questions:**
Answer the specific question asked, then stop. Don't elaborate unless asked.

**For behavioral questions (STAR):**
- Situation: Brief context (1 sentence)
- Action: What you specifically did (2-3 sentences)
- Result: Measurable outcome with EXACT metrics from your background (use precise numbers, don't round or simplify)

**CRITICAL - About numbers and metrics:**
- If your background says "92.6% cost reduction", say exactly that - NOT "90%" or "about 90%"
- If your background distinguishes "test" vs "production" numbers, preserve that distinction
- Never invent, round, or simplify numbers - use them exactly as written in your background

**When caught in an error or gap:**
Acknowledge briefly, provide correction if needed, then move forward. Don't over-explain.

Now answer the interview question following these guidelines."""

        # Append user's custom instructions if provided
        if user_profile and user_profile.get('custom_instructions'):
            custom_instructions = user_profile['custom_instructions'].strip()
            if custom_instructions:
                base_prompt += f"\n\n# YOUR SPECIFIC INTERVIEW CONTEXT & STYLE\n\n{custom_instructions}"

        return base_prompt

    async def generate_answer(
        self,
        question: str,
        resume_text: str = "",
        star_stories: list = None,
        talking_points: list = None,
        qa_pairs: list = None,
        use_cache: bool = True,
        user_profile: Optional[dict] = None
    ) -> str:
        """
        Generate an interview answer based on question and user context.

        Args:
            question: The interview question detected
            resume_text: User's resume content
            star_stories: List of STAR stories
            talking_points: List of key talking points
            qa_pairs: List of prepared Q&A pairs

        Returns:
            Generated answer suggestion
        """
        star_stories = star_stories or []
        talking_points = talking_points or []
        qa_pairs = qa_pairs or []

        # Check for matching Q&A pair first (using semantic similarity with OpenAI Embeddings)
        matching_qa = await self.find_matching_qa_pair(question, qa_pairs, user_profile.get('id') if user_profile else None)
        if matching_qa:
            logger.info(f"Using prepared Q&A pair for question: '{question}'")
            # Return the prepared answer directly
            return matching_qa['answer']

        # Check cache if no Q&A match
        if use_cache:
            cached_answer = self._get_cached_answer(question)
            if cached_answer:
                return cached_answer

        logger.info(f"Generating answer for question: '{question}'")
        logger.info(f"Context: resume={len(resume_text)} chars, stories={len(star_stories)}, points={len(talking_points)}, qa_pairs={len(qa_pairs)}")

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

        # Add Q&A pairs as reference (even if no exact match, Claude can use them as examples)
        if qa_pairs:
            qa_text = "\n\n".join([
                f"Q: {qa.get('question', '')}\nA: {qa.get('answer', '')}"
                for qa in qa_pairs[:5]  # Include top 5 Q&A pairs as reference
            ])
            context_parts.append(f"PREPARED Q&A PAIRS (use as reference if relevant):\n{qa_text}")

        context = "\n\n---\n\n".join(context_parts) if context_parts else "No specific context provided."

        system_prompt = self._get_system_prompt(user_profile)

        # Detect question type and frustration level
        context_info = self._detect_question_context(question)
        qtype = context_info["type"]
        frustrated = context_info["frustrated"]
        max_tokens = context_info["max_tokens"]
        instruction = context_info["instruction"]

        user_prompt = f"""CANDIDATE BACKGROUND:
{context}

INTERVIEW QUESTION:
{question}

Generate a suggested answer ({instruction}):"""

        try:
            logger.info(f"Sending request to Claude API (type: {qtype}, frustrated: {frustrated}, max_tokens: {max_tokens})")
            response = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                system=[
                    {
                        "type": "text",
                        "text": system_prompt,
                        "cache_control": {"type": "ephemeral"}  # Enable prompt caching for 90% cost reduction
                    }
                ],
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


    async def extract_qa_pairs_openai(self, text: str) -> list:
        """
        Extract Q&A pairs from free-form text using OpenAI Structured Outputs.

        PRIMARY METHOD - Uses OpenAI's parse() with Pydantic schemas for 100% valid output.
        Falls back to Claude Tool Use if OpenAI fails.

        Args:
            text: Free-form text containing questions and answers (any format)

        Returns:
            List of dicts with keys: question, answer, question_type, source
        """
        logger.info(f"Extracting Q&A pairs from text using OpenAI Structured Outputs ({len(text)} chars)")

        try:
            completion = await self.openai_client.beta.chat.completions.parse(
                model="gpt-4o-2024-08-06",
                messages=[
                    {"role": "system", "content": "You are an expert at extracting interview Q&A pairs from text. Extract all question-answer pairs regardless of formatting (markdown, code blocks, tables, Q:/A: format, etc.)."},
                    {"role": "user", "content": f"""Extract all interview Q&A pairs from the following text.

The text may be in any format (markdown headers, code blocks, tables, Q:/A: format, etc.).

Find every question-answer pair and return them in the structured format.

Text to parse:

{text}"""}
                ],
                response_format=QAPairList,
            )

            # Extract parsed data
            parsed_data = completion.choices[0].message.parsed
            if not parsed_data or not parsed_data.qa_pairs:
                logger.warning("No Q&A pairs extracted by OpenAI")
                return []

            # Convert Pydantic models to dicts and add source field
            qa_pairs = []
            for pair in parsed_data.qa_pairs:
                qa_pairs.append({
                    "question": pair.question,
                    "answer": pair.answer,
                    "question_type": pair.question_type,
                    "source": "bulk_upload"
                })

            logger.info(f"Successfully extracted {len(qa_pairs)} Q&A pairs using OpenAI Structured Outputs")
            return qa_pairs

        except Exception as e:
            logger.error(f"OpenAI Q&A extraction error: {str(e)}", exc_info=True)
            logger.warning("Falling back to Claude Tool Use")
            return await self.extract_qa_pairs_claude(text)


    async def extract_qa_pairs_claude(self, text: str) -> list:
        """
        Extract Q&A pairs from free-form text using Claude AI with Tool Use.

        BACKUP METHOD - kept for fallback if OpenAI fails.

        Uses Claude's Tool Use feature to guarantee valid JSON output,
        similar to how I understand user intent in conversation.

        Args:
            text: Free-form text containing questions and answers (any format)

        Returns:
            List of dicts with keys: question, answer, question_type, source
        """
        logger.info(f"Extracting Q&A pairs from text ({len(text)} chars)")

        # Define tool schema for structured extraction
        tools = [{
            "name": "save_qa_pairs",
            "description": "Save extracted interview Q&A pairs. Use this to store all question-answer pairs you find in the text, regardless of formatting (markdown, code blocks, tables, etc.).",
            "input_schema": {
                "type": "object",
                "properties": {
                    "qa_pairs": {
                        "type": "array",
                        "description": "Array of all Q&A pairs found in the text",
                        "items": {
                            "type": "object",
                            "properties": {
                                "question": {
                                    "type": "string",
                                    "description": "The interview question (cleaned up, no Q: prefix, no markdown headers)"
                                },
                                "answer": {
                                    "type": "string",
                                    "description": "The corresponding answer (cleaned up, no A: prefix, no code block markers)"
                                },
                                "question_type": {
                                    "type": "string",
                                    "enum": ["behavioral", "technical", "situational", "general"],
                                    "description": "Type of question: behavioral (tell me about, describe), technical (how does X work, explain), situational (what would you do), general (other)"
                                }
                            },
                            "required": ["question", "answer", "question_type"]
                        }
                    }
                },
                "required": ["qa_pairs"]
            }
        }]

        try:
            logger.info("Sending Q&A extraction request with Tool Use")
            response = self.client.messages.create(
                model=self.model,
                max_tokens=8192,
                tools=tools,
                messages=[{
                    "role": "user",
                    "content": f"""Extract all interview Q&A pairs from the following text.

The text may be in any format (markdown headers, code blocks, tables, Q:/A: format, etc.).

Find every question-answer pair and use the save_qa_pairs tool to save them.

Text to parse:

{text}"""
                }]
            )

            # Find tool use block in response
            tool_use_block = None
            for block in response.content:
                if block.type == "tool_use" and block.name == "save_qa_pairs":
                    tool_use_block = block
                    break

            if not tool_use_block:
                logger.error("No tool_use block found in response")
                logger.error(f"Response content: {response.content}")
                return []

            # Extract structured data from tool call
            qa_pairs = tool_use_block.input.get("qa_pairs", [])

            # Add source field
            for pair in qa_pairs:
                pair["source"] = "bulk_upload"

            logger.info(f"Successfully extracted {len(qa_pairs)} Q&A pairs using Tool Use")
            return qa_pairs

        except Exception as e:
            logger.error(f"Q&A extraction error: {str(e)}", exc_info=True)
            logger.error(f"Full response: {response if 'response' in locals() else 'No response'}")
            return []

    async def find_matching_qa_pair(self, question: str, qa_pairs: list, user_id: Optional[str] = None) -> Optional[dict]:
        """
        Find a matching Q&A pair using PROPER semantic similarity with OpenAI Embeddings.

        This replaces the old string-matching approach with real semantic similarity.

        Performance:
        - Uses cosine similarity on OpenAI embeddings (1536 dimensions)
        - Checks both main question and question variations
        - Falls back to string matching if embeddings unavailable

        Args:
            question: The detected interview question
            qa_pairs: List of user's Q&A pairs (dicts with question, answer, etc.)
            user_id: User ID for database-backed semantic search (optional)

        Returns:
            Matching Q&A pair dict if found (similarity >= 80%), None otherwise
        """
        if not qa_pairs:
            return None

        # Strategy 1: Use database-backed semantic search if user_id and embedding_service available
        if user_id and self.embedding_service:
            try:
                logger.info(f"Using OpenAI Embeddings for semantic search (user: {user_id})")
                match = await self.embedding_service.get_best_match(
                    user_id=user_id,
                    query_text=question,
                    similarity_threshold=self.semantic_threshold
                )

                if match:
                    logger.info(
                        f"✓ Found semantic match (OpenAI Embeddings, {match.get('similarity', 0.0):.2%}): "
                        f"'{question}' ~ '{match.get('question', '')[:50]}...'"
                    )
                    return match

            except Exception as e:
                logger.error(f"Semantic search failed, falling back to string matching: {str(e)}")

        # Strategy 2: Fallback to in-memory semantic matching with embeddings
        if self.embedding_service:
            try:
                logger.info("Using in-memory OpenAI Embeddings for semantic matching")

                # Generate embedding for query
                query_embedding = await self.embedding_service.generate_embedding(question)
                if not query_embedding:
                    raise Exception("Failed to generate query embedding")

                best_match = None
                best_similarity = 0.0
                matched_text = ""

                for qa_pair in qa_pairs:
                    # Check main question
                    qa_question = qa_pair.get("question", "")
                    qa_embedding = await self.embedding_service.generate_embedding(qa_question)

                    if qa_embedding:
                        similarity = self.embedding_service.calculate_cosine_similarity(
                            query_embedding, qa_embedding
                        )

                        if similarity > best_similarity:
                            best_similarity = similarity
                            best_match = qa_pair
                            matched_text = qa_question

                    # Check question variations
                    variations = qa_pair.get("question_variations", [])
                    if variations:
                        for variation in variations:
                            if variation and variation.strip():
                                var_embedding = await self.embedding_service.generate_embedding(variation)
                                if var_embedding:
                                    var_similarity = self.embedding_service.calculate_cosine_similarity(
                                        query_embedding, var_embedding
                                    )

                                    if var_similarity > best_similarity:
                                        best_similarity = var_similarity
                                        best_match = qa_pair
                                        matched_text = variation

                if best_similarity >= self.semantic_threshold:
                    logger.info(
                        f"✓ Found semantic match (in-memory, {best_similarity:.2%}): "
                        f"'{question}' ~ '{matched_text}'"
                    )
                    return best_match
                else:
                    logger.info(f"No semantic match found (best: {best_similarity:.2%})")
                    return None

            except Exception as e:
                logger.error(f"In-memory semantic matching failed: {str(e)}")

        # Strategy 3: Fallback to old string-based matching (deprecated but kept for safety)
        logger.warning("Using deprecated string matching - embeddings unavailable")
        normalized_q = normalize_question(question)
        threshold = 0.85

        best_match = None
        best_similarity = 0.0
        matched_text = ""

        for qa_pair in qa_pairs:
            qa_question = qa_pair.get("question", "")
            normalized_qa = normalize_question(qa_question)
            similarity = calculate_similarity(normalized_q, normalized_qa)

            if similarity > best_similarity:
                best_similarity = similarity
                best_match = qa_pair
                matched_text = qa_question

            variations = qa_pair.get("question_variations", [])
            if variations:
                for variation in variations:
                    if variation and variation.strip():
                        normalized_var = normalize_question(variation)
                        var_similarity = calculate_similarity(normalized_q, normalized_var)

                        if var_similarity > best_similarity:
                            best_similarity = var_similarity
                            best_match = qa_pair
                            matched_text = variation

        if best_similarity >= threshold:
            logger.info(f"Found match (string-based, {best_similarity:.2%}): '{question}' ~ '{matched_text}'")
            return best_match
        else:
            logger.info(f"No match found (best: {best_similarity:.2%})")
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


# Singleton instance (will be initialized with supabase client)
_claude_service: Optional[ClaudeService] = None

def get_claude_service(supabase: Optional[Client] = None) -> ClaudeService:
    """Get or create singleton Claude service instance"""
    global _claude_service
    if _claude_service is None:
        _claude_service = ClaudeService(supabase)
    return _claude_service

# For backward compatibility
claude_service = ClaudeService()
