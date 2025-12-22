# Interview Mate - Credit-Based Billing Implementation Summary

## ✅ 완료된 작업 (Backend)

### 1. 데이터베이스 스키마 생성
**파일:** `backend/database/migrations/030_credit_based_billing.sql`

4개 테이블 + Helper 함수 + RLS 정책:
- `pricing_plans`: 가격 플랜 정의 (credit packs + one-time purchases)
- `user_subscriptions`: 사용자 구독 및 크레딧 잔액
- `payment_transactions`: 결제 내역 및 감사 로그
- `credit_usage_log`: 크레딧 사용 상세 로그

#### Helper 함수:
```sql
get_user_interview_credits(user_id)  -- 사용 가능한 총 크레딧 조회
consume_interview_credit(user_id, session_id)  -- 크레딧 1개 차감 (FIFO)
user_has_feature(user_id, feature_code)  -- 기능 접근 권한 체크
get_user_features_summary(user_id)  -- 전체 요약 정보
```

### 2. 백엔드 API 구현

#### A. Subscription API (`app/api/subscriptions.py`)
사용자 구독 및 크레딧 관리

**Endpoints:**
```
GET  /api/subscriptions/plans                    # 전체 가격 플랜 조회 (public)
GET  /api/subscriptions/{user_id}/summary        # 사용자 기능 요약
GET  /api/subscriptions/{user_id}/subscriptions  # 사용자 구독 목록
GET  /api/subscriptions/{user_id}/credits        # 사용 가능한 크레딧 수
POST /api/subscriptions/{user_id}/credits/consume  # 크레딧 차감
GET  /api/subscriptions/{user_id}/credits/usage-log  # 사용 내역
GET  /api/subscriptions/{user_id}/feature/{code}  # 기능 접근 권한 체크
GET  /api/subscriptions/{user_id}/transactions    # 결제 내역
```

#### B. Payments API (`app/api/payments.py`)
Stripe 결제 처리 및 Webhook

**Endpoints:**
```
POST /api/payments/create-checkout-session  # Stripe 체크아웃 세션 생성
POST /api/payments/webhook                  # Stripe Webhook 처리
GET  /api/payments/session/{session_id}     # 결제 세션 상세 조회
```

**Webhook Events:**
- `checkout.session.completed`: 결제 완료 → 기능/크레딧 부여
- `payment_intent.succeeded`: 결제 성공 확인
- `payment_intent.payment_failed`: 결제 실패 처리
- `charge.refunded`: 환불 처리 → 기능 회수

### 3. 설정 파일 업데이트

#### `app/main.py`
- `subscriptions` 라우터 등록
- `payments` 라우터 등록

#### `app/core/config.py`
Stripe 설정 이미 존재:
```python
STRIPE_SECRET_KEY: str = ""
STRIPE_PUBLISHABLE_KEY: str = ""
STRIPE_WEBHOOK_SECRET: str = ""
```

#### `.env.example`
Stripe 환경 변수 가이드 추가:
```bash
STRIPE_SECRET_KEY=sk_test_...
STRIPE_PUBLISHABLE_KEY=pk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
```

---

## 🎯 가격 전략 (최종 확정)

### Credit Packs (Interview Practice)
| Pack | Price | Sessions | Per Session | Margin |
|------|-------|----------|-------------|--------|
| Starter | $4 | 10 | $0.40 | 74% |
| Popular | $8 | 25 | $0.32 | 82% ⭐ |
| Pro | $15 | 50 | $0.30 | 87% ⭐ |

**COGS:** ~$0.23/session (Deepgram $0.18 + Claude $0.05)

### One-Time Purchases
| Feature | Price | Usage | COGS | Margin |
|---------|-------|-------|------|--------|
| AI Q&A Generator | $10 | 1x | ~$0.05 | 99.5% |
| Q&A Management | $25 | Unlimited | ~$0 | 100% |

---

## 📋 다음 단계 (Frontend + Testing)

### Phase 1: 프론트엔드 구현 (남음)
1. **Pricing Page** (`/pricing`)
   - 크레딧 팩 가격표
   - 기능 비교표
   - Stripe Checkout 버튼

2. **Payment Success/Cancel Pages**
   - `/payment/success?session_id={id}`
   - `/payment/cancel`

3. **Feature Lock Components**
   - Interview 페이지: 크레딧 부족 시 프롬프트
   - Q&A Generator: 구매 안 한 경우 잠금
   - Q&A CRUD: Read-only 모드

4. **User Dashboard**
   - 남은 크레딧 표시
   - 구매 내역
   - 사용 통계

### Phase 2: Feature Gates 구현 (남음)
1. **WebSocket (Interview)**
   ```python
   # 연결 시 크레딧 체크
   credits = get_user_interview_credits(user_id)
   if credits <= 0:
       raise HTTPException(403, "No credits")

   # 면접 종료 시 크레딧 차감
   consume_interview_credit(user_id, session_id)
   ```

2. **Q&A Generator**
   ```python
   # 생성 전 체크
   has_access = user_has_feature(user_id, 'ai_qa_generation')
   usage = get_generator_usage(user_id)
   if not has_access or usage >= 1:
       raise HTTPException(403, "Purchase required")
   ```

3. **Q&A CRUD**
   ```python
   # 생성/수정/삭제 전 체크
   has_access = user_has_feature(user_id, 'qa_pairs_crud')
   if not has_access:
       raise HTTPException(403, "Purchase Q&A Management")
   ```

### Phase 3: 테스팅 (남음)
1. **Migration 실행**
   ```bash
   # Supabase SQL Editor에서 실행
   backend/database/migrations/030_credit_based_billing.sql
   ```

2. **Stripe 설정**
   - Stripe 계정 생성 (https://dashboard.stripe.com)
   - Test API Keys 발급
   - Webhook endpoint 등록: `https://yourdomain.com/api/payments/webhook`
   - Event 선택: `checkout.session.completed`, `payment_intent.*`, `charge.refunded`

3. **End-to-End 테스트**
   - [ ] 크레딧 팩 구매 → Stripe Checkout → 크레딧 부여 확인
   - [ ] 면접 시작 → 크레딧 차감 확인
   - [ ] 크레딧 0개 시 접근 차단 확인
   - [ ] AI Generator 구매 → 1회 생성 → 재사용 차단
   - [ ] Q&A Management 구매 → Unlimited CRUD 확인
   - [ ] 환불 처리 → 기능 회수 확인

---

## 🚀 배포 전 체크리스트

### 환경 변수 설정
```bash
# .env에 추가
STRIPE_SECRET_KEY=sk_live_...  # Production key로 변경!
STRIPE_PUBLISHABLE_KEY=pk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...
```

### 데이터베이스 마이그레이션
```sql
-- Supabase SQL Editor에서 실행
\i backend/database/migrations/030_credit_based_billing.sql
```

### Stripe Webhook 설정
1. Stripe Dashboard → Webhooks → Add endpoint
2. URL: `https://api.interviewmate.ai/api/payments/webhook`
3. Events:
   - `checkout.session.completed`
   - `payment_intent.succeeded`
   - `payment_intent.payment_failed`
   - `charge.refunded`

### 보안 체크
- [ ] Webhook signature 검증 활성화
- [ ] CORS 설정 확인
- [ ] RLS 정책 테스트
- [ ] API rate limiting 확인

---

## 💡 향후 개선 사항

### 1. 분석 및 모니터링
- Revenue 대시보드 (Stripe Dashboard 활용)
- COGS 추적 (Deepgram + OpenAI usage)
- Conversion funnel 분석

### 2. 프로모션
- 할인 쿠폰 시스템
- 추천 프로그램 (Referral credits)
- First-time user bonus (5 free sessions)

### 3. 유저 경험 개선
- 크레딧 부족 시 1-click 충전
- 자동 충전 (Auto-reload when < 5 credits)
- Gift credits (팀원에게 크레딧 선물)

### 4. 구독 모델 추가
- Monthly plan: $20/month (unlimited interviews)
- Annual plan: $200/year (2 months free)

---

## 📞 지원

문제 발생 시:
1. **로그 확인**: `backend/logs/`
2. **Stripe Dashboard**: 결제 이슈
3. **Supabase Logs**: DB 쿼리 이슈

---

## 📚 참고 문서

- [Stripe Checkout Docs](https://stripe.com/docs/payments/checkout)
- [Stripe Webhooks Guide](https://stripe.com/docs/webhooks)
- [Supabase Functions](https://supabase.com/docs/guides/database/functions)
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)
