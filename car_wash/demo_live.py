"""
Live demo slice of the car-wash study — for showing on stage.

Runs ONE condition (E_full_stack) for a handful of trials and streams a clean
line per trial so an audience can watch it "tick along" and agree with the
paper in real time. It does NOT replace experiment.py — it imports the exact
prompt, question, scoring, and API call from it so the live result is faithful
to the published study (single source of truth).

Usage:
    export ANTHROPIC_API_KEY="sk-ant-..."
    python demo_live.py            # 10 runs of E_full_stack
    python demo_live.py 5          # override run count (e.g. for rehearsal)

Full study / all conditions: see experiment.py.
"""

import sys
import time

from experiment import (
    CONDITIONS,
    QUESTION,
    score_response,
    ask,
    MODEL,
    TEMPERATURE,
)

CONDITION = "E_full_stack"      # 100% in the paper (20/20) — safest for a live run
DEFAULT_RUNS = 10

# ANSI colors, but only when writing to a real terminal (clean if piped/redirected)
_tty = sys.stdout.isatty()
def _c(code, s):
    return f"\033[{code}m{s}\033[0m" if _tty else s
GREEN, RED, YELLOW, DIM, BOLD = "32", "31", "33", "2", "1"


def snippet(text, width=60):
    """First non-empty line of the response, trimmed to one clean line."""
    line = next((l.strip() for l in text.splitlines() if l.strip()), text.strip())
    line = line.replace("*", "")
    return line[:width] + ("…" if len(line) > width else "")


def main():
    runs = int(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_RUNS
    system = CONDITIONS[CONDITION]["system"]

    bar = "━" * 66
    print(f"\n{_c(BOLD, bar)}")
    print(_c(BOLD, "  Car Wash · live reproduction"))
    print(bar)
    print(f"  Model:     {MODEL}   temp {TEMPERATURE}")
    print(f"  Condition: {CONDITION}  ({CONDITIONS[CONDITION]['description']})")
    print(f"  Question:  {_c(DIM, QUESTION)}")
    print(f"  Expected:  {_c(GREEN, 'drive')}   (paper: 100%, 20/20)")
    print("─" * 66, flush=True)

    passes = 0
    for i in range(1, runs + 1):
        text, latency = ask(system, [{"role": "user", "content": QUESTION}])
        score = score_response(text)
        if score == "pass":
            passes += 1
            verdict = _c(GREEN, "✅ PASS")
        elif score == "fail":
            verdict = _c(RED, "❌ FAIL")
        else:
            verdict = _c(YELLOW, "•  AMBIG")

        rate = passes / i
        print(
            f"  run {i:02d}/{runs}  {verdict}  {round(latency):>5}ms  "
            f"[{passes}/{i} = {rate:.0%}]  {_c(DIM, '› ' + snippet(text))}",
            flush=True,
        )
        time.sleep(0.3)

    print("─" * 66)
    final = _c(GREEN, f"{passes}/{runs} drive ({passes/runs:.0%})")
    match = _c(GREEN, "— matches the paper ✅") if passes / runs >= 0.9 else _c(YELLOW, "— see note")
    print(f"  RESULT: {final}  {match}")
    print(f"{bar}\n", flush=True)


if __name__ == "__main__":
    main()
