---
name: supabase-security
description: Diagnose and fix Supabase security vulnerabilities — RLS policies, exposed schemas, auth misconfigurations. Use when Supabase Security Advisor reports errors or when auditing database security.
---

# Supabase Security Audit & Fix

## When to Use

- Supabase Security Advisor reports errors or warnings
- Adding new tables that need RLS policies
- Auditing existing table security posture
- Investigating unauthorized data access concerns

## Diagnosis Steps

1. **Identify affected tables** from Security Advisor output (errors tab)
2. **Check migration files** at `backend/database/migrations/` for existing RLS definitions
3. **Verify actual DB state** — migrations may exist but not be applied
4. **Categorize issues:**
   - `RLS Disabled in Public` → table exposed to PostgREST without RLS
   - `Policy Exists RLS Disabled` → policies defined but RLS not enabled on table
   - `No Policies` → RLS enabled but no access policies defined

## Fix Patterns

### Enable RLS on table (most common fix)

```sql
ALTER TABLE public.{table_name} ENABLE ROW LEVEL SECURITY;
```

### User-owned data (has `user_id` column)

```sql
ALTER TABLE public.{table_name} ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own {table_name}"
    ON public.{table_name} FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own {table_name}"
    ON public.{table_name} FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own {table_name}"
    ON public.{table_name} FOR UPDATE
    USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own {table_name}"
    ON public.{table_name} FOR DELETE
    USING (auth.uid() = user_id);
```

### Public read-only data (no `user_id`, e.g. reference tables)

```sql
ALTER TABLE public.{table_name} ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Anyone can view {table_name}"
    ON public.{table_name} FOR SELECT
    USING (true);
```

### Service-role bypass (backend needs full access)

RLS policies don't affect `service_role` key by default in Supabase. The backend uses `SUPABASE_SERVICE_KEY` which bypasses RLS. Only `anon` key and client-side access are restricted.

## Project-Specific Notes

- **Migration files:** `backend/database/migrations/` (numbered 001-037+)
- **Supabase project ID:** `awxhkdneruigroiitgbs`
- **Tables with `user_id`:** profiles, resumes, star_stories, talking_points, sessions, session_answers, qa_pairs, user_contexts, interview_sessions, session_messages, generation_batches, user_interview_profiles, user_subscriptions, credit_usage_log
- **Public tables (no `user_id`):** questions, pricing_plans
- **Always create a new migration file** for schema changes — never edit existing migrations
- **Migration naming:** `{next_number}_{description}.sql`

## Verification

After applying fixes:
1. Click **Refresh** in Supabase Security Advisor
2. Confirm error count decreased
3. Check that app still functions (service_role key bypasses RLS, so backend should be unaffected)
4. Test client-side access if applicable

## Common Mistakes

- Enabling RLS without any policies → blocks ALL access (including reads)
- Forgetting `WITH CHECK` on INSERT policies → inserts silently fail
- Not accounting for `service_role` bypass → backend works but client breaks
- Applying RLS to tables used by Supabase Auth internals → auth breaks
