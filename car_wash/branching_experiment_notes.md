# Branching vs STAR-for-All Experiment (2026-03-08)

**목적:** Production prompt 구조 결정 (논문 미포함)
**코드:** `car_wash/experiment_branching.py`
**결과:** `car_wash/results/branching_20260308_015114/`

## 파라미터
- Model: claude-sonnet-4-6
- Judge: claude-sonnet-4-6
- Temperature: 0.7
- Runs per cell: 10
- Cells: 2 prompts x 5 questions = 10

## 두 프롬프트 비교

| 구분 | branching (원래 production) | star_all (실험 상태) |
|------|---------------------------|---------------------|
| 구조 | PREP (Point-Reason-Example-Point) + 질문 유형별 분기 | STAR 전체 적용, 분기 없음 |
| STAR 적용 | behavioral 질문에만 | 모든 질문에 |
| Yes/No 처리 | "10단어 이내" 명시 | 없음 |

## 결과

| 질문 유형 | branching | star_all | 승자 |
|-----------|-----------|----------|------|
| Car wash (pass rate) | **50%** (5/10) | 10% (1/10) | branching |
| Yes/No (criteria avg) | **67%** (15.6w) | 33% (42.0w) | branching |
| Direct (criteria avg) | 77% (75.1w) | **87%** (75.3w) | star_all |
| Behavioral (criteria avg) | **100%** (172.3w) | 95% (150.6w) | branching |
| Compound (criteria avg) | 100% (188.3w) | 100% (192.8w) | 동점 |

## Reasoning Order (결론 먼저 vs 추론 먼저)

| 질문 유형 | branching (C/R/M) | star_all (C/R/M) |
|-----------|-------------------|------------------|
| Yes/No | 10/0/0 | 10/0/0 |
| Direct | 10/0/0 | 10/0/0 |
| Behavioral | **1/5/4** | 6/1/3 |
| Compound | 8/0/2 | 9/0/1 |

C=conclusion_first, R=reasoning_first, M=mixed

## 핵심 발견

1. **Car wash: branching 50% vs star_all 10%**
   - branching이 더 높지만, n=10이므로 95% CI가 ~19-81%. 통계적으로 유의미하다고 보기 어려움.
   - star_all에서 ambiguous 5개 — STAR로 길게 풀어쓰면서 양쪽 다 언급하는 패턴.
   - 둘 다 production prompt 안에서는 STAR dilution 발생.

2. **Yes/No: star_all이 명확히 나쁨**
   - star_all: 평균 42단어. STAR 구조로 yes/no를 풀어쓰니 간결성 완전히 상실.
   - branching: 평균 15.6단어. 면접 답변으로 훨씬 적절.
   - starts_with_yes_or_no는 둘 다 100% — 첫 단어는 맞추지만 이후가 문제.

3. **Behavioral: branching이 reasoning_first 비율 높음**
   - branching: reasoning_first 50% (R5/M4)
   - star_all: conclusion_first 60% (C6/R1)
   - 역설적: PREP이 있는데 behavioral에만 STAR을 적용하는 분기가 오히려 reasoning 순서를 잘 유도.

4. **Direct/Compound: 큰 차이 없음**

## Production 결정을 위한 시사점

**둘 다 완벽하지 않다.**

- branching: 면접 답변 품질은 좋지만 (yes/no 간결, behavioral STAR), car wash 같은 implicit constraint 문제에서 50%는 불안정.
- star_all: car wash도 나쁘고(10%), yes/no도 나쁨(42w verbose). STAR을 모든 질문에 적용하면 오히려 역효과.

**가능한 방향:**
1. branching으로 revert — 면접 코칭 품질이 더 중요하다면
2. hybrid — branching 기본 + behavioral/constraint 질문에서 "결론 먼저" 지시를 제거
3. STAR 위치 변경 — STAR을 프롬프트 맨 끝에 배치하여 recency bias 활용

## 논문 미포함 사유
1. n=10으로 통계적 신뢰도 부족 (기존 데이터는 n=20, n=100)
2. 논문 목적("STAR dilution 증명")과 실험 목적("production 구조 결정")이 다름
3. star_all 10%는 기존 데이터(A:0%, B:30%)와 일관 — 새 정보 적음
