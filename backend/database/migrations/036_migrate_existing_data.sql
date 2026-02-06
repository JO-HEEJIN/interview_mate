-- Migration: Migrate existing data to use profile_id
-- Purpose: Link all existing data to a "Default" profile for each user
-- IMPORTANT: Run this AFTER 035_multi_profile_support.sql

-- =====================================================
-- STEP 1: Mark existing profiles as default
-- =====================================================

UPDATE public.user_interview_profiles
SET is_default = true,
    profile_name = 'Default'
WHERE is_default = false OR is_default IS NULL;

-- =====================================================
-- STEP 2: Create Default profiles for users who have data but no profile
-- =====================================================

-- 2.1 Users with contexts but no profile
INSERT INTO public.user_interview_profiles (user_id, profile_name, is_default, answer_style)
SELECT DISTINCT uc.user_id, 'Default', true, 'balanced'
FROM public.user_contexts uc
WHERE NOT EXISTS (
    SELECT 1 FROM public.user_interview_profiles uip
    WHERE uip.user_id = uc.user_id
)
ON CONFLICT (user_id, profile_name) DO NOTHING;

-- 2.2 Users with qa_pairs but no profile
INSERT INTO public.user_interview_profiles (user_id, profile_name, is_default, answer_style)
SELECT DISTINCT qp.user_id, 'Default', true, 'balanced'
FROM public.qa_pairs qp
WHERE NOT EXISTS (
    SELECT 1 FROM public.user_interview_profiles uip
    WHERE uip.user_id = qp.user_id
)
ON CONFLICT (user_id, profile_name) DO NOTHING;

-- 2.3 Users with star_stories but no profile (cast text to uuid)
INSERT INTO public.user_interview_profiles (user_id, profile_name, is_default, answer_style)
SELECT DISTINCT ss.user_id::uuid, 'Default', true, 'balanced'
FROM public.star_stories ss
WHERE NOT EXISTS (
    SELECT 1 FROM public.user_interview_profiles uip
    WHERE uip.user_id = ss.user_id::uuid
)
ON CONFLICT (user_id, profile_name) DO NOTHING;

-- 2.4 Users with talking_points but no profile (cast text to uuid)
INSERT INTO public.user_interview_profiles (user_id, profile_name, is_default, answer_style)
SELECT DISTINCT tp.user_id::uuid, 'Default', true, 'balanced'
FROM public.talking_points tp
WHERE NOT EXISTS (
    SELECT 1 FROM public.user_interview_profiles uip
    WHERE uip.user_id = tp.user_id::uuid
)
ON CONFLICT (user_id, profile_name) DO NOTHING;

-- =====================================================
-- STEP 3: Link existing data to Default profiles
-- =====================================================

-- 3.1 Link user_contexts to profile
UPDATE public.user_contexts uc
SET profile_id = (
    SELECT uip.id
    FROM public.user_interview_profiles uip
    WHERE uip.user_id = uc.user_id
      AND uip.is_default = true
    LIMIT 1
)
WHERE uc.profile_id IS NULL;

-- 3.2 Link qa_pairs to profile
UPDATE public.qa_pairs qp
SET profile_id = (
    SELECT uip.id
    FROM public.user_interview_profiles uip
    WHERE uip.user_id = qp.user_id
      AND uip.is_default = true
    LIMIT 1
)
WHERE qp.profile_id IS NULL;

-- 3.3 Link generation_batches to profile
UPDATE public.generation_batches gb
SET profile_id = (
    SELECT uip.id
    FROM public.user_interview_profiles uip
    WHERE uip.user_id = gb.user_id
      AND uip.is_default = true
    LIMIT 1
)
WHERE gb.profile_id IS NULL;

-- 3.4 Link interview_sessions to profile
UPDATE public.interview_sessions isess
SET profile_id = (
    SELECT uip.id
    FROM public.user_interview_profiles uip
    WHERE uip.user_id = isess.user_id
      AND uip.is_default = true
    LIMIT 1
)
WHERE isess.profile_id IS NULL;

-- 3.5 Link star_stories to profile (cast text to uuid)
UPDATE public.star_stories ss
SET profile_id = (
    SELECT uip.id
    FROM public.user_interview_profiles uip
    WHERE uip.user_id = ss.user_id::uuid
      AND uip.is_default = true
    LIMIT 1
)
WHERE ss.profile_id IS NULL;

-- 3.6 Link talking_points to profile (cast text to uuid)
UPDATE public.talking_points tp
SET profile_id = (
    SELECT uip.id
    FROM public.user_interview_profiles uip
    WHERE uip.user_id = tp.user_id::uuid
      AND uip.is_default = true
    LIMIT 1
)
WHERE tp.profile_id IS NULL;

-- =====================================================
-- STEP 4: Verify migration (optional check)
-- =====================================================

-- Count orphaned records (should be 0 after migration)
DO $$
DECLARE
    orphan_contexts INTEGER;
    orphan_qa INTEGER;
    orphan_stories INTEGER;
BEGIN
    SELECT COUNT(*) INTO orphan_contexts FROM public.user_contexts WHERE profile_id IS NULL;
    SELECT COUNT(*) INTO orphan_qa FROM public.qa_pairs WHERE profile_id IS NULL;
    SELECT COUNT(*) INTO orphan_stories FROM public.star_stories WHERE profile_id IS NULL;

    IF orphan_contexts > 0 OR orphan_qa > 0 OR orphan_stories > 0 THEN
        RAISE NOTICE 'Warning: Some records still have NULL profile_id. Contexts: %, QA: %, Stories: %',
            orphan_contexts, orphan_qa, orphan_stories;
    ELSE
        RAISE NOTICE 'Migration complete. All records linked to profiles.';
    END IF;
END $$;

-- =====================================================
-- DONE: Data migration complete
-- =====================================================
