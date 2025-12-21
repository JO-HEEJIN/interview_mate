-- Migration: Extend qa_pairs table for AI generation tracking
-- Purpose: Add metadata to track which generation batch and strategy created each Q&A

-- Add new columns for generation tracking
ALTER TABLE public.qa_pairs
    ADD COLUMN IF NOT EXISTS generation_batch_id UUID,
    ADD COLUMN IF NOT EXISTS context_sources JSONB DEFAULT '[]',
    ADD COLUMN IF NOT EXISTS generation_strategy VARCHAR(50);

-- Add constraint for generation_strategy
ALTER TABLE public.qa_pairs
    ADD CONSTRAINT qa_pairs_generation_strategy_check
    CHECK (generation_strategy IS NULL OR generation_strategy IN ('resume_based', 'company_aligned', 'job_posting', 'general', 'incremental'));

-- Update source constraint to include AI-generated sources
ALTER TABLE public.qa_pairs DROP CONSTRAINT IF EXISTS qa_pairs_source_check;

ALTER TABLE public.qa_pairs
    ADD CONSTRAINT qa_pairs_source_check
    CHECK (source IN ('manual', 'bulk_upload', 'ai_generated', 'incremental_ai'));

-- Create index for batch queries
CREATE INDEX IF NOT EXISTS idx_qa_pairs_batch ON public.qa_pairs(generation_batch_id) WHERE generation_batch_id IS NOT NULL;

-- Create index for generation strategy queries
CREATE INDEX IF NOT EXISTS idx_qa_pairs_strategy ON public.qa_pairs(user_id, generation_strategy) WHERE generation_strategy IS NOT NULL;
