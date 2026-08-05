#!/usr/bin/env python3
"""Task 3 driver for the phone-dead task (approved wording, constraint type:
stated -- the constraint is stated in the prompt but violated by the
intuitive answer "call").

Question: "My phone battery is dead. I need to book a table at a restaurant
100 meters away. Should I call them or walk over?"
Options: call (intuitive, wrong) vs walk (correct).

Reuses the paper_4 pipeline by monkeypatching module globals -- no paper_4
file is modified:
  gen    stage1_qwen_carwash with QUESTION and the walk/drive commit lexicon
         swapped to walk/call ("(walk|driv)" -> "(walk|call|phon)").
         The raw.jsonl fields committed_wrong/final_wrong keep stage1's
         walk-centric meaning ("committed walk") and are NOT meaningful for
         this task; the judge labels are the source of truth.
  judge  judge_rollouts.Judge with the rubric question line and answer enums
         swapped (rubric structure frozen, per the paper_4 rule).

Usage (cwd = paper_4):
  python task3_phone_dead.py gen --n 10 --conditions A_bare
  python task3_phone_dead.py judge --raw <raw.jsonl>
"""

import json
import re
import sys

sys.path.insert(0, "/Users/momo/interview_mate/car_wash/paper_4")

import stage1_qwen_carwash as s1  # noqa: E402
import judge_rollouts as jr  # noqa: E402

TASK_QUESTION = ("My phone battery is dead. I need to book a table at a "
                 "restaurant 100 meters away. Should I call them or walk over?")
WRONG = "call"
CORRECT = "walk"

OLD_ALT = "(walk|driv)"
NEW_ALT = "(walk|call|phon)"


def normalize_answer_task(word):
    return "walk" if word.lower().startswith("walk") else "call"


def patch_stage1():
    s1.QUESTION = TASK_QUESTION
    s1.COMMIT_PATTERNS = [p.replace(OLD_ALT, NEW_ALT) for p in s1.COMMIT_PATTERNS]
    s1.THINK_CONCLUSION_PATTERNS = [
        p.replace(OLD_ALT, NEW_ALT) for p in s1.THINK_CONCLUSION_PATTERNS]
    s1.NEGATION_GUARD = re.compile(
        s1.NEGATION_GUARD.pattern.replace(OLD_ALT, NEW_ALT), re.I)
    s1.normalize_answer = normalize_answer_task


RUBRIC = jr.RUBRIC.replace(
    '"I want to wash my car. The car wash is 100 meters away. '
    'Should I walk or drive?"',
    f'"{TASK_QUESTION}"').replace('"walk" | "drive" | null',
                                  '"call" | "walk" | null')


def extract_json_task(text):
    m = jr.JSON_RE.search(text)
    if not m:
        return None
    try:
        obj = json.loads(m.group(0))
    except json.JSONDecodeError:
        return None
    out = {}
    ca = obj.get("committed_answer")
    fa = obj.get("final_answer")
    out["committed_answer"] = ca if ca in ("call", "walk") else None
    out["final_answer"] = fa if fa in ("call", "walk") else None
    abr = obj.get("answer_before_reasoning")
    out["answer_before_reasoning"] = bool(abr) if isinstance(abr, bool) else None
    return out


def judge_raw(raw_path):
    judge = jr.Judge("Qwen/Qwen3-8B", "mps")
    jr.RUBRIC = RUBRIC  # Judge.label reads the module global via jr namespace
    out_path = raw_path.replace(".jsonl", "_judged.jsonl")
    n = 0
    with open(raw_path) as fin, open(out_path, "w") as fout:
        for line in fin:
            row = json.loads(line)
            labels_raw, text = judge.label(row["primary_text"])
            labels = extract_json_task(text)
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
        patch_stage1()
        sys.argv = (["stage1_qwen_carwash.py"] + sys.argv[2:]
                    + ["--device", "mps", "--thinking", "both",
                       "--temperature", "0.7", "--max-new-tokens", "4096",
                       "--seed-offset", "2000", "--no-challenge",
                       "--out-root",
                       "/Users/momo/interview_mate/car_wash/paper_5/results_phone_dead"])
        s1.main()
    elif mode == "judge":
        i = sys.argv.index("--raw")
        judge_raw(sys.argv[i + 1])
    else:
        raise SystemExit("mode must be gen or judge")


if __name__ == "__main__":
    main()
