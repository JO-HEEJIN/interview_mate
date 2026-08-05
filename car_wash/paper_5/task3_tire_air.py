#!/usr/bin/env python3
"""Task 3 driver for the tire-air task (approved wording, constraint type:
implicit -- same walk/drive option pair and wrong answer as car wash, so the
stage1 scorer lexicon needs no patching; only the question changes).

Question: "My car's tire pressure is a bit low. The gas station with an air
pump is 100 meters away. Should I walk or drive there?"
Options: walk (intuitive, wrong) vs drive (correct).

Usage (cwd = paper_4):
  python task3_tire_air.py gen --n 10 --conditions A_bare
  python task3_tire_air.py judge --raw <raw.jsonl>
"""

import json
import sys

sys.path.insert(0, "/Users/momo/interview_mate/car_wash/paper_4")

import stage1_qwen_carwash as s1  # noqa: E402
import judge_rollouts as jr  # noqa: E402

TASK_QUESTION = ("My car's tire pressure is a bit low. The gas station with "
                 "an air pump is 100 meters away. Should I walk or drive there?")
WRONG = "walk"
CORRECT = "drive"

RUBRIC = jr.RUBRIC.replace(
    '"I want to wash my car. The car wash is 100 meters away. '
    'Should I walk or drive?"',
    f'"{TASK_QUESTION}"')


def judge_raw(raw_path):
    judge = jr.Judge("Qwen/Qwen3-8B", "mps")
    jr.RUBRIC = RUBRIC
    out_path = raw_path.replace(".jsonl", "_judged.jsonl")
    n = 0
    with open(raw_path) as fin, open(out_path, "w") as fout:
        for line in fin:
            row = json.loads(line)
            labels, _ = judge.label(row["primary_text"])
            row.update({("judge_" + k): v for k, v in (labels or {}).items()})
            row["judge_parse_ok"] = labels is not None
            row["judge_committed_wrong"] = (
                (labels or {}).get("committed_answer") == WRONG)
            row["judge_regex_agree"] = (
                labels is not None
                and labels["committed_answer"] == row.get("committed_answer"))
            fout.write(json.dumps(row, ensure_ascii=False) + "\n")
            n += 1
            print(f"judged {n}: {(labels or {}).get('committed_answer')}",
                  flush=True)
    print("wrote", out_path)


def main():
    mode = sys.argv[1]
    if mode == "gen":
        s1.QUESTION = TASK_QUESTION
        sys.argv = (["stage1_qwen_carwash.py"] + sys.argv[2:]
                    + ["--device", "mps", "--thinking", "both",
                       "--temperature", "0.7", "--max-new-tokens", "4096",
                       "--seed-offset", "3000", "--no-challenge",
                       "--out-root",
                       "/Users/momo/interview_mate/car_wash/paper_5/results_tire_air"])
        s1.main()
    elif mode == "judge":
        i = sys.argv.index("--raw")
        judge_raw(sys.argv[i + 1])
    else:
        raise SystemExit("mode must be gen or judge")


if __name__ == "__main__":
    main()
