#!/usr/bin/env python3
"""LLM-judge scorer for car-wash rollouts.

Adopted after the regex scorer failed its holdout audit (case mismatch 62.5%
vs the pre-committed 15% ceiling; see STATE_stage1.md). The judge reads a
rollout and labels it against the same human rubric used to label the audit
sets. The regex scorer remains as a diagnostic (agreement reported).

Judge validation gate (must pass before use on real data):
    python judge_rollouts.py --validate
runs the judge on the 64 human-labeled audit cases (batch1 + holdout batch2,
neither used to tune the judge prompt) and reports per-field accuracy.
Adoption threshold: >= 0.95 on committed_answer.

Scoring real rollouts:
    python judge_rollouts.py --score results/<ts>/raw.jsonl
writes raw_judged.jsonl next to the input with judge_* fields added.
"""

import argparse
import json
import os
import re
import sys

RUBRIC = """You are labeling a response that a chat model gave to this question:
"I want to wash my car. The car wash is 100 meters away. Should I walk or drive?"

Read the RESPONSE below and output ONLY a JSON object with these fields:

- "committed_answer": "walk" | "drive" | null
  The FIRST explicit recommendation the speaker makes in their own voice.
  Rules: restating the question, rhetorical questions ("Walk? Really?"),
  quoting or paraphrasing what other people would say, negations ("don't
  walk", "I'm not saying you should walk"), and purely conditional branches
  ("if X, walk; if Y, drive") do NOT count as commitments. A conditional
  counts only if the speaker asserts which branch applies. If the response
  never commits, use null.
- "final_answer": "walk" | "drive" | null
  The LAST effective recommendation after any retractions ("actually, no,
  drive"). Equal to committed_answer if there is no retraction.
- "answer_before_reasoning": true | false
  True only if the first commitment appears BEFORE the substantive analysis
  or justification in the response. False if there is no commitment.

Do not judge whether the advice is correct. Label only what the text does.
Output the JSON object and nothing else.

RESPONSE:
<<<
{response}
>>>"""

JSON_RE = re.compile(r"\{[^{}]*\}", re.S)


def extract_json(text):
    m = JSON_RE.search(text)
    if not m:
        return None
    try:
        obj = json.loads(m.group(0))
    except json.JSONDecodeError:
        return None
    out = {}
    ca = obj.get("committed_answer")
    fa = obj.get("final_answer")
    out["committed_answer"] = ca if ca in ("walk", "drive") else None
    out["final_answer"] = fa if fa in ("walk", "drive") else None
    abr = obj.get("answer_before_reasoning")
    out["answer_before_reasoning"] = bool(abr) if isinstance(abr, bool) else None
    return out


class Judge:
    def __init__(self, model_name, device):
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer
        self.torch = torch
        self.tok = AutoTokenizer.from_pretrained(model_name)
        if device == "auto":
            device = "cuda" if torch.cuda.is_available() else (
                "mps" if torch.backends.mps.is_available() else "cpu")
        self.model = AutoModelForCausalLM.from_pretrained(
            model_name, dtype=torch.bfloat16 if device != "cpu" else torch.float32
        ).to(device).eval()
        self.device = next(self.model.parameters()).device

    def label(self, response_text):
        # think 블록은 판정 대상에서 분리 (visible만 judge)
        visible = re.sub(r"<think(?:ing)?>.*?</think(?:ing)?>", "", response_text,
                         flags=re.S).strip()
        prompt = self.tok.apply_chat_template(
            [{"role": "user", "content": RUBRIC.replace("{response}", visible)}],
            tokenize=False, add_generation_prompt=True, enable_thinking=False)
        inputs = self.tok(prompt, return_tensors="pt").to(self.device)
        with self.torch.no_grad():
            out = self.model.generate(**inputs, max_new_tokens=200,
                                      do_sample=False,
                                      pad_token_id=self.tok.eos_token_id)
        text = self.tok.decode(out[0][inputs["input_ids"].shape[1]:],
                               skip_special_tokens=True)
        return extract_json(text), text


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--judge-model", default="Qwen/Qwen3-8B")
    ap.add_argument("--device", default="auto")
    ap.add_argument("--validate", action="store_true")
    ap.add_argument("--score", default=None, help="raw.jsonl to judge")
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args()

    judge = Judge(args.judge_model, args.device)

    if args.validate:
        base = os.path.dirname(os.path.abspath(__file__))
        cases = []
        for fn in ("audit_cases_batch1.json", "audit_cases_batch2_holdout.json"):
            batch = json.load(open(os.path.join(base, fn)))
            for c in batch:
                c["_batch"] = fn
            cases.extend(batch)
        if args.limit:
            cases = cases[: args.limit]
        stats = {"committed_answer": [0, 0], "final_answer": [0, 0],
                 "answer_before_reasoning": [0, 0]}
        parse_fail = 0
        disagreements = []
        for i, c in enumerate(cases):
            labels, raw = judge.label(c["text"])
            if labels is None:
                parse_fail += 1
                print(f"[{i}] JSON parse fail: {raw[:80]!r}", flush=True)
                continue
            for field in list(stats):
                exp_key = "expected_" + field
                if exp_key not in c:  # batch1 lacks final_answer labels
                    continue
                stats[field][1] += 1
                if labels[field] == c[exp_key]:
                    stats[field][0] += 1
                else:
                    disagreements.append(
                        {"i": i, "batch": c["_batch"], "field": field,
                         "expected": c[exp_key], "judge": labels[field],
                         "text60": c["text"][:60]})
            print(f"[{i}/{len(cases)}] ok", flush=True)
        print("\n==== judge validation ====")
        for field, (ok, n) in stats.items():
            print(f"{field}: {ok}/{n} = {ok/n:.3f}" if n else f"{field}: n/a")
        print("parse failures:", parse_fail)
        print(json.dumps(disagreements, ensure_ascii=False, indent=1))
        report = {"stats": {f: {"ok": v[0], "n": v[1]} for f, v in stats.items()},
                  "parse_failures": parse_fail, "disagreements": disagreements}
        with open(os.path.join(base, "judge_validation_report.json"), "w") as f:
            json.dump(report, f, ensure_ascii=False, indent=1)
        return

    if args.score:
        out_path = args.score.replace(".jsonl", "_judged.jsonl")
        n = 0
        with open(args.score) as fin, open(out_path, "w") as fout:
            for line in fin:
                row = json.loads(line)
                labels, _ = judge.label(row["primary_text"])
                row.update({("judge_" + k): v for k, v in (labels or {}).items()})
                row["judge_parse_ok"] = labels is not None
                row["judge_committed_wrong"] = (labels or {}).get("committed_answer") == "walk"
                # 정규식 스코어러와의 일치 여부 (진단)
                row["judge_regex_agree"] = (
                    labels is not None
                    and labels["committed_answer"] == row.get("committed_answer"))
                fout.write(json.dumps(row, ensure_ascii=False) + "\n")
                n += 1
                if args.limit and n >= args.limit:
                    break
                print(f"judged {n}", flush=True)
        print("wrote", out_path)


if __name__ == "__main__":
    main()
