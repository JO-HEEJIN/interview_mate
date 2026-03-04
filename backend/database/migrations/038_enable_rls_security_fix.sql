-- Fix Supabase Security Advisor errors: RLS disabled on 3 tables
-- questions: ENABLE RLS was missing from initial migration (policy exists but RLS not enabled)
-- star_stories, talking_points: ENABLE RLS was in migration but got disabled/not applied

-- Enable RLS on questions (public read-only table, policy already exists)
ALTER TABLE public.questions ENABLE ROW LEVEL SECURITY;

-- Re-enable RLS on star_stories (user-owned, policies already exist)
ALTER TABLE public.star_stories ENABLE ROW LEVEL SECURITY;

-- Re-enable RLS on talking_points (user-owned, policies already exist)
ALTER TABLE public.talking_points ENABLE ROW LEVEL SECURITY;
