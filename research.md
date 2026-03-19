# InterviewMate - Technical Research Document

---

## 1. High-Level Architecture

InterviewMate는 실시간 면접 코칭 도구. 면접 오디오를 듣고, AI 답변 제안을 2초 이내에 생성.

**Core Pipeline:**
```
Audio (Browser/Overlay) → Deepgram STT (WebSocket) → Question Detection (Regex <1ms)
  → RAG + Context Lookup (parallel asyncio.gather) → Claude Sonnet 4.6 (streaming)
  → WebSocket → Client UI (실시간 표시)
```

**Tech Stack:**
- **Frontend:** Next.js 16, React 19, TypeScript, Tailwind v4, Supabase Auth
- **Backend:** FastAPI, Python 3.11, Uvicorn
- **Database:** Supabase (PostgreSQL + pgvector + RLS)
- **Vector DB:** Qdrant (semantic search)
- **LLM:** Claude Sonnet 4.6 (primary), GLM-4-Flash (code only, 미사용)
- **STT:** Deepgram Flux (streaming), Whisper-1 (fallback)
- **Embeddings:** OpenAI text-embedding-3-small (1536-dim)
- **Payments:** Stripe + Lemon Squeezy (dual processor)
- **Deployment:** Railway (backend), Vercel (frontend)
- **macOS Overlay:** Swift 5.9, AppKit, WKWebView, ScreenCaptureKit

---

## 2. Claude API Integration

### 2.1 Model & Client
- **Model:** `claude-sonnet-4-6` (하드코딩, `claude.py:217`)
- **Client:** `anthropic.Anthropic` (sync client, streaming은 context manager 사용)
- **Production Strategy:** `LLM_SERVICE=claude` (Claude only)

### 2.2 Streaming
- `client.messages.stream()` → sync context manager
- `stream.text_stream`에서 chunk 단위로 yield
- WebSocket으로 각 chunk를 `answer_stream_chunk` 타입으로 전송
- 로깅: `[Streaming] Requested: {model} | Actual: {model} | Usage: input={tokens}, output={tokens}`

### 2.3 Prompt Caching
```python
system=[{
    "type": "text",
    "text": system_prompt,
    "cache_control": {"type": "ephemeral"}  # Anthropic Prompt Caching
}]
```
- System prompt는 user_profile 기반으로 동적 생성되지만 세션 중 안정적
- 같은 세션 내 모든 질문에서 cache hit → ~90% 비용 절감

### 2.4 Tool Use
- **답변 생성:** Tool Use 미사용 (pure text streaming)
- **Q&A 추출 (fallback):** `save_qa_pairs` tool로 structured JSON 추출
  - Tool schema: `{qa_pairs: [{question, answer, question_type}]}`
  - `claude-sonnet-4-6`, max_tokens=8192

### 2.5 System Prompt 구조 (`_get_system_prompt()`)
```
You are {이름}, interviewing for {역할} at {회사}.

# Your Background
{프로젝트 요약} + Key Strengths

# Your Interview Style
- PREP: Point → Reason → Example → Point
- 구체적 숫자/메트릭, tradeoff 인정, 과도한 긍정 금지

# Communication Style (질문 타입별 word count)
- Yes/No → 10 words
- Direct → 30-80 words (PREP)
- Behavioral → 60-120 words (STAR)
- Compound → 100-150 words

# Answer Style: {concise|balanced|detailed}
- concise: max 30 words, bullet points
- balanced: 30-60 words
- detailed: 60-100 words

# Core Rules
1. ALWAYS answer the ACTUAL question asked
2. Use EXACT numbers from background (e.g., "92.6%" not "about 90%")
3. If prepared Q&A doesn't match, ignore them completely
```

### 2.6 Question Type Detection (`_detect_question_context()`)

| Type | Max Tokens | Instruction |
|------|-----------|-------------|
| yes_no | 40-60 | "YES/NO - MAXIMUM 5-10 WORDS" |
| direct | 80-200 | "Concisely using PREP structure" |
| deep_dive | 200-500 | "Thorough answer using specific background" |
| clarification | 60-150 | "MAXIMUM 30 WORDS" |
| general | 150-400 | "Using your specific background" |

- **Frustration detection:** "stop", "hold on", "that's not what i asked" → max_tokens 반감

---

## 3. Multi-Provider LLM Routing

### LLMService (`llm_service.py`)
```python
self.strategy = settings.LLM_SERVICE  # "claude" | "glm" | "hybrid"
```

| Strategy | Primary | Fallback | 현재 Production |
|----------|---------|----------|----------------|
| claude | Claude | None | **이것 사용 중** |
| glm | GLM-4-Flash | None | 미사용 |
| hybrid | GLM → Claude | Claude | 미사용 |

- `inspect.signature()`로 서비스별 지원 파라미터 동적 감지
- GLM은 코드에만 존재, latency 문제로 프로덕션 미사용
- GLM-4-Flash 가격: ~$0.00014/1K tokens (Claude 대비 ~7x 저렴)

---

## 4. Caching & Retrieval (3-Layer)

### Layer 1: In-Memory Answer Cache
- **Key:** `{user_id}:{normalized_question}`
- **Normalization:** 소문자, 구두점 제거, 공백 정리
- **Exact match:** O(1) dict lookup
- **Fuzzy match:** SequenceMatcher + Token Jaccard, **threshold 0.85**
- **Max size:** 50 entries, LRU eviction
- **Privacy:** user_id 없으면 캐시 접근 거부

### Layer 2: Uploaded Q&A Fast Lookup
- Per-user dict에 인덱싱 (`build_qa_index()`)
- 질문 + 모든 variations → normalized key로 매핑
- **Exact match:** O(1)
- **Similarity fallback:** 0.85 threshold, early exit at 0.95
- **성능:** <1ms (기존 ~500ms에서 개선)

### Layer 3: Qdrant RAG (Semantic Search)
- **Embedding:** OpenAI text-embedding-3-small (1536-dim)
- **Distance:** Cosine similarity
- **Threshold:** 0.55 (find_relevant_qa_pairs에서)
- **Max results:** 5개
- **Direct match:** similarity >= 0.70이면 stored answer 직접 반환 (LLM skip)
- **Compound question:** regex로 분해 → 각 sub-question 병렬 검색
- **Per-question timeout:** 5초

### Multi-Strategy Similarity (`calculate_similarity()`)
1. **Substring match:** shorter가 5+ words & longer의 40%+ → return 0.95
2. **Token Jaccard:** intersection/union of word tokens
3. **SequenceMatcher:** character-level difflib
4. → 세 전략 중 최대값 반환

---

## 5. Real-Time Pipeline

### 5.1 WebSocket Flow (`/ws/transcribe`)

**Client → Server:**
- Binary audio chunks (WebM/Opus)
- JSON messages: `config`, `context`, `generate_answer`, `start_recording`, `clear`, `finalize`

**Server → Client:**
- `transcription` (interim + final)
- `question_detected` (auto-detect)
- `answer_temporary` → `answer_stream_start` → `answer_stream_chunk` → `answer_stream_end`
- `credit_consumed` / `no_credits`

### 5.2 Question Detection (2-stage)

**Stage 1: Fast Pattern (`detect_question_fast`, <1ms)**
- Regex-based: question marks, question words, behavioral patterns
- Returns: `{is_question, question, question_type, confidence: "high"|"low"}`
- 기존 gpt-4o 호출 → regex heuristic으로 교체 (비용 절감)

**Stage 2: Claude Fallback (low confidence만)**
```python
if detection["confidence"] == "low" and detection["is_question"]:
    detection = await claude_service.detect_question(accumulated_text)
```

**Completeness Validation:**
- < 5 words → incomplete
- Ends with `?` → complete
- >= 8 words → complete (punctuation 무관)

### 5.3 Answer Generation (2 paths)

**Path A: Auto-Detect (on final transcript)**
1. `find_matching_qa_pair_fast()` — O(1) exact match
2. Cache hit → return stored answer instantly
3. Cache miss → parallel fetch:
   ```python
   await asyncio.gather(
       get_session_history(session_id),      # DB
       get_session_examples(session_id),     # DB
       claude_service.find_relevant_qa_pairs(question, user_id)  # Qdrant
   )
   ```
4. Stream answer via `llm_service.generate_answer_stream()`

**Path B: Manual (`generate_answer` message)**
- 동일 구조, user가 직접 "Generate Answer" 버튼 클릭 시

### 5.4 TTFT Optimization (RAG Parallelization)
- **Before:** Sequential: session DB → RAG → Claude = ~300ms overhead
- **After:** Parallel: session DB + RAG → Claude = ~100ms overhead
- `pre_fetched_qa_pairs` 파라미터로 caller가 미리 가져온 RAG 결과 전달
- 3개 파일 수정: `websocket.py`, `claude.py`, `llm_service.py`

---

## 6. Speech-to-Text (Deepgram)

### DeepgramStreamingService
- **Model:** `flux-general-en` (v2 API)
- **Encoding:** linear16 (PCM)
- **Sample Rate:** 16,000 Hz
- **EOT Threshold:** 0.7 (end-of-turn detection)
- **EOT Timeout:** 800ms
- **Eager EOT:** 0.3

### Audio Pipeline
```
Client (WebM/Opus) → ffmpeg (PCM 16kHz mono) → Deepgram WebSocket → Transcript callback
```
- ffmpeg subprocess: `ffmpeg -f webm -i pipe:0 -f s16le -ar 16000 -ac 1 pipe:1`
- Chunk size: 2560 bytes = 160ms at 16kHz mono
- Fallback: Whisper-1 (batch mode)

---

## 7. Q&A Extraction (Dual Provider)

### Primary: OpenAI Structured Outputs
- **Model:** `gpt-4o-2024-08-06`
- **Method:** `beta.chat.completions.parse()` + Pydantic schema
- **Schema:** `QAPairList(qa_pairs: List[QAPairItem])` → 100% valid JSON
- Source: `extract_qa_pairs_openai()`

### Fallback: Claude Tool Use
- **Model:** `claude-sonnet-4-6`, max_tokens=8192
- **Tool:** `save_qa_pairs` → structured JSON extraction
- Source: `extract_qa_pairs_claude()`
- Trigger: OpenAI 호출 실패 시 자동 fallback

---

## 8. Q&A Generation (AI-Powered)

### Distribution Strategy
**Initial Batch (30 Q&As):**
- 18 resume-based (60%) — behavioral + technical from experience
- 7 company-aligned (23%) — situational matching culture
- 5 job-posting (17%) — gap analysis
- 5 general — common questions personalized

**Incremental Batch (10 Q&As):**
- 5 resume-based, 2 company-aligned, 2 job-posting, 1 general

- **Model:** GPT-4o-mini (cheaper)
- **Temperature:** 0.8 (higher diversity)
- Categories generated in parallel via `asyncio.gather()`

---

## 9. Database Schema (Supabase/PostgreSQL)

### Core Tables (17개)
| Category | Tables |
|----------|--------|
| User | profiles, user_interview_profiles |
| Content | qa_pairs, star_stories, talking_points, questions, user_contexts, resumes |
| Sessions | interview_sessions, session_messages |
| Billing | pricing_plans, user_subscriptions, payment_transactions, credit_usage_log |
| AI | generation_batches |

### Row Level Security (RLS)
- 모든 user-owned 테이블에 RLS 적용 (`auth.uid()` 기반)
- questions, pricing_plans: public read-only
- Service role key는 RLS bypass (backend server-side)

### Key Stored Procedures
1. `consume_interview_credit()` — FIFO credit consumption + logging
2. `get_user_interview_credits()` — total available credits
3. `user_has_feature()` — feature access check
4. `grant_free_credits_on_signup()` — 3 credits auto-grant
5. `end_interview_session()` — mark complete, update stats
6. `find_similar_qa_pairs()` — pgvector semantic search (threshold 0.80)

### Vector Support
- `qa_pairs.question_embedding`: vector(1536)
- Index: IVFFlat, cosine distance, 100 lists
- Model: text-embedding-3-small

---

## 10. Credit & Billing System

### Pricing Plans
| Plan | Price | Credits | Type |
|------|-------|---------|------|
| credits_starter | $4 | 10 | credits |
| credits_popular | $8 | 25 | credits (20% off) |
| credits_pro | $15 | 50 | credits (25% off) |
| ai_generator | $10 | - | one_time feature |
| qa_management | $25 | - | one_time feature |
| free_starter | $0 | 3 | credits (signup bonus) |

### Credit Flow
1. User clicks "Start Recording" → `start_recording` message
2. Backend: `consume_interview_credit()` RPC (FIFO, oldest first)
3. Success → `credit_consumed` + remaining count
4. Failure → `no_credits` → redirect to /pricing

### Payment Processors
- **Stripe:** Primary, webhook handles `checkout.session.completed`
- **Lemon Squeezy:** Alternative, HMAC SHA-256 signature verification
- `PAYMENT_PROCESSOR` config selects active processor

---

## 11. macOS Overlay App

### Architecture
- Menu bar app (`LSUIElement = true`, Dock 아이콘 없음)
- WKWebView로 InterviewMate 웹앱 로드
- NSWindow: floating, transparent (85% opacity), 480x680

### System Audio Capture (ScreenCaptureKit)
```swift
config.capturesAudio = true
config.excludesCurrentProcessAudio = true
config.channelCount = 1
config.sampleRate = 16000
```
- Float32 PCM → Base64 인코딩 → JS로 전달
- Silence detection: 500 consecutive silent buffers (~10초) → auto-restart
- Track ended → native capture 자동 정지

### JavaScript Bridge (getDisplayMedia Proxy)
```javascript
navigator.mediaDevices = new Proxy(realMediaDevices, {
    get: (target, prop) => {
        if (prop === 'getDisplayMedia') return patchedGetDisplayMedia;
        // ...
    }
});
```
- Frontend가 `getDisplayMedia()` 호출 → Proxy가 intercept
- Native ScreenCaptureKit 시작 → `window.__nativeAudioQueue`에 audio push
- Frontend의 ScriptProcessorNode가 queue에서 직접 읽기
- Mic + system audio를 AudioContext에서 mix

### Keyboard Shortcuts
| Shortcut | Action |
|----------|--------|
| Cmd+Up/Down | Opacity +/-10% |
| Cmd+Shift+P | Toggle Always on Top |
| Cmd+Shift+T | Toggle Click Through (global hotkey, Carbon) |

### TCC Permission
- `CGRequestScreenCaptureAccess()` → system prompt
- 실패 시 NSAlert + System Settings 직접 링크
- Binary rebuild → TCC 무효화 (code signature 변경) → user가 재등록 필요

---

## 12. Frontend Details

### Audio Capture (Browser)
- **Sample Rate:** 16,000 Hz
- **Format:** WebM + Opus codec
- **Bitrate:** 128kbps
- **Chunk Interval:** 1000ms
- **Silence Threshold:** RMS < 5 for 800ms → finalize
- Echo cancellation, noise suppression, auto gain control enabled
- AudioWorklet (modern) → ScriptProcessorNode (fallback)

### Real-Time UI Components
- **TranscriptionDisplay:** Live text + pulsing cursor + word count
- **AnswerDisplay:** Streaming chunks with source badge (Pre-loaded/AI Generated)
- **AudioLevelIndicator:** 20-bar spectrum, color gradient green→red
- **RecordingControls:** Start/Pause/Resume/Stop + system audio toggle

### Multi-Profile System
- React Context (`ProfileContext`) for state management
- `localStorage.activeProfileId` persistence
- Profile switching → re-sends context to WebSocket
- CRUD: create, update, delete, duplicate, set-default

---

## 13. API Endpoints Summary

| Category | Endpoints | Key Features |
|----------|-----------|-------------|
| Interview Profiles | 8 endpoints | Multi-profile CRUD, set-default, duplicate |
| STAR Stories | 4 endpoints | CRUD with profile_id filter |
| Talking Points | 4 endpoints | CRUD with priority ordering |
| Q&A Pairs | 9 endpoints | CRUD, bulk-parse (Claude), bulk-upload, Qdrant sync |
| Context Upload | 7 endpoints | Resume PDF, screenshot OCR, text paste, AI Q&A generation |
| Interview Sessions | 6 endpoints | Start/end, messages, history, export (JSON/MD/text) |
| Subscriptions | 7 endpoints | Plans, credits, features, usage log |
| Payments (Stripe) | 3 endpoints | Checkout, webhook, session status |
| Payments (Lemon Squeezy) | 2 endpoints | Checkout, webhook |
| WebSocket | 1 endpoint | `/ws/transcribe` (real-time) |

---

## 14. Key Thresholds & Constants

| Component | Value | Purpose |
|-----------|-------|---------|
| Answer Cache Similarity | 0.85 | Question match for cache hit |
| Q&A Index Similarity | 0.85 | Fast lookup match |
| Q&A Index Early Exit | 0.95 | Skip remaining checks |
| RAG Search Threshold | 0.55 | Find relevant Q&As (permissive) |
| RAG Direct Match | 0.70 | Skip LLM, use stored answer |
| Qdrant Cosine Threshold | 0.80 | Vector search quality |
| Substring Match | 5+ words, 40%+ length | Multi-strategy similarity |
| Cache Max Size | 50 entries | LRU eviction |
| Max RAG Results | 5 | Per question |
| Max Sub-Questions | 3 | Compound decomposition |
| Audio Chunk Size | 2560 bytes | 160ms at 16kHz |
| Silence Duration | 800ms | Finalize trigger |
| Silent Buffer Auto-Restart | 500 buffers (~10s) | Overlay SCStream restart |

---

## 15. Cost Optimization Techniques

1. **Prompt Caching** (`cache_control: ephemeral`) — ~90% cost reduction on system prompt
2. **RAG Direct Match** (>= 0.70) — skip LLM generation entirely
3. **Answer Cache** (in-memory) — skip both RAG and LLM
4. **Regex Question Detection** — replaced gpt-4o call (<1ms vs ~1000ms)
5. **Regex Question Decomposition** — replaced gpt-4o call (<1ms vs ~500-2000ms)
6. **GPT-4o-mini for Q&A Generation** — cheaper than GPT-4o
7. **text-embedding-3-small** — ~$0.02/1M tokens
8. **RAG Parallelization** — asyncio.gather() reduces TTFT by ~200ms
9. **Multi-provider routing** — GLM-4-Flash available as 7x cheaper fallback (architecture ready)

---

## 16. Privacy & Security

1. **Cache Scoping:** `{user_id}:{question}` key, no user_id → access denied
2. **Qdrant Filtering:** `user_id` payload filter on every search
3. **RLS:** All user tables enforced at DB level (`auth.uid()`)
4. **GDPR Deletion:** `delete_user_qa_pairs()` for complete vector removal
5. **Service Role Key:** Server-only, never exposed to client
6. **Supabase Anon Key:** Client-side, RLS-protected

---

## 17. Deployment

| Component | Platform | Notes |
|-----------|----------|-------|
| Backend | Railway | Docker, ffmpeg pre-installed |
| Frontend | Vercel | Next.js 16, auto-deploy |
| Database | Supabase | PostgreSQL + pgvector + RLS |
| Vector DB | Qdrant Cloud | Or self-hosted on Railway |
| Overlay | Local build | Swift Package Manager |

**Backend Dockerfile:**
```dockerfile
FROM python:3.11-slim
RUN apt-get update && apt-get install -y ffmpeg
COPY requirements.txt . && pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**38 migrations**, 17 core tables, 12+ stored procedures, 40+ indexes.

---
---

# Security Audit Research

> Date: 2026-03-07
> Source: Black-box 외부 감사 보고서 (`interviewmate_security_audit.docx`) + 코드베이스 내부 조사 (5개 병렬 에이전트)
> Scope: 8개 취약점 + 추가 발견 1건에 대한 코드 레벨 팩트시트 및 수정 계획

---

## Finding #1: Full Database Schema Exposed via Supabase REST API

### 현재 상태
- 17개 테이블 모두 `public` 스키마에 존재
- 별도 스키마(private, internal 등) 없음
- PostgREST 노출 스키마 설정 없음 (Supabase 기본값 = public 전체 노출)
- Supabase config.toml 또는 supabase.json 없음 (Dashboard에서만 관리)
- REST API `/rest/v1/` 엔드포인트가 OpenAPI/Swagger 스펙 전체 노출

### 노출되는 민감 테이블/컬럼
| 테이블 | 민감 컬럼 |
|--------|-----------|
| profiles | password_hash, stripe_customer_id, email |
| payment_transactions | stripe_payment_intent_id, stripe_charge_id, receipt_url |
| user_contexts | extracted_text (이력서 원문) |
| resumes | file_url, extracted_text |
| user_subscriptions | stripe_customer_id, lemon_squeezy_customer_id |

### 노출되는 RPC 함수 (12개)
- consume_interview_credit, find_similar_qa_pairs, get_user_interview_credits
- user_has_feature, get_user_features_summary, get_session_history
- get_session_examples, end_interview_session, grant_free_credits_on_signup 등

### 수정 계획
**Option A: Supabase Dashboard에서 API 노출 제한** (권장, 즉시 가능)
1. Supabase Dashboard > Settings > API > Schema settings
2. 노출 스키마에서 민감 테이블 제외하거나, 별도 `api` 스키마 생성 후 필요한 것만 노출

**Option B: private 스키마로 민감 테이블 이동** (마이그레이션 필요)
1. `CREATE SCHEMA private;` 생성
2. 민감 테이블(payment_transactions, credit_usage_log 등)을 private 스키마로 이동
3. 프론트엔드에서 직접 접근하지 않는 테이블만 이동 가능
4. 백엔드는 service_role_key로 접근하므로 스키마 무관

**Option C: PostgREST 에러 힌트 비활성화** (Finding #7 동시 해결)
- Supabase Dashboard > Settings > API > "Extra search path" 설정 조정

### 관련 파일
- `backend/database/migrations/` — 38개 마이그레이션 전체
- `backend/app/core/config.py` — Supabase 설정

---

## Finding #2: password_hash Column in profiles Table

### 현재 상태
- **마이그레이션:** `backend/database/migrations/005_add_password_hash.sql`
  - Line 3: `ADD COLUMN IF NOT EXISTS password_hash TEXT`
  - Line 6: `CREATE INDEX IF NOT EXISTS idx_profiles_password_hash ON public.profiles(password_hash) WHERE password_hash IS NOT NULL`
- **백엔드 참조:** 없음 (Python 코드에서 미사용)
- **프론트엔드 참조:** 없음 (Supabase Auth만 사용: `supabase.auth.signUp()`, `supabase.auth.signInWithPassword()`)
- **RLS 정책:** profiles 테이블 SELECT/UPDATE (`auth.uid() = id`) — password_hash 컬럼 필터링 없음

### 위험도
- Supabase Auth는 `auth.users` 테이블에서 별도로 비밀번호 관리
- profiles.password_hash는 **완전히 dead column** — 어디서도 사용하지 않음
- RLS 우회 시 모든 사용자의 password_hash 노출 가능

### 수정 계획
```sql
-- 새 마이그레이션: 039_remove_password_hash.sql
DROP INDEX IF EXISTS idx_profiles_password_hash;
ALTER TABLE public.profiles DROP COLUMN IF EXISTS password_hash;
```

### 관련 파일
- `backend/database/migrations/005_add_password_hash.sql` — 컬럼 생성
- `backend/database/migrations/001_initial_schema.sql:115-119` — profiles RLS 정책

---

## Finding #3: Open User Registration

### 현재 상태
- **회원가입:** Supabase Auth에 위임 (`supabase.auth.signUp()`)
- **프론트엔드:** `frontend/src/app/auth/register/page.tsx`
  - 이메일 + 비밀번호 (최소 8자) + 이름
  - OAuth (Google, GitHub) 지원
  - 환불 정책 동의 체크박스 필수
- **이메일 인증:** Supabase Dashboard 설정에 의존 (코드에서 제어 불가)
  - 프론트엔드에 "Check your email to confirm your account" 메시지 존재 → 인증 활성화 상태로 추정
  - 에러 페이지에도 "Error sending the verification email" 핸들링 있음
- **가입 시 자동 처리:**
  1. `handle_new_user()` 트리거 → profiles 레코드 생성
  2. `grant_free_credits_on_signup()` 트리거 → 3 크레딧 부여
- **disable_signup:** `false` (Supabase 기본값)

### RLS 정책 전수 검토 — `authenticated` vs `auth.uid()` 체크

**결과: 모든 사용자 데이터 테이블이 `auth.uid() = user_id` 사용 (안전)**

| 테이블 | 정책 | USING 절 |
|--------|------|----------|
| profiles | SELECT/UPDATE | `auth.uid() = id` |
| resumes | CRUD | `auth.uid() = user_id` |
| star_stories | CRUD | `auth.uid() = user_id` |
| talking_points | CRUD | `auth.uid() = user_id` |
| sessions | SELECT/INSERT/UPDATE | `auth.uid() = user_id` |
| session_answers | SELECT/INSERT | subquery → `sessions.user_id = auth.uid()` |
| qa_pairs | CRUD | `auth.uid() = user_id` |
| user_contexts | CRUD | `auth.uid() = user_id` |
| generation_batches | SELECT/INSERT/UPDATE | `auth.uid() = user_id` |
| user_interview_profiles | CRUD | `auth.uid() = user_id` |
| user_subscriptions | SELECT only | `auth.uid() = user_id` |
| payment_transactions | SELECT only | `auth.uid() = user_id` |
| credit_usage_log | SELECT only | `auth.uid() = user_id` |
| interview_sessions | ALL | `auth.uid() = user_id` |
| session_messages | ALL | subquery → `interview_sessions.user_id = auth.uid()` |
| questions | SELECT only | `USING (true)` — 공개 |
| pricing_plans | SELECT only | `USING (is_active = true)` — 공개 |

### 수정 계획
1. **Supabase Dashboard에서 이메일 인증 필수 확인** (이미 활성화 상태로 추정)
2. **Rate limiting 추가** (추가 발견과 연계)
3. RLS는 이미 안전 — `authenticated` role만 체크하는 정책 **없음**

---

## Finding #4: Missing Critical Security Headers

### 현재 상태

**백엔드 (FastAPI) — `backend/app/main.py:72-95` SecurityHeadersMiddleware**
| 헤더 | 상태 | 값 |
|------|------|-----|
| X-Content-Type-Options | SET | `nosniff` |
| X-Frame-Options | SET | `DENY` |
| X-XSS-Protection | SET | `1; mode=block` |
| Referrer-Policy | SET | `strict-origin-when-cross-origin` |
| Strict-Transport-Security | SET (prod) | `max-age=31536000; includeSubDomains` |
| Server header | REMOVED | |
| Content-Security-Policy | **MISSING** | |
| Permissions-Policy | **MISSING** | |

**프론트엔드 (Next.js) — `frontend/next.config.ts`**
- 설정 비어있음 (빈 NextConfig 객체)
- 보안 헤더 없음
- middleware.ts 없음

**Vercel — `frontend/vercel.json`**
- 기본 빌드 설정만 존재
- 보안 헤더 설정 없음
- Vercel 기본 헤더에만 의존

### 수정 계획

**A. 프론트엔드 — `frontend/next.config.ts`에 헤더 추가:**
```typescript
const nextConfig: NextConfig = {
  async headers() {
    return [
      {
        source: "/(.*)",
        headers: [
          { key: "X-Frame-Options", value: "DENY" },
          { key: "X-Content-Type-Options", value: "nosniff" },
          { key: "Referrer-Policy", value: "strict-origin-when-cross-origin" },
          { key: "Permissions-Policy", value: "camera=(), microphone=(self), geolocation=()" },
          {
            key: "Content-Security-Policy",
            value: [
              "default-src 'self'",
              "script-src 'self' 'unsafe-inline' 'unsafe-eval'",  // Next.js 필요
              "style-src 'self' 'unsafe-inline'",                  // Tailwind 필요
              "img-src 'self' data: https:",
              "connect-src 'self' https://*.supabase.co wss://*.supabase.co https://api.deepgram.com https://api.stripe.com",
              "frame-ancestors 'none'",
            ].join("; "),
          },
        ],
      },
    ];
  },
};
```

> CSP 주의: `unsafe-inline`/`unsafe-eval`은 Next.js 동작에 필요. microphone=(self)는 인터뷰 기능에 필수.

**B. 백엔드 — `backend/app/main.py` SecurityHeadersMiddleware에 추가:**
```python
response.headers["Content-Security-Policy"] = "default-src 'none'; frame-ancestors 'none'"
response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
```

### 관련 파일
- `backend/app/main.py:72-95` — SecurityHeadersMiddleware
- `frontend/next.config.ts` — 빈 설정
- `frontend/vercel.json` — 기본 설정

---

## Finding #5: Wildcard CORS Policy

### 감사 보고서 vs 코드 불일치 발견

**감사 보고서:** `Access-Control-Allow-Origin: *` (와일드카드)

**코드 (`backend/app/core/config.py:71-80`):**
```python
CORS_ORIGINS: List[str] = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "https://interviewmate.tech",
    "https://www.interviewmate.tech"
]
CORS_ALLOW_CREDENTIALS: bool = True
CORS_ALLOW_METHODS: List[str] = ["*"]
CORS_ALLOW_HEADERS: List[str] = ["*"]
```

**분석:**
- 백엔드 Origins는 명시적 화이트리스트 — **코드 상 안전**
- Methods/Headers만 와일드카드 (Origins 제한으로 수용 가능)
- 감사 보고서의 `*` 발견은 **프론트엔드(Vercel) 응답** 또는 **Supabase REST API 응답**일 가능성 높음
- `TrustedHostMiddleware`가 `allowed_hosts=["*"]`로 되어 있으나 CORS와 무관

### 확인 필요 사항
- Vercel 프론트엔드 응답의 CORS 헤더 확인 (curl로 테스트)
- Supabase REST API의 CORS 응답 확인

### 수정 계획
1. 백엔드 CORS는 이미 적절 — 코드 변경 불필요
2. Vercel/Supabase 측 CORS 확인 후 필요 시 제한

---

## Finding #6: Supabase Anon Key Exposed in Frontend Bundle

### 현재 상태
- Supabase anon key는 설계상 공개 (Supabase 공식 문서 확인)
- 프론트엔드 `.env`에서 `NEXT_PUBLIC_SUPABASE_ANON_KEY`로 사용
- 민감 API 키(Deepgram, Claude, Stripe)는 프론트엔드 미노출 (서버 사이드만)

### 위험 완화 요소
- 모든 17개 테이블에 RLS 활성화
- 사용자 데이터 테이블 전부 `auth.uid() = user_id` 체크
- anon key 단독으로는 인증된 사용자 데이터 접근 불가

### 수정 계획
- Finding #1 해결 시 (스키마 노출 차단) 위험도 대폭 감소
- 별도 코드 수정 불필요

---

## Finding #7: Error Messages Leak Table Names

### 현재 상태
- PostgREST 기본 동작: 존재하지 않는 테이블 쿼리 시 "Perhaps you meant..." 힌트
- Finding #1의 스키마 노출과 중복되지만, Swagger 차단해도 남는 문제

### 수정 계획
- Finding #1과 동시 해결 — 스키마 노출 차단 시 에러 힌트도 제한됨
- Supabase Dashboard > API Settings에서 "extra search path" 조정

---

## Finding #8: No security.txt

### 현재 상태
- `frontend/public/.well-known/` 디렉토리 없음
- `security.txt` 파일 없음

### 수정 계획
```
# frontend/public/.well-known/security.txt
Contact: security@interviewmate.tech
Expires: 2027-03-07T00:00:00.000Z
Preferred-Languages: en, ko
Canonical: https://interviewmate.tech/.well-known/security.txt
```

---

## 추가 발견: WebSocket 인증 미검증 (보고서 외) — CRITICAL

### 코드 조사 중 감사 보고서에 없는 심각한 취약점 발견

**백엔드가 서버 사이드 인증(JWT 검증)을 하지 않음**

**현재 인증 흐름:**
```
Frontend (Supabase Client)
    | sends user_id in WebSocket message (no JWT)
    v
WebSocket Endpoint (websocket.py)
    | trusts user_id, no validation
    v
Supabase Client (service_role_key — bypasses RLS!)
    | queries using user_id variable in WHERE clause
    v
Database (RLS bypassed by service_role)
```

**문제 코드:**
- `backend/app/api/websocket.py:428-433` — user_id null 체크만 존재, 유효성 검증 없음
- `backend/app/api/websocket.py:699-727` — 클라이언트가 보낸 user_id로 프로필/Q&A 조회
- `backend/app/core/supabase.py` — `SUPABASE_SERVICE_ROLE_KEY`로 클라이언트 생성 (RLS 우회)

**공격 시나리오:**
1. 공격자가 WebSocket 연결 (`wss://api.interviewmate.tech/ws/transcribe`)
2. 임의의 user_id를 config 메시지에 포함
3. 백엔드가 service_role_key로 `supabase.table("qa_pairs").eq("user_id", fake_id)` 실행
4. RLS 우회되어 타인의 Q&A 데이터, 이력서, 인터뷰 세션 접근 가능

**명시적 auth 미들웨어:** 없음
- FastAPI dependencies에 인증 관련 코드 없음
- Bearer token 검증 없음
- JWT 디코딩 없음

**Rate limiting:**
- `backend/app/core/config.py:94-96`에 설정값 존재 (`RATE_LIMIT_PER_MINUTE: 60`, `RATE_LIMIT_BURST: 10`)
- 하지만 **구현되지 않음** — 미들웨어에 적용 안 됨, `slowapi` 등 패키지 미설치

### 수정 계획
1. **WebSocket 핸드셰이크 시 JWT 토큰 검증 추가**
   - 프론트엔드: Supabase 세션 토큰을 query param 또는 첫 메시지에 포함
   - 백엔드: `supabase.auth.get_user(token)` 또는 JWT 직접 디코딩으로 user_id 추출
   - 클라이언트 제공 user_id 무시, 토큰에서 추출한 user_id만 사용

2. **user 작업에 anon_key + JWT 사용 고려**
   - service_role_key는 관리 작업(크레딧 소비, 배치 처리)에만 사용
   - user 데이터 조회에는 anon_key + 사용자 JWT로 RLS 활용

3. **Rate limiting 실제 구현**
   - `slowapi` 설치 후 미들웨어/디펜던시로 적용
   - WebSocket 연결 수 제한

### 관련 파일
- `backend/app/api/websocket.py` — WebSocket 핸들러
- `backend/app/core/supabase.py` — Supabase 클라이언트
- `backend/app/core/config.py:94-96` — Rate limit 설정값 (미사용)
- `frontend/src/hooks/useWebSocket.ts` — WebSocket 클라이언트

---

## 우선순위 정리

| # | 심각도 | 항목 | 수정 범위 | 작업 유형 |
|---|--------|------|----------|----------|
| 1 | **CRITICAL** | WebSocket JWT 인증 추가 | 백엔드 + 프론트엔드 코드 수정 | 코드 |
| 2 | **CRITICAL** | password_hash 컬럼 제거 | DB 마이그레이션 1개 | SQL |
| 3 | **CRITICAL** | DB 스키마 노출 차단 | Supabase Dashboard 설정 | 수동 |
| 4 | **HIGH** | 보안 헤더 추가 (CSP, Permissions-Policy) | next.config.ts + main.py | 코드 |
| 5 | **HIGH** | CORS 확인 (Vercel/Supabase 측) | 확인 후 필요 시 수정 | 확인 |
| 6 | **MEDIUM** | Rate limiting 구현 | slowapi 설치 + 미들웨어 | 코드 |
| 7 | **LOW** | 에러 메시지 테이블명 유출 | #3과 동시 해결 | 수동 |
| 8 | **INFO** | security.txt 추가 | 정적 파일 1개 | 파일 |

---

## 긍정적 발견 (이미 잘 되어 있는 것)

- 17개 테이블 전부 RLS 활성화 (migration 038에서 누락 3개도 수정 완료)
- 모든 사용자 데이터 정책이 `auth.uid() = user_id` 사용 (단순 `authenticated` 체크 없음)
- 빌링 테이블(user_subscriptions, payment_transactions, credit_usage_log)은 SELECT-only 정책
- HSTS 활성화 (max-age=63072000)
- 민감 API 키(Deepgram, Claude, Stripe) 프론트엔드 미노출
- Source maps 미노출 (.js.map → 404)
- .env, .git/config, /admin 접근 불가
- robots.txt에 /api/, /admin/, /auth/ 크롤링 차단
- 백엔드 CORS origins 명시적 화이트리스트 (4개 도메인만)
- Server 헤더 제거
- 결제 webhook HMAC 서명 검증 (Lemon Squeezy)

---

## 작업 중 발생한 사고 기록 (Post-Mortem)

### 사고 1: CSP 헤더가 프론트엔드 API 호출 전면 차단

**발생 시점:** 2026-03-07, CSP 헤더 추가 후 Vercel 배포 완료 시점
**증상:** "No Profile Selected" — 모든 프로필/구독 데이터 미표시, 콘솔에 CSP 위반 에러 대량 발생
**근본 원인:** `next.config.ts`의 `connect-src`에 Railway 백엔드 URL(`https://*.railway.app`)을 누락. `wss://*.railway.app`만 추가하고 `https://`를 빠뜨림. 또한 Google Fonts URL도 `style-src`/`font-src`에 누락.
**영향:** 프론트엔드에서 백엔드 API 호출이 브라우저 CSP에 의해 전부 차단 → 사이트 사실상 사용 불가
**해결:** `connect-src`에 `https://*.railway.app` 추가, `style-src`에 `https://fonts.googleapis.com`, `font-src`에 `https://fonts.gstatic.com` 추가 → 커밋 `140b6dd`
**교훈:**
- CSP 헤더 추가 시 반드시 **모든 외부 도메인**을 확인 (API, WebSocket, 폰트, 스타일시트 등)
- CSP는 한 번에 배포하지 말고, 먼저 `Content-Security-Policy-Report-Only` 모드로 테스트 후 적용하는 것이 안전
- 배포 직후 브라우저 개발자 도구 Console 확인 필수

### 사고 2: Supabase "Harden Data API"로 스키마 노출 차단 시도 → 백엔드 장애 위험

**발생 시점:** 2026-03-07, Supabase Dashboard에서 Harden Data API 실행
**시도한 작업:** `public` 스키마를 Exposed schemas에서 제거하고 빈 `api` 스키마만 노출
**위험:** 백엔드가 Supabase Python SDK(`supabase.table()`)를 사용하는데, 이는 내부적으로 PostgREST REST API를 호출. `public` 스키마가 Exposed schemas에서 제거되면 **service_role_key로도 테이블 접근 불가** (RLS bypass ≠ 스키마 노출 설정)
**실제 결과:** 설정 페이지에서 `public`이 여전히 남아있어 실제 장애는 발생하지 않음 (Supabase UI가 자동 복구했거나 제거가 완전히 적용되지 않음)
**교훈:**
- Supabase Harden Data API는 **프론트엔드가 REST API를 직접 사용하지 않는 경우에만** 안전하게 적용 가능
- 그러나 **백엔드가 Supabase SDK를 사용하면 PostgREST 의존** → public 스키마 제거 불가
- 스키마 노출 차단의 대안: RLS 강화 + password_hash 제거로 실질적 위험 감소 (이미 완료)
- Supabase 설정 변경 전 반드시 `supabase.table()` / `.rpc()` 사용 여부 확인

### 사고 예방 체크리스트 (향후 참조)

1. **CSP 헤더 추가 전:**
   - 브라우저 Network 탭에서 모든 외부 도메인 목록 수집
   - `Content-Security-Policy-Report-Only`로 먼저 테스트
   - connect-src, style-src, font-src, img-src, script-src 각각 확인
2. **Supabase 스키마 변경 전:**
   - 백엔드가 PostgREST (SDK `supabase.table()`)를 사용하는지 확인
   - 직접 PostgreSQL 연결(`psycopg2`/`asyncpg`)이면 스키마 노출 설정 무관
   - PostgREST 사용 시 `public` 스키마 제거 불가
3. **보안 변경 배포 전:**
   - staging 환경에서 먼저 테스트 (없으면 로컬에서 production 설정으로 테스트)
   - 배포 직후 핵심 유저 플로우 확인 (로그인 → 프로필 로드 → 인터뷰 시작)
