"""
Run F_role_star_profile condition: Role + STAR + Profile (no RAG).
Isolates whether the 85%→100% jump comes from Profile or RAG.

Uses same settings as experiment.py Run 2.
"""

import os
import json
import time
import re
from datetime import datetime
from pathlib import Path
import anthropic

# ---- Config (same as experiment.py) ----
ANTHROPIC_API_KEY = os.environ["ANTHROPIC_API_KEY"]
MODEL = "claude-sonnet-4-5-20250929"
RUNS = 20
TEMPERATURE = 0.7

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

QUESTION = "I want to wash my car. The car wash is 100 meters away. Should I walk or drive?"
CHALLENGE = "How will I get my car washed if I am walking?"

F_CONDITION = {
    "system": (
        "You are an expert advisor helping people make practical decisions. "
        "Always think through problems carefully and consider all relevant factors. "
        "Provide clear, actionable recommendations.\n\n"
        "When answering any question, use the STAR method:\n"
        "- Situation: Describe the current situation\n"
        "- Task: What needs to be accomplished\n"
        "- Action: What specific action to take\n"
        "- Result: What the expected outcome will be\n\n"
        "User Profile:\n"
        "- Name: Sarah\n"
        "- Location: Suburban area, owns a 2022 Honda Civic\n"
        "- Current situation: At home, car is parked in the driveway\n"
        "- Goal: Complete daily errands efficiently"
    ),
    "description": "Role + STAR + Profile (no RAG). Isolates Profile contribution.",
}

# ---- Scoring (same as experiment.py Run 2) ----
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
    lower = re.sub(r'\*{1,2}', '', text.lower())
    pass_hits = sum(1 for p in PASS_PATTERNS if re.search(p, lower))
    fail_hits = sum(1 for p in FAIL_PATTERNS if re.search(p, lower))
    if pass_hits > 0 and fail_hits == 0:
        return "pass"
    elif fail_hits > 0 and pass_hits == 0:
        return "fail"
    elif pass_hits > 0 and fail_hits > 0:
        if pass_hits >= fail_hits * 2:
            return "pass"
        elif fail_hits >= pass_hits * 2:
            return "fail"
        return "ambiguous"
    else:
        return "ambiguous"


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


def main():
    print(f"F_role_star_profile: Role + STAR + Profile (no RAG)")
    print(f"Model: {MODEL} | Runs: {RUNS} | Temp: {TEMPERATURE}")
    print()

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_dir = Path(f"results/{ts}")
    out_dir.mkdir(parents=True, exist_ok=True)

    system = F_CONDITION["system"]
    results = []

    for i in range(RUNS):
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
            "condition": "F_role_star_profile",
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
        print(f"  [{i+1:02d}/{RUNS}] {tag}")

        time.sleep(0.3)

    # Save results
    with open(out_dir / "raw.jsonl", "w") as f:
        for r in results:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    # Summary
    total = len(results)
    passes = sum(1 for r in results if r["primary_score"] == "pass")
    fails = sum(1 for r in results if r["primary_score"] == "fail")
    ambiguous = sum(1 for r in results if r["primary_score"] == "ambiguous")
    challenged = [r for r in results if r["challenge_score"] is not None]
    recovered = sum(1 for r in challenged if r["challenge_score"] == "pass")
    latencies = sorted(r["primary_latency_ms"] for r in results)

    summary = {
        "F_role_star_profile": {
            "total": total,
            "primary_pass": passes,
            "primary_fail": fails,
            "primary_ambiguous": ambiguous,
            "primary_pass_rate": round(passes / total, 3),
            "challenged": len(challenged),
            "recovered": recovered,
            "recovery_rate": round(recovered / len(challenged), 3) if challenged else None,
            "median_latency_ms": latencies[len(latencies) // 2],
            "description": F_CONDITION["description"],
        }
    }

    with open(out_dir / "summary.json", "w") as f:
        json.dump(summary, f, indent=2)

    pass_rate = passes / total
    recovery = f"{recovered}/{len(challenged)} ({recovered/len(challenged):.1%})" if challenged else "n/a"

    print(f"\n=== F_role_star_profile RESULT ===")
    print(f"Pass rate: {pass_rate:.1%} ({passes}/{total})")
    print(f"Recovery: {recovery}")
    print(f"Median latency: {latencies[len(latencies) // 2]}ms")

    print(f"\n=== ALL CONDITIONS COMPARISON ===")
    print(f"{'Condition':<25} {'Pass Rate':>10}")
    print("-" * 40)
    print(f"{'A_bare':<25} {'0%':>10}")
    print(f"{'B_role_only':<25} {'0%':>10}")
    print(f"{'C_role_star':<25} {'85%':>10}")
    print(f"{'D_role_profile':<25} {'30%':>10}")
    print(f"{'E_full_stack':<25} {'100%':>10}")
    print(f"{'F_role_star_profile':<25} {f'{pass_rate:.0%}':>10}")

    print(f"\nResults saved to: {out_dir}/")


if __name__ == "__main__":
    main()
