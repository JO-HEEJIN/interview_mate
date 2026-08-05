# Qwen3-8B Archive Verification Report

Model: Qwen/Qwen3-8B (bf16, MPS, M5 Max 128GB). Extraction venv:
/Users/momo/qwen3_venv (python 3.13.9, torch 2.12.1, transformers 5.13.1,
peft 0.19.1, safetensors 0.8.0 — full freeze in paper_5/requirements_freeze.txt).

## Task 1 — original 22 rollouts + 8 neutral baselines (2026-08-05)

Re-extraction of residual-stream activations (all 36 decoder-block outputs)
by teacher-forced prefill of the stored rollout texts
(paper_4/results/merged_final/raw_judged.jsonl, selection =
stage2_ao_experiment.select_rollouts, identical 22-rollout set as
ao_probes_grid_q3.jsonl).

Verification gates (script: paper_5/extract_task1.py, full log:
paper_5/logs/task1.log, machine-readable: gate_report.json):

- Gate A (token offsets): 22 rollouts x 3 values (a_start_tok, commit_tok,
  n_tok) = 66 comparisons against the values stored in
  stage2_results/ao_probes_grid_q3.jsonl. Mismatches: 0.
- Gate B (re-extraction determinism): 30 items (22 rollouts + 8 baselines),
  two independent prefills, cosine over all 36 layers at every archived
  position. Minimum cosine: 0.99999738 (L18-only minimum: 0.99999905).
  Threshold 0.999: passed.
- Gate C (oracle equivalence): the stage2 oracle probes re-run greedy at the
  stored spans (Q3, segment mode). 156 probe comparisons (22 rollouts x 6
  grid spans + 8 neutrals x 3 spans). Exact response-text matches: 156/156.
  Mismatch cases: 0.
- Neutral baseline text authenticity: the stored jsonl kept only
  response_head[:120]; responses were regenerated greedy (thinking off,
  max_new_tokens 256, adapters disabled — replicating stage2_ao_neutral.py)
  and matched the stored heads 8/8. Full texts now preserved in
  baselines/texts.jsonl.

Evidence that the original stage2 oracle generation was greedy (Gate C
precondition): paper_4/stage2_ao_segment.py:103 —
generation_kwargs={"do_sample": False, "temperature": 0.0,
"max_new_tokens": 40}; this script produced ao_probes_grid_q3.jsonl
(log tag [stage2s] in stage2_ao_grid_q3.log, --out ao_probes_grid_q3.jsonl).

Adapter-state note: stage2's run_oracle collects target activations with
adapters ENABLED (oracle LoRA loaded; ao_demo_lib._collect_target_activations
calls model.enable_adapters() even for target_lora_path=None). The archive
replicates that state. Measured effect (rollout 160, L18, adapters on vs
off): cosine min 0.8554 / mean 0.9837 across the sequence — the LoRA
materially changes activations, so the enabled state is part of the data
definition and is recorded in the manifest.

Storage format check (reloaded from disk via safetensors, not assumed):
acts bf16 [36, P, 4096], positions int64 [P], all values finite,
abs-max ~1.9e4 (known Qwen residual-stream outlier features).
22 rollout files + texts.jsonl(22) in original_22/, 8 + texts.jsonl(8) in
baselines/, 22 reference files in reference_vectors/, 3 verbatim source
copies in originals/.

## Task 2 — scaled car-wash generation (2026-08-06, early stop)

- A_bare x on/off, sampled n=200 per arm, seeds 1000-1199, temp 0.7 /
  top_p 0.95 / max_new_tokens 4096, no challenge turn. C_role_star arms
  NOT run (time constraint; machine wipe 09:00).
- Judge (local Qwen3-8B, greedy): parse 402/402. final_split (sampled):
  off walk 164 / drive 5 / null 31; on walk 171 / drive 19 / null 10;
  total walk 335 / drive 24 / null 41.
- Targets: total n >= 100 -> 422 (with original_22), met.
  drive-commit >= 30 -> 24, NOT met (accepted per standing order).
- Vectors NOT extracted (06:30 cutoff); texts.jsonl (400 rows, with exact
  generation prefixes) archived in scaled_carwash/; regenerable per
  REGENERATE.md. planned_selection_85.txt records the prepared plan.

## Task 3 — new tasks (2026-08-05/06)

- phone_dead: 22 rollouts (20 sampled seeds 2000-2009 + greedy x2),
  vectors 22/22 (anchored 9, every5 13), gate B min 0.999997 over 22
  entries, all pass. Behavioral split (sampled): call 1 / walk 19 / null 0.
- tire_air: 22 rollouts (seeds 3000-3009 + greedy x2), vectors 22/22
  (anchored 16, every5 6), gate B min 0.9999978, all pass. Behavioral
  split (sampled): walk 14 / drive 3 / null 3.

## Final packaging smoke test (2026-08-06 07:2x, seed 42)

5 random safetensors reloaded from disk: shapes [36, P, 4096], dtype
bfloat16, positions int64 strictly increasing, all values finite,
abs-max range 1.5e3-1.9e4. 5/5 OK. Index-vs-file position-count coherence
checked for one sample in each of 4 subsets: 4/4 match.
Archive: 96 safetensors files, 3.4GB total.
