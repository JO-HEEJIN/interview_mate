# Interview Prep — Directive vs Socratic & Statsig A/B Test

오늘(2026-05-13) 실제 코드/실험 상태 기반으로 작성. 검증 안 된 수치/존재하지 않는 기능 제외.

---

## 사실 베이스라인 (답변 작성 시 절대 넘지 말 것)

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

**셋째, prompt 설계 자체가 결과에 압도적인 영향을 줄 수 있습니다.** 별도 연구에서 확인한 게 있는데, 10줄짜리 STAR reasoning prompt는 단독 환경에서 100% 정답률을 보이지만 60줄짜리 production prompt에 같은 STAR 구조를 끼워넣으면 효과가 거의 사라집니다. prompt 복잡도가 structured reasoning을 희석시킨다는 결과인데, 이건 이번 A/B test가 측정하려는 directive vs socratic 효과보다 잠재적으로 훨씬 큰 변수입니다. 그래서 prompt를 함부로 늘리지 않고 두 variant를 비슷한 분량으로 유지하려고 했습니다."

### 🚨 절대 말하지 말 것

- ❌ "Cache hit rate 30%" — 검증된 수치 아님. 본인 룰 위배.
- ❌ "프로젝트 일시 중단" — 실험은 여전히 running. "데이터 모이는 걸 기다리는 단계"가 정확.
- ❌ "Session completion rate 측정" — rate 아님. event_count임. rate 계산하려면 별도 작업 필요.

---

## 키워드 흐름

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

## 자기 룰 (이 답변의 핵심 가치)

> "검증 안 된 수치를 변호하기보다 갭을 인정하는 게 낫다."

면접관에게 정직성과 자기 인식 능력을 동시에 보여주는 답변. 30%, "context-aware toggle", "session-type detection" 같은 검증 불가능한 디테일을 빼고, 오늘 실제로 발견하고 고친 버그를 정직성의 근거로 사용.
