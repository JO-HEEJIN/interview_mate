#!/usr/bin/env python3
"""Compute and persist every statistic reported in the paper and email.

Reads only the raw result JSONs; writes stage2_results/statistics.json so
each reported p-value is traceable to committed data + committed code.
All Fisher tests are one-sided (greater) against the neutral-context
oracle default (walk 4 / drive 19 over 23 decisive read-outs).
"""

import json

from scipy.stats import binomtest, fisher_exact

NEUTRAL = [4, 19]  # walk, drive decisive read-outs in ao_neutral_control


def fisher(walk, rest):
    return fisher_exact([[walk, rest], NEUTRAL], alternative="greater")[1]


def main():
    grid = [json.loads(l) for l in open("stage2_results/ao_probes_grid_q3.jsonl")]
    lex = json.load(open("stage2_results/lexical_strata.json"))
    gw = [r for r in grid if r["judge_committed_answer"] == "walk"]
    gd = [r for r in grid if r["judge_committed_answer"] == "drive"]

    def p4_hits(sel):
        return sum(1 for r in sel if r["probes"]["P4_precommit"]["verdict"] == "walk")

    up = sum(1 for r in gw if r["probes"]["P0_assistant_start"]["verdict"] != "walk"
             and r["probes"]["P4_precommit"]["verdict"] == "walk")
    dn = sum(1 for r in gw if r["probes"]["P0_assistant_start"]["verdict"] == "walk"
             and r["probes"]["P4_precommit"]["verdict"] != "walk")

    both = [r for r in lex if r["ctx_has_walk"] and r["ctx_has_drive"]]
    bw = sum(1 for r in both if r["verdict"] == "walk")
    bd = sum(1 for r in both if r["verdict"] == "drive")
    dboth = [r for r in both if r["answer"] == "drive"]
    dbw = sum(1 for r in dboth if r["verdict"] == "walk")
    dbd = sum(1 for r in dboth if r["verdict"] == "drive")

    p5w = sum(1 for r in gw if r["probes"]["P5_postcommit"]["verdict"] == "walk")

    stats = {
        "neutral_default": {"walk": NEUTRAL[0], "drive": NEUTRAL[1],
                            "walk_share": NEUTRAL[0] / sum(NEUTRAL)},
        "P4_walk_group_vs_neutral": {
            "hits": p4_hits(gw), "n": len(gw), "p": fisher(p4_hits(gw), len(gw) - p4_hits(gw))},
        "P4_drive_group_vs_neutral": {
            "hits": p4_hits(gd), "n": len(gd), "p": fisher(p4_hits(gd), len(gd) - p4_hits(gd))},
        "P4_combined_vs_neutral": {
            "hits": p4_hits(grid), "n": len(grid),
            "p": fisher(p4_hits(grid), len(grid) - p4_hits(grid))},
        "P5_positive_control_walk_group": {
            "hits": p5w, "n": len(gw), "p": fisher(p5w, len(gw) - p5w)},
        "positional_gradient_sign_test_P0_to_P4": {
            "improved": up, "worsened": dn,
            "p": binomtest(up, up + dn, 0.5, alternative="two-sided").pvalue},
        "balanced_field_walk_share": {
            "walk": bw, "drive": bd, "share": bw / (bw + bd),
            "p_decisive": fisher(bw, bd)},
        "drive_rollouts_balanced_field": {
            "walk": dbw, "drive": dbd, "n_probes": len(dboth),
            "p_decisive_20v1": fisher(dbw, dbd),
            "p_conservative_walk_vs_all": fisher(dbw, len(dboth) - dbw),
            "note": "email/paper display 20/28 fractions -> use p_conservative; "
                    "decisive-only framing (20:1 vs 4:19) -> p_decisive"},
    }
    with open("stage2_results/statistics.json", "w") as f:
        json.dump(stats, f, indent=1)
    print(json.dumps(stats, indent=1))


if __name__ == "__main__":
    main()
