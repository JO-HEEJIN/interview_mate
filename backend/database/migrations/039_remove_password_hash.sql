-- Migration: Remove unused password_hash column from profiles table
-- The password_hash column was added in migration 005 but never used.
-- Supabase Auth handles authentication separately in auth.users table.
-- Keeping this column is a security risk (redundant attack surface).

DROP INDEX IF EXISTS idx_profiles_password_hash;
ALTER TABLE public.profiles DROP COLUMN IF EXISTS password_hash;
