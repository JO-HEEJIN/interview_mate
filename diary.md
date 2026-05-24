# diary.md

> InterviewMate 가격·신뢰 정책 재설계 기획
> 2026-05-24

---

## 왜 이걸 다시 손대는가

유저가 40명 가입했는데 결제까지 간 사람이 5명이다. 12.5% 전환율이다. SaaS 평균(2~5%)으로 보면 나쁘지 않은 숫자지만, 우리 제품 특성을 고려하면 *훨씬 더 나와야 정상*이다. 이력서를 올리고 30번 정도 모의 면접을 돌리면 Claude가 사용자 맥락을 거의 외우다시피 한 상태가 되어 답변이 무서울 정도로 개인화된다. 그 단계까지 한 번 가본 유저는 이걸 끊기 어렵다. 결제 전환은 "결제 페이지를 잘 보여주느냐"가 아니라 *그 경험까지 닿게 해주느냐*의 문제다.

지금 무료 체험은 3 세션이다. 3번으로는 절대 그 경험에 닿을 수 없다. RAG 캐시도 비어 있고, Q&A 풀도 좁고, 답변 스타일도 표준값이다. 유저는 "그냥 그저 그런 면접 챗봇"만 보고 떠난다. 그래서 3 → 30으로 끌어올리는 게 이번 작업의 가장 큰 줄기다. 단순히 후하게 주려는 게 아니라, **lock-in이 작동하기 시작하는 임계점까지 끌고 가는** 의도다.

거기에 얹힌 두 가지 더 있다. 환불정책이 *모순된 상태로* 여기저기 흩어져 있어서 신뢰를 깎는다. 그리고 문의·피드백 창구가 푸터에 mailto 한 줄로만 묻혀 있어서 유저가 "문제가 생기면 어디다 말하지" 하고 두려움을 갖는다. 이 두 개도 함께 정리한다.

---

## 진단 — 가정과 사실 대조

작업 전에 코드베이스를 깊게 읽었더니, 내가 "없다"고 생각했던 것들 중 상당수가 *있긴 한데 망가져 있는* 상태였다. 이게 더 위험하다. 새로 만드는 것보다 모순을 청소하는 게 우선이다.

### 진단 1 — 환불정책은 "없다"가 아니라 "모순되어 있다"

- `auth/register/page.tsx:204` 가입 시 체크박스: *"All purchases are final. No refunds except for technical issues within 7 days."*
- `faq/page.tsx:57-58`: 위와 같은 톤 (no refund 원칙 + 기술적 예외)
- **`pricing/page.tsx:309-312`**: *"We offer a 7-day money-back guarantee. Contact support if you're not satisfied."*

가입할 땐 "환불 안 됨"이라고 동의시켜놓고, 가격 페이지에선 "7일 환불 보장"이라고 광고한다. 어느 쪽을 믿어야 할지 모르는 유저는 "이 사람들 정책이 일관성이 없으니 결제 후엔 또 무슨 말이 나올지 모른다"고 본다. 이건 결제 직전에 신뢰를 깎는 가장 흔한 패턴이다.

게다가 정식 정책은 앱 안에 없고, 가입 페이지가 **외부 GitHub `REFUND_POLICY.md` 링크**로 빠진다. 클릭하면 깃허브 raw 마크다운이 뜬다. SaaS 제품에서 가입 직전에 깃허브로 튀는 건 거의 농담에 가깝다. 그리고 그 GitHub 파일조차 "all sales final" 톤이라, 결국 *세 군데 모두 톤이 다르다*.

**결정:** 7-day money-back guarantee로 통일 (가격 페이지 톤이 정답). 정식 정책 문서를 그 톤에 맞춰 다시 쓰고, 앱 안 `/refund` 페이지로 옮긴다. 가입 체크박스도 그 인앱 페이지로 연결한다.

### 진단 2 — Trial 3 세션은 lock-in 임계점 한참 아래

이게 가장 중요한 결정이다. 단순한 숫자 변경처럼 보이지만 가격 사다리 전체를 다시 짜야 한다.

**이유:** 지금 유료 starter 팩이 $4에 10 크레딧이다. 무료를 30으로 올리면 10짜리 팩을 살 이유가 사라진다(이미 30 받았는데 왜 10을 또 사겠나). 그래서 트라이얼 사이즈를 올리는 순간 **그 위 사다리들의 크레딧/가격을 함께 상향 조정**해야 한다.

**원가 현실성 (서브에이전트 조사):**
- Claude Sonnet 4.6 (prompt caching 적용) 1세션 추론 비용: $0.025 ~ $0.054
- Deepgram STT (10~20분): $0.04 ~ $0.10
- 임베딩·DB 부수 비용: 무시 가능
- **1 세션 = $0.07 ~ $0.16 raw API 비용**
- **30 세션 무료 = 유저당 $2 ~ $5 직접 비용**

이 숫자가 결정적이다. 가입자 100명 중 20명이 30세션을 다 쓰고 떠난다 해도 $40~$100. 그 대신 lock-in 효과로 결제 전환이 5명 → 15명만 늘어도 (보수적으로 starter $4 한정) 추가 매출이 손실을 덮는다. 마진을 양보하면서 전환율을 사는 거래다.

**한 가지 우려:** 현재 코드베이스에 **세션당 토큰/비용 로깅이 없다**. 30 세션 트라이얼을 풀어두고 실제 비용이 예상치를 벗어나도 우리는 모른다. 트라이얼 확대와 함께 *최소한의 세션 비용 기록* 정도는 깔아두는 게 안전하다 (별도 작업 항목으로 분리).

### 진단 3 — 피드백·문의 창구는 묻혀 있고 이메일이 3개다

- `Footer.tsx:20`: `info@birth2death.com` (mailto, 동작함)
- `faq/page.tsx:169`: `support@interviewmate.tech` (클릭 안 되는 텍스트)
- `REFUND_POLICY.md`: `support@interviewmate.ai` (또 다른 도메인)

세 군데가 세 가지 이메일을 쓴다. 유저 입장에선 "이 회사가 진짜 존재하는 곳인가?" 의심이 들 수 있다. 그리고 이미 동작하는 푸터 mailto조차 본문 흐름 밖에 있어서 *결제를 망설이는 순간*에 눈에 들어오지 않는다.

**결정:** 세 군데 전부 `info@birth2death.com`으로 통일. 푸터에 환불/문의 링크 추가해서 눈에 띄게. 별도 백엔드/폼은 만들지 않는다 (surgical 원칙 — mailto로 충분).

---

## One-Time Purchase 정책 변경 — "첫 프로필 무료"

여기는 유저가 직접 제안한 부분이다. 정리하면:

- 지금 `ai_generator` ($10, 이력서 → Q&A 자동 생성)과 `qa_management` ($25, Q&A CRUD/벌크업로드)는 한 번 결제하면 *유저당* 평생 활성화된다.
- 새 정책: **첫 프로필**에서는 이 두 기능을 *무료로 체험* 가능. **두 번째 프로필부터** 결제해야 활성화.

**근거 (유저 의도):** 첫 프로필을 만든 직후가 가장 "와 이거 진짜 쓸 만한데?" 하는 순간이다. 그때 페이월에 막히면 그냥 떠난다. 한 번 경험시킨 다음 두 번째 프로필(예: 다른 회사 지원, 다른 직무 준비)을 만들 때 결제 흐름이 자연스러워진다. 게다가 *프로필을 duplicate해도 Q&A 데이터는 복사되지 않는다* (확인 완료: `interview_profile.py:275-321`). 그래서 두 번째 프로필에선 ai_generator/qa_management가 실제로 다시 필요한 상황이라 결제 명분이 선다.

**구현 포인트 (조사 완료):**
- 프로필은 user당 N개 가능 (`user_interview_profiles` 테이블, migration 035에서 UNIQUE 제거)
- 백엔드 feature 플래그는 *유저 단위*로 저장 (`user_subscriptions` 테이블), 프로필 단위 아님
- 그래서 "첫 프로필 무료" 판정은 **백엔드 `get_user_features_summary()`에서 `profiles.length === 1`이면 두 플래그를 강제로 true 반환**하는 방식이 가장 surgical
- 프론트 게이팅 사이트(이미 매핑됨):
  - `context-upload/page.tsx:794` — Generate Q&A 버튼
  - `qa-pairs/page.tsx:388, 398, 669, 678` — Bulk/Add/Edit/Delete 버튼
- 백엔드 엔드포인트는 현재 *명시적 권한 체크가 없다* (프론트 리다이렉트에만 의존). 이건 별개 보안 이슈인데, 이번 변경에서 함께 고칠지 surgical하게 패스할지는 유저 결정 필요.

**한 가지 미묘한 점:** `ai_generator`는 현재 `usage_limit=1` (Q&A 생성 1회만 가능), `qa_management`는 무제한이다. "첫 프로필 무료"가 *이 한도 그대로* 따라가는지 (= 1회 무료 생성 + 무제한 CRUD), 아니면 다른 의미인지 확정이 필요하다. 가장 자연스러운 해석은 "유료와 동일한 권한을 첫 프로필에 한해 무료로" — 즉 1회 생성 + 무제한 CRUD.

---

## 기존 40명에 대한 처우

유저 결정: 신규 트라이얼 사이즈만큼 기존 유저에게도 추가 지급.

**구현:** Migration 033이 신규 가입자에게만 트리거된다. 기존 40명은 이미 3개를 다 썼다. 일회성 data migration으로 각 기존 유저에게 `user_subscriptions` 새 row를 `plan_code='free_starter'`(또는 별도 `goodwill_topup` plan_code)로 발급. FIFO 소비 로직(migration 030)이 자동으로 사용해준다.

**고려:** 
- 멱등성: 같은 마이그레이션을 두 번 돌려도 두 번 지급되지 않아야 한다. → `IF NOT EXISTS` 가드 (특정 metadata 플래그로 식별) 필수.
- "지급량 = 신규 트라이얼량" vs "지급 후 잔액 = 신규 트라이얼량"? 후자는 이미 일부 쓴 유저가 손해 본다. 전자가 단순하고 공정. → **차액 보전이 아니라 신규 트라이얼량을 그대로 추가 지급** (확정 필요).
- 기존 유저의 *첫 프로필 무료 ai_generator/qa_management* 권한도 자동으로 따라가는가? 기존 유저는 이미 default 프로필이 있다 → 자동으로 혜택 받음. 단, 이미 $10/$25 결제한 유저는 환불 대상이 되나? 그건 아니라고 본다(이미 사용 중이라). 결정 필요.

---

## 단계별 구현 계획

순서대로 진행. 각 단계는 다음 단계로 가기 전 검증 가능한 산출물을 남긴다.

### Phase 0 — 결정사항 확정 (코드 변경 0)
이 diary를 유저가 확인하고 아래 "미해결 결정사항" 섹션을 메꿔준다. 답이 다 채워지면 Phase 1 시작.

### Phase 1 — 환불정책·문의 정리 (가장 surgical, 코드 의존성 적음)
1. `REFUND_POLICY.md`를 7-day money-back 톤으로 재작성, 이메일 `info@birth2death.com`으로 통일
2. `frontend/src/app/refund/page.tsx` 신설 → 동일 내용 인앱 렌더
3. `Footer.tsx`에 Refund 링크 추가 (Terms/Privacy가 없는 건 별도 이슈로 surface — 이번 PR 범위 밖)
4. `auth/register/page.tsx:194-205` 외부 깃허브 링크 → `/refund` 라우트로 변경, 인라인 카피도 일치시킴
5. `faq/page.tsx:57-58, 169` 카피·이메일 통일 (mailto 클릭 가능하게)
6. `pricing/page.tsx:309-312`는 톤 유지, `/refund` 링크만 추가
7. 다국어 FAQ 12개도 같은 이메일/카피 변경 필요한지 점검

**검증:** 회원가입 → 환불 링크 → /refund 페이지 정상 렌더; 푸터 → /refund 클릭 가능; 세 군데 카피 톤 일치; 이메일 검색 시 `info@birth2death.com` 단일 결과.

### Phase 2 — 가격 사다리 재설계 (DB 마이그레이션)
1. 새 마이그레이션 파일: `backend/database/migrations/0XX_pricing_redesign_2026_05.sql`
   - `UPDATE pricing_plans SET credits_amount = <NEW> WHERE plan_code='free_starter'`
   - `UPDATE pricing_plans SET credits_amount = ..., price_usd = ... WHERE plan_code IN ('credits_starter','credits_popular','credits_pro')`
   - (선택) 새 tier `INSERT`
2. Lemon Squeezy 대시보드에서 각 variant의 가격을 새 값에 동기화 (유저가 직접 수행, 체크리스트 제공)
3. 새 tier가 있다면 Railway env var (`LEMON_SQUEEZY_VARIANT_*`) 추가, `config.py:61-66` + `lemon_squeezy.py:213-228` 수정
4. 프론트는 자동 — `pricing/page.tsx`가 `/api/subscriptions/plans`에서 DB값을 가져옴

**검증:** `/pricing` 페이지가 새 가격/크레딧 표시; Lemon Squeezy 체크아웃 결과 새 가격 표시; 결제 후 webhook이 새 credits_amount만큼 지급.

### Phase 3 — 기존 40명 top-up (멱등 데이터 마이그레이션)
1. 마이그레이션: 각 기존 유저(`SELECT id FROM profiles`)에 대해 `user_subscriptions` 새 row insert
   - `plan_code = 'free_starter'`, `credits_amount = <NEW_TRIAL>`, metadata에 `{"topup_2026_05": true}` 같은 식별자
   - `WHERE NOT EXISTS (SELECT 1 FROM user_subscriptions WHERE user_id = ? AND metadata->>'topup_2026_05' = 'true')` 가드
2. 검증 쿼리: 기존 40명 전원이 새 row를 정확히 1개씩 가졌는지

**검증:** 임의 기존 유저로 로그인 → 잔여 크레딧이 정확히 새 트라이얼량만큼 증가; 같은 마이그레이션을 두 번 돌려도 잔액 변화 없음.

### Phase 4 — First-profile-free 게이팅
1. `get_user_features_summary()` DB 함수 또는 `subscriptions.py:88-114` 핸들러 수정:
   ```
   profile_count = SELECT COUNT(*) FROM user_interview_profiles WHERE user_id = ?
   IF profile_count <= 1:
       ai_generator_available = true
       qa_management_available = true
       (단, 기존 결제 여부와 OR — 결제했으면 그대로 true)
   ```
2. 프론트는 `useUserFeatures` 응답을 그대로 신뢰 → 코드 변경 거의 없음
3. (선택, 유저 결정 의존) 백엔드 엔드포인트에 명시적 권한 체크 추가 — `context_upload.py:389-455`, `qa_pairs.py:155-260`에서 `user_has_feature()` 호출

**검증:** 새 유저 가입 → 첫 프로필만 있는 상태에서 `/profile/context-upload` 진입 → "Generate Q&A" 버튼 활성화; 두 번째 프로필 생성 → 같은 버튼 클릭 → `/pricing` 리다이렉트.

### Phase 5 — (선택) 세션 비용 로깅
30 세션 트라이얼이 경제적으로 작동하는지 모니터링하기 위한 최소 인프라:
- `session_costs` 테이블 + `claude.py:1056` 부근에 token_count INSERT
- 별도 PR로 분리 권장 (이번 작업의 본류는 아님)

---

## 확정된 결정사항 (2026-05-24)

| 항목 | 확정값 |
|---|---|
| **새 트라이얼 크레딧** | 30 (3 → 30) |
| **credits_starter** | 25 @ $5 (그대로 유지 — "결제 의례용" 진입점, 실용성은 적음) |
| **credits_popular** | 60 @ $10 (10 → 60) |
| **credits_pro** | 150 @ $20 (50 → 150) |
| **기존 40명 top-up** | 전원 +30 (단, `kate@gmail.com` 제외) |
| **first-profile 무료 자동 적용** | YES — 기존 유저의 default 프로필에도 자동 |
| **기결제자 (5명) 보상** | 추가 +50 보너스 크레딧 + 진심 어린 사과 이메일 |
| **이탈 유저 재활성화 이메일** | 두 그룹 모두 발송 (제목은 함께 결정 — 어그로 톤 필요, 이탈자라 약한 제목으론 안 열림) |
| **백엔드 enforcement** | 별도 PR (이번 범위 밖) |
| **세션 비용 로깅** | 추후 (운영 모니터링 후 필요시) |
| **ToS / Privacy 신설** | 별도 트래킹 (법적 갭이지만 본 PR 범위 밖) |

### 가격 사다리 단가 분석 (참고)

| Tier | 크레딧 | 가격 | 단가 | 마진(원가~$0.1/세션 기준) |
|---|---|---|---|---|
| free_starter | 30 | $0 | $0 | -$3 (의도된 손실 — lock-in 투자) |
| credits_starter | 25 | $5 | $0.200 | ~50% |
| credits_popular | 60 | $10 | $0.167 | ~40% |
| credits_pro | 150 | $20 | $0.133 | ~25% |

**주의:** starter(25)가 무료(30)보다 작아서 합리적 유저는 안 산다. 유저 결정으로 그대로 유지(소액 결제 진입 의례 의미). 향후 데이터 보고 폐기 여부 재검토.

---

## 다음 액션 — 작업 순서

1. **Phase 1** — 환불·문의 정리 (가장 surgical, 즉시 시작)
2. **Phase 2** — 가격 사다리 DB 마이그레이션 (+ Lemon Squeezy 대시보드 동기화 체크리스트)
3. **Phase 3** — 기존 40명 top-up 마이그레이션 (kate 제외, 기결제자 +50 보너스 분기 처리)
4. **Phase 4** — first-profile-free 게이팅 구현
5. **Phase 5** — 이탈 유저 재활성화 이메일 (제목 함께 브레인스토밍, kate 제외)

---

## 배포 체크리스트 (Phase 2~4 작성 완료 후 운영)

### 1. 마이그레이션 적용 순서

```
041_pricing_redesign_2026_05.sql       — 가격 사다리 + 트리거 동적화
042_topup_existing_users_2026_05.sql   — 기존 40명 top-up (Pass 1 universal + Pass 2 paid apology)
043_first_profile_free_gating.sql      — get_user_features_summary OR first_profile_free
```

각 마이그레이션은 BEGIN/COMMIT으로 감싸져 있어 실패 시 자동 롤백됨.

### 2. Lemon Squeezy 대시보드 수동 동기화

새 tier 추가는 없음 → env var / 코드 변경 불필요. **각 variant의 가격만 LS 대시보드에서 수정**:

| Plan code | 새 가격 | LS variant env var (참조용) |
|---|---|---|
| credits_starter | $5.00 (변경 없음 가능 — 원래 $4 → $5) | `LEMON_SQUEEZY_VARIANT_CREDITS_STARTER` |
| credits_popular | $10.00 ($8 → $10) | `LEMON_SQUEEZY_VARIANT_CREDITS_POPULAR` |
| credits_pro | $20.00 ($15 → $20) | `LEMON_SQUEEZY_VARIANT_CREDITS_PRO` |
| ai_generator | $10.00 (변경 없음) | — |
| qa_management | $25.00 (변경 없음) | — |

⚠️ LS variant price와 `pricing_plans.price_usd`가 불일치하면 체크아웃 시 LS 가격이 표시됨 → 반드시 동기화.

### 3. 검증 쿼리 (마이그레이션 적용 후)

```sql
-- 041 검증: 새 가격 반영 확인
SELECT plan_code, credits_amount, price_usd
FROM public.pricing_plans
WHERE plan_code IN ('free_starter','credits_starter','credits_popular','credits_pro')
ORDER BY display_order;
-- 기대: 30/0, 25/5, 60/10, 150/20

-- 041 검증: 트리거 동적 동작 확인 (실제 새 가입 발생 시)
SELECT credits_remaining FROM user_subscriptions
WHERE plan_code='free_starter'
ORDER BY purchased_at DESC LIMIT 1;
-- 기대: 30

-- 042 검증: 기존 유저 top-up 결과
SELECT
  metadata->>'granted_reason' AS reason,
  COUNT(*) AS users_granted,
  SUM(credits_remaining) AS total_credits_granted
FROM public.user_subscriptions
WHERE metadata->>'granted_reason' IN ('topup_2026_05_universal','topup_2026_05_paid_apology')
GROUP BY reason;
-- 기대: universal ~39명 × 30, paid_apology ~5명 × 50

-- 042 검증: kate 제외 확인
SELECT us.metadata->>'granted_reason'
FROM public.user_subscriptions us
JOIN auth.users au ON us.user_id = au.id
WHERE au.email = 'kate@gmail.com'
  AND us.metadata->>'granted_reason' LIKE 'topup_2026_05%';
-- 기대: 0 rows

-- 043 검증: 프로필 1개 유저는 두 플래그 모두 true
SELECT
  p.id,
  (SELECT COUNT(*) FROM user_interview_profiles WHERE user_id = p.id) AS profile_count,
  get_user_features_summary(p.id) -> 'ai_generator_available' AS ai_avail,
  get_user_features_summary(p.id) -> 'qa_management_available' AS qa_avail
FROM public.profiles p
LIMIT 5;
-- 기대: profile_count <= 1인 유저는 두 컬럼 모두 true

-- 멱등성 확인: 042를 두 번 돌려도 row count 동일
-- (BEGIN ... DO $$ ... COMMIT; 한 번 더 실행 후 NOTICE가 0/0 나오면 OK)
```

### 4. 알려진 잔여 UX 이슈 (별도 작업)

- **`/pricing` 페이지의 "Owned" 배지**: first-profile-free 유저에게 ai_generator/qa_management가 "Owned"로 표시되어 마치 구매한 것처럼 보임. 정확한 표기는 "Free on first profile". → 별도 작업으로 분리 가능. API에 `*_source: 'purchased' | 'first_profile_free'` 필드 추가 + 프론트 배지 분기.
- **2번째 프로필 생성 시 paywall 전환 안내 부재**: 두 번째 프로필 만든 직후 ai_generator 버튼 클릭 시 `/pricing`으로 리다이렉트되는데, "왜 갑자기?" 설명이 없음 → 토스트나 banner로 안내 권장.
- **백엔드 엔드포인트 enforcement 부재**: 결정대로 별도 PR로 분리.
