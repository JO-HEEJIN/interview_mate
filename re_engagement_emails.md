# Re-engagement Email Drafts

> Two segments, English-only, with a free-credit incentive.
> Drafts only — not sent. Numbers (credit amounts, expiry) and subject
> lines are placeholders; finalize with founder before send.

---

## Segment A — Signup-only Churned

**Definition**

- Created account, never made a payment
- Last activity ≥ 14 days ago (tune in Task #10 against actual data)
- Verified email, not in test-account exclusion list (kate, midmost44, csoheon, info@birth2death.com per MEMORY)

**Incentive**

- **+10 free credits**, expires 30 days after grant
- Matches current signup bonus size — no resentment from new users who got 30 base
- Grant via `user_credits` insert with `metadata = {"reason": "reengagement_2026_06_signup_churn"}` (idempotent guard like the May top-up)

### Subject line candidates (A/B)

1. `We just shipped 4 new tools for your interview prep`
2. `Saved you a seat — 10 credits inside`

### Preheader

`Anki export, session history, scenario picker, security upgrade — all live since you signed up.`

### Body

```
Hi {first_name|there},

You signed up for InterviewMate but didn't get a chance to use it yet.
A few things changed in the last two weeks that I think address the
"I don't know where to start" friction first-time users told us about:

  • Scenario picker — pick the round (system design, PhD admission, F1
    visa, anything) and answers adapt to it.
  • Session history — every interview is auto-saved to /profile/sessions
    so you don't lose your run if the browser crashes.
  • Anki CSV export — pull your Q&A pairs and review them offline /
    spaced repetition.
  • Security hardening — JWT enforcement on every user-scoped endpoint.
    Your data is yours.

To make a fresh start easier, I added **10 credits** to your account.
Use them by **{expiry_date}**. One credit = one full live-interview
session.

  → Start a session: https://interviewmate.tech/interview

If something stopped you the first time, hit reply and tell me. I read
everything.

— J****
InterviewMate
```

### CTA

- Primary button: `Start a session`
- URL: `https://interviewmate.tech/interview`
- (Hybrid scenario picker auto-shows on first /interview visit per
  PR #29 — first-time UX is now smoother)

### Sign-off

Founder personal sign-off (J****). PII rule 6.6 compliant.

---

## Segment B — Paid Churned

**Definition**

- One or more successful payments via Stripe or Lemon Squeezy
- Last interview session ≥ 21 days ago
- Still has unused credits, OR depleted credits with no recent top-up
- Same test-account exclusion

**Incentive**

- **+30 bonus credits**, expires 30 days after grant
- 30 = half a credits_popular tier; meaningful but not so much we
  signal "we'll just give it away"
- Grant guard via `user_credits` insert with `metadata.reason =
  "reengagement_2026_06_paid_churn"`

### Subject line candidates (A/B)

1. `Came back to InterviewMate? On us — bonus credits inside`
2. `{first_name}, here's what's new since you left`

### Preheader

`Picking up where you left off — 30 bonus credits, 7-day refund guarantee, four new features.`

### Body

```
Hi {first_name|there},

You bought credits for InterviewMate but haven't run a session in a
while. I wanted to be upfront about two things:

First, the things you flagged (directly or indirectly) are fixed or in
progress:

  • Live Interview is now labeled correctly (it was "Interview
    Practice" — implied mock mode).
  • Past sessions are saved at /profile/sessions and exportable to
    Anki, plain text, or Markdown.
  • Scenario picker on /interview prompts the round once and tailors
    answers to it.
  • Backend auth: every user-scoped HTTP endpoint now requires JWT.
    No more service-role-key bypass paths.

Second, we ship a 7-day money-back guarantee on every purchase —
that's been the policy since the May refund unification. If anything
ever doesn't work for you, email info@birth2death.com and I'll
process it personally.

To say thanks for sticking around: **30 bonus credits** on your
account, good through **{expiry_date}**. They stack with whatever you
have left.

  → Pick up where you left off: https://interviewmate.tech/interview

If you canceled because something specific broke or didn't land, I'd
genuinely like to hear it. Reply to this email — it comes to me, not
a queue.

— J****
InterviewMate
```

### CTA

- Primary button: `Pick up where you left off`
- URL: `https://interviewmate.tech/interview`
- Secondary link inline: `https://interviewmate.tech/refund` (explicit
  acknowledgment that the policy exists — reduces "trapped" anxiety)

### Sign-off

Same founder personal sign-off.

---

## Operational notes

### Grant mechanics

Both segments use the same SQL pattern (mirroring `topup_2026_05_paid_apology` from MEMORY billing section). Sketch — finalize before run:

```sql
-- Segment A: signup-only churned, +10 credits, 30-day expiry
INSERT INTO public.user_credits (user_id, credits_amount, expires_at, metadata)
SELECT
  u.id,
  10,
  NOW() + INTERVAL '30 days',
  jsonb_build_object(
    'granted_reason', 'reengagement_2026_06_signup_churn',
    'granted_at', NOW()
  )
FROM auth.users u
WHERE u.created_at < NOW() - INTERVAL '14 days'
  AND NOT EXISTS (
    SELECT 1 FROM public.payment_transactions p WHERE p.user_id = u.id AND p.status = 'completed'
  )
  AND NOT EXISTS (
    SELECT 1 FROM public.user_credits c
    WHERE c.user_id = u.id
      AND c.metadata->>'granted_reason' = 'reengagement_2026_06_signup_churn'
  )
  AND u.email NOT IN (
    'kate@gmail.com', 'midmost44@gmail.com', 'csoheon@...', 'info@birth2death.com'
    -- TODO: pull canonical exclusion list before run
  );
```

(Segment B SQL omitted here — same shape with `EXISTS payment_transactions` instead of `NOT EXISTS`, and 30 instead of 10.)

### Send mechanics — not decided

This doc covers **drafts only**. Decisions still open:

- Which ESP (Resend / Postmark / Loops / Lemon Squeezy email API / supabase auth.send)?
- Sender domain warm-up status — info@birth2death.com may be cold; check before bulk send.
- Volume estimate — pull from Task #10 once the exclusion list is final.
- Send timing — Tue/Wed mid-morning Pacific is convention but no data to back it for our audience.
- Tracking — open/click tracking only if we already have ESP infrastructure for it. Don't add a vendor just for this batch.

### Why no Korean version

User decision: English-only this round. Korean draft can be a follow-up if data shows ≥ 30% of churned users prefer KR (we don't know yet).

---

## Out of scope

- Active-user announcement (PR #27-#31 changelog post). User passed on 3-segment split — separate effort if we decide later.
- Discount codes (Lemon Squeezy variant setup overhead). Credit grant chosen instead — strictly less infra work, strictly more retention-positive incentive.
- Open/click instrumentation if we don't already have an ESP that does it free.
