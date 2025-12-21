-- Migration: Add question_variations to qa_pairs table
-- Allows users to add multiple question phrasings for better Q&A matching
-- Example: "Tell me about yourself" can have variations like:
--   - "Introduce yourself"
--   - "Walk me through your background"
--   - "Give me a brief overview of your experience"

-- Add question_variations column (JSONB array of strings)
ALTER TABLE public.qa_pairs
    ADD COLUMN IF NOT EXISTS question_variations JSONB DEFAULT '[]'::jsonb;

-- Add index for better search performance on variations
CREATE INDEX IF NOT EXISTS idx_qa_pairs_variations
    ON public.qa_pairs USING GIN (question_variations);

-- Add comment explaining the column
COMMENT ON COLUMN public.qa_pairs.question_variations IS
    'Array of alternative question phrasings that should match this Q&A pair. Used to improve semantic matching for interview questions.';

-- Example update (for testing):
-- UPDATE public.qa_pairs
-- SET question_variations = '["Introduce yourself", "Walk me through your background"]'::jsonb
-- WHERE question = 'Tell me about yourself';
