-- Migration: Add custom_instructions to user_interview_profiles
-- Allows users to define their own answer generation rules and context
-- This makes the system generic and customizable for any user, not just one specific use case

-- Add custom_instructions column (TEXT for long-form instructions)
ALTER TABLE public.user_interview_profiles
    ADD COLUMN IF NOT EXISTS custom_instructions TEXT DEFAULT '';

-- Add comment explaining the column
COMMENT ON COLUMN public.user_interview_profiles.custom_instructions IS
    'User-specific instructions for AI answer generation.

    This field allows users to customize how the AI should generate interview answers:
    - Market-specific context (e.g., "For Korea market, consider latency and sovereignty")
    - Answer style preferences (e.g., "Be brutally honest, not a cheerleader")
    - Domain expertise (e.g., "For healthcare questions, emphasize HIPAA compliance")
    - Competitive positioning (e.g., "When asked about Claude, acknowledge Tokyo region advantage")

    These instructions are appended to the base system prompt to create personalized answer generation.

    Example:
    "For Korea market questions:
    - Always acknowledge no Korea region (150-200ms latency)
    - Mention sovereign AI political pressure
    - Suggest hybrid architecture as pragmatic solution

    My answer style:
    - Lead with specifics, not generalities
    - Acknowledge when alternatives might be better
    - Use PREP structure: Point → Reason → Example → Point"';

-- No index needed - this is only read when generating answers, not queried
