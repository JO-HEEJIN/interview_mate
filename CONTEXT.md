# InterviewMate — Current State

## Product

InterviewMate is an interview preparation and mock-session app. Users add their
own background and target role, generate practice Q&A, and rehearse timed
sessions. Spoken questions are transcribed in real time and the app returns
response suggestions grounded in the user's prepared context.

Public copy describes preparation, rehearsal, and mock sessions. For formal
interviews, exams, and admissions processes, users are told to follow the
organizer's rules and disclose AI assistance where required. Retired pages
that described live-interview use (`/comparison`, `/faq/<lang>`) permanently
redirect to `/faq`.

## Request path

Browser audio (WebM/Opus, 1 s chunks) → FastAPI WebSocket → FFmpeg subprocess
(16 kHz PCM) → Deepgram `flux-general-en` streaming STT with end-of-turn
events (800 ms EOT timeout) → question detection → prepared-answer match
(≥0.85 returns the user's own answer) → Qdrant retrieval filtered by user_id
(up to 3 parallel sub-queries, 5 s timeout each) → Claude `claude-sonnet-4-6`
streaming with prompt caching.

Claude is the only answer model. The GLM hybrid mode in `llm_service.py` is
off by default.

## Authentication and authorization

The backend uses the Supabase service-role client, which bypasses RLS, so
authorization is enforced in the API layer:

- HTTP: `get_current_user_id` verifies the Supabase JWT (401 if missing or
  invalid). Routes with `{user_id}` in the path call `require_user_match`.
- Routes keyed by a resource id enforce ownership:
  - interview sessions: `require_session_owner` (404 if missing, 403 if owned
    by another user) on end, update, messages, history, delete, export
  - STAR stories, talking points, Q&A pairs: update/delete/increment queries
    are filtered by `user_id = <token user>` (404 otherwise)
- Payments: `create-checkout-session` requires the body `user_id` to match the
  token (the webhook grants credits to that id); `reconcile/{user_id}` requires
  a matching token. The webhook is authenticated by HMAC signature instead.
- `/api/interview/generate-answer` and `/detect-question` require a valid token.
- WebSocket: the `context` message must carry a valid `access_token`; a
  client-supplied `user_id` is never trusted.
- Frontend calls authenticated routes through `authFetch`; file exports use
  `authDownload` because a plain link cannot send the Authorization header.

## Known gaps

- `DeepgramStreamingService` is a module-level singleton holding one Deepgram
  connection and FFmpeg process; concurrent sessions are not isolated.
- Anthropic streaming uses the synchronous client inside async code, which
  blocks the event loop while tokens stream.
- Credit-pack `order_created` webhooks are not idempotent on redelivery.
- The 60/min default rate limit is not applied to undecorated routes
  (`SlowAPIMiddleware` is not installed).
- No automated test suite or CI; Sentry is configured but not initialized.
