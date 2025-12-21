-- Migration: Create user_contexts table for storing uploaded context materials
-- Purpose: Store resume, company info, job posting, and additional context with extracted text

-- Create user_contexts table
CREATE TABLE IF NOT EXISTS public.user_contexts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
    context_type VARCHAR(50) NOT NULL CHECK (
        context_type IN ('resume', 'company_info', 'job_posting', 'additional')
    ),
    source_format VARCHAR(50) NOT NULL CHECK (
        source_format IN ('pdf', 'image', 'text')
    ),
    file_name VARCHAR(255),
    file_path TEXT,
    extracted_text TEXT NOT NULL,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for faster queries
CREATE INDEX idx_user_contexts_user ON public.user_contexts(user_id);
CREATE INDEX idx_user_contexts_type ON public.user_contexts(user_id, context_type);

-- Enable Row Level Security (RLS)
ALTER TABLE public.user_contexts ENABLE ROW LEVEL SECURITY;

-- RLS Policies: Users can only access their own contexts
CREATE POLICY "Users can view their own contexts"
    ON public.user_contexts
    FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own contexts"
    ON public.user_contexts
    FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own contexts"
    ON public.user_contexts
    FOR UPDATE
    USING (auth.uid() = user_id)
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can delete their own contexts"
    ON public.user_contexts
    FOR DELETE
    USING (auth.uid() = user_id);

-- Add trigger for updated_at timestamp
CREATE OR REPLACE FUNCTION update_user_contexts_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_user_contexts_timestamp
    BEFORE UPDATE ON public.user_contexts
    FOR EACH ROW
    EXECUTE FUNCTION update_user_contexts_updated_at();
