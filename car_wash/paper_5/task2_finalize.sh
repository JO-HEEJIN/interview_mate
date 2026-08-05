#!/bin/bash
# Autonomous Task-2 early-stop chain (standing orders 2026-08-06):
# wait for A_bare/on seed 1199 -> kill generation -> filter A_bare rows ->
# judge all of them. Output: raw_abare_judged.jsonl
LOG=/Users/momo/interview_mate/car_wash/paper_5/logs/task2_gen.log
DIR=/Users/momo/interview_mate/car_wash/paper_5/results/20260805_143206
until grep -q "think=on sampled#1199" "$LOG"; do sleep 5; done
echo "[finalize] seed 1199 seen, killing generation"
pkill -f stage1_qwen_carwash.py
sleep 5
/Users/momo/qwen3_venv/bin/python - <<'PY'
import json
rows = [json.loads(l) for l in open("/Users/momo/interview_mate/car_wash/paper_5/results/20260805_143206/raw.jsonl")]
keep = [r for r in rows if r["condition"] == "A_bare"]
with open("/Users/momo/interview_mate/car_wash/paper_5/results/20260805_143206/raw_abare.jsonl", "w") as f:
    for r in keep:
        f.write(json.dumps(r, ensure_ascii=False) + "\n")
print(f"[finalize] kept {len(keep)}/{len(rows)} A_bare rows")
PY
cd /Users/momo/interview_mate/car_wash/paper_4
/Users/momo/qwen3_venv/bin/python judge_rollouts.py --score "$DIR/raw_abare.jsonl" --device mps
echo "[finalize] judge done"
