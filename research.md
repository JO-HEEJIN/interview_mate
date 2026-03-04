# InterviewMate - Technical Research Document

> Hiring manager call prep: 코드베이스 전체를 분석한 팩트시트.
> 모든 수치, 모델명, 설정값은 실제 코드에서 확인한 것.

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
