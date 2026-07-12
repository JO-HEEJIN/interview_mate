#!/usr/bin/env python3
"""Aggregate judge-scored rollouts + extract stratified manual-gate sample.

Usage: python aggregate_judged.py results/<ts>/raw_judged.jsonl
Writes: results/<ts>/condition_rates.json, manual_gate_sample.md
"""

import json
import random
import sys
from collections import defaultdict

SEED = 42  # 고정 seed — 수동 게이트 샘플 재현용


def main():
    path = sys.argv[1]
    rows = [json.loads(l) for l in open(path)]
    outdir = path.rsplit("/", 1)[0]

    # ---- 조건별 집계 (judge 라벨 기준) ----
    groups = defaultdict(list)
    for r in rows:
        groups[(r["condition"], r["thinking_mode"], r["kind"])].append(r)

    table = []
    for (cond, think, kind), g in sorted(groups.items()):
        n = len(g)
        cw = sum(1 for r in g if r.get("judge_committed_wrong"))
        fw = sum(1 for r in g if r.get("judge_final_answer") == "walk")
        null_commit = sum(1 for r in g if r.get("judge_committed_answer") is None)
        agree = sum(1 for r in g if r.get("judge_regex_agree"))
        parse_ok = sum(1 for r in g if r.get("judge_parse_ok"))
        no_think = sum(1 for r in g
                       if think == "on" and not r.get("has_think_block"))
        table.append({
            "condition": cond, "thinking": think, "kind": kind, "n": n,
            "judge_committed_wrong": cw, "pct_committed_wrong": round(cw / n, 3),
            "judge_final_wrong": fw, "pct_final_wrong": round(fw / n, 3),
            "judge_no_commit": null_commit,
            "regex_agree": agree, "parse_ok": parse_ok,
            "no_think_block": no_think,
        })
    with open(f"{outdir}/condition_rates.json", "w") as f:
        json.dump(table, f, indent=1)

    # 콘솔 표
    hdr = f"{'condition':<14} {'think':<5} {'kind':<8} {'n':>3} {'cw':>3} {'%cw':>6} {'fw':>3} {'%fw':>6} {'null':>4} {'agree':>5} {'noThk':>5}"
    print(hdr)
    print("-" * len(hdr))
    for t in table:
        print(f"{t['condition']:<14} {t['thinking']:<5} {t['kind']:<8} {t['n']:>3} "
              f"{t['judge_committed_wrong']:>3} {t['pct_committed_wrong']:>6} "
              f"{t['judge_final_wrong']:>3} {t['pct_final_wrong']:>6} "
              f"{t['judge_no_commit']:>4} {t['regex_agree']:>5} {t['no_think_block']:>5}")

    # ---- 층화 수동 게이트 샘플 (사용자 지시: 조건별 >=2 + no-think-block 포함) ----
    rng = random.Random(SEED)
    for i, r in enumerate(rows):
        r["_idx"] = i
    picked, picked_ids = [], set()

    def take(pool, k):
        pool = [r for r in pool if r["_idx"] not in picked_ids]
        chosen = rng.sample(pool, min(k, len(pool)))
        for r in chosen:
            picked_ids.add(r["_idx"])
        picked.extend(chosen)

    conds = sorted({r["condition"] for r in rows})
    for c in conds:  # 조건별 2개
        take([r for r in rows if r["condition"] == c], 2)
    # thinking on + think 블록 없음 4개
    take([r for r in rows if r["thinking_mode"] == "on"
          and not r.get("has_think_block")], 4)
    # 잔여 무작위 → 총 20
    take(rows, 20 - len(picked))

    with open(f"{outdir}/manual_gate_sample.md", "w") as f:
        f.write("# 수동 게이트 샘플 (층화 20, seed=42)\n\n"
                "각 항목: judge 라벨이 원문과 맞는지 확인. 불일치 시 표기.\n\n")
        for r in sorted(picked, key=lambda r: r["_idx"]):
            f.write(f"## [{r['_idx']}] {r['condition']} / thinking={r['thinking_mode']} / {r['kind']}\n\n")
            f.write(f"- judge: committed={r.get('judge_committed_answer')} "
                    f"final={r.get('judge_final_answer')} "
                    f"abr={r.get('judge_answer_before_reasoning')}\n"
                    f"- regex: committed={r.get('committed_answer')} "
                    f"(agree={r.get('judge_regex_agree')})\n"
                    f"- has_think_block={r.get('has_think_block')}\n\n"
                    f"```\n{r['primary_text']}\n```\n\n"
                    f"- [ ] judge 라벨 정확\n\n---\n\n")
    print(f"\nwrote {outdir}/condition_rates.json, {outdir}/manual_gate_sample.md "
          f"({len(picked)} samples)")


if __name__ == "__main__":
    main()
