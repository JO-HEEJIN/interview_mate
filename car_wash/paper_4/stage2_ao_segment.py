#!/usr/bin/env python3
"""STAGE 2 iteration 2: segment-input probes.

Token-window majority voting failed the positive-control gate (P5 stayed
3/16; consistent no-signal, not flakiness). Per the pre-set branch, feed
each grid window as ONE segment probe (all activations in the span injected
into a single oracle question) instead of independent per-token questions.

Grid spans (P0-P4 strictly pre-commit; text-inversion control intact):
  P0 [a_start, a_start+4]         P1/P2/P3 5-token spans at 25/50/75%
  P4 [commit_tok-5, commit_tok-1]
  P5 [commit_tok, commit_tok+8]   -- includes the emitted commit tokens:
     strengthened positive control (can the oracle read AT the answer?)

Output: stage2_results/ao_probes_segment.jsonl
"""

import json
import os

import torch
from peft import LoraConfig
from transformers import AutoModelForCausalLM, AutoTokenizer

from ao_demo_lib import load_lora_adapter, run_oracle
from stage1_qwen_carwash import CONDITIONS, QUESTION, build_messages
from stage2_ao_experiment import (
    HAND_POSITIONS, MERGED, ORACLE_LORA, ORACLE_Q, GRID_FRACS, select_rollouts)
from stage2_ao_window import classify

MODEL = "Qwen/Qwen3-8B"
OUTDIR = "stage2_results"


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--oracle-q", default=ORACLE_Q)
    ap.add_argument("--out", default="ao_probes_segment.jsonl")
    args = ap.parse_args()

    os.makedirs(OUTDIR, exist_ok=True)
    rows = [json.loads(l) for l in open(MERGED)]
    picked = select_rollouts(rows)
    print(f"[stage2s] {len(picked)} rollouts", flush=True)

    device = torch.device("mps")
    tokenizer = AutoTokenizer.from_pretrained(MODEL)
    tokenizer.padding_side = "left"
    if not tokenizer.pad_token_id:
        tokenizer.pad_token_id = tokenizer.eos_token_id
    model = AutoModelForCausalLM.from_pretrained(
        MODEL, dtype=torch.bfloat16).to(device).eval()
    torch.set_grad_enabled(False)
    model.add_adapter(LoraConfig(), adapter_name="default")
    load_lora_adapter(model, ORACLE_LORA)
    print("[stage2s] model + oracle LoRA ready", flush=True)

    out_path = os.path.join(OUTDIR, args.out)
    done = set()
    if os.path.exists(out_path):
        done = {json.loads(l)["_idx"] for l in open(out_path)}
        print(f"[stage2s] resume: {len(done)} done", flush=True)

    with open(out_path, "a", encoding="utf-8") as fh:
        for r in picked:
            if r["_idx"] in done:
                continue
            prefix = tokenizer.apply_chat_template(
                build_messages(CONDITIONS[r["condition"]],
                               [{"role": "user", "content": QUESTION}]),
                tokenize=False, add_generation_prompt=True,
                enable_thinking=(r["thinking_mode"] == "on"))
            target = prefix + r["primary_text"]
            commit_char = HAND_POSITIONS.get(r["_idx"], r.get("commit_char_pos"))
            commit_abs = len(prefix) + commit_char
            enc = tokenizer(target, return_offsets_mapping=True,
                            add_special_tokens=False)
            offsets = enc["offset_mapping"]
            n_tok = len(offsets)
            a_start = next(i for i, (s, e) in enumerate(offsets) if s >= len(prefix))
            commit_tok = next((i for i, (s, e) in enumerate(offsets) if e > commit_abs),
                              n_tok - 1)

            spans = [("P0_assistant_start", a_start, a_start + 4)]
            for f, lbl in zip(GRID_FRACS, ("P1_25", "P2_50", "P3_75")):
                c = a_start + round(f * (commit_tok - a_start))
                spans.append((lbl, c - 2, c + 2))
            spans.append(("P4_precommit", commit_tok - 5, commit_tok - 1))
            spans.append(("P5_postcommit", commit_tok, min(commit_tok + 8, n_tok - 1)))

            probes = {}
            for label, lo, hi in spans:
                if label != "P5_postcommit":
                    lo = max(lo, a_start)
                    hi = min(hi, commit_tok - 1)  # 커밋 전 엄수
                if hi < lo:
                    lo = hi = max(min(lo, n_tok - 1), a_start)
                results = run_oracle(
                    model=model, tokenizer=tokenizer, device=device,
                    target_prompt=target, target_lora_path=None,
                    oracle_prompt=args.oracle_q, oracle_lora_path=ORACLE_LORA,
                    generation_kwargs={"do_sample": False, "temperature": 0.0,
                                       "max_new_tokens": 40},
                    segment_start_idx=lo, segment_end_idx=hi + 1,
                    oracle_input_types=["segment"],
                )
                resp = results.segment_responses[0] if results.segment_responses else None
                probes[label] = {"span": [lo, hi], "response": resp,
                                 "verdict": classify(resp)}
            out = {
                "_idx": r["_idx"], "condition": r["condition"],
                "thinking_mode": r["thinking_mode"],
                "judge_committed_answer": r["judge_committed_answer"],
                "commit_tok": commit_tok, "a_start_tok": a_start, "n_tok": n_tok,
                "probes": probes,
            }
            fh.write(json.dumps(out, ensure_ascii=False) + "\n")
            fh.flush()
            print(f"[{r['_idx']}] {r['condition']}/{r['thinking_mode']} ans={r['judge_committed_answer']} "
                  + " ".join(f"{l.split('_')[0]}:{p['verdict'][0]}" for l, p in probes.items()),
                  flush=True)
    print("[stage2s] done ->", out_path, flush=True)


if __name__ == "__main__":
    main()
