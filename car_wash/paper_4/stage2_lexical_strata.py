#!/usr/bin/env python3
"""Lexical stratification of Q3 grid probes (text-inversion control).

For every pre-commit probe in ao_probes_grid_q3.jsonl, decode (a) the probed
5-token span itself and (b) a +/-25-token context window, and flag whether
the literal word walk/drive occurs there. If oracle walk read-outs survive
in the stratum WITHOUT the word "walk" nearby, they cannot be lexical
leakage (Arya-style text-inversion); if the signal lives only where the
word is present, STAGE 2 is not separable from text reading.

Pure re-analysis of existing data — no model, no new probes.
Output: stage2_results/lexical_strata.json + console report.
"""

import json
import re

from transformers import AutoTokenizer

from stage1_qwen_carwash import CONDITIONS, QUESTION, build_messages
from stage2_ao_experiment import HAND_POSITIONS, MERGED

MODEL = "Qwen/Qwen3-8B"
GRID = "stage2_results/ao_probes_grid_q3.jsonl"
PRECOMMIT = ["P0_assistant_start", "P1_25", "P2_50", "P3_75", "P4_precommit"]
CTX = 25  # tokens each side for the wide stratum
WALK_RE = re.compile(r"\bwalk(?:s|ed|ing)?\b", re.I)
DRIVE_RE = re.compile(r"\bdriv(?:e|es|ing|en)\b", re.I)


def main():
    tokenizer = AutoTokenizer.from_pretrained(MODEL)
    merged = [json.loads(l) for l in open(MERGED)]
    probes_rows = [json.loads(l) for l in open(GRID)]

    records = []
    for pr in probes_rows:
        src = merged[pr["_idx"]]
        prefix = tokenizer.apply_chat_template(
            build_messages(CONDITIONS[src["condition"]],
                           [{"role": "user", "content": QUESTION}]),
            tokenize=False, add_generation_prompt=True,
            enable_thinking=(src["thinking_mode"] == "on"))
        target = prefix + src["primary_text"]
        ids = tokenizer(target, add_special_tokens=False)["input_ids"]
        for label in PRECOMMIT:
            p = pr["probes"][label]
            lo, hi = p["span"]
            span_text = tokenizer.decode(ids[lo:hi + 1])
            ctx_text = tokenizer.decode(ids[max(0, lo - CTX):hi + 1 + CTX])
            records.append({
                "_idx": pr["_idx"], "label": label,
                "answer": pr["judge_committed_answer"],
                "verdict": p["verdict"],
                "span_has_walk": bool(WALK_RE.search(span_text)),
                "ctx_has_walk": bool(WALK_RE.search(ctx_text)),
                "span_has_drive": bool(DRIVE_RE.search(span_text)),
                "ctx_has_drive": bool(DRIVE_RE.search(ctx_text)),
                "span_text": span_text, "ctx_text": ctx_text,
            })

    with open("stage2_results/lexical_strata.json", "w") as f:
        json.dump(records, f, ensure_ascii=False, indent=1)

    def rate(sel):
        w = sum(1 for r in sel if r["verdict"] == "walk")
        return f"{w}/{len(sel)}" + (f" = {w/len(sel):.0%}" if sel else "")

    print(f"total pre-commit probes: {len(records)} "
          f"(22 rollouts x {len(PRECOMMIT)} sites)\n")
    for flag in ("span_has_walk", "ctx_has_walk"):
        for present in (True, False):
            sel = [r for r in records if r[flag] == present]
            print(f"{flag}={present}: walk read-outs {rate(sel)}")
        print()
    print("-- P4 only (the headline site) --")
    p4 = [r for r in records if r["label"] == "P4_precommit"]
    for flag in ("span_has_walk", "ctx_has_walk"):
        for present in (True, False):
            sel = [r for r in p4 if r[flag] == present]
            print(f"P4 {flag}={present}: {rate(sel)}")
    print("\n-- drive-committing rollouts, P4 (the strongest claim) --")
    dp4 = [r for r in p4 if r["answer"] == "drive"]
    for r in dp4:
        print(f"[{r['_idx']}] verdict={r['verdict']} span_walk={r['span_has_walk']} "
              f"ctx_walk={r['ctx_has_walk']}  span={r['span_text'][:60]!r}")


if __name__ == "__main__":
    main()
