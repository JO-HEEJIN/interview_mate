# Committed Before Reasoning — car-wash pre-commitment study

Behavioral reproduction of an answer-before-reasoning failure on Qwen3-8B,
plus preliminary activation-oracle probing of the commitment before it is
emitted. Paper draft: [`draft_carwash_paper.md`](draft_carwash_paper.md).

The task: *"I want to wash my car. The car wash is 100 meters away. Should
I walk or drive?"* — only *drive* works (the car must be at the car wash).
Qwen3-8B commits to "walk" in 85–100% of rollouts per condition, and a
4k-token thinking budget does not fix it.

Everything runs on a single Apple-silicon laptop (MPS, bf16). No CUDA, no
quantization, no cloud GPU.

## Requirements

```
python >= 3.11
torch, transformers, peft, pydantic, scipy, tqdm
```

Models download from Hugging Face on first run: `Qwen/Qwen3-8B` (~16 GB)
and the oracle LoRA
`adamkarvonen/checkpoints_latentqa_cls_past_lens_addition_Qwen3-8B`.

## Pipeline (in order)

| Step | Command | Output |
|---|---|---|
| 1. Generate rollouts | `python stage1_qwen_carwash.py --device mps --n 20 --thinking both --max-new-tokens 4096` | `results/<ts>/raw.jsonl` (210 rows) |
| 2. Validate the LLM judge | `python judge_rollouts.py --validate` | accuracy vs. 64 human-labeled cases (gate: ≥95%) |
| 3. Score rollouts | `python judge_rollouts.py --score results/<ts>/raw.jsonl` | `raw_judged.jsonl` |
| 4. Aggregate + manual-gate sample | `python aggregate_judged.py results/<ts>/raw_judged.jsonl` | `condition_rates.json`, `manual_gate_sample.md` |
| 5. Oracle probes (grid) | `python stage2_ao_segment.py --oracle-q "Is the model going to say walk or drive?" --out ao_probes_grid_q3.jsonl` | `stage2_results/ao_probes_grid_q3.jsonl` |
| 6. Neutral-context baseline | `python stage2_ao_neutral.py` | `stage2_results/ao_neutral_control.jsonl` |
| 7. Lexical stratification | `python stage2_lexical_strata.py` | `stage2_results/lexical_strata.json` |
| 8. All reported statistics | `python compute_statistics.py` | `stage2_results/statistics.json` |

Long generation runs support resume (`--resume-dir results/<ts>`): completed
(condition, mode, kind, seed) rollouts are skipped and appended to the same
file.

The probe-variant scripts kept for the audit trail (they document the
failed configurations discussed in the paper): `stage2_ao_experiment.py`
(single-token probes), `stage2_ao_window.py` (window majority voting),
`stage2_ao_qab.py` (oracle question A/B on the positive control),
`stage2_oracle_smoke.py` (pathway smoke test).

## Key files

- `stage1_qwen_carwash.py` — 5-condition rollout harness (greedy + sampled,
  thinking on/off, challenge turn, resume).
- `judge_rollouts.py` — LLM-judge scorer with a frozen rubric; `--validate`
  runs the adoption gate against `audit_cases_batch1.json` +
  `audit_cases_batch2_holdout.json` (64 human-labeled cases, never used to
  tune the rubric).
- `ao_demo_lib.py` — activation-oracle demo library vendored from
  [adamkarvonen/activation_oracles](https://github.com/adamkarvonen/activation_oracles)
  (notebook library cell), with a 4-line compatibility patch for newer
  transformers (`apply_chat_template` returning `BatchEncoding`). MPS works
  unmodified; 8-bit quantization replaced by bf16.
- `stage2_lexical_strata.py` — text-inversion control: stratifies every
  pre-commit probe by literal walk/drive occurrence in the injected span
  and in ±25-token context.
- `compute_statistics.py` — derives every p-value in the paper from the
  committed raw JSONs (`stage2_results/statistics.json`).
- `results/merged_final/` — the 210 judge-scored rollouts behind the
  behavioral table (thinking-off arm from the first full run; thinking-on
  arm regenerated at 4,096 tokens after the truncation artifact described
  in the paper, §2.3).

## Headline numbers (all reproducible via step 8)

- Wrong commitment (walk): 85–100% per condition, both thinking modes;
  194 walk / 10 drive / 6 none over 210 rollouts.
- Oracle question sensitivity: positive control 2/16 (open question) →
  11/16 (closed question), same activations and positions.
- Pre-commit walk read-outs vs. 17% neutral default: walk-committing
  rollouts 10/16 (p=.005), drive-committing rollouts 5/6 (p=.005).
- Text-inversion control: in balanced lexical fields, walk share 72% vs.
  17% default (p=4e-6); drive-committing rollouts 20/28 walk vs. 1/28
  drive (conservative p=1.3e-4).
- Not significant: within-rollout positional gradient (p=.34). Treated as
  preliminary throughout.
