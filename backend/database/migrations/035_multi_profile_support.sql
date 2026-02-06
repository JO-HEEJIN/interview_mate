-- Migration: Add multi-profile support
-- Purpose: Allow users to have multiple interview profiles (e.g., Google SWE, MIT PhD, F1 Visa)

-- =====================================================
-- STEP 1: Modify user_interview_profiles table
-- =====================================================

-- 1.1 Drop the UNIQUE constraint on user_id (allows multiple profiles per user)
ALTER TABLE public.user_interview_profiles
    DROP CONSTRAINT IF EXISTS user_interview_profiles_user_id_key;

-- 1.2 Add profile_name column (required, default 'Default' for existing profiles)
ALTER TABLE public.user_interview_profiles
    ADD COLUMN IF NOT EXISTS profile_name VARCHAR(100) NOT NULL DEFAULT 'Default';

-- 1.3 Add is_default flag (one default profile per user)
ALTER TABLE public.user_interview_profiles
    ADD COLUMN IF NOT EXISTS is_default BOOLEAN DEFAULT false;

-- 1.4 Add new unique constraint (user_id + profile_name must be unique)
ALTER TABLE public.user_interview_profiles
    ADD CONSTRAINT unique_user_profile_name UNIQUE(user_id, profile_name);

-- 1.5 Update index for common queries (user + default lookup)
CREATE INDEX IF NOT EXISTS idx_user_interview_profiles_user_default
    ON public.user_interview_profiles(user_id, is_default);

-- =====================================================
-- STEP 2: Add profile_id to user_contexts
-- =====================================================

ALTER TABLE public.user_contexts
    ADD COLUMN IF NOT EXISTS profile_id UUID REFERENCES public.user_interview_profiles(id) ON DELETE CASCADE;

CREATE INDEX IF NOT EXISTS idx_user_contexts_profile
    ON public.user_contexts(profile_id);

-- =====================================================
-- STEP 3: Add profile_id to qa_pairs
-- =====================================================

ALTER TABLE public.qa_pairs
    ADD COLUMN IF NOT EXISTS profile_id UUID REFERENCES public.user_interview_profiles(id) ON DELETE CASCADE;

CREATE INDEX IF NOT EXISTS idx_qa_pairs_profile
    ON public.qa_pairs(profile_id);

-- =====================================================
-- STEP 4: Add profile_id to generation_batches
-- =====================================================

ALTER TABLE public.generation_batches
    ADD COLUMN IF NOT EXISTS profile_id UUID REFERENCES public.user_interview_profiles(id) ON DELETE CASCADE;

CREATE INDEX IF NOT EXISTS idx_generation_batches_profile
    ON public.generation_batches(profile_id);

-- =====================================================
-- STEP 5: Add profile_id to interview_sessions
-- =====================================================

ALTER TABLE public.interview_sessions
    ADD COLUMN IF NOT EXISTS profile_id UUID REFERENCES public.user_interview_profiles(id) ON DELETE SET NULL;

CREATE INDEX IF NOT EXISTS idx_interview_sessions_profile
    ON public.interview_sessions(profile_id);

-- =====================================================
-- STEP 6: Add profile_id to star_stories
-- =====================================================

ALTER TABLE public.star_stories
    ADD COLUMN IF NOT EXISTS profile_id UUID REFERENCES public.user_interview_profiles(id) ON DELETE CASCADE;

CREATE INDEX IF NOT EXISTS idx_star_stories_profile
    ON public.star_stories(profile_id);

-- =====================================================
-- STEP 7: Add profile_id to talking_points (if needed)
-- =====================================================

ALTER TABLE public.talking_points
    ADD COLUMN IF NOT EXISTS profile_id UUID REFERENCES public.user_interview_profiles(id) ON DELETE CASCADE;

CREATE INDEX IF NOT EXISTS idx_talking_points_profile
    ON public.talking_points(profile_id);

-- =====================================================
-- DONE: Schema changes complete
-- Run 036_migrate_existing_data.sql next to migrate existing data
-- =====================================================
