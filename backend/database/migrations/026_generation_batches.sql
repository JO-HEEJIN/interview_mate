-- Migration: Create generation_batches table for tracking Q&A generation jobs
-- Purpose: Audit trail and monitoring for AI-powered Q&A generation

-- Create generation_batches table
CREATE TABLE IF NOT EXISTS public.generation_batches (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
    status VARCHAR(50) NOT NULL DEFAULT 'pending' CHECK (
        status IN ('pending', 'in_progress', 'completed', 'failed')
    ),
    batch_type VARCHAR(50) NOT NULL CHECK (
        batch_type IN ('initial', 'incremental')
    ),
    target_count INTEGER NOT NULL CHECK (target_count > 0),
    generated_count INTEGER DEFAULT 0 CHECK (generated_count >= 0),
    context_snapshot JSONB NOT NULL,
    category_breakdown JSONB DEFAULT '{}',
    error_message TEXT,
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for efficient queries
CREATE INDEX idx_generation_batches_user ON public.generation_batches(user_id);
CREATE INDEX idx_generation_batches_status ON public.generation_batches(status);
CREATE INDEX idx_generation_batches_created ON public.generation_batches(created_at DESC);

-- Enable Row Level Security (RLS)
ALTER TABLE public.generation_batches ENABLE ROW LEVEL SECURITY;

-- RLS Policies: Users can only access their own generation batches
CREATE POLICY "Users can view their own batches"
    ON public.generation_batches
    FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own batches"
    ON public.generation_batches
    FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own batches"
    ON public.generation_batches
    FOR UPDATE
    USING (auth.uid() = user_id)
    WITH CHECK (auth.uid() = user_id);

-- Add check constraint to ensure completed_at is after started_at
ALTER TABLE public.generation_batches
    ADD CONSTRAINT generation_batches_time_check
    CHECK (started_at IS NULL OR completed_at IS NULL OR completed_at >= started_at);
