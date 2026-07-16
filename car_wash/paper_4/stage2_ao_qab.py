#!/usr/bin/env python3
"""STAGE 2 final attempt: oracle question A/B on the positive control only.

Segment-mode positive control failed (P5 2/15 interim) with the baseline
question. This run distinguishes (a) bad question wording from (b) oracle
capability limit — the pre-agreed LAST attempt before closing STAGE 2.

Probes: P5 span [commit_tok, commit_tok+8] (commit tokens included, segment
input — the strongest-signal configuration), all 22 rollouts, two question
variants. Baseline Q1 numbers come from ao_probes_segment.jsonl.

Output: stage2_results/ao_probes_qab.jsonl
"""

import json
import os

import torch
from peft import LoraConfig
from transformers import AutoModelForCausalLM, AutoTokenizer

from ao_demo_lib import load_lora_adapter, run_oracle
from stage1_qwen_carwash import CONDITIONS, QUESTION, build_messages
from stage2_ao_experiment import (
    HAND_POSITIONS, MERGED, ORACLE_LORA, select_rollouts)
from stage2_ao_window import classify

MODEL = "Qwen/Qwen3-8B"
OUTDIR = "stage2_results"
QUESTIONS = {
    "Q2_recommending": "What is the model recommending?",
    "Q3_forced_choice": "Is the model going to say walk or drive?",
}


def main():
    os.makedirs(OUTDIR, exist_ok=True)
    rows = [json.loads(l) for l in open(MERGED)]
    picked = select_rollouts(rows)
    print(f"[qab] {len(picked)} rollouts x {len(QUESTIONS)} questions", flush=True)

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
    print("[qab] model + oracle LoRA ready", flush=True)

    out_path = os.path.join(OUTDIR, "ao_probes_qab.jsonl")
    done = set()
    if os.path.exists(out_path):
        done = {json.loads(l)["_idx"] for l in open(out_path)}
        print(f"[qab] resume: {len(done)} done", flush=True)

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
            commit_tok = next((i for i, (s, e) in enumerate(offsets) if e > commit_abs),
                              n_tok - 1)
            lo, hi = commit_tok, min(commit_tok + 8, n_tok - 1)

            answers = {}
            for qkey, qtext in QUESTIONS.items():
                results = run_oracle(
                    model=model, tokenizer=tokenizer, device=device,
                    target_prompt=target, target_lora_path=None,
                    oracle_prompt=qtext, oracle_lora_path=ORACLE_LORA,
                    generation_kwargs={"do_sample": False, "temperature": 0.0,
                                       "max_new_tokens": 40},
                    segment_start_idx=lo, segment_end_idx=hi + 1,
                    oracle_input_types=["segment"],
                )
                resp = results.segment_responses[0] if results.segment_responses else None
                answers[qkey] = {"response": resp, "verdict": classify(resp)}
            out = {
                "_idx": r["_idx"], "condition": r["condition"],
                "thinking_mode": r["thinking_mode"],
                "judge_committed_answer": r["judge_committed_answer"],
                "p5_span": [lo, hi], "answers": answers,
            }
            fh.write(json.dumps(out, ensure_ascii=False) + "\n")
            fh.flush()
            print(f"[{r['_idx']}] ans={r['judge_committed_answer']} "
                  + " ".join(f"{k}:{v['verdict'][0]}" for k, v in answers.items()),
                  flush=True)
    print("[qab] done ->", out_path, flush=True)


if __name__ == "__main__":
    main()
