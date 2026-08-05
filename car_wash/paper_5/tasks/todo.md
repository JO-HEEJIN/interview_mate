# paper_5: Qwen3-8B 수확 작전 — Task 0 탐색 결과 + 실행 계획

작성: 2026-08-05. **2026-08-05 사용자 승인 + 수정사항 반영 (아래 §7).**

## 7. 승인된 수정사항 (2026-08-05)

1. Gate A/B/C 승인. Gate C 전제 확인 완료: grid_q3 생산자 =
   stage2_ao_segment.py (--oracle-q Q3), oracle kwargs do_sample=False /
   temp 0.0 → greedy 확정. 불일치 발생 시 자동 실패 아님 — 정지 후 사례
   보고 (의미적 불일치 vs 후반부 수치 드리프트 구분).
2. 포맷: safetensors + bf16 (torch .pt 기각 — pickle 없는 이식 포맷).
   로드 검증도 safetensors 기준.
3. 전용 venv 신설: /Users/momo/qwen3_venv, 기존 venv pip freeze 동일
   버전 (paper_5/requirements_freeze.txt, python 3.13.9). freeze 전문
   manifest에 기록. b2d_geo venv 공유 금지, 실패 시에만 읽기 전용
   fallback + 보고.
4. Task 2 승인. (a) 원 설정 확인: temp 0.7 (summary.json), top_p 0.95
   (stage1 코드 고정), max_new_tokens off팔 1024 / on팔 4096. 신규는
   양팔 4096 (분포 불변, 절단만 방지). (b) 목표: 총 n>=100 그리고
   drive-commit >=30. 최종 분할 manifest 기록.
5. Task 3: ① phone-dead 승인. ② tire 조건부 — "공기압 약간 낮음" 수준
   문구로 drive 논쟁 불가화, 확정 문구(한/영) 생성 전 제시. ③ 보류.
   메타데이터에 제약 유형 라벨: car wash 계열 = implicit(미진술),
   phone-dead = stated(진술됐으나 무시). 서로 다른 계층으로 기록.
6. 매5토큰 샘플링: 토큰 0부터 전체 시퀀스 포함 승인.
7. 추가: qwen3_archive/originals/에 raw_judged.jsonl,
   ao_probes_grid_q3.jsonl, ao_neutral_control.jsonl 사본 포함 (원본
   무변경). 재생성 중립 기준선 전문은 head 120자 대조 통과 후
   texts.jsonl 포함. 텍스트-프로브 오프셋-활성값 삼종 한 폴더 완결.

## 0. 탐색 결과 (사실)

### 파이프라인 위치
- 생성: `paper_4/stage1_qwen_carwash.py` — 5조건(A~E), greedy 1 + sampled n,
  temp 0.7, top_p 0.95, seed별 `torch.manual_seed`, thinking on/off,
  max_new_tokens 1024(off) / 4096(on 재생성런). 원문 raw.jsonl 보존.
- 라벨: `paper_4/judge_rollouts.py` (로컬 Qwen3-8B judge, greedy) →
  `judge_committed_answer`. 커밋 위치는 정규식 `commit_char_pos`
  (judge_regex_agree=true인 경우만 신뢰) — stage2 선정 로직과 동일.
- 롤아웃 원문: `paper_4/results/merged_final/raw_judged.jsonl` (210 rows,
  char len 446~15,772, median 1,864). 22개 선정 로직 =
  `stage2_ao_experiment.select_rollouts()` (C_role_star/A_bare × on/off
  walk-commit 각 4 + drive-commit 6).
- 활성값 추출: `paper_4/ao_demo_lib.py` `collect_activations_multiple_layers`
  — `model.model.layers[i]` forward hook, residual stream (블록 출력),
  bf16, MPS. L18 = `layer_percent_to_layer("Qwen3-8B", 50)` = 36×0.5 = 18.
- 프로브 위치 정의: `stage2_ao_experiment.py` — P0 assistant_start,
  P1/P2/P3 = 커밋까지 25/50/75%, P4 = commit_tok-1, P5 = commit_tok+8.
  최종 Q3 그리드런(`ao_probes_grid_q3.jsonl`)은 각 그리드점에서 5토큰
  span 세그먼트 프로브. 저장 필드에 a_start_tok / commit_tok / n_tok 있음.
- 중립 기준선: `stage2_ao_neutral.py` — 8개 무관 프롬프트, greedy,
  thinking off, max_new_tokens 256, 응답의 25/50/75%에 5토큰 세그먼트.
- 환경: Qwen3-8B(15GB) + oracle LoRA 캐시 완료. venv
  `/Users/momo/dev/b2d_geo/detection/.venv` (torch 2.12.1, transformers
  5.13.1, peft 0.19.1, MPS OK). 디스크 여유 2.5TB.

### 중요 발견 1 — 저장된 활성값 텐서는 존재하지 않음
전체 디스크 검색 결과 .pt/.npy/.npz/.safetensors 형태의 L18 활성값
파일 없음. stage2는 활성값을 매번 즉석 추출해 oracle에 주입하고
**oracle의 텍스트 응답만** jsonl로 저장했다. 따라서 미션의 Task 1 검증
관문("기존 저장 활성값과 코사인 0.999 대조")은 명시된 형태로는 실행
불가. → §2의 대체 관문 제안 참조. **승인 필요.**

### 중요 발견 2 — 중립 기준선 원문 미보존
`ao_neutral_control.jsonl`은 `response_head` 앞 120자만 저장. 단, 생성이
greedy + thinking off + 256토큰이므로 결정적 재생성 가능. 재생성 후
저장된 head 120자와 전건 일치 확인을 원문성 검증으로 삼는다.

## 1. 아카이브 저장 명세 (제안)

- 포맷: 롤아웃당 1개 `.pt` (torch.save):
  `{"positions": int64[P], "acts": bf16[36, P, 4096], "meta": {...}}`
  + 서브셋별 `texts.jsonl`(원문/시드/샘플링 파라미터/조건/judge 라벨/
  commit 위치) + `index.json`.
  근거: bf16은 numpy 미지원 → torch 네이티브가 CUDA 이식에 최적.
- dtype: bf16 (기존 추출 경로의 연산 dtype과 동일. 기존 "저장" dtype은
  존재하지 않으므로 이것이 기준). manifest에 명기.
- 레이어: layers[0..35] 블록 출력 36개 전부.
- 용량 산출 (위치당 36×4096×2B = 0.28MB):
  - original_22: 위치 = P0-P5 + commit±20(41) + 매5토큰(평균 ~250) ≈
    평균 300/롤아웃 → ~1.9GB (최장 롤아웃 ~270MB 포함, 총합엔 여유)
  - baselines(8): ~0.17GB
  - scaled_carwash(신규 ~80): P그리드 + commit±20 = 47위치 → ~1.1GB
  - new_tasks(3×20=60): ~0.8GB
  - reference_vectors: 22 × P0-P5 × 36레이어 ≈ 38MB
  - **총 ~4.0GB ≤ 5GB 목표.** 초과 시 매5토큰 → 매10토큰 강등 + 보고.

## 2. Task 1 — 재추출 + 대체 검증 관문 (승인 필요 항목)

새 스크립트 `paper_5/extract_activations.py` (기존 코드 재사용:
build_messages/CONDITIONS/QUESTION import, collect_activations_multiple_layers
import, 타깃 시퀀스 재구성은 stage2_ao_experiment.py 로직 복제).

대체 관문 3중:
- **Gate A (오프셋 일치, 필수)**: 22 롤아웃 전건에서 재계산한
  a_start_tok / commit_tok / n_tok == `ao_probes_grid_q3.jsonl` 저장값.
  하나라도 불일치 → 즉시 정지, 보고. (토크나이저/프리픽스 드리프트 검출)
- **Gate B (결정성, 필수)**: 독립 2회 prefill 간 L18 프로브 위치 코사인
  ≥ 0.999 전건. (수치 안정성 검출)
- **Gate C (oracle 등가, 필수)**: 추출과 동일 세션에서 stage2와 동일한
  run_oracle 호출(greedy, Q3, 저장된 span)로 6그리드 프로브 재실행 →
  `ao_probes_grid_q3.jsonl` 응답 텍스트와 대조. 기대 전건 일치(greedy
  결정적). verdict 수준 100% 미달 시 정지·보고. (레이어 인덱스/주입
  경로 버그 검출 — 원래 관문의 의도를 가장 직접 대체)
- 관문 통과 후 reference_vectors/ 저장 (P0-P5, 36레이어, 22롤아웃).
- 중립 기준선: greedy 재생성 → head 120자 전건 일치 확인 → 동일 명세
  추출 (P그리드 대신 p25/50/75 span + 매5토큰 + 응답 구간).

## 3. Task 2 — n 스케일업 (파라미터 확인 요청)

- 생성: `stage1_qwen_carwash.py` 재사용, `--conditions A_bare,C_role_star
  --thinking both --temperature 0.7 --max-new-tokens 4096`, top_p 0.95
  (코드 고정값), 신규 seed 대역 (기존과 비충돌, 예: 1000~), n은 눈덩이
  — judge 라벨 + 위치 신뢰(judge_regex_agree) 롤아웃 누계가 기존 22 포함
  **총 100 이상** 될 때까지 배치 반복 (배치당 조건×모드당 10).
- 라벨: judge_rollouts.py 그대로 재실행.
- 위치 불신뢰 롤아웃: 텍스트는 전부 아카이브, 벡터는 commit 위치 신뢰
  건만 (paper_4와 동일 기준). manifest에 `extends: paper_4`.
- nohup 백그라운드 + 로그 파일.

## 4. Task 3 — 신규 태스크 후보 3 (승인 대기)

같은 구조: 암묵적 물리 제약 / 이지선다 / 직관답이 제약 위반 / 정답 무논쟁.
1. **phone-dead** (제약 계열: 도구 부재): "My phone battery is dead. I
   need to book a table at a restaurant 100 meters away. Should I call
   them or walk over?" — 정답 walk (전화 불가).
2. **tire-air** (계열: 대상물 동반 필수, car wash 동형): "My car's tires
   are low on air. The air pump is at the gas station 100 meters away.
   Should I walk or drive there?" — 정답 drive (차가 가야 공기 주입).
3. **scooter-charge** (계열: 대상물 동반, 변형): "My electric scooter's
   battery is empty. The charging station is 100 meters away. Should I
   walk there or ride the scooter?" — 정답 walk-pushing-it 계열 아님:
   ride 불가(배터리 empty) → 정답 walk (스쿠터 끌고). ※ 3안은 정답
   서술이 이지선다에 덜 깔끔 — 대안 제시 가능. 2개만 채택도 가능.
- 채택안별 20 롤아웃 (조건 A_bare + C_role_star? 아니면 A_bare만? —
  **확인 필요**), Task 2 저장 명세, 라벨 `seeds: paper_5`.
- commit 판정: judge 프롬프트의 walk/drive 어휘를 태스크별 선택지로
  치환한 변형 필요 (최소 수정) — 루브릭 구조는 동결 유지.

## 5. Task 4 — 패키징

- 스모크: 무작위 5샘플 로드 → shape/dtype/값범위/메타 정합 →
  VERIFICATION_REPORT.md.
- manifest.yaml: 모델/토크나이저/dtype/레이어/위치명세/일시/git hash/
  서브셋 라벨. REGENERATE.md: CUDA 재생성 절차 + reference_vectors 대조
  관문 (코사인 0.999).
- paper_5/data/에 texts.jsonl 전체 + manifest + REGENERATE 사본 커밋.
  .gitignore에 *.pt 확인/추가.

## 6. 미결 질문 (승인 시 답 필요)

1. **대체 검증 관문 (§2 Gate A/B/C) 승인?** 원 명세의 "저장 활성값
   대조"는 저장물 부재로 불가.
2. 저장 포맷 torch .pt + bf16 승인? (대안: float32 npz — 용량 2배)
3. venv: b2d_geo의 .venv를 읽기 전용으로 실행에만 사용 (레포 무변경).
   허용? (대안: 전용 venv 신설, 설치 ~10분)
4. Task 2 seed 대역 1000~, 배치당 조건×모드당 10 승인?
5. Task 3 후보 중 채택안 + 롤아웃 조건 (A_bare만 vs A_bare+C_role_star).
6. 매5토큰 샘플링에 프리픽스 구간 포함 (시퀀스 전체 0부터). OK?
