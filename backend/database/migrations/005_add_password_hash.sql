-- Add password_hash column to profiles table for credentials login
ALTER TABLE public.profiles
ADD COLUMN IF NOT EXISTS password_hash TEXT;

-- Add index for faster lookups
CREATE INDEX IF NOT EXISTS idx_profiles_password_hash ON public.profiles(password_hash) WHERE password_hash IS NOT NULL;
