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

## STAGE 2 착수 (2026-07-16) — oracle 경로 로컬 MPS 검증 완료

- AO 저장소: /Users/momo/dev/activation_oracles (repo 밖 클론).
  oracle LoRA: adamkarvonen/checkpoints_latentqa_cls_past_lens_addition_Qwen3-8B.
- 데모 노트북 라이브러리 셀 → ao_demo_lib.py 벤더링. **이탈 1건**:
  신형 transformers가 apply_chat_template(tokenize=True)에서 BatchEncoding
  반환 → list 언랩 4줄 패치 (create_training_datapoint). 그 외 원본 그대로.
- CUDA+8bit 대신 MPS+bf16 (bitsandbytes MPS 불가). Colab 불필요.
- 스모크 (stage2_oracle_smoke.py): car wash 질문 29토큰 전 위치 oracle 응답.
  중간 토큰에서 "optimal time to leave for the car wash" — 활성값에서
  도메인 의미 판독 확인. 경계 토큰(im_start/개행)은 모호 — 정상.
- 다음 결정 (사용자와): oracle 질문 문구 / 위치 그리드 / §2 통제 구성.

## STAGE 2 1차 프로브 결과 (2026-07-16, stage2_results/ao_probes.jsonl)

- 설계: 22 롤아웃(walk 16 = C/A×on/off×4, drive 6) × 그리드 6위치
  (P0 시작, P1-P3 커밋까지 25/50/75%, P4 커밋 직전, P5 커밋+8).
  oracle 질문 "What answer is this model going to give?", 단일토큰 프로브,
  greedy. 스크립트 stage2_ao_experiment.py (resume 내장).
- walk군 배타언급 적중: P0 0/16, P1 1/16, **P2 8/16**, P3 6/16,
  P4 4/16, P5 3/16. drive군: 전위치 ~0 (P3 2/6뿐).
- 해석 (정직): ① 커밋 텍스트 이전 P2에서 50% 신호 — pre-commitment
  시사 예비 신호. ② **그러나 양성통제 P5(텍스트 노출 후)가 3/16로 약함**
  — 단일토큰 프로브 신뢰도 부족, 이 상태로는 주장 불가 (설계문서
  "노이즈 심함, 반복+통계" 경고 실증). ③ drive군 0 근접 — oracle의
  walk 어휘 편향 vs 진짜 활성값 차이 미분리, 통제 필요.
- [160]: P2에서 walk 언급, P4/P5 무관 응답(도메인 이탈 환각) —
  단일 프로브 노이즈 전형.
- 다음 후보: 위치창 평균(그리드점당 ±2 토큰 5프로브 다수결),
  segment 입력 모드, layer 25/75% 스윕, oracle 질문 A/B.

## STAGE 2 이터레이션 1 결과 (2026-07-16) — 관문 실패, segment 모드 진입

- 창-다수결(±2, 5표): walk군 P5 3/16 -> 3/16 **복구 실패** (사용자 관문
  ~10/16+). P5 투표 13/16 롤아웃이 4-5표 none — 요동 아닌 일관 무신호.
  다수결이 P2 8->4, P4 4->0으로 산발 신호도 억제 — v1 P2 50%는 노이즈 쪽.
- 사전 분기 집행: 토큰 프로브(단일/다중) 기각 -> **segment 입력 모드**
  (stage2_ao_segment.py, 실행 중). 변경: 구간째 1질문 주입, 양성통제
  P5=[commit_tok, +8]로 커밋 토큰 포함 강화 (P0-P4는 커밋 전 엄수 유지).
- layer 스윕/질문 A/B는 양성통제 선 이후 (사용자 순서 지시).

## STAGE 2 최종 (2026-07-16) — 질문 A/B 복구 → 그리드 → 중립 통제 (B) 판정

- segment도 P5 2/16 실패 → **질문 A/B가 원인 갈랐다**: Q1 개방형 2/16,
  Q2 "recommending" 7/16, **Q3 폐쇄형("walk or drive?") 11/16** — 질문
  문구 문제(a), LatentQA 분포엔 폐쇄형. 도구 한계 아니었음.
- Q3 전체 그리드: walk군 P0 6/16 → P4 10/16 → P5 11/16 (단조 경향,
  페어드 P0→P4 개선7/악화3 p≈0.34 단독 비유의). drive군 커밋 전
  위치가 walk로 판독 (P4 5/6) → (A)편향/(B)조기 walk-lean 판별 필요.
- **중립 통제 (8 무관 프롬프트 × 3위치): oracle 고유 walk율 4/23=17%**
  (기본값 drive 83%). 사전 규칙 구간(40-60/≥70) 밖, 방향은 (B) 지지:
  walk 판독만 정보적 — 커밋 전 walk 판독률 15/22=68% vs 기준선 17%.
- **(B) 판정**: pre-commitment(walk)가 커밋 전 활성값에서 판독되며,
  drive 최종답 롤아웃조차 커밋 전엔 walk-lean — STAGE 1 "기본상태
  walk, thinking이 늦게 전복" 행동 서사의 내부 대응물.
- 각주: drive 판독은 무정보(oracle 기본값), 양성통제는 walk쪽만 성립,
  drive군 n=6. 위치 곡선 단독 통계 약함 — 중립 대비로만 유의.
- 사전 합의대로 STAGE 2 프로빙 종료. 산출: stage2_ao_{experiment,window,
  segment,qab,neutral}.py + stage2_results/*.jsonl 5종.

## Lexical 층화 (2026-07-16, 기존 데이터 재분석) — text-inversion 관문 통과

- stage2_lexical_strata.py: 커밋 전 110프로브를 (a)주입 구간 5토큰
  (b)±25토큰 문맥의 walk/drive 단어 유무로 층화.
- **주입 구간 inversion 기각**: 구간에 walk 있으면 25%(2/8), 없으면
  63%(64/102). drive 단어 든 구간 6건이 walk로 판독 (" not need to
  drive." → walk).
- **균형 어휘장(둘 다, 90/110=82%)이 결정타**: walk판독 52 vs drive 20
  — walk share 72% vs oracle 중립 기본 17% (p=4e-6), 50:50 대비 p=1e-4.
  drive-커밋 롤아웃의 균형장: walk 20/28, drive 1/28 (p=1e-7) —
  어휘장은 둘 다 명명, oracle 기본은 drive, 최종답도 drive인데 판독은
  walk. 순수 텍스트 읽기로 설명 불가.
- 잔여 경고: 단일 단어 장(walk-only 12/12, drive-only 추종)에선 oracle이
  어휘장을 따름 — 소수층 개별 프로브는 해석 불가. ±25토큰은 "local"의
  한 조작화일 뿐.
- 초안 §3.4 신설 + 한계 개정 + 초록 반영.

## 발행 전 감사 (2026-07-16, 3렌즈 워크플로 + 적대검증) — 18건 확정, v0.3

- **블로커 1 (통계)**: §3.4 풀링 Fisher가 롤아웃 내 5프로브를 독립 취급
  (pseudoreplication). 수정: 클러스터 보정 1차화 — 균형장 per-rollout
  다수결 vs 중립 per-prompt 다수결(1/8). walk군 9/16 p=.051(경계),
  **drive군 6/6 p=.002**, 합산 15/22 p=.010. 풀링 수치는 descriptive 강등.
  §3.3 P4 검정(롤아웃당 1프로브)은 원래 깨끗 — 유지.
- **블로커 2 (§2.3 수치)**: "all 32 null" → 실제 null 35 / 절단 31 /
  진성 무커밋 4. "45–75%" → 45–95%.
- **regex 오염**: \bdriv\w*가 "driveway" 매치 — lexical 문맥 플래그
  경미 이동 (BOTH 90→89, drive-span 9→8 중 walk 5). **프로브 verdict는
  0/132 변화 (강건)**. 엄밀 경계 regex로 교체, 전 산출물 재계산.
- 기타: 13/16→10/16, 3.7×→3.6×, [160] 묘사 정정(차 위치를 '스치고
  지나감'이 정확 — '파악했다' 아님), 교차참조 3.4→2.4, "strictly worse"
  완화, 근거 누락 10건 본문 반영 (bf16/디코딩/게이트 임계/수동게이트
  스펙/layer 기본값/선정규칙/drive 6-10 제외기준/중립 분모/사전 구간).
- 한계 추가: 단일 layer, 비무작위 선정.
- ⚠ 발송된 Euan 메일의 20/28(p=1e-4)은 감사 전 수치 — 교정 후 20/27,
  클러스터 보정으로는 6/6 p=.002. 방향 불변, 답장 시 논문이 진실원.

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
