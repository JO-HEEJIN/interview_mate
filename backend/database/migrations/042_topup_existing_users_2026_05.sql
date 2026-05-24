-- Migration 042: Top-up existing users with new trial allocation + apology bonus
--
-- Companion to migration 041 (pricing redesign). Retroactively grants:
--
--   Pass 1 — Universal re-engagement top-up:
--     +<free_starter.credits_amount> credits (= 30) to EVERY existing user.
--     Lets users who already burned their 3-credit trial come back and
--     experience the personalization that kicks in around 20–30 sessions.
--
--   Pass 2 — Apology bonus for prior one-time feature purchasers:
--     +50 ADDITIONAL credits to users who already paid for ai_generator
--     or qa_management. Those features just became free for the user's first
--     profile (see Phase 4 of diary.md), so the apology is owed.
--
-- Exclusions:
--   - kate@gmail.com (admin/test account, see migration 040)
--   - admin-granted subscriptions (metadata.granted_by = 'admin') — these are
--     comp grants, not real purchases.
--
-- Idempotency:
--   Each pass guards on metadata.granted_reason so re-runs are safe.
--   Metadata flags:
--     - 'topup_2026_05_universal'
--     - 'topup_2026_05_paid_apology'
--
-- Cost ceiling (worst case if every user spends every credit):
--   ~34 unpaid users × 30 credits   = 1020 credits  ≈ $102 raw API
--   ~5 paid users × 80 credits     =  400 credits  ≈ $40  raw API
--   Total: ~$142 — bounded re-engagement spend.

BEGIN;

DO $$
DECLARE
    kate_user_id     UUID;
    universal_grant  INTEGER;
    apology_grant    INTEGER := 50;
    universal_count  INTEGER := 0;
    apology_count    INTEGER := 0;
BEGIN
    -- ------------------------------------------------------------------
    -- Resolve exclusion + grant amounts
    -- ------------------------------------------------------------------
    SELECT id INTO kate_user_id
    FROM auth.users
    WHERE email = 'kate@gmail.com';

    SELECT credits_amount INTO universal_grant
    FROM public.pricing_plans
    WHERE plan_code = 'free_starter';

    IF universal_grant IS NULL OR universal_grant <= 0 THEN
        RAISE EXCEPTION 'free_starter plan not found or has invalid credits_amount; aborting top-up. Run migration 041 first.';
    END IF;

    -- ------------------------------------------------------------------
    -- Pass 1: Universal top-up (every existing user except kate)
    -- ------------------------------------------------------------------
    INSERT INTO public.user_subscriptions (
        user_id,
        plan_code,
        plan_type,
        status,
        credits_total,
        credits_used,
        credits_remaining,
        metadata
    )
    SELECT
        p.id,
        'free_starter',
        'credits',
        'active',
        universal_grant,
        0,
        universal_grant,
        jsonb_build_object(
            'granted_reason', 'topup_2026_05_universal',
            'granted_at',     NOW(),
            'note',           'Re-engagement top-up for pricing redesign'
        )
    FROM public.profiles p
    WHERE p.created_at < NOW()  -- existing-users-only boundary
      AND (kate_user_id IS NULL OR p.id <> kate_user_id)
      AND NOT EXISTS (
          SELECT 1 FROM public.user_subscriptions us
          WHERE us.user_id = p.id
            AND us.metadata->>'granted_reason' = 'topup_2026_05_universal'
      );

    GET DIAGNOSTICS universal_count = ROW_COUNT;
    RAISE NOTICE 'Pass 1 (universal): granted % credits to % existing users', universal_grant, universal_count;

    -- ------------------------------------------------------------------
    -- Pass 2: Apology bonus for prior paid one-time feature purchasers
    -- (excludes admin comp grants and kate)
    -- ------------------------------------------------------------------
    INSERT INTO public.user_subscriptions (
        user_id,
        plan_code,
        plan_type,
        status,
        credits_total,
        credits_used,
        credits_remaining,
        metadata
    )
    SELECT
        paid.user_id,
        'free_starter',
        'credits',
        'active',
        apology_grant,
        0,
        apology_grant,
        jsonb_build_object(
            'granted_reason', 'topup_2026_05_paid_apology',
            'granted_at',     NOW(),
            'note',           'Apology bonus — one-time features became free on first profile'
        )
    FROM (
        SELECT DISTINCT user_id
        FROM public.user_subscriptions
        WHERE plan_code IN ('ai_generator', 'qa_management')
          AND status IN ('active', 'depleted')
          AND COALESCE(metadata->>'granted_by', '') <> 'admin'
          AND (kate_user_id IS NULL OR user_id <> kate_user_id)
    ) AS paid
    WHERE NOT EXISTS (
        SELECT 1 FROM public.user_subscriptions existing
        WHERE existing.user_id = paid.user_id
          AND existing.metadata->>'granted_reason' = 'topup_2026_05_paid_apology'
    );

    GET DIAGNOSTICS apology_count = ROW_COUNT;
    RAISE NOTICE 'Pass 2 (apology): granted % credits to % paid users', apology_grant, apology_count;

    RAISE NOTICE 'Top-up complete — universal: % users, apology: % users', universal_count, apology_count;
END $$;

COMMIT;
