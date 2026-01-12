# InterviewMate.ai - Lemon Squeezy Payment Integration

Session started: Dec 24, 2025

## Project Overview

InterviewMate.ai is a real-time AI-powered interview assistant that helps job seekers during interviews.

**Architecture:**
- Backend: FastAPI (Python) with Claude API, Deepgram transcription
- Frontend: Next.js 14 (TypeScript/React)
- Database: PostgreSQL via Supabase
- Payment: Migrating from Stripe to Lemon Squeezy

## Context

User's financial situation:
- Bank of America account frozen (fraud issue)
- Wyoming LLC canceled (needs $154 to reactivate)
- Cannot use Stripe (requires US bank account)
- Lemon Squeezy supports Korean bank accounts and doesn't require LLC

## Implementation Plan

### Backend (Completed)
- [x] Create lemon_squeezy.py API module
  - Checkout session creation endpoint
  - Webhook handler for order events
  - HMAC signature verification
- [x] Add Lemon Squeezy config to config.py
  - API key, store ID, webhook secret
  - Product variant IDs (5 products)
  - Payment processor selection flag
- [x] Register router in main.py
- [x] Update .env.example with Lemon Squeezy variables
- [x] Commit backend changes

### Frontend (Completed)
- [x] Update pricing page checkout endpoint
  - Changed from `/api/payments/create-checkout-session`
  - To `/api/lemon-squeezy/create-checkout-session`
  - Removed Stripe session_id placeholder from success URL
- [x] Update FAQ payment methods section
  - Changed from "Stripe, Link, Google Pay, Apple Pay"
  - To "Lemon Squeezy, cards, PayPal, Apple Pay"
- [x] Update payment success page
  - Handle both Stripe (with session_id) and Lemon Squeezy (no session_id)
  - Lemon Squeezy uses webhook-based confirmation
- [x] Commit frontend changes (commit 3b1a6c1)
- [x] Push to remote repository

### Next Steps (After Code Complete)
- [ ] Complete Lemon Squeezy account setup
- [ ] Create 5 products in Lemon Squeezy dashboard:
  1. Credits 4 pack ($4)
  2. Credits 10 pack ($10)
  3. Credits 15 pack ($15)
  4. AI Generator one-time ($10)
  5. Q&A Management one-time (TBD)
- [ ] Get product variant IDs from dashboard
- [ ] Configure webhook URL in Lemon Squeezy
- [ ] Update Railway environment variables with Lemon Squeezy credentials
- [ ] Test checkout flow end-to-end

## Files Modified

### Backend
- `backend/app/api/lemon_squeezy.py` (created)
- `backend/app/core/config.py` (modified)
- `backend/app/main.py` (modified)
- `backend/.env.example` (modified)

### Frontend
- `frontend/src/app/pricing/page.tsx` (modified)
- `frontend/src/app/payment/success/page.tsx` (modified)

## Technical Notes

- Parallel implementation: Stripe code remains intact
- Reusing existing database tables: payment_transactions, user_subscriptions
- Using httpx for HTTP requests (already in requirements.txt)
- PAYMENT_PROCESSOR env var allows switching between processors
- Lemon Squeezy fee: 5% + $0.50 per transaction
- Lemon Squeezy is MoR (Merchant of Record): handles all tax compliance

---

## Work Log

### Previous Session
- Implemented Lemon Squeezy backend integration
- Created checkout and webhook endpoints
- Committed backend changes to git

### Current Session
- Modified frontend pricing page to use Lemon Squeezy endpoint
- Updated FAQ to mention Lemon Squeezy payment methods
- Updated payment success page to handle both Stripe and Lemon Squeezy
- Committed frontend changes (3b1a6c1)
- Pushed all changes to remote repository
- All code implementation complete

---

## Review Section

### Code Changes Completed

**Backend (Previous Session)**
1. Created `backend/app/api/lemon_squeezy.py`:
   - `/api/lemon-squeezy/create-checkout-session` endpoint
   - `/api/lemon-squeezy/webhook` endpoint with HMAC signature verification
   - Handlers for order_created and order_refunded events
   - Maps plan codes to Lemon Squeezy variant IDs

2. Updated `backend/app/core/config.py`:
   - Added 9 Lemon Squeezy environment variables
   - Added PAYMENT_PROCESSOR selection flag

3. Updated `backend/app/main.py`:
   - Registered lemon_squeezy router

4. Updated `backend/.env.example`:
   - Documented all Lemon Squeezy configuration variables

**Frontend (Current Session)**
1. Updated `frontend/src/app/pricing/page.tsx`:
   - Changed checkout endpoint to Lemon Squeezy
   - Simplified success URL (no session_id placeholder)
   - Updated FAQ payment methods section

2. Updated `frontend/src/app/payment/success/page.tsx`:
   - Made compatible with both Stripe and Lemon Squeezy
   - No session_id required for Lemon Squeezy (webhook-based)

### Key Technical Decisions

- Parallel implementation: Stripe code remains intact for future flexibility
- Reused existing database schema (payment_transactions, user_subscriptions)
- No new dependencies needed (httpx already in requirements.txt)
- Simple endpoint swap on frontend (no dual payment UI needed)
- Webhook-based payment confirmation for Lemon Squeezy

### Git Commits

- Backend: commit 372c6de
- Frontend: commit 3b1a6c1
- All changes pushed to origin/main

### Remaining Manual Steps

User must complete these setup tasks:

1. Finish Lemon Squeezy account creation
2. Create 5 products in Lemon Squeezy dashboard:
   - Credits 4 pack: $4
   - Credits 10 pack: $10
   - Credits 15 pack: $15
   - AI Generator: $10 (one-time)
   - Q&A Management: TBD (one-time)
3. Copy variant IDs from dashboard
4. Set up webhook URL: https://your-domain.com/api/lemon-squeezy/webhook
5. Update Railway environment variables:
   - LEMON_SQUEEZY_API_KEY
   - LEMON_SQUEEZY_STORE_ID
   - LEMON_SQUEEZY_WEBHOOK_SECRET
   - LEMON_SQUEEZY_VARIANT_CREDITS_4
   - LEMON_SQUEEZY_VARIANT_CREDITS_10
   - LEMON_SQUEEZY_VARIANT_CREDITS_15
   - LEMON_SQUEEZY_VARIANT_AI_GENERATOR
   - LEMON_SQUEEZY_VARIANT_QA_MANAGEMENT
   - PAYMENT_PROCESSOR=lemon_squeezy
6. Test end-to-end checkout flow

### Implementation Quality

- All changes are minimal and focused
- No breaking changes to existing functionality
- Clean separation between Stripe and Lemon Squeezy
- Database agnostic (works with both processors)
- Frontend gracefully handles both payment flows
- Code ready for production after environment variables are configured
