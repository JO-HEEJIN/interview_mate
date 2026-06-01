# diary_v2.md

> InterviewMate UX 재설계 — 이탈 인터뷰 답신 1건이 일으킨 대규모 수정
> 2026-05-25

---

## 시작

피드백을 받고 나서 대규모 수정을 결정했다. 받았던 피드백은:

```
써 보고 느낀 점은 이래요.

1. 뭘 해야 할지 모르겠다.
Start Recording을 눌러서 말하면 그 주제에 대해 자세히 피드백해 주는 거 같지만,
뭘 말하는 게 좋을지부터 생각해야 해서 막막합니다. 면접? 면접이라면 주제는?
내 직업에 관해서? 아니면 일상생활?
그래서 '오늘의 과제' 같은 걸 도입해서 명확한 주제로 말할 수 있는 기능이
있다면 좋겠어요.

2. 복습용 anki export 기능이 있으면 좋겠다.
저는 영어 학습을 anki로 하는데, 제가 학습한 내용을 anki 서식에 맞게 자동으로
원자화든 cloze든 anki 소식에 맞게 적용되고 csv로 내보낼 수 있다면 좋지 않을까
하는 생각이 들었어요. 복습은 중요하니까요.

3. 말하기만 되는 건지?
말하기와 작문은 꽤 관련이 있지 않나 싶은데 작문 쪽이 없어서 아쉬워요.

4. 접근성이 너무 낮아요.
구글에 interviewmate, 인터뷰메이트 등으로 검색하면 똑같은 이름의 사이트가
많이 나와서 어디를 들어가야 할지 모르겠어요.
```

N=1이지만 결정적인 답신이다. 답신 더 받아볼 필요 없다고 판단했다. 이유: 4 피드백 모두 **하나의 근본 원인** — *유저가 무엇을 해야 할지 모른다* — 으로 수렴하기 때문이다.

PR #11~21로 conversion 갭(가격, lock-in, 환불, 신뢰)을 메웠지만 그건 *경제적 layer*였다. 진짜 갭은 *인지 layer* — **유저가 사이트에 들어왔을 때 다음 한 클릭을 모른다**. 30 free credits를 줘도 그 첫 한 클릭이 막막하면 클릭 자체를 안 한다.

---

## 핵심 가설

> 유저는 글을 읽지 않는다. 스크롤도 내리지 않는다. 너무 많은 내용이 온보딩에 있다.

지금 홈페이지에는 4개 풀-스크린 섹션이 있다:

1. Hero (제품 설명 + CTA + bouncing arrow)
2. How It Works (3-step 설명)
3. **Powered by Leading AI Technology** (Deepgram + Claude 소개)
4. Use Cases (4종 면접 타입)

신규 유저가 위에서 아래로 *읽고* 결심하고 *Start Interview* 또는 *View Pricing*을 누른다 — 이게 우리 가정. 실제로는 첫 화면에서 H1 + 한두 줄만 보고 다음 행동을 *그 자리에서* 결정한다. 안 보이면 떠난다.

유저가 "뭘 해야 할지 모르겠다"고 한 건 우리 onboarding이 *설명형*이지 *행동형*이 아니라서다.

해결 방향: **첫 화면에서 한 큰 행동 버튼**. 나머지는 절제.

---

## Block 1 — 메인 페이지 간소화 (가장 작은 surgical 변경)

`frontend/src/app/page.tsx` 손봄. 세 항목:

1. **bouncing 화살표 정적화** — `animate-bounce` 제거. 화살표는 유지 (스크롤 indicator 역할), 움직임만 죽임. 시각적 노이즈 절제.
2. **H1 바로 아래에 큼지막한 "Let's begin" 버튼** — 애니메이션 있는 primary CTA. hover 시 보색(흑백 반전). 클릭 시 `/profile/interview-settings`로 이동.
3. **"Powered by Leading AI Technology" 섹션 통째 제거** — line 104-146. 기술 자랑은 conversion에 도움 안 된다. 절제.

→ 한 번 머지하면 새 신규 유저가 *첫 클릭*까지 막힘이 줄어든다.

---

## Block 2 — Profiles 페이지 대규모 재설계

새 브랜치 `profiles`. 한 PR에 다 들어가지만 commit은 액션별 세분화.

### 2.1. 메뉴 라벨 변경: Settings → Profiles

`Header.tsx`의 메뉴 항목. "Settings"라는 단어는 사이트 전체 설정 느낌인데, 실제로 그 페이지가 하는 일은 *interview profile 한 개 편집*. **Profiles**가 정확.

### 2.2. Your Background 카드 — Write / Upload picker

지금은 비어있으면 그냥 빈 textarea. 신규 유저는 *뭘 적어야 하나* 막막함 (피드백 1번의 변형).

새 흐름:
- 비어있을 때: placeholder "click here"
- 카드 클릭 → 카드 안에 두 버튼 (왼쪽 **Write**, 오른쪽 **Upload**)
- **Write** → 원래 textarea 활성 (기존 동작)
- **Upload** → AI Generator 기능 통째로 modal/window로 등장

### 2.3. Upload window — AI Generator 재활용 + 차이점

AI Generator는 원래 Q&A 생성용. 이제 *background 추출용*으로 재활용. 차이:

- 헤더 텍스트: "AI-Powered Q&A Generation" → **"AI Background Generation"**
- 파일 업로드 라벨 아래에 연한 주황색 작은 글씨: **"only PDF, md, docx"**
- 그 아래 disclaimer: **"(we support English only now)"**
- 기존 *optional*이었던 **Organization Information** + **Interview Details** → **required**
- 사용자 프로필 미니카드 ("Default / Solutions Architect @ OpenAI") 제거
- Generate 버튼 텍스트: "Generate Q&A Pairs" → **"Result"**
- **파싱 로직 변경**: Q&A 30개 생성이 아니라 **유저 background 정보를 정리해 추출**
- "Result" 클릭 시 파싱된 background가 Your Background 카드에 **streaming으로** 채워짐 (시간 걸리니 진행 보이기)
- 출력은 **마크다운 없이** plain text (일반인 가독성)

### 2.4. Profile 페이지 추가 정리 (절제)

- **Communication Style 카드 제거** — 쓸모 없음
- **Skills & Expertise (comma-separated) 제거**
- **Key Strengths (comma-separated) 제거**
- **Your Background 카드 가로폭 확장** — 한 눈에 보이게 (스크롤 절제)
- **Custom Instructions를 cursor pointer로 가려두기** — 고급 유저용 hidden

결과: 화면에 보이는 건 **Basic Information** + **Your Background** 두 카드만.

### 2.5. 하단 애니메이션 CTA — "Go to Interview"

Profile 설정 후 다음 한 클릭이 *명확*해야 함. 페이지 하단에 애니메이션 들어간 큰 버튼 → `/interview`로 이동.

(자동저장 + 기존 Save Profile / Cancel 버튼은 유지)

---

## 작업 방식

- **commit은 액션별 atomic 세분화** (한 commit = 한 의미)
- **PR은 묶음** — Block 1 한 PR, Block 2 한 PR (commit 여러 개)
- **PR body는 내용 요약** (4-section: Why / What / Verification / Out of scope)

---

## 의도적으로 안 하는 것 (out of scope, follow-up)

- **Anki CSV export** (피드백 2번) — 작은 feature, 가치 있지만 별도 PR로
- **작문 모드** (피드백 3번) — product scope 확장, 큰 결정. 데이터 더 모인 후
- **SEO + branding** (피드백 4번) — 마케팅 layer, 별도 trail
- **"오늘의 과제" 시나리오 picker** (피드백 1번의 추가 제안) — Block 2가 onboarding 갭의 *프로필 layer*는 메우지만, 인터뷰 페이지 자체의 onboarding 갭은 별개. follow-up

이 세 가지는 Block 2 머지 후 데이터 보고 결정.

---

## Phase 7 회고 — Block 2 이후 후속 PR들 (2026-05-25 → 06-01)

Block 2 머지 후 follow-up 4개 다 들어감. 순서대로:

### PR #27 — Anki Q&A export (피드백 2번)
- `/profile/qa-pairs`에 ⬇ Export to Anki 버튼. 백엔드 `GET /api/qa-pairs/{user_id}/export` CSV (Front/Back/Tags, UTF-8 BOM, `csv.QUOTE_ALL`)
- 가장 작은 작업이라 첫 자리. 1시간 안에 끝.

### main 직접 commit — "Interview Practice" → "Live Interview"
- 1줄 라벨 변경 2곳 (`interview/page.tsx:486`, `payment/success/page.tsx:149`). PR 안 만들고 main에 직접.
- 피드백 1번의 절반 해결 — "뭘 해야 할지 모르겠다"의 일부 원인이 *라벨이 mock mode를 암시*하는 거였음 (이건 실시간 tool인데).

### PR #28 — Session history + Anki/Text/MD export (피드백 1번 일부 + 2번 후속)
- 사용자가 trade-off (lock-in vs portability) 결정 → **둘 다 가는 결정**. 사이트 히스토리 + 다운로드 동시.
- 기존 `interview_sessions`/`session_messages`에 이미 매 메시지가 저장되고 있었음 (websocket.py:89). 백엔드 추가는 export endpoint 확장 1개. 신규는 frontend 페이지 2개(/profile/sessions, /profile/sessions/[id]).
- `/interview` 헤더에 "📋 Past sessions →" 항상 노출 — 매 세션이 lock-in 신호.

### PR #29 — Onboarding scenario picker (피드백 1번의 나머지 절반)

**문제:** 라벨 변경(B)으론 "뭘 해야 할지 모르겠다"의 절반만 해결. 나머지 절반은 *세션을 시작하기 전 의도 설정*이 없다는 것.

**노출 결정:** Hybrid (첫 세션 모달 + 이후 헤더 링크). 항상 모달은 숙련자 friction, 첫 세션만은 재설정 경로 부재. Hybrid가 두 비용 다 작음.

**Effect 결정 — car_wash 긴장:**
초안에서 "system prompt에 hint 한 줄 추가"를 권장했지만 사용자가 즉시 제동 — "system prompt가 길어질수록 환각/품질 저하 우려". 정당한 지적. car_wash 발견의 정신은 *"레이어 추가 누적이 핵심 reasoning을 희석"*이고, 60줄→61줄에서 dilution이 갑자기 0이 되는 게 아님. 단지 작아질 뿐.

→ **Option 4 (user-turn cue)** 로 선회. 시스템 프롬프트는 한 글자도 안 건드리고 매 question에 `[Round: X]` prefix만 LLM-bound copy에 붙임. RAG search/DB 저장은 raw question 그대로 (cosine 유사도/히스토리 깨끗 유지). Dilution risk 0.

**Chip suggestion 도메인 중립:** InterviewMate는 SWE / PhD / Visa / Marketing 등 다양한 use case. SWE 중심 default chip이면 non-SWE가 답답함. → "Behavioral / System design / Case / Coding / PhD admission / Visa" 6개 혼합.

**구현 분해 (3 commit):**
1. Backend — `websocket.py` scenario state + 컨텍스트 핸들러 + LLM 호출 직전 prefix
2. Frontend — `ScenarioPickerModal` 컴포넌트 + `sendContext` 타입 확장 (rule 3.0 동기화)
3. Frontend — `/interview` 통합 (localStorage flag, badge, Change link)

**교훈:**
- 사용자가 *본인 코드베이스에서 나온 자기 연구*를 알고 있을 때, 그 연구와 충돌하는 권장은 정직하게 인정하고 대안 제시해야 함. "1줄이라 괜찮아"는 게으른 추정.
- 환각/품질 우려가 있으면 **시스템 프롬프트 무수정** 옵션이 항상 가장 안전. 비용은 attention signal이 약간 더 약하다는 것뿐 — 가까운 user-turn cue는 멀리 있는 system instruction보다 attention 우위.
