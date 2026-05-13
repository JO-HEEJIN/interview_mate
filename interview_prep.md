# Interview Prep — Latency, Directive vs Socratic & Statsig A/B Test

오늘(2026-05-13) 실제 코드/실험 상태 기반으로 작성. 검증 안 된 수치/존재하지 않는 기능 제외.

---

## 사실 베이스라인 — A/B Test (답변 작성 시 절대 넘지 말 것)

| 항목 | 실제 상태 |
|---|---|
| 실험명 | `interview_system_prompt_v1` (Statsig) |
| 시작일 | 2026-03-19 |
| 파라미터 | `system_prompt_variant` = `"A"` or `"B"` |
| Prompt A | Directive coaching (직접 피드백, 인지 부하 낮음) |
| Prompt B | Socratic (잘한 점 인정 → 약한 부분에 깊이 있는 질문 하나) |
| 배분 | 50/50, user_id 해싱 기반 |
| 실제 적용 | `backend/app/api/websocket.py`에서 `get_variant()` → `get_prompt_for_variant()` → Claude system prompt 분기 |
| Cumulative Exposures (오늘 기준) | unique users 6명 (Test 4, Control 2) |
| Primary Metric | `feedback_satisfaction_score (mean)` — 오늘 생성 |
| Secondary Metrics | `feedback_submitted (event_count)`, `session_completed (event_count)`, `session_started (event_count)` |
| Hypothesis | "Prompt B는 Prompt A보다 mean user satisfaction을 15% 이상 높인다" |
| 통계 결과 | **없음.** sample size 부족 (n=6) |
| Context-aware toggle | ❌ **존재하지 않음** |
| User override UI | ❌ **존재하지 않음** |
| 세션 타입(live vs practice) 기반 분기 | ❌ **존재하지 않음** |

## 사실 베이스라인 — Latency Pipeline

| 항목 | 실제 상태 | 위치 |
|---|---|---|
| MediaRecorder 내부 버퍼링 | 100ms | `frontend/src/hooks/useAudioRecorder.ts:417` |
| WebSocket 청크 전송 간격 | **1000ms (1초)** | `useAudioRecorder.ts:41` (`chunkInterval = 1000`) |
| Silence detection (프론트) | 800ms | `useAudioRecorder.ts:44` |
| Silence detection (Deepgram EOT) | 800ms | `deepgram_service.py:59` (`eot_timeout_ms=800`) |
| STT 모델 | Deepgram **Flux** (`flux-general-en`) | `deepgram_service.py:55` |
| Fallback STT | Whisper-1 / Nova-3 | `deepgram_service.py:390` |
| 오디오 포맷 변환 | FFmpeg, asyncio subprocess (비동기) | `deepgram_service.py:156, 176` |
| Claude streaming | 활성화 (`messages.stream(...)`) | `claude.py:713-726` |
| Claude 모델 | `claude-sonnet-4-6` | memory + config |
| **End-to-end latency 측정** | ❌ **없음** | — |
| Per-component latency 측정 | ❌ **없음** (session duration만 측정) | `websocket.py:827, 1092` |
| "sub-500ms" 출처 | Deepgram 공식 marketing 수치, **자체 측정 아님** | — |
| "2.5초", "800ms first token", "1.5-2s total" | **검증 불가**, 코드에 없음 | — |

---

## 답변 1 — Sub-500ms Latency 어떻게 달성?

### 1차 답변 (30초)

"정확히 말씀드리면, 이력서의 'sub-500ms'는 STT 레이어, 즉 Deepgram Flux의 공식 transcription latency 표방치를 기반으로 한 표현이고, 제가 production에서 직접 측정해서 확인한 숫자는 아닙니다.

직접 검증한 건 아키텍처와 silence detection 동작입니다. 1초 단위 오디오 청크를 WebSocket으로 전송하면 백엔드가 FFmpeg를 asyncio subprocess로 비동기 변환해서 Deepgram streaming에 흘려보내고, 800ms 무음이 감지되면 end-of-turn으로 처리해서 Claude streaming 호출이 트리거됩니다. Claude streaming은 활성화돼있지만 first-token이나 total response time을 측정하는 instrumentation은 아직 안 깔려 있습니다."

### 2차 답변 (면접관이 더 깊이 물으면)

"파이프라인 구조를 분해하면 네 단계입니다.

**1단계:** 프론트엔드 MediaRecorder가 100ms 단위로 audio chunk를 내부 버퍼링하고, 1초마다 WebSocket으로 백엔드에 전송합니다 (`useAudioRecorder.ts:41`).

**2단계:** 백엔드가 WebM/Opus를 FFmpeg async subprocess로 linear16 PCM 변환합니다 (`deepgram_service.py:156`). 동기 처리하면 audio 입력이 막히기 때문에 `asyncio.create_subprocess_exec`로 백그라운드 conversion task를 띄웁니다.

**3단계:** Deepgram Flux streaming STT입니다. `eot_timeout_ms=800`이라 800ms 무음이면 utterance 종료로 인식합니다. 프론트엔드 silence detection과 정확히 일치시켜서 양쪽이 같은 타이밍으로 turn을 끊도록 했습니다.

**4단계:** Claude Sonnet 4.6 streaming입니다. `messages.stream()`으로 token 단위 yield해서 사용자가 첫 응답을 빨리 볼 수 있게 합니다.

**솔직한 한계:** end-to-end latency나 단계별 latency를 측정하는 instrumentation을 아직 안 깔았습니다. 측정되는 건 session 전체 duration뿐이라 각 컴포넌트의 실제 latency 수치는 추정에 의존합니다. production scale-up 전에 OpenTelemetry 또는 자체 timing log를 컴포넌트별로 까는 게 우선 todo입니다. '2.5초 이내' 같은 wall은 사용자 행동 관찰에서 나온 design intent지 측정 결과가 아닙니다."

### 🚨 절대 말하지 말 것 (원본 답변에 있던 검증 불가 수치)

- ❌ "100ms 단위 오디오 청크를 WebSocket으로 전송" — **실제 1000ms (1초)**. 100ms는 MediaRecorder 내부 버퍼 단위지 WS 전송 주기 아님.
- ❌ "전체 파이프라인 latency 약 2.5초 이내" — **측정 instrumentation 없음**. 검증 불가.
- ❌ "first token까지 약 800ms, 전체 응답까지 1.5-2초" — **코드 어디에도 측정 없음**. 외부 벤치마크일 가능성.
- ❌ "sub-500ms"를 본인이 측정한 것처럼 단정 — Deepgram **vendor claim**임을 반드시 명시.

### 💡 이 답변의 강점

1. **vendor claim과 자체 측정을 구분** — 면접관이 "어떻게 측정?" 물어도 안 막힘
2. **검증된 숫자만 사용** (1000ms WS 인터벌, 800ms silence, 100ms 버퍼)
3. **instrumentation gap을 자기가 짚음** — 시니어 신호
4. **next step (OpenTelemetry) 명시** — 단순 비판이 아니라 개선 방향까지

---

## 답변 2 — Directive vs Socratic Prompt 스타일

### 1차 답변 (45초)

"두 가지 코칭 스타일을 비교하는 A/B 실험을 production에 배포했습니다.

**Prompt A (Directive)** 는 즉시 피드백 스타일입니다. 답변의 구조와 명확성을 평가하고 구체적인 개선점을 직접 짚어줍니다. 압박 상황에서 인지 부하가 낮고, 사용자가 당장 답이 필요할 때 유리합니다.

**Prompt B (Socratic)** 는 답을 주는 대신 안내합니다. 먼저 잘한 점을 구체적인 예시로 인정하고, 가장 약한 부분에 대해 깊이 있는 질문 하나를 던집니다. 사용자가 따라 외우는 게 아니라 스스로 발견하게 만듭니다. 학습과 retention에는 더 효과적이라는 가설입니다.

인프라는 Statsig로 50/50 split을 구현했고, 백엔드가 사용자 ID 해시로 그룹을 배정한 뒤 해당 프롬프트를 Claude API에 주입합니다. 가설은 'Socratic이 평균 satisfaction rating을 15% 이상 높인다'입니다."

### 2차 답변 (결과 물으면) — 정직 카드와 연결

"솔직하게 말씀드리면, 인프라는 완성됐지만 통계적으로 의미 있는 결과는 아직 없습니다. unique exposed users가 6명입니다.

다만 오늘 실험 상태를 점검하면서 의미 있는 버그를 하나 발견하고 고쳤습니다. feedback rating(+1=👍, -1=👎)을 Statsig에 보낼 때 `StatsigEvent.value` 필드 대신 metadata에 string으로 넣고 있었습니다. 그래서 Statsig가 event count는 잡았지만 평균을 계산할 수가 없었어요. numeric value 필드로 전송하도록 수정했고, 이제 `feedback_satisfaction_score (mean)` 메트릭이 자동 생성돼서 실험의 Primary Metric으로 연결돼 있습니다.

즉 인프라 측면에서는 SDK 호출, variant 배정, prompt 분기, 이벤트 로깅, 메트릭 집계까지 end-to-end로 작동하는 상태가 됐고, 다음은 트래픽이 모이는 걸 기다리는 단계입니다."

### 🚨 절대 말하지 말 것 (원본 답변에 있던 fabricated 내용)

- ❌ "Directive 사용은 라이브 인터뷰 세션에서, Socratic은 연습 세션에서 더 많았다" — 데이터 없음. 배정은 user_id 해시 기반이지 세션 타입 기반이 아님.
- ❌ "Context-aware toggle을 만들었다 / 시스템이 세션 타입을 감지해서 모드를 기본값으로 설정한다" — 존재하지 않는 기능.
- ❌ "사용자가 override 가능" — UI에 그런 버튼 없음 (👍👎는 feedback 수집용이지 variant 선택 아님).

### 💡 A/B Test 메커니즘 이해 (면접관이 깊이 물을 때)

**자주 헷갈리는 점 (본인도 처음에 헷갈렸음):**

> "👍는 Socratic 선호, 👎는 Directive 선호 아니야?"

**아니에요.** 메커니즘은 이렇게 작동합니다:

```
로그인 시점:
  user_id → hash → 50% 확률로 A 또는 B 배정 → 영구 고정

세션 진행:
  A 그룹 사용자 → 항상 Directive 답변만 받음 → 👍/👎 누름
  B 그룹 사용자 → 항상 Socratic 답변만 받음 → 👍/👎 누름

각 user_id의 모든 👍/👎는 자기 그룹 버킷으로 들어감.
"어느 버튼을 눌렀냐"가 아니라 "어느 그룹에서 누가 눌렀냐"가 attribution.
```

따라서:
- Socratic 그룹 사용자가 👍 1번 + 👎 1번 누르면 → Socratic mean rating = 0
- Directive 그룹에는 그 사용자 데이터 안 들어감
- 그 사용자가 어느 그룹인지는 `hash(user_id)`로 결정됨, 사용자는 모름

**핵심:** randomization으로 두 그룹의 confounder(노이즈)를 평균적으로 동일하게 만든 뒤, 그룹 간 outcome 차이를 prompt 스타일 효과로 귀속시키는 게 A/B test의 논리. sample size가 커야 그 귀속이 통계적으로 valid함.

---

## 답변 3 — Statsig A/B Test 결과 (정직 카드)

### 1차 답변 (30-45초)

"Statsig A/B test 인프라는 실제로 production에 배포되어 작동합니다. variant 배정, 시스템 프롬프트 분기, 이벤트 로깅까지 end-to-end로 동작합니다.

다만 정직하게 말씀드릴 부분이 있습니다. **InterviewMate 트래픽이 통계적 유의성을 확보할 sample size에 도달하지 못했습니다.** 오늘 기준 unique exposed users 6명입니다. Test 4명, Control 2명. 그래서 'Socratic이 Directive보다 낫다/못하다'는 통계적 결론은 가지고 있지 않습니다.

가지고 있는 건 인프라 자체, 그리고 오늘 점검 중에 발견한 데이터 파이프라인 버그를 추적해서 고친 경험입니다."

### 2차 답변 (더 깊이 물으면)

"이 경험에서 세 가지 학습이 있었습니다.

**첫째, A/B test 인프라 구축과 그것을 의미 있게 활용하는 건 별개 문제입니다.**
SDK 호출되고 이벤트 들어오는 것까지는 됐는데, 메트릭 정의가 잘못돼서 Statsig가 평균을 계산할 수 없는 형태로 데이터가 쌓이고 있었습니다. `log_event`의 value 파라미터 대신 metadata에 string으로 rating을 넣어서, 자동 생성되는 Sum/Mean 메트릭에 값이 비어 있었어요. event count는 잡혔지만 satisfaction 평균 자체를 집계할 수 없는 상태. 오늘 그걸 발견하고 `StatsigEvent.value`로 numeric 전송하도록 수정해서 commit/push 했습니다.

**둘째, MVP 솔로 제품에서 sample size가 안 나오는 단계에서는 통제된 실험보다 사용 로그 기반 행동 관찰이 더 실용적인 경우가 많습니다.** 어느 단계에 어느 도구를 쓰는지 판단하는 게 중요합니다. 다만 인프라는 미리 깔아두면 트래픽 늘었을 때 즉시 활용 가능합니다. 그래서 지금 단계에서도 인프라 자체는 유지하는 게 합리적이라고 봤습니다.

**셋째, prompt 설계 자체가 결과에 압도적인 영향을 줄 수 있습니다.** 별도 연구에서 확인한 게 있는데, 10줄짜리 STAR reasoning prompt는 단독 환경에서 100% 정답률을 보이지만 60줄짜리 production prompt에 같은 STAR 구조를 끼워넣으면 효과가 거의 사라집니다. prompt 복잡도가 structured reasoning을 희석시킨다는 결과인데, 이건 이번 A/B test가 측정하려는 directive vs socratic 효과보다 잠재적으로 훨씬 큰 변수입니다. 그래서 prompt를 함부로 늘리지 않고 두 variant를 비슷한 분량으로 유지하려고 했습니다.

**넷째, outcome metric의 construct validity도 처음부터 신경 썼어야 했습니다.** 지금 Primary metric으로 쓰는 👍/👎 feedback은 사실 'prompt 스타일에 대한 평가'가 아니라 '방금 받은 답변 전반에 대한 평가'입니다. latency, 모델 품질, RAG 컨텍스트, 질문 난이도 같은 confounder가 다 섞여 들어옵니다. randomization으로 이 노이즈를 상쇄하려면 sample size가 더 커야 하는데, 그게 안 되는 단계에서는 더 직접적인 outcome — 예를 들어 같은 질문에 두 답변을 보여주고 사용자가 선택하게 하는 within-user comparison, 또는 며칠 후 같은 질문을 다시 했을 때의 retention 기반 학습 효과 — 같은 측정을 설계했어야 한다는 회고가 있습니다."

### 🚨 절대 말하지 말 것

- ❌ "Cache hit rate 30%" — 검증된 수치 아님. 본인 룰 위배.
- ❌ "프로젝트 일시 중단" — 실험은 여전히 running. "데이터 모이는 걸 기다리는 단계"가 정확.
- ❌ "Session completion rate 측정" — rate 아님. event_count임. rate 계산하려면 별도 작업 필요.

---

## 사실 베이스라인 — Contamination Prevention

| 주장 | 검증 결과 | 위치 |
|---|---|---|
| Qdrant payload에 user_id 저장 | ✅ | `qdrant_service.py:126-130` |
| Qdrant search `must` filter (user_id) | ✅ | `qdrant_service.py:257-263` |
| LRU cache key `f"{user_id}:{normalized_q}"` | ✅ | `claude.py:414, 453` |
| user_id 없으면 cache skip (안전장치) | ✅ | `claude.py:407-409` |
| Cross-user prefix filtering | ✅ | `claude.py:426-427` |
| `find_relevant_qa_pairs(user_id=...)` | ✅ | `claude.py:289-294` |
| Per-user `_qa_indices` dict | ✅ | `claude.py:511-527` |
| Supabase RLS on qa_pairs | ✅ | `migrations/002:25, 28-38` |
| RLS on interview_sessions, session_messages | ✅ | `migrations/032:77-90` |
| Session 변수 connection-local | ✅ | `websocket.py:348-367` |
| Audio = streaming pipes only, no disk write | ✅ | `deepgram_service.py` 전체 |
| Example dedup 스코프 | ⚠️ **per-session** (per-user 아님) | `websocket.py:366`, `migrations/032:116-128` |
| `clear_cache()` 글로벌 wipe | ⚠️ **알려진 갭** — 모든 동시접속자 영향 | `claude.py:468-473` |

---

## 답변 4 — User_id Split Contamination 방지

### 1차 답변 (45초)

"user_id scoping은 access control에 해당하고, contamination(데이터 교차 오염)은 별개 문제로 분리해서 다뤘습니다.

InterviewMate에서 세 가지 contamination 벡터를 분리해서 처리했습니다.

**첫째, Qdrant 벡터 스토어.** 모든 임베딩 payload에 user_id를 저장하고, semantic search 쿼리는 `must` filter clause로 user_id 매칭을 강제합니다. 사용자 A의 이력서 컨텍스트가 사용자 B의 RAG 결과에 섞이지 않게 했습니다.

**둘째, in-memory LRU cache.** Cache key를 `user_id:question_hash` 형태로 namespace 분리했고, user_id가 없으면 아예 cache를 skip하는 안전장치까지 넣었습니다. 같은 질문을 두 사용자가 해도 각자의 배경 기반 답변을 받게 됩니다.

**셋째, session history.** WebSocket connection-local 변수로 관리하고, example deduplication은 per-session scope로 동작합니다. 공유 example pool 없음."

### 2차 답변 (면접관이 더 깊이 물으면)

"가장 paranoid하게 신경 쓴 영역은 semantic cache였습니다. Cache hit은 정의상 공유 응답이기 때문입니다. Cache key를 user-scoped로 만들고, 추가로 iteration할 때 prefix check를 한 번 더 해서 같은 사용자가 같은 질문 패턴을 보낼 때만 cache hit이 발생하게 했습니다.

Zero audio storage도 가장 명백한 contamination surface를 제거하는 결정이었습니다. 오디오는 FFmpeg asyncio subprocess의 stdin/stdout 파이프로만 흐르고 Deepgram에 직접 stream됩니다. 디스크, S3, Supabase storage 어디에도 persist되지 않습니다. 저장 안 하면 leak할 수 없으니까요.

디자인 원칙은 RLS를 데이터베이스에서 끝내지 않고 **모든 레이어** — Qdrant 벡터 스토어, in-memory cache, WebSocket session memory — 에 일관되게 적용하는 것이었습니다. Supabase RLS는 `qa_pairs`, `interview_sessions`, `session_messages` 테이블에 모두 `auth.uid() = user_id` 정책으로 적용돼있고, 애플리케이션 레이어가 그걸 우회할 수 없게 모든 query에서 user_id를 명시적으로 전달합니다."

### 💡 면접관이 깊이 물을 때 — 알려진 갭

"한 가지 알고 있는 갭은 `clear_cache()`가 글로벌 singleton wipe라는 점입니다 (`claude.py:468-473`). 사용자 A가 cache clear 요청을 보내면 사용자 B의 in-memory cache까지 함께 비워집니다.

**데이터 누출은 아닙니다** — 키가 `user_id:` prefix로 namespace 분리돼있어서 다른 유저 데이터를 읽을 수 없습니다. 하지만 **DoS 벡터**입니다. 사용자 A가 사용자 B의 working cache를 의도적으로 무효화할 수 있어요.

수정 방법은 `clear_cache(user_id)` 시그니처로 바꿔서 해당 prefix entry만 삭제하면 됩니다. contamination은 아니지만 multi-tenancy 관점에서 고쳐야 할 사항으로 인지하고 있습니다."

### 🚨 미세 정확성 보정 (원본 답변 대비)

- ⚠️ "Example deduplication도 per-user scope" → 정확히는 **per-session(connection-local)**. 한 사용자가 두 세션을 돌리면 첫 세션 example이 두 번째 세션에 dedup되지 않음. 사용자 관점 결과는 비슷하지만 면접관이 정확히 물으면 *per-session*이 맞음.
- ✅ 나머지 주장은 모두 코드로 검증됨 (위 베이스라인 테이블 참조).

---

## 사실 베이스라인 — Supabase RLS 사건

| 항목 | 실제 상태 | 위치 |
|---|---|---|
| 발견 경로 | **Supabase Security Advisor 자동 flag** (본인 발견 아님) | migration 038 주석 |
| 실제 노출 테이블 수 | **3개** | `038_enable_rls_security_fix.sql` |
| 노출 테이블 목록 | `questions`, `star_stories`, `talking_points` | migration 038 |
| `qa_pairs` 노출 여부 | ❌ **노출 안 됨** (migration 002부터 RLS 있었음) | `migrations/002:25, 28-38` |
| `interview_sessions` 노출 여부 | ❌ **노출 안 됨** (migration 032부터 RLS 있었음) | `migrations/032:77-90` |
| 수정 마이그레이션 | `038_enable_rls_security_fix.sql` (2026-03-04) | — |
| Anon key 브라우저 노출 | ✅ **의도된 설계** (`NEXT_PUBLIC_SUPABASE_ANON_KEY`) | `frontend/src/lib/supabase.ts:3-6` |
| 백엔드 인증 방식 | **service_role key** (RLS 우회) | `backend/app/core/supabase.py:18` |
| 백엔드 보호 메커니즘 | RLS 아님 → **application-layer user_id 필터링** | 모든 API route |
| 현재 RLS 커버리지 | 17/17 테이블 모두 RLS + policy 적용 | 전체 migrations |
| "2 critical vulnerabilities" 표현 | ⚠️ **repo에 없음** — 본인 해석 | — |
| "schema exposure"를 vulnerability로 셈 | ⚠️ **generic Supabase 동작**이지 이 프로젝트 고유 취약점 아님 | — |

---

## 답변 5 — Supabase Anon Key RLS 사건

### 1차 답변 (45초)

"Supabase Security Advisor가 RLS가 비활성화된 3개 테이블을 flag해서 수정한 사건이었습니다.

Supabase anon key는 브라우저에 노출되는 public JWT입니다. PostgREST가 자동 생성한 REST endpoint에 접근하는 자격증명인데, **RLS 정책이 없으면 그 anon key만으로 데이터를 읽고 쓸 수 있습니다.**

InterviewMate에서 실제 영향받은 테이블은 `star_stories`(사용자 STAR 응답), `talking_points`(이력서 talking points), `questions`(공용 reference 데이터)였습니다. user-owned 데이터인 `qa_pairs`, `interview_sessions`는 처음부터 RLS가 적용돼있었지만, 이후에 추가된 테이블들에서 ENABLE RLS 구문이 빠져있던 게 원인이었습니다.

수정은 `038_enable_rls_security_fix.sql`로 3개 테이블 모두 RLS + `auth.uid() = user_id` 정책 적용해서 해결했고, 그 이후로 모든 user-owned 테이블에 RLS를 일관되게 적용하는 워크플로를 정착시켰습니다."

### 2차 답변 (면접관이 더 깊이 물으면)

"이 사건에서 두 가지 학습이 있었습니다.

**첫째, `public key` ≠ `safe without RLS`.** Anon key는 design상 브라우저에 노출되는 public credential이지만, '공개됐다'와 '안전하다'는 다른 명제입니다. RLS 없으면 anon key 하나로 데이터 read/write가 가능합니다. 그래서 이후로는 Supabase 테이블을 추가할 때 **`CREATE TABLE`과 같은 마이그레이션 안에서 `ENABLE ROW LEVEL SECURITY` + policy를 같이 작성**하는 패턴으로 굳혔습니다. 분리하면 잊어버립니다.

**둘째, RLS만 의존하는 게 충분하지 않다는 점.** 백엔드 FastAPI는 `SUPABASE_SERVICE_ROLE_KEY`를 사용하는데, service role은 design상 RLS를 우회합니다. 즉 백엔드에서는 RLS가 안전망 역할을 못 합니다. 그래서 모든 백엔드 query에 `.eq('user_id', user_id)` 같은 application-layer 필터를 명시적으로 넣어서, RLS 우회 경로에서도 cross-user access가 안 되게 만들었습니다.

정리하면 **다층 방어**입니다:
- 프론트엔드 직접 쿼리 (anon key) → DB RLS가 막음
- 백엔드 쿼리 (service_role) → application-layer user_id 필터가 막음
- Qdrant 쿼리 → `must` filter가 막음 (RLS 아님, vector store filter)
- In-memory cache → key prefix namespacing이 막음 (RLS 아님, application 패턴)

각 레이어가 같은 원칙(user_id 격리)을 자기 메커니즘으로 enforce합니다."

### 🚨 절대 말하지 말 것 (원본 답변 대비 정정 사항)

- ❌ "2 critical vulnerabilities" — repo 어디에도 없는 표현. Supabase Security Advisor는 "**RLS disabled on 3 tables**"로 flag함. 정확한 표현 사용.
- ❌ "schema 노출이 critical vulnerability 중 하나" — PostgREST의 generic 동작이지 이 프로젝트 고유 취약점이 아님. 면접관이 "그건 Supabase 기본 아닌가요?"로 반박 가능. **빼는 게 안전**.
- ❌ "사용자 Q&A 프로필, 세션 기록, 인터뷰 응답 캐시가 cross-access 가능한 상태였다" — `qa_pairs`(migration 002)와 `interview_sessions`(migration 032)는 처음부터 RLS 있었음. 실제 노출 테이블은 `star_stories`, `talking_points`, `questions`. **사실관계 정정 필수**.
- ⚠️ "user-scoped RLS를 모든 레이어에 적용했다 — DB, Qdrant, cache" — 개념은 OK지만 technically imprecise. Qdrant에는 RLS 개념 자체가 없음(filter clause). Cache도 RLS 아님(prefix namespace). 면접관이 "Qdrant에 RLS가 어떻게 적용되나요?"로 들어가면 막힘. **"각 레이어가 같은 원칙을 자기 메커니즘으로 enforce"라고 정확히 표현**.

### 💡 강한 자체 인지 (선택 사용)

면접관이 "어떻게 발견하셨나요?"라고 물으면:

"**솔직히 제가 코드를 보다가 발견한 게 아니라, Supabase Security Advisor 대시보드가 flag한 걸 보고 수정한 케이스입니다.** 그게 오히려 학습 포인트였어요 — 보안 이슈는 자기 눈으로 못 잡는 경우가 많아서 자동화된 advisor / linter / scanner를 layer로 깔아두는 게 단일 reviewer보다 reliable하다는 점입니다. 이후로 Supabase 마이그레이션 추가할 때마다 Security Advisor 페이지를 routine check하는 게 워크플로에 들어갔습니다."

---

## 키워드 흐름

**답변 1:**
- "sub-500ms"는 Deepgram Flux **vendor claim**, 자체 측정 아님 (정직성 카드)
- 검증된 숫자: WS 1초 인터벌, MediaRecorder 100ms 버퍼, silence detection 800ms (프론트=백엔드 일치)
- 아키텍처: WS → FFmpeg async → Deepgram Flux streaming → Claude streaming
- Instrumentation gap 인정 + OpenTelemetry next-step 명시

**답변 2:**
- Directive = 직접 답, 인지 부하 낮음, 압박 상황
- Socratic = 가이드 질문, 학습/retention
- Statsig 50/50 split, user_id 해시 기반 배정
- 백엔드가 Claude API에 system prompt 분기 주입
- 가설: Socratic → satisfaction 15%↑

**답변 3:**
- 인프라 구축 OK (end-to-end 작동)
- Sample size 6명, 통계 결론 불가
- 오늘 발견/수정한 버그: rating이 metadata string으로 들어가서 Mean 집계 안 됨 → value 필드 numeric으로 수정
- 학습 1: 인프라 ≠ 활용 (메트릭 정의가 핵심)
- 학습 2: MVP 솔로 단계 = 관찰이 실험보다 실용적, 인프라는 선제적으로
- 학습 3: prompt 복잡도가 reasoning structure를 희석 (car wash 연구 연결)
- 학습 4: outcome metric의 construct validity — 👍/👎는 prompt 스타일 평가가 아니라 답변 전반 평가. confounder 다수. within-user comparison이나 retention 기반 측정이 더 valid했을 것

**답변 4:**
- Access control vs Contamination 개념 분리
- 3 벡터: Qdrant must filter / LRU cache user_id namespacing / WS session 변수 connection-local
- Zero audio storage = pipes only, no persistence (가장 명백한 surface 제거)
- 다층 RLS: DB(Supabase auth.uid()) + 애플리케이션(user_id explicit pass) + cache(prefix namespace)
- 알려진 갭: `clear_cache()` 글로벌 wipe = DoS 벡터 (contamination 아님)
- 미세 보정: example dedup은 per-user 아닌 **per-session** scope

**답변 5:**
- Supabase Security Advisor가 flag → 3개 테이블 RLS missing (`questions`, `star_stories`, `talking_points`)
- "2 critical vulnerabilities" 표현 X / "schema exposure"는 generic Supabase 동작이지 vulnerability 아님 — **둘 다 빼야**
- 실제 노출된 데이터: STAR 응답, talking points (Q&A pairs/sessions는 처음부터 RLS 보호됨 — 정정 필요)
- Fix: migration 038로 3개 테이블에 RLS + policy 적용
- 핵심 인사이트: 'public key' ≠ 'safe without RLS' / 백엔드는 service_role 사용 → application-layer user_id 필터 필수
- 다층 방어: DB RLS / app filter / Qdrant must filter / cache prefix — **각 레이어가 같은 원칙을 자기 메커니즘으로 enforce** (RLS 만능 아님)
- 정직 카드: Security Advisor가 자동 발견한 거지 본인이 코드 보다 찾은 게 아님

## 자기 룰 (이 답변의 핵심 가치)

> "검증 안 된 수치를 변호하기보다 갭을 인정하는 게 낫다."

면접관에게 정직성과 자기 인식 능력을 동시에 보여주는 답변. 30%, "context-aware toggle", "session-type detection" 같은 검증 불가능한 디테일을 빼고, 오늘 실제로 발견하고 고친 버그를 정직성의 근거로 사용.
