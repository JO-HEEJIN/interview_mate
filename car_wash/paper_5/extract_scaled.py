#!/usr/bin/env python3
"""Extract archive activations for newly generated rollouts (Task 2 scaled
car-wash set and Task 3 new tasks).

Storage spec (todo.md section 3): all texts archived; activations only for
rollouts with a trusted commit position (judge_regex_agree and
commit_char_pos >= 0 — the paper_4 stage2 eligibility rule). Positions =
P0-P5 grid spans + commit_tok +-20. Greedy rows are excluded (deterministic
duplicates of the paper_4 greedy references).

Gate: per-rollout determinism check (two independent prefills, cosine at all
archived positions across all 36 layers must be >= 0.999). The offset/oracle
gates ran in Task 1 (same code path); there is no stored oracle output to
compare new rollouts against.

Usage (cwd = paper_4):
  python extract_scaled.py --raw <raw_judged.jsonl> --subset scaled_carwash \
      [--question "..."] [--system-key from-row]

Writes to /Users/momo/qwen3_archive/<subset>/: rollout_s<seed>_<cond>_<mode>.
safetensors, texts.jsonl, index.json, gate_report.json.
"""

import argparse
import json
import os
import sys

import torch
from peft import LoraConfig
from safetensors.torch import save_file
from transformers import AutoModelForCausalLM, AutoTokenizer

sys.path.insert(0, "/Users/momo/interview_mate/car_wash/paper_4")

from ao_demo_lib import load_lora_adapter  # noqa: E402
from stage1_qwen_carwash import CONDITIONS, QUESTION, build_messages  # noqa: E402
from stage2_ao_experiment import GRID_FRACS, ORACLE_LORA  # noqa: E402
from extract_task1 import (  # noqa: E402
    ARCHIVE, MODEL, N_LAYERS, collect_all_layers, min_cosine_at)


def grid_spans(a_start, commit_tok, n_tok):
    """Same span construction as stage2_ao_segment.py."""
    spans = [("P0_assistant_start", a_start, a_start + 4)]
    for f, lbl in zip(GRID_FRACS, ("P1_25", "P2_50", "P3_75")):
        c = a_start + round(f * (commit_tok - a_start))
        spans.append((lbl, c - 2, c + 2))
    spans.append(("P4_precommit", commit_tok - 5, commit_tok - 1))
    spans.append(("P5_postcommit", commit_tok, min(commit_tok + 8, n_tok - 1)))
    out = []
    for label, lo, hi in spans:
        if label != "P5_postcommit":
            lo = max(lo, a_start)
            hi = min(hi, commit_tok - 1)
        if hi < lo:
            lo = hi = max(min(lo, n_tok - 1), a_start)
        out.append((label, lo, hi))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw", required=True, help="raw_judged.jsonl path")
    ap.add_argument("--subset", required=True,
                    help="archive subdir (scaled_carwash | new_tasks/<name>)")
    ap.add_argument("--question", default=QUESTION,
                    help="user question used at generation time")
    ap.add_argument("--wrong-answer", default="walk",
                    help="task's intuitive-but-wrong option (metadata only)")
    ap.add_argument("--constraint-type", default="implicit",
                    help="implicit | stated (metadata only)")
    args = ap.parse_args()

    outdir = os.path.join(ARCHIVE, args.subset)
    os.makedirs(outdir, exist_ok=True)

    rows = [json.loads(l) for l in open(args.raw)]
    eligible = [r for r in rows if r["kind"] == "sampled"
                and r.get("judge_regex_agree")
                and r.get("judge_committed_answer")
                and r.get("commit_char_pos", -1) >= 0]
    print(f"[extract] {len(rows)} rows, {len(eligible)} eligible", flush=True)

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
    model.enable_adapters()  # match the stage2/Task-1 collection state
    print("[extract] model ready", flush=True)

    report = {"gate_B": [], "skipped": []}
    index = []
    texts_path = os.path.join(outdir, "texts.jsonl")
    done = set()
    if os.path.exists(texts_path):
        done = {json.loads(l)["rollout_id"] for l in open(texts_path)}
        print(f"[extract] resume: {len(done)} done", flush=True)

    with open(texts_path, "a", encoding="utf-8") as tf:
        # all texts (including non-eligible) go to texts.jsonl once
        for r in rows:
            if r["kind"] != "sampled":
                continue
            rid = f"s{r['seed']}_{r['condition']}_{r['thinking_mode']}"
            prefix = tokenizer.apply_chat_template(
                build_messages(CONDITIONS[r["condition"]],
                               [{"role": "user", "content": args.question}]),
                tokenize=False, add_generation_prompt=True,
                enable_thinking=(r["thinking_mode"] == "on"))
            if rid not in done:
                tf.write(json.dumps({
                    "rollout_id": rid, "condition": r["condition"],
                    "thinking_mode": r["thinking_mode"], "kind": r["kind"],
                    "seed": r["seed"], "temperature": r["temperature"],
                    "top_p": 0.95, "max_new_tokens": 4096,
                    "question": args.question,
                    "wrong_answer": args.wrong_answer,
                    "constraint_type": args.constraint_type,
                    "judge_committed_answer": r.get("judge_committed_answer"),
                    "judge_final_answer": r.get("judge_final_answer"),
                    "judge_regex_agree": r.get("judge_regex_agree"),
                    "commit_char_pos": r.get("commit_char_pos"),
                    "eligible_for_vectors": r in eligible,
                    "prefix": prefix, "primary_text": r["primary_text"],
                }, ensure_ascii=False) + "\n")
                tf.flush()

            if r not in eligible:
                continue
            vec_path = os.path.join(outdir, f"rollout_{rid}.safetensors")
            if os.path.exists(vec_path):
                continue
            target = prefix + r["primary_text"]
            commit_abs = len(prefix) + r["commit_char_pos"]
            enc = tokenizer(target, return_offsets_mapping=True,
                            add_special_tokens=False)
            offsets = enc["offset_mapping"]
            n_tok = len(offsets)
            a_start = next(i for i, (s, e) in enumerate(offsets)
                           if s >= len(prefix))
            commit_tok = next((i for i, (s, e) in enumerate(offsets)
                               if e > commit_abs), n_tok - 1)
            spans = grid_spans(a_start, commit_tok, n_tok)
            positions = sorted(
                {t for _, lo, hi in spans for t in range(lo, hi + 1)}
                | set(range(max(commit_tok - 20, 0),
                            min(commit_tok + 20, n_tok - 1) + 1)))

            acts1 = collect_all_layers(model, tokenizer, device, target)
            acts2 = collect_all_layers(model, tokenizer, device, target)
            cmat = min_cosine_at(acts1, acts2, positions)
            gb = {"rollout_id": rid,
                  "min_cosine_all_layers": float(cmat.min()),
                  "pass": bool(cmat.min() >= 0.999)}
            report["gate_B"].append(gb)
            if not gb["pass"]:
                report["skipped"].append(rid)
                print(f"[{rid}] GATE B FAIL {gb['min_cosine_all_layers']:.6f} "
                      "- vectors not saved", flush=True)
                del acts1, acts2
                continue

            save_file(
                {"acts": acts1[:, torch.tensor(positions), :].contiguous(),
                 "positions": torch.tensor(positions, dtype=torch.int64)},
                vec_path, metadata={"rollout_id": rid})
            index.append({
                "rollout_id": rid, "condition": r["condition"],
                "thinking_mode": r["thinking_mode"], "seed": r["seed"],
                "judge_committed_answer": r["judge_committed_answer"],
                "a_start_tok": a_start, "commit_tok": commit_tok,
                "n_tok": n_tok, "n_positions": len(positions),
                "grid_spans": {l: [lo, hi] for l, lo, hi in spans},
                "dtype": "bfloat16",
                "positions_file": os.path.basename(vec_path),
            })
            del acts1, acts2
            print(f"[{rid}] ans={r['judge_committed_answer']} "
                  f"B={gb['min_cosine_all_layers']:.6f} pos={len(positions)}",
                  flush=True)

    idx_path = os.path.join(outdir, "index.json")
    if os.path.exists(idx_path):
        index = json.load(open(idx_path)) + index
    with open(idx_path, "w") as f:
        json.dump(index, f, indent=1)
    with open(os.path.join(outdir, "gate_report.json"), "w") as f:
        json.dump(report, f, indent=1, ensure_ascii=False)
    n_ok = sum(1 for g in report["gate_B"] if g["pass"])
    print(f"[extract] done. vectors={n_ok} gateB_fail={len(report['skipped'])}",
          flush=True)


if __name__ == "__main__":
    main()
