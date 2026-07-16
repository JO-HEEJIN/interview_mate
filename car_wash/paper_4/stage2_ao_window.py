#!/usr/bin/env python3
"""STAGE 2 iteration 1: window-majority probes (positive-control recovery).

Same 22 rollouts and grid as stage2_ao_experiment.py, but each grid point
becomes a 5-token window probed in one run_oracle call; the label's verdict
is the majority exclusive mention over the window. Window clamping preserves
the text-inversion control: P0-P4 windows never reach commit_tok; P5 window
stays strictly after the commit tokens.

Gate (user-set): if P5 (commit text visible) recovers under majority voting
(3/16 -> ~10/16+), probes are trustworthy and P2/P4 become interpretable.
If P5 stays low, single/multi-token probes can't read commitment -> move to
segment-input mode.

Output: stage2_results/ao_probes_window.jsonl
"""

import json
import os

import torch
from peft import LoraConfig
from transformers import AutoModelForCausalLM, AutoTokenizer

from ao_demo_lib import load_lora_adapter, run_oracle
from stage1_qwen_carwash import CONDITIONS, QUESTION, build_messages
from stage2_ao_experiment import (
    DRIVE_RE, HAND_POSITIONS, MERGED, ORACLE_LORA, ORACLE_Q, WALK_RE,
    GRID_FRACS, select_rollouts)

MODEL = "Qwen/Qwen3-8B"
OUTDIR = "stage2_results"
HALF = 2  # window = grid point +/- HALF (5 probes)


def classify(resp):
    w, d = bool(WALK_RE.search(resp or "")), bool(DRIVE_RE.search(resp or ""))
    if w and not d:
        return "walk"
    if d and not w:
        return "drive"
    return "ambig" if w else "none"


def main():
    os.makedirs(OUTDIR, exist_ok=True)
    rows = [json.loads(l) for l in open(MERGED)]
    picked = select_rollouts(rows)
    print(f"[stage2w] {len(picked)} rollouts", flush=True)

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
    print("[stage2w] model + oracle LoRA ready", flush=True)

    out_path = os.path.join(OUTDIR, "ao_probes_window.jsonl")
    done = set()
    if os.path.exists(out_path):
        done = {json.loads(l)["_idx"] for l in open(out_path)}
        print(f"[stage2w] resume: {len(done)} done", flush=True)

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

            centers = [("P0_assistant_start", a_start)]
            for f, lbl in zip(GRID_FRACS, ("P1_25", "P2_50", "P3_75")):
                centers.append((lbl, a_start + round(f * (commit_tok - a_start))))
            centers.append(("P4_precommit", commit_tok - 1))
            centers.append(("P5_postcommit", min(commit_tok + 8, n_tok - 1)))

            probes = {}
            for label, c in centers:
                lo, hi = c - HALF, c + HALF
                if label == "P5_postcommit":
                    lo = max(lo, commit_tok + 1)          # 전부 커밋 후
                    hi = min(hi, n_tok - 1)
                else:
                    lo = max(lo, a_start)                 # 전부 커밋 전
                    hi = min(hi, commit_tok - 1)
                if hi < lo:
                    lo = hi = max(min(c, n_tok - 1), a_start)
                results = run_oracle(
                    model=model, tokenizer=tokenizer, device=device,
                    target_prompt=target, target_lora_path=None,
                    oracle_prompt=ORACLE_Q, oracle_lora_path=ORACLE_LORA,
                    generation_kwargs={"do_sample": False, "temperature": 0.0,
                                       "max_new_tokens": 40},
                    token_start_idx=lo, token_end_idx=hi + 1,
                    oracle_input_types=["tokens"],
                )
                votes = {}
                resps = {}
                for pos in range(lo, hi + 1):
                    resp = results.token_responses[pos]
                    resps[pos] = resp
                    v = classify(resp)
                    votes[v] = votes.get(v, 0) + 1
                n_win = hi - lo + 1
                majority = max(votes, key=votes.get)
                verdict = majority if (majority in ("walk", "drive")
                                       and votes[majority] * 2 > n_win) else "none"
                probes[label] = {"window": [lo, hi], "votes": votes,
                                 "verdict": verdict, "responses": resps}
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
    print("[stage2w] done ->", out_path, flush=True)


if __name__ == "__main__":
    main()
