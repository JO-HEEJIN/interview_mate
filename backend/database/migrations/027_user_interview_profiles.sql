-- User Interview Profiles Table
-- Stores personalized interview context for answer generation

CREATE TABLE IF NOT EXISTS public.user_interview_profiles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,

    -- Basic Information
    full_name VARCHAR(255),
    target_role VARCHAR(255),
    target_company VARCHAR(255),

    -- Background (Markdown supported)
    projects_summary TEXT,  -- Main projects with achievements and metrics
    technical_stack TEXT[], -- Array of technologies/skills

    -- Communication Preferences
    answer_style VARCHAR(50) DEFAULT 'balanced' CHECK (
        answer_style IN ('concise', 'balanced', 'detailed')
    ),
    key_strengths TEXT[],  -- Array of key strengths to emphasize

    -- Advanced: Custom System Prompt (optional)
    custom_system_prompt TEXT,  -- If set, overrides template

    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    -- Constraints
    UNIQUE(user_id)  -- One profile per user
);

-- Index for fast user lookup
CREATE INDEX idx_user_interview_profiles_user ON public.user_interview_profiles(user_id);

-- Update timestamp trigger
CREATE OR REPLACE FUNCTION update_user_interview_profiles_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_user_interview_profiles_updated_at
    BEFORE UPDATE ON public.user_interview_profiles
    FOR EACH ROW
    EXECUTE FUNCTION update_user_interview_profiles_updated_at();

-- Enable RLS
ALTER TABLE public.user_interview_profiles ENABLE ROW LEVEL SECURITY;

-- RLS Policies
CREATE POLICY "Users can view their own interview profile"
    ON public.user_interview_profiles
    FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own interview profile"
    ON public.user_interview_profiles
    FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own interview profile"
    ON public.user_interview_profiles
    FOR UPDATE
    USING (auth.uid() = user_id)
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can delete their own interview profile"
    ON public.user_interview_profiles
    FOR DELETE
    USING (auth.uid() = user_id);

-- Grant permissions
GRANT ALL ON public.user_interview_profiles TO authenticated;
GRANT ALL ON public.user_interview_profiles TO service_role;
