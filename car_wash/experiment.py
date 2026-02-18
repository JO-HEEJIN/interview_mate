"""
Car Wash Prompt Architecture Experiment
Variable isolation study: which InterviewMate prompt element improves task grounding?

Uses Anthropic SDK directly - same key as InterviewMate backend. No OpenRouter needed.

Usage:
    pip install anthropic
    export ANTHROPIC_API_KEY="sk-ant-..."
    python experiment.py

Results written to: results/<timestamp>/
    raw.jsonl     - every trial with full response text
    summary.json  - pass rates per condition
    report.md     - human-readable table with DeepSeek predictions vs actual
"""

import os
import json
import time
import re
from datetime import datetime
from pathlib import Path
import anthropic


# ---- Config ----

ANTHROPIC_API_KEY = os.environ["ANTHROPIC_API_KEY"]
MODEL = "claude-sonnet-4-5-20250929"  
RUNS_PER_CONDITION = 20
TEMPERATURE = 0.7

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

# Same question as ryan-allen/car-wash-evals
QUESTION = "I want to wash my car. The car wash is 100 meters away. Should I walk or drive?"
CHALLENGE = "How will I get my car washed if I am walking?"


# ---- 5 Experimental Conditions ----

CONDITIONS = {
    "A_bare": {
        "system": None,
        "description": "No system prompt. Baseline.",
    },
    "B_role_only": {
        "system": (
            "You are an expert advisor helping people make practical decisions. "
            "Always think through problems carefully and consider all relevant factors. "
            "Provide clear, actionable recommendations."
        ),
        "description": "Role definition only.",
    },
    "C_role_star": {
        "system": (
            "You are an expert advisor helping people make practical decisions. "
            "Always think through problems carefully and consider all relevant factors.\n\n"
            "When answering any question, use the STAR method:\n"
            "- Situation: What is the actual situation being described?\n"
            "- Task: What needs to be accomplished?\n"
            "- Action: What action achieves the task given the situation?\n"
            "- Result: What outcome does this action produce?\n\n"
            "Provide clear, actionable recommendations."
        ),
        "description": "Role + STAR reasoning framework.",
    },
    "D_role_profile": {
        "system": (
            "You are an expert advisor helping people make practical decisions. "
            "Always think through problems carefully and consider all relevant factors.\n\n"
            "User profile:\n"
            "- Name: Sarah\n"
            "- Location: Suburban area, owns a vehicle (2022 Honda Civic)\n"
            "- Current situation: At home with car parked in driveway\n"
            "- Goal: Complete daily errands efficiently\n\n"
            "Always personalize your advice to the user's specific situation and constraints."
        ),
        "description": "Role + user physical context profile.",
    },
    "E_full_stack": {
        "system": (
            "You are an expert personal assistant helping Sarah make practical, situation-aware decisions.\n\n"
            "User profile:\n"
            "- Name: Sarah\n"
            "- Location: Suburban area, owns a vehicle (2022 Honda Civic)\n"
            "- Current situation: At home with car parked in driveway\n"
            "- Goal: Complete daily errands efficiently\n\n"
            "When answering any question, use the STAR method:\n"
            "- Situation: What is the actual physical situation described?\n"
            "- Task: What concrete outcome must be achieved?\n"
            "- Action: What action accomplishes the task given the physical constraints?\n"
            "- Result: What is the outcome?\n\n"
            "Retrieved context:\n"
            "- User's Honda Civic needs washing after a long road trip\n"
            "- User is planning errands this afternoon\n\n"
            "Provide specific, grounded advice based on Sarah's actual situation."
        ),
        "description": "Full stack: role + STAR + profile + RAG context.",
    },
}


# ---- Scoring - mirrors ryan-allen/car-wash-evals logic ----

PASS_PATTERNS = [
    r"\bshould\s+drive\b",
    r"\bshould\s+definitely\s+drive\b",
    r"\brecommend\s+driving\b",
    r"\bdrive\s+your\s+car\b",
    r"\btake\s+your\s+car\b",
    r"\bbring\s+your\s+car\b",
    r"\bdrive\s+to\s+the\s+car\s+wash\b",
    r"\bdrive\s+it\s+(there|over|to)\b",
    r"\bcar\s+needs\s+to\s+be\s+(at|there|present)\b",
    r"\bcar\s+must\s+be\s+present\b",
    r"\bneed\s+the\s+car\s+(at|there)\b",
    r"\bbest\s+to\s+drive\b",
    r"\bbetter\s+to\s+drive\b",
    r"\b(answer|solution)\s+is\s+to\s+drive\b",
]
FAIL_PATTERNS = [
    r"\bshould\s+walk\b",
    r"\bshould\s+definitely\s+walk\b",
    r"\brecommend\s+walking\b",
    r"\bwalk\s+to\s+the\s+car\s+wash\b",
    r"\bwalk\s+there\b",
    r"\bbest\s+to\s+walk\b",
    r"\bbetter\s+to\s+walk\b",
    r"\bgo\s+on\s+foot\b",
    r"\b(answer|solution)\s+is\s+to\s+walk\b",
]


def score_response(text: str) -> str:
    """Score based on recommendation intent, not bare word mentions."""
    # Strip markdown bold/italic so **walk** matches \bwalk\b
    lower = re.sub(r'\*{1,2}', '', text.lower())
    pass_hits = sum(1 for p in PASS_PATTERNS if re.search(p, lower))
    fail_hits = sum(1 for p in FAIL_PATTERNS if re.search(p, lower))
    if pass_hits > 0 and fail_hits == 0:
        return "pass"
    elif fail_hits > 0 and pass_hits == 0:
        return "fail"
    elif pass_hits > 0 and fail_hits > 0:
        # Both present — use ratio to decide dominant recommendation
        if pass_hits >= fail_hits * 2:
            return "pass"
        elif fail_hits >= pass_hits * 2:
            return "fail"
        return "ambiguous"
    else:
        return "ambiguous"


# ---- API ----

def ask(system, messages):
    kwargs = {
        "model": MODEL,
        "max_tokens": 512,
        "messages": messages,
        "temperature": TEMPERATURE,
    }
    if system:
        kwargs["system"] = system
    start = time.time()
    response = client.messages.create(**kwargs)
    latency_ms = (time.time() - start) * 1000
    return response.content[0].text, latency_ms


# ---- Runner ----

def run_condition(name, condition, runs):
    results = []
    system = condition["system"]
    print(f"\n[{name}] {condition['description']}")

    for i in range(runs):
        primary_text, primary_latency = ask(system, [{"role": "user", "content": QUESTION}])
        primary_score = score_response(primary_text)

        challenge_text = challenge_score = challenge_latency = None
        if primary_score != "pass":
            history = [
                {"role": "user", "content": QUESTION},
                {"role": "assistant", "content": primary_text},
                {"role": "user", "content": CHALLENGE},
            ]
            challenge_text, challenge_latency = ask(system, history)
            challenge_score = score_response(challenge_text)

        result = {
            "condition": name,
            "trial": i + 1,
            "primary_text": primary_text,
            "primary_score": primary_score,
            "primary_latency_ms": round(primary_latency),
            "challenge_text": challenge_text,
            "challenge_score": challenge_score,
            "challenge_latency_ms": round(challenge_latency) if challenge_latency else None,
        }
        results.append(result)

        tag = primary_score
        if challenge_score:
            tag += f" -> {challenge_score}"
        print(f"  [{i+1:02d}/{runs}] {tag}")

        time.sleep(0.3)

    return results


def summarize(results):
    total = len(results)
    passes = sum(1 for r in results if r["primary_score"] == "pass")
    fails = sum(1 for r in results if r["primary_score"] == "fail")
    ambiguous = sum(1 for r in results if r["primary_score"] == "ambiguous")
    challenged = [r for r in results if r["challenge_score"] is not None]
    recovered = sum(1 for r in challenged if r["challenge_score"] == "pass")
    latencies = sorted(r["primary_latency_ms"] for r in results)

    return {
        "total": total,
        "primary_pass": passes,
        "primary_fail": fails,
        "primary_ambiguous": ambiguous,
        "primary_pass_rate": round(passes / total, 3),
        "challenged": len(challenged),
        "recovered": recovered,
        "recovery_rate": round(recovered / len(challenged), 3) if challenged else None,
        "median_latency_ms": latencies[len(latencies) // 2],
    }


def write_report(out_dir, summaries):
    deepseek = {
        "A_bare": "0%",
        "B_role_only": "5-10%",
        "C_role_star": "50%",
        "D_role_profile": "40%",
        "E_full_stack": "98%",
    }
    lines = [
        "# Car Wash Prompt Architecture: Variable Isolation Results\n",
        f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        f"Model: {MODEL} | Runs per condition: {RUNS_PER_CONDITION}\n",
        "| Condition | DeepSeek Prediction | Actual Pass Rate | Recovery Rate | Median Latency |",
        "|-----------|--------------------|-----------------:|--------------|----------------|",
    ]
    for name, s in summaries.items():
        recovery = f"{s['recovery_rate']:.1%}" if s["recovery_rate"] is not None else "n/a"
        actual = f"{s['primary_pass_rate']:.1%} ({s['primary_pass']}/{s['total']})"
        lines.append(f"| {name} | {deepseek.get(name,'?')} | {actual} | {recovery} | {s['median_latency_ms']}ms |")

    lines.append("\n## Key Question\n")
    lines.append(
        "Is C (STAR) higher than D (profile)? DeepSeek predicted yes (50% vs 40%).\n"
        "If D > C: profile injection is the dominant mechanism.\n"
        "If C > D: STAR framework is the key driver of task grounding."
    )
    with open(out_dir / "report.md", "w") as f:
        f.write("\n".join(lines))


def main():
    print(f"Car Wash Prompt Architecture Experiment")
    print(f"Model: {MODEL} | Conditions: {len(CONDITIONS)} | Runs each: {RUNS_PER_CONDITION}")

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_dir = Path(f"results/{ts}")
    out_dir.mkdir(parents=True, exist_ok=True)

    all_results = []
    summaries = {}

    for name, condition in CONDITIONS.items():
        trials = run_condition(name, condition, RUNS_PER_CONDITION)
        all_results.extend(trials)
        s = summarize(trials)
        s["description"] = condition["description"]
        summaries[name] = s

    with open(out_dir / "raw.jsonl", "w") as f:
        for r in all_results:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    with open(out_dir / "summary.json", "w") as f:
        json.dump(summaries, f, indent=2)

    write_report(out_dir, summaries)

    latest = Path("results/latest")
    if latest.exists() or latest.is_symlink():
        latest.unlink()
    latest.symlink_to(ts, target_is_directory=True)

    print("\n=== RESULTS ===")
    deepseek = {"A_bare": "0%", "B_role_only": "5-10%", "C_role_star": "50%",
                "D_role_profile": "40%", "E_full_stack": "98%"}
    print(f"{'Condition':<22} {'Predicted':>10} {'Actual':>8} {'Recovery':>10}")
    print("-" * 55)
    for name, s in summaries.items():
        recovery = f"{s['recovery_rate']:.1%}" if s["recovery_rate"] is not None else "n/a"
        print(f"{name:<22} {deepseek.get(name,'?'):>10} {s['primary_pass_rate']:>7.1%} {recovery:>10}")

    print(f"\nResults: {out_dir}/report.md")


if __name__ == "__main__":
    main()
