# learning_log.md

> InterviewMate Conversion Overhaul (2026-05-23 ~ 2026-05-24) — 한 큰 작업을 끝까지 굴리면서 얻은,
> **다른 프로젝트에도 그대로 적용 가능한** 룰 모음. 다음 큰 작업 시작할 때 *이 문서부터 다시 읽는다*.
>
> 각 룰 끝에 우리 케이스를 짧게 인용해 추상적이지 않게.

---

## 0. 가장 먼저 — 작업 들어가기 전 메타 룰

### 0.1. 큰 작업 전 `diary.md`(또는 `plan.md`) 먼저 쓴다

코드 한 줄 건드리기 전에:
- 사용자가 진단한 문제 N개를 **그대로 받아 적지 말고** 코드베이스 병렬 조사로 검증
- 결정해야 할 것을 **표로** (옵션 / 권장안 / reasoning)
- 단계별 plan + 각 단계 검증 SQL/명령을 한 문서에 모음
- 미해결 결정사항 섹션을 만들고 사용자 confirm 받기 전엔 코드 진행 X

→ 우리 케이스: `diary.md`가 작업의 절반을 차지함. 나중에 deploy 체크리스트·검증 쿼리·잔여 UX 트래킹으로도 재사용됨. **계획 문서가 곧 운영 문서가 되도록 쓰는 게 ROI 최고.**

### 0.2. 사용자가 "X가 없다"고 한 것은 *없는 게 아니라 모순되어 있을* 가능성

새로 만들기 전에 grep으로 기존 상태 전수조사. 발견되면 통합/정리가 우선이지 신설 아님.

→ 우리 케이스: "환불정책 없다" → 실제로는 register checkbox + FAQ + pricing FAQ + 외부 GitHub 마크다운 4곳에 서로 다른 톤으로 흩어져 있었음. "support 이메일 없다" → `info@birth2death.com` (footer, 동작) / `support@interviewmate.tech` (FAQ, 텍스트) / `support@interviewmate.ai` (REFUND_POLICY.md) 세 개 떠다님.

### 0.3. 사용자 직관 ("좆됨", "이상해")과 실제 데이터를 분리

직관은 가설일 뿐. 데이터 받기 전에 진단 SQL/쿼리/스크린샷부터 요청.

→ 우리 케이스: tayheart 결제자가 DB에 없다 → "데이터 누락 좆됨" → 실제는 가입 이메일(tayheart18)과 LS billing 이메일(tayheart16)이 typo로 달라서 *진단 쿼리가 잘못 매칭한 것*. 시스템은 정상 작동 중이었음.

### 0.4. Surgical 원칙 — touch only what you must

- 같은 PR에 묶으면 리뷰 어려움 → atomic 분리 (영역별)
- 인접 코드 "개선" 금지
- 다른 영역 정리는 follow-up task로 분리
- 한 PR = 한 응집된 변경

→ 우리 케이스: PR #11이 billing migrations / legal copy / docs 3개 atomic commit. PR #12는 homepage hotfix만. PR #13은 STAR + copy buttons만. 리뷰·롤백 모두 깔끔.

---

## 1. Planning — 코드 한 줄 쓰기 전

### 1.1. 가정 vs 사실 대조 표

작업 시작 시 표 만든다:

| 사용자 주장 | 실제 코드 상태 | 진짜 문제 |
|---|---|---|
| X 기능 없음 | 모순된 3곳에서 X 언급 | 통합 + 정리 |
| 가격이 비싸서 안 산다 | 가격 외에 trial 부족 + 신뢰 갭 | 다층 fix |

→ 표 만들면 사용자에게 보여주고 자기 진단이 부분적임을 인정하기 좋음.

### 1.2. 비즈니스 결정은 `AskUserQuestion` — 권장안 + reasoning 같이

가격, trial 사이즈, top-up 방식, 사과 정책, 환불 톤 등 **비즈니스/legal 결정은 사용자 confirm 필수**. 권장안 하나 + reasoning 같이 제시해서 사용자가 다른 선택도 가능하게.

CLAUDE.md 프로젝트 룰: "When running any experiment, always ask the user to confirm key parameters." → 가격·정책도 같은 정신.

### 1.3. 비용/임팩트 정량화

"X로 lock-in 효과" 같은 주장은 숫자로 받친다.

→ 우리 케이스: 1세션 raw API 비용 = $0.07~$0.16 → 30 free trial = $2~5/user → 100명 신규 가입자 중 20명이 전부 쓰면 worst-case $100. 결제 전환이 5→15만 늘어도 본전. **정량화 없으면 결정이 sound하지 않음.**

### 1.4. 가격 사다리 경제 정합성

가격 결정 시 모든 tier 단가 + lock-in 임계점 + 결제 동기를 한 표로:

| Tier | 양 | 가격 | 단가 | 마진(원가 기준) | 결제 동기 |
|---|---|---|---|---|---|
| free | 30 | $0 | $0 | 손실 (의도된 lock-in 투자) | — |
| starter | 25 | $5 | $0.20 | ~50% | **없음** (← surface해야 함) |

→ "starter < free" 같은 경제 모순은 즉시 surface해서 사용자 결정 받기.

### 1.5. 외부 서비스 의존성 미리 파악

DB만으로 끝나지 않는 변경은 외부 sync 체크리스트 미리 만든다.

→ 우리 케이스: 가격 변경은 `pricing_plans` UPDATE + Lemon Squeezy dashboard variant 가격 수동 sync + 상품명도 ("Popular Pack - 25 Sessions" → "60 Sessions"). 하나라도 빠지면 결제 시점 가격 불일치.

---

## 2. Migrations (DB schema/data)

### 2.1. 번호 충돌 확인

```bash
ls backend/database/migrations | tail
```

사용자 지정 번호도 검증한다. 우리 케이스: 사용자가 "039/040으로 진행" 지시했는데 둘 다 이미 사용 중 → 041/042로 변경 + 사용자에게 surface.

### 2.2. 트리거 함수에 hardcoded value 박지 말기

magic number는 lookup table로 동적 read.

→ 우리 케이스: `grant_free_credits_on_signup` 트리거가 `3`을 세 군데 하드코딩 → trial 변경 시 마이그레이션 또 필요. `SELECT credits_amount FROM pricing_plans WHERE plan_code='free_starter'`로 동적화하니 향후 trial 변경은 한 줄 UPDATE.

### 2.3. 멱등성 (metadata flag로 가드)

```sql
WHERE NOT EXISTS (
    SELECT 1 FROM user_subscriptions
    WHERE user_id = ? AND metadata->>'granted_reason' = 'topup_2026_05_universal'
)
```

데이터 마이그레이션은 두 번 돌려도 안전. 멱등성 가드 없으면 사고. metadata.granted_reason 같은 명시적 식별자.

### 2.4. "기존 N명에게 작업" 시 cutoff 명시

```sql
AND p.created_at < NOW()
```

신규 가입자가 마이그레이션 도중에 영향 받지 않도록.

### 2.5. 예외 대상 명시

admin / test / special accounts 명시적 exclusion.

→ 우리 케이스: top-up 마이그레이션에서 `kate@gmail.com` (admin grant) + `metadata.granted_by = 'admin'` 둘 다 제외. SQL에서 explicit.

### 2.6. 데이터 마이그레이션 발급량 결정 trade-off 명시

"전체에 +N" vs "잔액을 N까지 보전" vs "구매 시점 약속 양" — 각각 trade-off 표로 제시 후 사용자 결정.

### 2.7. 마이그레이션 적용 ≠ PR 머지

Supabase는 SQL 직접 실행. PR body에 명시 + 머지 후 즉시 reminder.

→ 우리가 PR #11 머지 후 사용자가 SQL 적용 잊었을 가능성 surface해서 미리 안내함.

---

## 3. Code

### 3.1. Type duplication = 빌드 깨짐 시한폭탄

같은 타입을 inline 정의 여러 곳에 두면 새 필드 추가 시 일부만 업데이트 → Vercel/CI 빌드 깨짐.

→ 우리 케이스: `pricing/page.tsx`가 자체 inline `UserFeatures` interface 유지 + `useUserFeatures.ts`도 별도 export. PR #14에서 새 `*_source` 필드 추가했을 때 hook 쪽만 업데이트 → Vercel 빌드 fail → fix-up commit 필요.

**원칙:** hook의 exported type을 import. 또는 monorepo의 shared types 폴더.

### 3.2. Server vs client component 경계 (Next.js App Router)

server component는 빠르고 SEO 좋음. client component는 인터랙티브. 작은 인터랙티브 부분만 client로 분리:

→ 우리 케이스: `guide/page.tsx` (server) + `CopyButton.tsx` (client, `'use client'`). 핸들러만 client component, 페이지 자체는 server로 유지.

### 3.3. 작은 컴포넌트는 라이브러리 추가하지 말기

Toast 같은 30줄짜리 컴포넌트는 직접 구현이 npm install보다 빠르고 의존성도 절약.

→ 우리 케이스: `Toast.tsx` 자체 구현 (53줄). `react-hot-toast`/`sonner` 추가 안 함.

### 3.4. useEffect cascade 항상 의심

글로벌 hook (auth listener, route change listener 등)이 모든 event에 같은 무거운 작업 → visibility/route change 시 cascade refetch.

→ 우리 케이스: `ProfileContext.onAuthStateChange`가 `TOKEN_REFRESHED`에도 무조건 `loadProfiles` → 탭 전환마다 6초 cascade. fix: `lastLoadedUserIdRef`로 실제 user 변화 시에만.

**패턴:**
```tsx
const lastLoadedRef = useRef<string | null>(null);
// inside listener:
if (lastLoadedRef.current === newId) return; // skip refresh-only events
lastLoadedRef.current = newId;
await loadX(newId);
```

### 3.5. 신규 유저 0-state 시점 테스트 필수

모든 dep-array 의존 fetch는 dep 비어있을 때 isLoading false로 set 안 하면 무한 로딩.

→ 우리 케이스: `qa-pairs/page.tsx`가 `if (userId && activeProfile) fetchQAPairs()` 인데 fetchQAPairs만 isLoading=false. 0 profile 유저는 영원히 "Loading…". fix: dep 미충족 + 로딩 끝났을 때도 명시적으로 isLoading=false.

**패턴:**
```tsx
useEffect(() => {
    if (userId && dep) {
        fetchX();
    } else if (userId && !dep && !depLoading) {
        setIsLoading(false); // 무한 spinner 방지
    }
}, [userId, dep, depLoading]);
```

### 3.6. 비슷한 변경 시 grep sweep (잠재 누락 찾기)

가격 변경: `\$N|\$0\.NM|sessions for|"price"|/[NM] sessions`
이메일 변경: 모든 도메인/주소 grep
정책 문구 변경: 핵심 동사 grep ("All sales final", "no refund" 등)

→ 우리 케이스: pricing 페이지는 DB 동적 fetch라 자동 업데이트되지만 `homepage` / `layout.tsx jsonLd` / `schema.json` / `config/site.ts`는 hardcoded → grep으로 4곳 동시 발견 + 한 PR로 fix.

### 3.7. PR 생성 전 Vercel 빌드 미리 (선택)

TypeScript strict 빌드 깨짐 미리 잡기. 큰 변경은 push 전에 `npm run build` 또는 `vercel build` 로컬 실행.

→ 우리 PR #14가 push 후 build fail로 fix-up commit 필요했음. 미리 빌드했으면 한 commit으로 끝났을 거.

### 3.8. 외부 서비스 client는 모듈 레벨 singleton으로 캐싱

Supabase / S3 / Stripe / OpenAI 등 SDK client는 **매 호출마다 새로 만들면 안 됨.** HTTP keep-alive · SSL handshake · connection pool 재사용을 다 깨버린다.

코드 리뷰 시 함수 안에 `return create_client(...)` 같은 패턴 보이면 → 그 함수가 per-request 호출되는지 확인. yes면 latency 폭탄.

**패턴 (Python lazy singleton):**

```python
_client: Optional[Client] = None

def get_client() -> Client:
    global _client
    if _client is None:
        _client = create_client(...)
    return _client
```

대부분의 SDK client (supabase-py, httpx, boto3 등)는 thread-safe라 single shared instance가 안전.

**우리 케이스 (PR #18):**
- `get_supabase_client()`가 `return create_client(...)` — 매 호출 새 instance
- 모든 FastAPI endpoint, WebSocket auth가 함수 호출 → 매 request에 fresh HTTP session
- `/summary` 측정: SQL 3.766 ms vs wire 1400 ms → 1396 ms gap이 전부 client construction overhead
- singleton fix 후: 1400 ms → 779 ms (거의 절반). 첫 fetch만 cold start, 그 후엔 connection pool warm

**관련 anti-pattern (Frontend):** React에서도 같은 본질 — heavy resource를 useEffect cleanup 없이 매 render 다시 만들지 말기. 단 frontend는 cold-cache 영향 적음.

---

## 4. Debugging

### 4.1. 가설 좁히기 — 단서 → 가설 N → 단서 → 가설 1

추측 fix 절대 금지. 진단 데이터 없이는 plan만.

5개 가설 → 1개 단서로 3개 제거 → 2개 → DevTools 1개 단서 → 1개 확정.

→ 우리 케이스: latency 6초 원인 5개 가설 → "interview 페이지는 빠름" 단서로 WS reconnect 가설 제거 → 2개 남음 (cold start vs auth cascade) → DevTools Network에 5번 반복 fetch 보고 cascade 확정.

### 4.2. DevTools Network 탭 = 진실의 원천

| 패턴 | 가설 |
|---|---|
| 첫 요청 1개가 N초, 나머지 빠름 | Cold start |
| 짧은 요청 여러 개 직렬로 N초 누적 | Cascade refetch |
| N초 동안 Network에 아무것도 → 갑자기 처리 | Browser tab throttle |

### 4.3. 가짜 에러 인식 (시간 낭비 방지)

- `"asynchronous response... message channel closed"` → 브라우저 확장 (React DevTools, Grammarly, Adblock 등)
- `"ResizeObserver loop limit exceeded"` → 무해, 자동 복구
- `"Hydration failed because the initial UI does not match"` → 진짜 SSR/CSR 불일치 (조사 필요)
- 시크릿 모드로 확인 = 확장 노이즈 판별

### 4.4. UID 기준 진단 (이메일 X)

`auth.users.email`은 case-sensitivity + typo + 변경 가능. UUID로 join.

→ 우리 케이스: tayheart16(LS) vs tayheart18(가입) 케이스가 이메일 진단이었으면 "데이터 누락"으로 결론 → 잘못된 보전 마이그레이션 생성할 뻔. UID로 봤더니 정상 매칭.

### 4.5. 진단 결과는 사람이 한 번에 해석 가능해야

각 row가 자가 설명적이게 별도 컬럼:

```sql
SELECT
  email,
  status,
  COALESCE(metadata->>'granted_by', '(real purchase)') AS source,
  EXISTS (...) AS got_followup
FROM ...
```

`(real purchase)` vs `admin` vs `refunded` 명확히 분리 → 사용자가 한눈에 진짜 vs 가짜 결제 구분.

### 4.6. "이미 정상" 가능성 항상 의심

진단이 "버그 확정"으로 보여도, 우리 진단 자체가 틀렸을 가능성 30% 이상. 보전/fix 마이그레이션 작성 전에 한 번 더 검증.

→ 우리 케이스: paid_apology=1로 "버그" 확정 직전에 정밀 진단 → admin grant + refunded 빼면 실제 진짜 결제자는 soobon80 한 명뿐. **정상 동작이었음.** 마이그레이션 작성 안 함.

---

## 5. Deployment

### 5.1. PR 머지 ≠ Migration 적용 reminder

PR body에 "Deployment" 섹션 + 머지 후 별도 메시지로 알림.

### 5.2. Backend ↔ Frontend 순서 critical

새 필드 추가 PR에서 frontend가 그 필드 의존하면 backend SQL 먼저 적용 안 하면 frontend가 fallback (또는 깨짐).

→ 우리 PR #14가 그런 케이스. migration 044 적용 안 하면 `*_source` 필드가 `'locked'`로 fallback → 옛 동작.

### 5.3. 외부 서비스 sync 체크리스트

LS / Stripe / Statsig / Resend 등 외부에 데이터/설정 있는 곳은 코드 변경 후 수동 sync 필요한지 체크. 체크리스트로 PR body에 명시.

### 5.4. PR 라이프사이클 결정 (atomic vs 묶음)

기준:
- **Atomic**: 영역 다름, 독립적으로 revert 가능, 다른 사람에게도 의미 있음 → 분리
- **묶음**: 한 영역, 같이 안 가면 깨짐, 작은 fix → 같은 PR

우리 케이스 5 PR (각각 응집):
- #11 billing + legal + docs (3 commits, 한 PR)
- #12 homepage hotfix (1 commit)
- #13 STAR + copy buttons (2 commits)
- #14 owned badge + paywall toast + double-submit (3 commits + 1 fixup)
- #15 cascade fix + qa-pairs fix + free trial label (3 commits)

---

## 6. Communication

### 6.1. 사용자 정보 줄 때 즉시 진단 — 추측 fix 금지

특히 critical UX (latency, 무한 로딩, 결제) 추측으로 코드 변경 = 위험.

### 6.2. 비즈니스 결정 vs 코드 결정 분리

| 종류 | 처리 |
|---|---|
| 비즈니스 결정 (가격, 정책, 메시지 톤) | `AskUserQuestion` 필수 |
| 코드 결정 (라이브러리 선택, 패턴) | 권장안으로 진행 + 1줄 노트 |
| 컨벤셔널 default (브랜치 이름 등) | 진행 + 메시지에 명시 |

### 6.3. "좆됨" 신호 받으면 침착하게 단계별

1. 좋은 소식 (시스템 정상 부분 — 안심시키기)
2. 진짜 문제 분리 (있다면)
3. 진단 정보 요청 (한 번에 모음)
4. 추측 fix 안 함

### 6.4. PR body는 self-documenting

4 섹션 구조:
- **Why** — 비즈니스 동기 (한 단락)
- **What's in this PR** — 변경 요약 (표 또는 bullet)
- **Verification / Deployment** — 머지 후 할 일
- **Out of scope** — 의도적으로 안 한 것

다른 사람이 description만 보고 의도·범위·검증법 이해 가능해야.

### 6.5. 추가 task로 분리 = 명시적으로 surface

작업 중 발견된 별개 이슈는 즉시 fix 안 하고 task로 트래킹 (TaskCreate). PR body의 "Out of scope" + task 링크.

→ 우리가 만든 follow-up task: Owned 배지 분기, multi-FAQ pricing, LS guest-checkout, RLS restore, double-submit guard, custom instruction UX, profile-loading hang.

---

## 7. Anti-patterns (절대 안 함)

- ❌ 사용자 confirm 없이 가격·정책 임의 결정
- ❌ DB 트리거에 hardcoded magic number
- ❌ 데이터 마이그레이션 멱등성 가드 없음
- ❌ 추측 fix (Network 데이터 안 보고 latency 가설 → 코드 변경)
- ❌ 같은 타입 inline 중복 정의 (빌드 깨짐 시한폭탄)
- ❌ 신규 유저 0-state 테스트 안 함
- ❌ 외부 서비스 sync 후 reminder 없음
- ❌ 이메일 기반 진단 (UID로 해야 함)
- ❌ 사용자 진단 그대로 받아들이고 grep 없이 새로 만들기
- ❌ 큰 PR 한 번에 (atomic 분리 안 함)
- ❌ "기존 작동" 가정 — 진단 SQL로 검증 안 함

---

## 8. 다음 큰 작업 시작 체크리스트

새 큰 작업 시작 시 이 순서대로:

1. [ ] `plan.md` (또는 `diary.md`) 생성, 사용자 진단 받아쓰지 말고 코드베이스 grep으로 검증
2. [ ] "가정 vs 사실" 표 작성 → 사용자에게 보여주고 격차 confirm
3. [ ] 비즈니스 결정 사항 `AskUserQuestion`으로 한 번에 (최대 4개)
4. [ ] 마이그레이션 번호 충돌 확인 (`ls migrations | tail`)
5. [ ] 외부 서비스 (LS / Stripe / etc.) sync 체크리스트 미리
6. [ ] 단계별 plan (Phase 0~N) — 각 단계 검증법 같이
7. [ ] 알려진 잔여 issue를 "Out of scope" task로 분리
8. [ ] 한 PR 당 한 응집된 변경 (atomic commits 내부 OK)
9. [ ] PR body: Why / What / Verification / Out of scope 4섹션
10. [ ] 머지 후 외부 sync + DB migration reminder (자동 아님)
11. [ ] 신규 유저 0-state 시점 직접 테스트
12. [ ] 다음 작업 전 이 `learning_log.md`에 새 룰 추가

---

## 부록 A: 이번 세션 PR 목록 (5개)

- **PR #11** — 가격 정책 (3→30 trial, tier 재구성) + first-profile-free + 환불 정책 7-day money-back 통일 + diary.md
- **PR #12** — 홈페이지 stale pricing hotfix (DB 동적 페이지가 아닌 hardcoded 페이지 4곳)
- **PR #13** — STAR template default for new profiles + Guide page STAR rewrite + 복사 버튼
- **PR #14** — "Owned" vs "Free on first profile" 배지 분기 + double-submit guard + 2nd-profile paywall toast
- **PR #15** — Tab-switch latency cascade fix + qa-pairs 무한 로딩 fix + Free trial 라벨링

## 부록 B: 이번 세션 마이그레이션 (4개)

- **041** — `pricing_plans` 가격 사다리 변경 + `grant_free_credits_on_signup` 트리거 동적화
- **042** — 기존 유저 universal +30 top-up + paid 유저 +50 사과 보너스 (kate / admin 제외, 멱등 metadata flag)
- **043** — `get_user_features_summary`에 `first_profile_free` 조건 OR (profile_count ≤ 1)
- **044** — 같은 함수에 `*_source` 필드 + `profile_count` 노출 (purchased / first_profile_free / locked 분기)

## 부록 C: 미해결 trail (다른 PR로 분리됨)

- Task #10/#11 — 이탈 유저 재활성화 이메일 (인터뷰 답신 후)
- Task #13 — LS guest-checkout reconciliation (가입 시 LS 매칭)
- Task #18 — 다국어 FAQ 11개 stale pricing
- Task #19 — RLS 복원 (보안 critical)
- Task #20 — context-upload / stories / interview-settings 같은 무한 로딩 패턴

---

*이 문서는 살아있다. 다음 작업에서 새 패턴/실수 발견하면 즉시 추가.*
