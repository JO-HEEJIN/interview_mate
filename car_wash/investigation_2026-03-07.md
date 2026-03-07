# Car Wash STAR Investigation (2026-03-07~08)

## 발단
- InterviewMate에서 car wash 질문에 엉뚱한 Pre-loaded 답변이 나옴
- 버그 수정 과정에서 STAR framework 관련 근본적 문제 발견

## 버그 수정 (4건)
1. **calculate_similarity 동일 길이 버그** — `min/max(key=len)` 같은 길이 시 같은 객체 반환 → 0.95 false positive (`260a54f`)
2. **RAG direct match threshold** — 0.70 → 0.85 (`028e5a4`)
3. **Frontend streaming source 미전달** — streamingSourceRef 추가 (`028e5a4`)
4. **비면접 질문 감지** — 패턴 없는 짧은 질문 → low confidence → Claude API 검증 (`dd9a582`)

## STAR Framework 조사

### 발견 1: 논문 프롬프트 ≠ InterviewMate 프롬프트
- **논문 C_role_star:** 10줄, "any question"에 STAR 적용, STAR이 프롬프트 핵심
- **InterviewMate:** 60+줄, STAR은 behavioral 질문에만 적용, PREP이 기본 구조
- InterviewMate는 S-A-R (Task 단계 없음), 논문은 S-T-A-R
- Task 단계("What needs to be accomplished?")가 implicit constraint를 드러내는 핵심

### 발견 2: InterviewMate에서 이전에 "Drive"가 나온 이유
- Anthropic 프로필에서 car wash Q&A 없이 "Drive" 답변 → STAR 때문이라 생각했음
- 답변 분석: "50 meters is a 2-minute round trip" — **거리 기반 추론 (오답 이유)**
- implicit constraint ("차가 세차장에 있어야 함") 언급 없음
- Default 프로필: "Walk. 15 meters is about 10 steps" — 역시 거리 기반 추론
- **둘 다 같은 잘못된 추론, 다른 결론** → Anthropic 프로필의 "Drive"는 우연

### 발견 3: 통제 실험 (experiment_profile_star.py)
Model: claude-sonnet-4-6, Temperature: 0.7, 20 runs × 3 conditions

| 조건 | Pass Rate | Constraint 감지 | 정답+정답이유 |
|------|-----------|----------------|------------|
| A_star_anthropic (InterviewMate + Anthropic 프로필) | **0%** | 0% | 0% |
| B_star_default (InterviewMate + Default 프로필) | **30%** | 35% | 10% |
| C_star_only (논문 원본 프롬프트) | **100%** | 100% | **100%** |

- 논문의 STAR 프롬프트: claude-sonnet-4-6에서도 100% pass, 100% constraint
- InterviewMate 프롬프트에 STAR 넣어도: 0~30% — STAR 효과가 사라짐

### 발견 4: STAR이 작동하지 않는 이유 — "결론 먼저" 구조
Experiment 프로필 (custom instruction: "Use STAR format", Q&A 0개):
```
**Short answer: Walk.**
**STAR breakdown:**
- Situation: Car wash is 50 meters away
- Task: Get your car washed efficiently
- Action: Walk there first to confirm, then **drive your car** to the wash
- Result: No fuel wasted

**The real nuance:** You *have* to drive the car there — it's getting washed.
**Bottom line:** Drive your car to the wash.
```
- STAR reasoning이 실행되어 constraint를 인식함 ("you have to drive the car there")
- **하지만 "Short answer: Walk."을 먼저 출력한 후 STAR 추론**
- InterviewMate 프롬프트의 "Lead with specifics", "Point first" 지시가 결론을 먼저 강제
- 논문 프롬프트는 STAR reasoning이 먼저 실행되어 결론 도출 → 올바른 순서

### 발견 5: 100-run 검증 실험 (2026-03-08)
"20번으로는 부족하다, 100번 돌리자"

**조건:** C_star_only (논문 원본 프롬프트)
**Model:** claude-sonnet-4-6, Temperature: 0.7, **100 runs**

| 지표 | 결과 |
|------|------|
| Pass (Drive) | **100/100 (100%)** |
| Fail (Walk) | 0/100 (0%) |
| Ambiguous | 0/100 (0%) |
| Constraint 감지 | **100/100 (100%)** |
| Pass + Constraint | **100/100 (100%)** |

- 단 한 번의 실패도 없음. 100/100 완벽한 결과.
- 논문의 STAR 프롬프트는 claude-sonnet-4-6에서 **완전히 신뢰할 수 있음**
- 20-run에서의 100%가 우연이 아님을 n=100으로 확인
- 원래 논문(claude-sonnet-4-5)에서 85%였던 것이 모델 향상으로 100%가 됨

### 발견 6: InterviewMate에서의 비결정적 답변 (2026-03-08)
Experiment 프로필 (Q&A 0개, custom instruction에 논문 STAR 프롬프트 포함):
- **같은 질문, 같은 프로필**인데 때로는 "Walk", 때로는 "Drive"
- 11:54 PM → "Walk — clearly." (STAR 추론했으나 constraint 못 잡음)
- 11:56 PM → "Drive to the Car Wash" (STAR 추론으로 constraint 잡음)
- 12:02 AM → "Drive — but only because you need the car washed." (constraint 정확히 잡음)
- **원인:** InterviewMate 프롬프트에서 STAR 효과가 확률적 (30% 수준). Temperature 0.7에서 운 좋으면 맞고 나쁘면 틀림.
- Experiment 프로필 설정: Alex Kim, PhD defences @ Stanford MBA, Background: neural network optimization, 3 papers, Skills: Data analysis, Strengths: Research, Style: Balanced

## 핵심 결론
1. **논문의 실험 결과(C_role_star 85~100%)는 유효** — 짧은 프롬프트에서 STAR reasoning은 작동함
2. **"InterviewMate 프롬프트 아키텍처를 검증했다"는 주장은 틀림** — 실험 프롬프트와 실제 프롬프트가 다름
3. **프롬프트 복잡도가 STAR 효과를 죽임** — 다른 지시들(answer first, be concise, use exact numbers)이 STAR reasoning을 override
4. **"결론 먼저" 패턴이 근본 원인** — 모델이 결론을 먼저 내리고 나서 STAR로 추론하면, 이미 잘못된 결론에 맞춰 추론을 왜곡함
5. **Anthropic 프로필에서의 "Drive"는 우연** — 통제 실험에서 0% pass 확인
6. **STAR 자체는 완벽** — 100/100 (n=100) on claude-sonnet-4-6
7. **모델 향상** — 같은 STAR 프롬프트: claude-sonnet-4-5 85% → claude-sonnet-4-6 100%

## 후속 논문 계획
핵심 주제: **프롬프트 복잡도가 structured reasoning (STAR) 효과를 어떻게 희석시키는가**

논문에 포함할 핵심 데이터:
1. **C_star_only:** 100/100 (100%) — STAR 자체는 완벽하게 작동
2. **InterviewMate + STAR:** 0~30% — 복잡한 프롬프트가 STAR 효과를 죽임
3. **"결론 먼저" 메커니즘:** 모델이 결론을 먼저 출력하면 STAR 추론이 왜곡됨
4. **모델 간 비교:** claude-sonnet-4-5 85% → claude-sonnet-4-6 100% (같은 프롬프트)
5. **프로필 영향:** Anthropic 0%, Default 30% — 프로필 컨텍스트도 STAR에 간섭

## 논문 수정 필요 사항 (원래 논문)
1. 실험이 InterviewMate 프롬프트가 아닌 별도 간소화 프롬프트를 테스트한 것임을 명시
2. STAR 효과가 프롬프트 복잡도에 따라 희석된다는 limitation 추가
3. "결론 먼저 vs 추론 먼저" 순서가 STAR 효과의 핵심 메커니즘일 수 있음을 논의
4. InterviewMate에서 정답이 나온 건 RAG 컨텍스트 또는 persona 우연이었음을 정정

## 실험 코드/결과 위치
- `car_wash/experiment.py` — 원래 논문 실험 (6 conditions)
- `car_wash/experiment_profile_star.py` — 3-condition 실험 스크립트
- `car_wash/results/profile_star_20260307_233627/` — 20-run 실험
- `car_wash/results/c_star_only_100_20260308_002609/` — **100-run 검증 실험**

## 관련 커밋
- `028e5a4` — RAG threshold + frontend source fix
- `260a54f` — calculate_similarity equal-length bug fix
- `dd9a582` — Question detection confidence tightening
- `f64a4a7` — Add Task step to STAR
- `37c6f8b` — [EXPERIMENT] Apply STAR to all questions, remove branching

## 시스템 프롬프트 현재 상태
`backend/app/services/claude.py`의 `_get_system_prompt()`가 **실험 상태**:
- STAR이 모든 질문에 적용 (behavioral만이 아님)
- PREP/질문 유형별 분기 제거됨
- 이 실험 상태를 유지할지 production으로 되돌릴지 결정 필요
