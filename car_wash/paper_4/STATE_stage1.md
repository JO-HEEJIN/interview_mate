# STAGE 1 상태 파일 (세션 인계용) — 2026-07-12

새 세션 부트스트랩: 이 파일 + FABLE_handoff_stage1_reproduction.md +
stage1_qwen_carwash.py 헤더 주석이면 전체 맥락 복원됨.

## 확정 사실 (2026-07-12 스모크)

- **재현 확인됨 (정성 1건)**: Qwen3-8B, A_bare, greedy, thinking=off에서
  walk 오답 커밋 ("...efficient and environmentally friendly to **walk**...
  So, **walk to the car wash**!"). 추론은 walk와 내부 정합하나 과제 전제
  (차가 세차장에 있어야 함)를 무시 — 원 현상과 동형.
- **주의: 아직 재현율 아님** — greedy 1건. 풀런(5조건×N, temp 0.7)으로
  조건별 일관성 확인 전에는 논문용 수치 없음. STAGE 2 착수 금지 유지.
- **스코어러 실물 수정 2건** (합성 감사가 못 잡은 것 — 실물 게이트의 실증):
  ① 형용사+to 권고("efficient to walk")·쉼표/마크다운 낀 명령형 패턴 추가
  ② 아포스트로피 버그 — 인용 제거기가 it's~Here's를 인용문으로 오인해
  구간 블랭킹 → 홑따옴표를 인용 집합에서 제외. 수정 후 스모크 재채점
  committed_wrong=True 정확, 회귀 7/7.
- **보조지표 한계 실측**: answer_before_reasoning은 "100 meters" 재진술이
  추론 마커에 걸려 False — 포맷/재진술 교란. 주 지표는 committed_wrong.

## 현재 상태

- 구현: `stage1_qwen_carwash.py` 완성 (5조건 verbatim, greedy 1 + sampled N,
  thinking on/off, 챌린지 턴, raw.jsonl+summary.json). 스코어러 단위테스트 통과.
- 진행 중 1: Qwen3-8B 로컬 다운로드 (~/.cache/huggingface, 16GB 중 진행) →
  완료 시 `--smoke --device mps`가 A_bare 첫 롤아웃 출력 (venv:
  /Users/momo/dev/b2d_geo/detection/.venv/bin/python 사용).
- ⚠ 홀드아웃 결과 수신 시 **스코어러 버전부터 확인** — 위 실물 수정 2건
  이전 버전으로 채점됐을 수 있음. 기수정 계열 불일치는 현행판 재채점으로
  정산 후에만 불일치율 판정.
- 진행 중 2: 홀드아웃 감사 워크플로 (신규 함정 4렌즈 × 8케이스 → 수정본
  스코어러 대조). 결과 미수신 시점에 이 파일 작성됨.
- 완료: 1차 적대 감사 32케이스 → 불일치 12 → 수정 6종 → 원 루브릭 10/10.

## 스코어러 수정 6종 (전부 일반 규칙, 케이스 하드코딩 0)

1. 커밋 패턴 계열 추가: you must/need to/have to, TL;DR:, Verdict:,
   final answer:, 1인칭 "I'd (just) walk", 명령형 "so/just drive it over".
   ※ 열거식 본질의 꼬리 위험 잔존 — 홀드아웃과 실물 수동 대조가 보완.
2. 부정 가드 구조 교체: 직접 인접 6형태 → 커밋 앞 60자 윈도우 +
   부정·전언 어휘군 (not saying / not going to / would tell you / enthusiast 등).
3. 인용부호 내부 발화 제거 (10~200자 인용 스팬 공백 치환 후 탐색).
4. 헤드라인 커밋 패턴에서 ':' 제외 — 비교 나열 섹션헤더("Driving:") 오탐 차단.
5. <think> 외 <thinking> 태그 변형 분리 지원.
6. 의미론 분리: committed_*(첫 커밋=선커밋 구성개념) vs final_*(마지막 유효
   권고) + retracted. 집계에 pct_final_wrong, pct_retracted 추가.

## 홀드아웃 설계 (과적합 판정)

- 신규 4렌즈 (1차와 분류군 분리): 수사의문·반어 / 조건 분기 이중권고 /
  장문 만연체 속 묻힌 커밋 / 재진술·요약 반복.
- 생성자는 스코어러 구현 비공개 상태로 사람-기준 라벨.
- 조건분기형은 사람도 갈릴 수 있음 — 불일치를 "스코어러 결함 vs 라벨
  모호"로 구분 보고.

## Go / No-Go 임계 (홀드아웃 불일치율, 라벨-모호 제외 후)

- **≤ 5%**: 스코어러 신뢰 — 풀런 진행.
- **5~15%**: 결함 유형만 일반 규칙로 수정 → **또 다른 신규 홀드아웃**으로
  재검 (같은 배치 재사용 금지).
- **> 15%**: 정규식 접근 한계 판정 — LLM-judge 채점(별도 모델로 라벨) 전환
  검토. 단 judge 도입 시 judge 자체의 검증 계획 필요.

## 홀드아웃 판정 결과 (2026-07-12) — 임계 초과, LLM-judge 전환

- 현행판 스코어러 확인(mtime+결정성 2회) 후 채점: **케이스 불일치 62.5%
  (20/32), 필드 45.8%** — >15% 임계 초과 → 사전 규칙대로 정규식 단독 기각.
- 구조: 적극 오탐 1건(수사의문 물음표 가드 부재)뿐, 나머지 전부 미검출
  (비키워드 콜론·문중 명령형·어순 도치·em-dash). 열거식의 구조적 한계.
- 전환: `judge_rollouts.py` — LLM-judge 채점(로컬 Qwen3-8B, greedy, JSON
  루브릭). **채택 게이트: 합성 64케이스(사람 라벨, judge 미튜닝) 정확도
  committed_answer ≥0.95.** 정규식은 보조 진단(judge 일치율 리포트)으로 강등.
- 검증셋 보존: audit_cases_batch1.json(32) + audit_cases_batch2_holdout.json(32).
- 논문 최종 채점은 외부 judge 재실행 가능 (raw 텍스트 보존이 보장).

## Judge 검증 결과 (2026-07-12) — 게이트 통과, 채택

- committed_answer **62/64 = 96.9%** (게이트 ≥95% 통과), final_answer 31/32,
  parse 실패 0. 상세: judge_validation_report.json.
- committed_answer 불일치 2건 모두 사전 예고된 라벨-모호 계열
  (부정형 "Don't walk"의 함의 커밋, 조건분기형) — 명백한 judge 오류 0건.
- **answer_before_reasoning 53/64 = 82.8% — 신뢰 불가, 보조 강등 확정.**
  논문 주장에서 제외, 수동 게이트에서만 확인. ⚠ 검증셋에 맞춘 프롬프트
  튜닝 금지 (정규식과 동일한 과적합 함정) — 루브릭 프롬프트 동결.
- 채점 실행: `judge_rollouts.py --score results/<ts>/raw.jsonl` →
  raw_judged.jsonl (judge_* 필드 + 정규식 일치 진단 judge_regex_agree).

## 풀런 1차 결과 (2026-07-12, results/20260712_141841) — 재현 확정 + 아티팩트 1건

- **재현 확정 (rate 수준)**: thinking-off에서 조건별 walk 오답 커밋
  85~100% (A 85, B 90, C/D/E 100%). greedy off 전조건 100%.
- **전역**: judge 커밋 walk=170 / drive=1 / null=39. 커밋한 롤아웃의
  99.4%가 오답 — 현상이 확률적 아니라 준결정적.
- **아티팩트**: thinking-on null 39중 32건 = `<think>` 미폐쇄 절단
  (max_new_tokens=1024 부족). thinking-on 수치 오염 → **4096으로
  thinking-on 팔 전체 재생성 중** (--thinking on, 새 results dir).
  off 팔은 절단 0건(>3600자 0) — 유지.
- 절단된 think 꼬리들: 모델이 전제("차가 세차장에 있어야")와 씨름하는
  흔적 — thinking은 전제를 건드리나 non-thinking은 즉답. STAGE 2 가설감.
- 병합 규칙: off=1차 런, on=재생성 런. 집계는 aggregate_judged.py.

## 최종 병합 결과 (2026-07-13, results/merged_final) — STAGE 1 수치 확정

- 절단 아티팩트 완전 제거 (4096 예산, no-think-block 0/210).
- walk 오답 커밋률 (judge, sampled n=20): off A85/B90/C100/D100/E100 %,
  **on A85/B90/C100/D85/E85 %**. greedy 전조건·전모드 100%.
- **핵심 발견: thinking이 현상을 못 고침.** 절단런의 "thinking 완화"는
  아티팩트였음. 전체 예산 생각 후에도 85~100% walk 커밋 — 장고 끝 오답.
- drive(정답) 커밋: 210중 10건 (off 1, on 9) — thinking이 주는 건 ~5%p의
  미미한 구제뿐. C_role_star는 양 모드 100% (STAR 구조가 고착 최강).
- 커밋 분포: off walk100/drive1/null4, on walk94/drive9/null2.
- 산출: results/merged_final/{raw_judged.jsonl, condition_rates.json,
  manual_gate_sample.md(층화 20, seed=42)}.
- 남은 게이트: 수동 hand-check 20 → 통과 시 STAGE 1 종료, STAGE 2 논의.

## 수동 게이트 통과 (2026-07-13, 사용자 직접 검수) — STAGE 1 공식 종료

- **20/20 judge 라벨 정확** (manual_gate_sample.md에 [v] 체크 보존).
- 사용자 지정 핵심 케이스 (논문 전시물):
  - **[160] C_role_star/on**: think 블록이 상황 정확 파악 후 결정적 질문
    ("차를 세차장에 가져가야")에 미도달, "걸음 수 효율" 축 이탈 →
    "추론 성실·답 오류"의 결정적 실물. Figure 1 후보.
  - **[22] B_role_only/off**: 정규식 미검출(None)을 judge가 정확 검출(walk)
    — 채점기 전환 정당화의 실물 증거.
- 게이트 전체 통과 이력: judge 검증 96.9% / 라벨 결정성 8/8 / 홀드아웃
  프로토콜 집행(정규식 기각) / 풀런 210 / 수동 20/20.
- **STAGE 2 (activation oracle) 착수 가능 상태.** 설계는
  pre_commitment_AO_experiment_design_v0.md §1 STAGE 2 + §2 통제 참조.

## 필수 최종 게이트 (합성 검증과 무관하게 무조건)

풀런 후 **실제 Qwen 롤아웃 15~20개를 수동 대조** (스펙 의무).
추출은 층화 (사용자 지시 2026-07-12): ① 각 조건(5개) 최소 2개
② thinking_mode=on ∧ has_think_block=False 케이스 의도 포함 (풀런 중
실재 확인됨 — 버그 vs Qwen 동작 판별 겸용) ③ 잔여는 무작위, 고정 seed.
합성 홀드아웃은 필요조건일 뿐 — 집계 신뢰는 이 게이트 통과 후에만.
불일치 발견 시 해당 유형 수정 → 전체 재채점 (재생성은 불필요, raw.jsonl
텍스트에 스코어러만 재적용).

## 그 다음 (변경 없음)

스모크 눈검사 → 풀런 (5조건 × [greedy+20] × thinking both, 로컬 MPS 가능)
→ 수동 게이트 → summary 보고. STAGE 2 착수 금지 (STAGE 1 재현 확인 후).
