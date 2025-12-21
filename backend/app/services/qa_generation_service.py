"""
Q&A Generation Service
Intelligent generation of interview Q&A pairs from multiple context sources

Generates 30 initial Q&A pairs across 4 categories:
- Resume-based (18): Behavioral/technical from experience
- Company-aligned (7): Situational matching culture
- Job posting (5): Gap analysis, JD alignment
- General (5): Common questions personalized

Incremental generation: 10 more Q&A pairs when new context added
"""

import logging
from typing import List, Dict, Any, Optional
from uuid import UUID, uuid4
from openai import AsyncOpenAI
from anthropic import Anthropic
from pydantic import BaseModel, Field
from difflib import SequenceMatcher

from app.core.config import settings
from app.core.supabase import get_supabase_client

logger = logging.getLogger(__name__)

# Pydantic schemas for OpenAI Structured Outputs
class QAPairGenerated(BaseModel):
    question: str = Field(description="Interview question")
    answer: str = Field(description="Suggested answer based on user's context")
    question_type: str = Field(description="behavioral, technical, situational, or general")
    generation_strategy: str = Field(description="resume_based, company_aligned, job_posting, or general")
    reasoning: str = Field(description="Why this Q&A was generated from the context")

class QAPairBatch(BaseModel):
    qa_pairs: List[QAPairGenerated] = Field(description="List of generated Q&A pairs")


class QAGenerationService:
    def __init__(self):
        self.openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.claude_client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        self.supabase = get_supabase_client()

        # Category distribution for 30 initial Q&As
        self.initial_distribution = {
            'resume_based': 18,      # 60% - behavioral/technical from experience
            'company_aligned': 7,     # 23% - situational matching culture
            'job_posting': 5,         # 17% - gap analysis, JD alignment
            'general': 5              # Common questions
        }

        # Category distribution for 10 incremental Q&As
        self.incremental_distribution = {
            'resume_based': 5,
            'company_aligned': 2,
            'job_posting': 2,
            'general': 1
        }

    async def generate_initial_qa_batch(
        self,
        user_id: str,
        batch_id: Optional[UUID] = None
    ) -> Dict[str, Any]:
        """
        Generate initial 30 Q&A pairs from all available user contexts.

        Strategy:
        1. Fetch all user contexts (resume, company, job posting, additional)
        2. Generate 18 resume-based Q&As (behavioral + technical)
        3. Generate 7 company-aligned situational Q&As
        4. Generate 5 job-posting gap analysis Q&As
        5. Generate 5 general interview Q&As
        6. Save to database with batch tracking

        Args:
            user_id: User ID
            batch_id: Optional batch ID (generated if not provided)

        Returns:
            Dict with batch_id, generated_count, category_breakdown, qa_pairs
        """
        if not batch_id:
            batch_id = uuid4()

        logger.info(f"Starting initial Q&A generation for user {user_id}, batch {batch_id}")

        # Step 1: Fetch all user contexts
        contexts = await self._fetch_user_contexts(user_id)
        if not contexts['resume']:
            raise ValueError("Resume is required for Q&A generation")

        # Step 2: Create generation batch record
        await self._create_batch_record(
            user_id,
            batch_id,
            'initial',
            30,
            contexts
        )

        # Step 3: Generate Q&As by category
        all_qa_pairs = []

        try:
            # Generate resume-based Q&As (18 pairs)
            logger.info("Generating 18 resume-based Q&As...")
            resume_qas = await self._generate_resume_based_qas(
                contexts,
                count=self.initial_distribution['resume_based']
            )
            all_qa_pairs.extend(resume_qas)
            logger.info(f"Generated {len(resume_qas)} resume-based Q&As")

            # Generate company-aligned Q&As (7 pairs)
            if contexts['company_info']:
                logger.info("Generating 7 company-aligned Q&As...")
                company_qas = await self._generate_company_aligned_qas(
                    contexts,
                    count=self.initial_distribution['company_aligned']
                )
                all_qa_pairs.extend(company_qas)
                logger.info(f"Generated {len(company_qas)} company-aligned Q&As")
            else:
                logger.warning("No company info available, skipping company-aligned Q&As")

            # Generate job-posting Q&As (5 pairs)
            if contexts['job_posting']:
                logger.info("Generating 5 job-posting Q&As...")
                job_qas = await self._generate_job_posting_qas(
                    contexts,
                    count=self.initial_distribution['job_posting']
                )
                all_qa_pairs.extend(job_qas)
                logger.info(f"Generated {len(job_qas)} job-posting Q&As")
            else:
                logger.warning("No job posting available, skipping job-posting Q&As")

            # Generate general Q&As (5 pairs)
            logger.info("Generating 5 general Q&As...")
            general_qas = await self._generate_general_qas(
                contexts,
                count=self.initial_distribution['general']
            )
            all_qa_pairs.extend(general_qas)
            logger.info(f"Generated {len(general_qas)} general Q&As")

            # Step 4: Save to database
            logger.info(f"Saving {len(all_qa_pairs)} Q&A pairs to database...")
            saved_pairs = await self._save_qa_pairs(user_id, batch_id, all_qa_pairs)

            # Step 5: Update batch record
            category_breakdown = {
                'resume_based': len([q for q in all_qa_pairs if q.generation_strategy == 'resume_based']),
                'company_aligned': len([q for q in all_qa_pairs if q.generation_strategy == 'company_aligned']),
                'job_posting': len([q for q in all_qa_pairs if q.generation_strategy == 'job_posting']),
                'general': len([q for q in all_qa_pairs if q.generation_strategy == 'general']),
            }

            await self._update_batch_record(
                batch_id,
                'completed',
                len(saved_pairs),
                category_breakdown=category_breakdown
            )

            logger.info(f"✅ Successfully generated {len(saved_pairs)} Q&A pairs for user {user_id}")

            return {
                'batch_id': str(batch_id),
                'generated_count': len(saved_pairs),
                'category_breakdown': category_breakdown,
                'qa_pairs': saved_pairs
            }

        except Exception as e:
            await self._update_batch_record(batch_id, 'failed', 0, error=str(e))
            logger.error(f"Q&A generation failed: {e}", exc_info=True)
            raise

    async def generate_incremental_qa_batch(
        self,
        user_id: str,
        new_context_ids: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Generate 10 additional Q&A pairs when new context is added.

        Strategy:
        - Focus on newly added context
        - Generate 5 resume-based, 2 company, 2 job posting, 1 general
        - Avoid duplicating existing Q&As

        Args:
            user_id: User ID
            new_context_ids: IDs of newly added contexts (optional)

        Returns:
            Dict with batch_id, generated_count, qa_pairs
        """
        batch_id = uuid4()

        logger.info(f"Starting incremental Q&A generation for user {user_id}")

        # Fetch all contexts + existing Q&As for deduplication
        contexts = await self._fetch_user_contexts(user_id)
        existing_qas = await self._fetch_existing_questions(user_id)

        # Create batch record
        await self._create_batch_record(
            user_id,
            batch_id,
            'incremental',
            10,
            contexts
        )

        try:
            all_qa_pairs = []

            # Generate with deduplication
            logger.info("Generating 5 incremental resume-based Q&As...")
            resume_qas = await self._generate_resume_based_qas(
                contexts,
                count=5,
                avoid_duplicates=existing_qas
            )
            all_qa_pairs.extend(resume_qas)

            if contexts['company_info']:
                logger.info("Generating 2 incremental company-aligned Q&As...")
                company_qas = await self._generate_company_aligned_qas(
                    contexts,
                    count=2,
                    avoid_duplicates=existing_qas
                )
                all_qa_pairs.extend(company_qas)

            if contexts['job_posting']:
                logger.info("Generating 2 incremental job-posting Q&As...")
                job_qas = await self._generate_job_posting_qas(
                    contexts,
                    count=2,
                    avoid_duplicates=existing_qas
                )
                all_qa_pairs.extend(job_qas)

            logger.info("Generating 1 incremental general Q&A...")
            general_qas = await self._generate_general_qas(
                contexts,
                count=1,
                avoid_duplicates=existing_qas
            )
            all_qa_pairs.extend(general_qas)

            # Save and update
            saved_pairs = await self._save_qa_pairs(
                user_id,
                batch_id,
                all_qa_pairs,
                source='incremental_ai'
            )
            await self._update_batch_record(batch_id, 'completed', len(saved_pairs))

            logger.info(f"✅ Generated {len(saved_pairs)} incremental Q&A pairs")

            return {
                'batch_id': str(batch_id),
                'generated_count': len(saved_pairs),
                'qa_pairs': saved_pairs
            }

        except Exception as e:
            await self._update_batch_record(batch_id, 'failed', 0, error=str(e))
            raise

    async def _generate_resume_based_qas(
        self,
        contexts: Dict[str, Any],
        count: int,
        avoid_duplicates: Optional[List[str]] = None
    ) -> List[QAPairGenerated]:
        """
        Generate behavioral/technical Q&As from resume.

        Mix: 60% behavioral (STAR method), 40% technical

        Args:
            contexts: All user contexts
            count: Number of Q&As to generate
            avoid_duplicates: List of existing questions to avoid

        Returns:
            List of QAPairGenerated objects
        """
        resume_text = contexts['resume']
        additional_context = "\n\n".join(contexts.get('additional', []))

        dedup_instruction = ""
        if avoid_duplicates:
            dedup_instruction = f"\n\nIMPORTANT: AVOID generating questions similar to these existing ones:\n{', '.join(avoid_duplicates[:10])}"

        prompt = f"""You are an expert interview coach. Generate {count} high-quality interview Q&A pairs based on this candidate's resume.

RESUME:
{resume_text}

{f"ADDITIONAL CONTEXT:\n{additional_context}" if additional_context else ""}

INSTRUCTIONS:
1. Generate {count} Q&A pairs that interviewers would likely ask based on this resume
2. Mix of behavioral (60%) and technical (40%) questions
3. Questions should target specific projects, achievements, and skills mentioned
4. Answers should:
   - Use STAR method (Situation, Task, Action, Result) for behavioral questions
   - Provide technical depth and show expertise for technical questions
   - Reference specific numbers, metrics, and achievements from the resume
   - Sound natural and conversational (not robotic)
   - Be 60-90 seconds when spoken aloud
5. Make questions diverse - cover different experiences, projects, and skills{dedup_instruction}

BEHAVIORAL QUESTIONS (60%) should ask about:
- Specific projects mentioned (e.g., "Tell me about the [project name] project and your role")
- Challenges faced ("Describe a time you had to optimize costs in a production system")
- Team collaboration, leadership, conflict resolution
- Problem-solving and decision-making
- Impact and results ("Walk me through how you achieved [specific metric]")

TECHNICAL QUESTIONS (40%) should ask about:
- Architecture decisions ("How did you design the [system name] architecture?")
- Technical tradeoffs ("Why did you choose [technology A] over [technology B]?")
- Implementation details ("Explain your approach to [technical challenge]")
- System design and scalability
- Performance optimization

ANSWER GUIDELINES:
- Behavioral: Use STAR method, reference specific metrics (e.g., "reduced costs by 92.6%")
- Technical: Show depth, explain reasoning, discuss tradeoffs
- Keep answers concise but comprehensive (60-90 seconds)
- Sound like a real person, not a textbook

Generate exactly {count} Q&A pairs."""

        try:
            completion = await self.openai_client.beta.chat.completions.parse(
                model="gpt-4o-2024-08-06",
                messages=[
                    {"role": "system", "content": "You are an expert interview coach creating realistic, high-quality interview Q&A pairs tailored to the candidate's specific experience."},
                    {"role": "user", "content": prompt}
                ],
                response_format=QAPairBatch,
                temperature=0.8  # Higher diversity for varied questions
            )

            parsed = completion.choices[0].message.parsed

            if not parsed or not parsed.qa_pairs:
                logger.error("OpenAI returned no Q&A pairs")
                return []

            # Set strategy and validate question types
            for qa in parsed.qa_pairs:
                qa.generation_strategy = 'resume_based'
                if qa.question_type not in ['behavioral', 'technical']:
                    # Default to behavioral if type is unclear
                    qa.question_type = 'behavioral'

            logger.info(f"Generated {len(parsed.qa_pairs)} resume-based Q&As")
            return parsed.qa_pairs[:count]  # Ensure exact count

        except Exception as e:
            logger.error(f"Resume-based Q&A generation failed: {e}", exc_info=True)
            raise

    async def _generate_company_aligned_qas(
        self,
        contexts: Dict[str, Any],
        count: int,
        avoid_duplicates: Optional[List[str]] = None
    ) -> List[QAPairGenerated]:
        """
        Generate situational Q&As matching company culture/mission.

        Args:
            contexts: All user contexts
            count: Number of Q&As to generate
            avoid_duplicates: List of existing questions to avoid

        Returns:
            List of QAPairGenerated objects
        """
        company_text = "\n\n".join(contexts.get('company_info', []))
        resume_text = contexts['resume']

        if not company_text:
            logger.warning("No company info available for company-aligned Q&As")
            return []

        dedup_instruction = ""
        if avoid_duplicates:
            dedup_instruction = f"\n\nAVOID duplicating: {', '.join(avoid_duplicates[:10])}"

        prompt = f"""Generate {count} situational interview Q&A pairs that align with this company's culture and mission.

COMPANY INFORMATION:
{company_text}

CANDIDATE RESUME (for context):
{resume_text[:2000]}...

INSTRUCTIONS:
1. Generate {count} situational questions that test alignment with company values/culture
2. Questions should be "What would you do if..." or "How would you handle..." scenarios
3. Questions must be relevant to this specific company's mission, values, and challenges
4. Answers should:
   - Demonstrate understanding of company mission and values
   - Reference candidate's relevant experience from resume
   - Show how past experience prepares them for company-specific challenges
   - Sound authentic and thoughtful (not generic)
   - Be 60-90 seconds when spoken{dedup_instruction}

FOCUS AREAS:
- Company values and culture fit
- Decision-making aligned with company principles
- Handling conflicts between competing priorities
- Stakeholder management in company context
- Company-specific challenges or initiatives

EXAMPLES OF GOOD QUESTIONS:
- "How would you prioritize feature development if [company value] conflicts with user demand?"
- "Describe how you'd approach [company-specific challenge] based on your experience"
- "What would you do if you discovered a technical decision violates [company principle]?"
- "How would you handle a situation where [company mission] and [business goal] are in tension?"

Generate exactly {count} company-aligned Q&A pairs."""

        try:
            completion = await self.openai_client.beta.chat.completions.parse(
                model="gpt-4o-2024-08-06",
                messages=[
                    {"role": "system", "content": "You create situational interview questions that test company culture fit and alignment with mission/values."},
                    {"role": "user", "content": prompt}
                ],
                response_format=QAPairBatch,
                temperature=0.8
            )

            parsed = completion.choices[0].message.parsed

            if not parsed or not parsed.qa_pairs:
                return []

            for qa in parsed.qa_pairs:
                qa.generation_strategy = 'company_aligned'
                qa.question_type = 'situational'

            return parsed.qa_pairs[:count]

        except Exception as e:
            logger.error(f"Company-aligned Q&A generation failed: {e}", exc_info=True)
            return []  # Graceful degradation

    async def _generate_job_posting_qas(
        self,
        contexts: Dict[str, Any],
        count: int,
        avoid_duplicates: Optional[List[str]] = None
    ) -> List[QAPairGenerated]:
        """
        Generate Q&As focused on job requirements and gap analysis.

        Args:
            contexts: All user contexts
            count: Number of Q&As to generate
            avoid_duplicates: List of existing questions to avoid

        Returns:
            List of QAPairGenerated objects
        """
        job_text = "\n\n".join(contexts.get('job_posting', []))
        resume_text = contexts['resume']

        if not job_text:
            logger.warning("No job posting available for job-posting Q&As")
            return []

        prompt = f"""Generate {count} interview Q&A pairs focused on this job posting's requirements.

JOB POSTING:
{job_text}

CANDIDATE RESUME:
{resume_text[:2000]}...

INSTRUCTIONS:
1. Generate {count} questions that probe specific job requirements
2. Identify potential gaps between resume and job requirements
3. Create questions that let candidate bridge gaps with transferable skills
4. Mix technical requirements (50%) and soft skills/qualifications (50%)
5. Answers should address gaps honestly while highlighting relevant experience{f"\n\nAVOID: {', '.join(avoid_duplicates[:10])}" if avoid_duplicates else ""}

FOCUS AREAS:
- Required technical skills/technologies mentioned in JD
- Years of experience or seniority level expectations
- Specific tools, frameworks, or methodologies listed
- Domain knowledge requirements
- Responsibilities that aren't obvious from resume
- Required vs nice-to-have qualifications

QUESTION TYPES:
- Gap-bridging: "This role requires [X]. How would you quickly ramp up?"
- Transferable skills: "You have experience with [A]. How would you apply that to [B]?"
- Depth-testing: "The job mentions [requirement]. Can you walk me through your experience with that?"
- Scenario-based: "In this role, you'd need to [responsibility]. How would you approach that?"

ANSWER STRATEGY:
- Be honest about experience gaps
- Highlight transferable skills and quick learning ability
- Reference specific examples from resume that demonstrate adaptability
- Show enthusiasm and clear learning plan for new areas

Generate exactly {count} job-requirement Q&A pairs."""

        try:
            completion = await self.openai_client.beta.chat.completions.parse(
                model="gpt-4o-2024-08-06",
                messages=[
                    {"role": "system", "content": "You create questions that probe job requirement fit and help candidates bridge experience gaps with transferable skills."},
                    {"role": "user", "content": prompt}
                ],
                response_format=QAPairBatch,
                temperature=0.7
            )

            parsed = completion.choices[0].message.parsed

            if not parsed or not parsed.qa_pairs:
                return []

            for qa in parsed.qa_pairs:
                qa.generation_strategy = 'job_posting'
                # Mix of technical and situational based on content
                if any(keyword in qa.question.lower() for keyword in ['technical', 'technology', 'how does', 'explain', 'architecture']):
                    qa.question_type = 'technical'
                else:
                    qa.question_type = 'situational'

            return parsed.qa_pairs[:count]

        except Exception as e:
            logger.error(f"Job posting Q&A generation failed: {e}", exc_info=True)
            return []

    async def _generate_general_qas(
        self,
        contexts: Dict[str, Any],
        count: int,
        avoid_duplicates: Optional[List[str]] = None
    ) -> List[QAPairGenerated]:
        """
        Generate common interview questions personalized to candidate.

        Args:
            contexts: All user contexts
            count: Number of Q&As to generate
            avoid_duplicates: List of existing questions to avoid

        Returns:
            List of QAPairGenerated objects
        """
        resume_text = contexts['resume']
        company_text = "\n\n".join(contexts.get('company_info', []))

        prompt = f"""Generate {count} common interview Q&A pairs, personalized to this candidate.

CANDIDATE RESUME:
{resume_text[:1500]}...

COMPANY (if available):
{company_text[:1000] if company_text else "Generic company"}

INSTRUCTIONS:
Generate {count} common interview questions with highly personalized answers.

COMMON QUESTIONS TO CHOOSE FROM:
1. "Tell me about yourself" - 60-second elevator pitch
2. "Why are you interested in this role/company?"
3. "What are your greatest strengths?"
4. "What's a weakness you're working on?"
5. "Where do you see yourself in 5 years?"
6. "Why should we hire you?"
7. "Tell me about a time you failed and what you learned"
8. "What's your biggest professional achievement?"
9. "Do you have any questions for us?"

ANSWER REQUIREMENTS:
- Reference specific resume achievements and metrics
- Show genuine interest in company (if info available)
- Be concise (60-90 seconds when spoken)
- Sound natural and authentic, not robotic
- For "Tell me about yourself": Follow past → present → future structure
- For strengths: Back up with concrete examples
- For weaknesses: Show self-awareness and growth mindset

Generate exactly {count} general Q&A pairs."""

        try:
            completion = await self.openai_client.beta.chat.completions.parse(
                model="gpt-4o-2024-08-06",
                messages=[
                    {"role": "system", "content": "You create personalized answers to common interview questions based on the candidate's specific background."},
                    {"role": "user", "content": prompt}
                ],
                response_format=QAPairBatch,
                temperature=0.6  # Slightly lower for more consistent common questions
            )

            parsed = completion.choices[0].message.parsed

            if not parsed or not parsed.qa_pairs:
                logger.error("OpenAI returned no general Q&A pairs")
                return []

            for qa in parsed.qa_pairs:
                qa.generation_strategy = 'general'
                qa.question_type = 'general'

            return parsed.qa_pairs[:count]

        except Exception as e:
            logger.error(f"General Q&A generation failed: {e}", exc_info=True)
            raise

    async def _fetch_user_contexts(self, user_id: str) -> Dict[str, Any]:
        """Fetch all user contexts from database."""
        result = self.supabase.table("user_contexts") \
            .select("*") \
            .eq("user_id", user_id) \
            .execute()

        contexts = {
            'resume': None,
            'company_info': [],
            'job_posting': [],
            'additional': []
        }

        for row in result.data:
            context_type = row['context_type']
            if context_type == 'resume':
                contexts['resume'] = row['extracted_text']
            elif context_type == 'company_info':
                contexts['company_info'].append(row['extracted_text'])
            elif context_type == 'job_posting':
                contexts['job_posting'].append(row['extracted_text'])
            elif context_type == 'additional':
                contexts['additional'].append(row['extracted_text'])

        return contexts

    async def _fetch_existing_questions(self, user_id: str) -> List[str]:
        """Fetch existing question texts for deduplication."""
        result = self.supabase.table("qa_pairs") \
            .select("question") \
            .eq("user_id", user_id) \
            .execute()

        return [row['question'] for row in result.data]

    async def _create_batch_record(
        self,
        user_id: str,
        batch_id: UUID,
        batch_type: str,
        target_count: int,
        contexts: Dict[str, Any]
    ):
        """Create generation batch tracking record."""
        self.supabase.table("generation_batches").insert({
            'id': str(batch_id),
            'user_id': user_id,
            'batch_type': batch_type,
            'target_count': target_count,
            'status': 'in_progress',
            'context_snapshot': contexts,
            'started_at': 'now()'
        }).execute()

    async def _update_batch_record(
        self,
        batch_id: UUID,
        status: str,
        generated_count: int,
        error: Optional[str] = None,
        category_breakdown: Optional[Dict[str, int]] = None
    ):
        """Update batch record with results."""
        update_data = {
            'status': status,
            'generated_count': generated_count,
            'completed_at': 'now()'
        }

        if error:
            update_data['error_message'] = error

        if category_breakdown:
            update_data['category_breakdown'] = category_breakdown

        self.supabase.table("generation_batches").update(update_data).eq('id', str(batch_id)).execute()

    async def _save_qa_pairs(
        self,
        user_id: str,
        batch_id: UUID,
        qa_pairs: List[QAPairGenerated],
        source: str = 'ai_generated'
    ) -> List[Dict[str, Any]]:
        """Save generated Q&A pairs to database."""
        data = []
        for qa in qa_pairs:
            data.append({
                'user_id': user_id,
                'question': qa.question,
                'answer': qa.answer,
                'question_type': qa.question_type,
                'source': source,
                'generation_batch_id': str(batch_id),
                'generation_strategy': qa.generation_strategy,
                'context_sources': {'reasoning': qa.reasoning}
            })

        result = self.supabase.table("qa_pairs").insert(data).execute()
        return result.data

# Global instance
qa_generation_service = QAGenerationService()
