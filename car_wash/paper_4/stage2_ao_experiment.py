#!/usr/bin/env python3
"""STAGE 2: activation-oracle probes at pre/post-commit positions.

For selected STAGE 1 rollouts, rebuild the exact generation-time sequence
(prefix + generated text), collect layer-50% activations by teacher-forced
prefill, and ask the oracle at grid positions:

  P0 assistant_start | P1/P2/P3 25/50/75% of the span to the commit token
  P4 commit_tok - 1 (text-inversion critical: commit text not yet emitted)
  P5 commit_tok + 8 (positive control: commit text visible)

Selection (merged_final, judge labels): 8 C_role_star walk-commits (incl.
hand-positioned [160]), 8 A_bare walk-commits, all drive-commits with a
reliable position (6; 4 excluded, regex found no span). Positions come from
regex commit_char_pos only where judge agreed (judge_regex_agree).

Output: stage2_results/ao_probes.jsonl (one row per rollout, responses per
grid label + walk/drive mention flags).
"""

import json
import os
import re

import torch
from peft import LoraConfig
from transformers import AutoModelForCausalLM, AutoTokenizer

from ao_demo_lib import load_lora_adapter, run_oracle
from stage1_qwen_carwash import CONDITIONS, QUESTION, build_messages

MODEL = "Qwen/Qwen3-8B"
ORACLE_LORA = "adamkarvonen/checkpoints_latentqa_cls_past_lens_addition_Qwen3-8B"
ORACLE_Q = "What answer is this model going to give?"
MERGED = "results/merged_final/raw_judged.jsonl"
OUTDIR = "stage2_results"
HAND_POSITIONS = {160: 2781}  # [160] '**Action**: Walk...' — regex missed, hand-labeled
GRID_FRACS = (0.25, 0.5, 0.75)

WALK_RE = re.compile(r"\bwalk\w*\b", re.I)
DRIVE_RE = re.compile(r"\bdriv\w*\b", re.I)


def select_rollouts(rows):
    for i, r in enumerate(rows):
        r["_idx"] = i

    def eligible(r):
        if r["_idx"] in HAND_POSITIONS:
            return True
        return bool(r.get("judge_regex_agree")) and r.get("commit_char_pos", -1) >= 0

    picked = []
    for cond in ("C_role_star", "A_bare"):
        for mode in ("on", "off"):
            pool = [r for r in rows
                    if r["condition"] == cond and r["thinking_mode"] == mode
                    and r.get("judge_committed_answer") == "walk" and eligible(r)]
            # [160]을 앞으로 (사용자 지정 전시 케이스)
            pool.sort(key=lambda r: (r["_idx"] not in HAND_POSITIONS, r["_idx"]))
            picked.extend(pool[:4])
    drive = [r for r in rows
             if r.get("judge_committed_answer") == "drive" and eligible(r)]
    picked.extend(drive)
    return picked


def main():
    os.makedirs(OUTDIR, exist_ok=True)
    rows = [json.loads(l) for l in open(MERGED)]
    picked = select_rollouts(rows)
    print(f"[stage2] {len(picked)} rollouts selected", flush=True)

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
    print("[stage2] model + oracle LoRA ready", flush=True)

    out_path = os.path.join(OUTDIR, "ao_probes.jsonl")
    done = set()
    if os.path.exists(out_path):
        done = {json.loads(l)["_idx"] for l in open(out_path)}
        print(f"[stage2] resume: {len(done)} rollouts already probed", flush=True)

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

            grid = [("P0_assistant_start", a_start)]
            for f, lbl in zip(GRID_FRACS, ("P1_25", "P2_50", "P3_75")):
                grid.append((lbl, a_start + round(f * (commit_tok - a_start))))
            grid.append(("P4_precommit", max(commit_tok - 1, a_start)))
            grid.append(("P5_postcommit", min(commit_tok + 8, n_tok - 1)))

            probes = {}
            seen = {}
            for label, pos in grid:
                if pos in seen:  # 그리드 붕괴(이른 커밋) 시 중복 호출 회피
                    probes[label] = dict(probes[seen[pos]], position=pos)
                    continue
                seen[pos] = label
                results = run_oracle(
                    model=model, tokenizer=tokenizer, device=device,
                    target_prompt=target, target_lora_path=None,
                    oracle_prompt=ORACLE_Q, oracle_lora_path=ORACLE_LORA,
                    generation_kwargs={"do_sample": False, "temperature": 0.0,
                                       "max_new_tokens": 40},
                    token_start_idx=pos, token_end_idx=pos + 1,
                    oracle_input_types=["tokens"],
                )
                resp = results.token_responses[pos]
                probes[label] = {
                    "position": pos,
                    "response": resp,
                    "mentions_walk": bool(WALK_RE.search(resp or "")),
                    "mentions_drive": bool(DRIVE_RE.search(resp or "")),
                }
            out = {
                "_idx": r["_idx"], "condition": r["condition"],
                "thinking_mode": r["thinking_mode"], "kind": r["kind"],
                "seed": r.get("seed"),
                "judge_committed_answer": r["judge_committed_answer"],
                "commit_char_pos": commit_char,
                "hand_positioned": r["_idx"] in HAND_POSITIONS,
                "a_start_tok": a_start, "commit_tok": commit_tok,
                "n_tok": n_tok, "probes": probes,
            }
            fh.write(json.dumps(out, ensure_ascii=False) + "\n")
            fh.flush()
            print(f"[{r['_idx']}] {r['condition']}/{r['thinking_mode']} "
                  f"commit_tok={commit_tok}/{n_tok} "
                  + " ".join(f"{l}:{'W' if p['mentions_walk'] else ''}"
                             f"{'D' if p['mentions_drive'] else ''}"
                             for l, p in probes.items()),
                  flush=True)
    print("[stage2] done ->", out_path, flush=True)


if __name__ == "__main__":
    main()
