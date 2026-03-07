"""
Car Wash STAR + Profile Interaction Experiment
Tests whether STAR reasoning works differently across InterviewMate profiles.

Conditions:
1. STAR + Anthropic profile (Forward Deployed Engineer @ Anthropic)
2. STAR + Default profile (Solutions Architect @ OpenAI)
3. STAR only (no profile — paper's C_role_star reproduction with claude-sonnet-4-6)

Scoring: pass/fail + implicit constraint detection (car needs to be at car wash)

Usage:
    export ANTHROPIC_API_KEY="sk-ant-..."
    python experiment_profile_star.py
"""

import os
import json
import time
import re
from datetime import datetime
from pathlib import Path
import anthropic

# ---- Config ----

MODEL = "claude-sonnet-4-6"
RUNS_PER_CONDITION = 20
TEMPERATURE = 0.7

client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

QUESTION = "I want to wash my car. The car wash is 100 meters away. Should I walk or drive?"


# ---- InterviewMate system prompt template (current production) ----

def build_interviewmate_prompt(name, role, company, projects, style, strengths, custom_instructions=None):
    strengths_text = ''
    if strengths:
        strengths_list = '\n'.join([f"- {s}" for s in strengths])
        strengths_text = f"\n\n**Key Strengths to Emphasize:**\n{strengths_list}"

    style_instructions = {
        'concise': '- Be extremely concise and direct\n- Prefer bullet points over paragraphs\n- Maximum 30 words for most answers',
        'balanced': '- Balance detail with brevity\n- Use 30-60 words for most answers\n- Provide context but stay focused',
        'detailed': '- Provide comprehensive explanations\n- Use 60-100 words when appropriate\n- Include relevant context and examples'
    }
    style_guide = style_instructions.get(style, style_instructions['balanced'])

    prompt = f"""You are {name}, interviewing for {role} at {company}.

# Your Background

{projects if projects else 'No specific background provided. Use [placeholder] format for specific examples, projects, and metrics.'}{strengths_text}

# Your Interview Style

**Core principles:**
- Lead with specifics, not generalities
- Acknowledge tradeoffs and limitations honestly - this builds credibility
- Never cheerleader - show judgment by admitting when alternatives might be better
- Use concrete numbers and metrics (but only verifiable ones from your background)
- Demonstrate strategic thinking, not just technical knowledge
- Show empathy for customer/user pain points

**When answering any question, use the STAR method:**
- Situation: What is the actual situation being described?
- Task: What needs to be accomplished? What is the goal or constraint?
- Action: What action achieves the task given the situation?
- Result: What outcome does this action produce?

# Communication Style

**Answer style: {style}**
{style_guide}

**Core rules:**
1. ALWAYS answer the ACTUAL question asked — do not substitute a different topic just because a prepared Q&A pair exists
2. Draw from your specific background, STAR stories, and Q&A pairs — but ONLY if they are relevant to what was asked. If prepared answers don't match, ignore them completely
3. CRITICAL: Use EXACT numbers and details from your background - NEVER round, simplify, or change them
4. If your background has specific metrics (e.g., "92.6% reduction"), use those EXACT numbers
5. If your background provides context (e.g., "test vs production"), include that nuance
6. If caught in error, admit it briefly and move on
7. Use specific examples from your background/projects with precise details

**CRITICAL - About numbers and metrics:**
- If your background says "92.6% cost reduction", say exactly that - NOT "90%" or "about 90%"
- If your background distinguishes "test" vs "production" numbers, preserve that distinction
- Never invent, round, or simplify numbers - use them exactly as written in your background

**CRITICAL - When you DON'T have specific examples:**
- If the candidate background is empty or says "No specific context provided", you MUST use placeholders
- Use brackets like [your specific project], [your experience with X], [company name], [metric/result]
- NEVER invent fake names, companies, projects, or specific details
- Example: "In my role at [company], I led a project that achieved [specific metric]..."
- This helps the candidate fill in their own real experiences

**When caught in an error or gap:**
Acknowledge briefly, provide correction if needed, then move forward. Don't over-explain.

Now answer the interview question following these guidelines."""

    if custom_instructions:
        prompt += f"\n\n# YOUR SPECIFIC INTERVIEW CONTEXT & STYLE\n\n{custom_instructions}"

    return prompt


# ---- Paper's original C_role_star prompt ----

PAPER_STAR_PROMPT = (
    "You are an expert advisor helping people make practical decisions. "
    "Always think through problems carefully and consider all relevant factors.\n\n"
    "When answering any question, use the STAR method:\n"
    "- Situation: What is the actual situation being described?\n"
    "- Task: What needs to be accomplished?\n"
    "- Action: What action achieves the task given the situation?\n"
    "- Result: What outcome does this action produce?\n\n"
    "Provide clear, actionable recommendations."
)


# ---- Profile data (from InterviewMate production DB) ----

ANTHROPIC_PROFILE = build_interviewmate_prompt(
    name="Heejin Jo",
    role="Forward Deployed Engineer, Applied AI",
    company="Anthropic",
    projects="""    - Running Birth2Death (1-person startup): two live products
      - InterviewMate: AI interview coaching platform (Claude API, real-time STT, streaming answers)
        - Generating revenue, live users
      - TaskFlow: visionOS productivity app (Swift, RealityKit)
    - Architecture: semantic_cache.py (0.92 threshold), router.py (mental health patterns), cost_tracker.py
    - GitHub: github.com/JO-HEEJIN/birth2death-backend, pushed yesterday

    **Latest OpenAI Knowledge (Dec 2025):**
    - gpt-realtime (GA): $32/1M input, WebRTC, 66.5% function calling accuracy
    - o1-pro: $600/1M output, 60% fewer reasoning tokens vs o1-preview
    - Prompt Caching: 90% cost reduction for 1024+ token prompts
    - ChatGPT Apps: 800M users, MCP-based SDK
    - Enterprise AI 2025: 75% report productivity gains, 8x message growth YoY""",
    style="balanced",
    strengths=["Cost optimization", "Technical decision making", "AI/ML engineering", "Performance optimization"],
    custom_instructions="""For Anthropic-specific questions:
- Emphasize alignment with Anthropic's mission of AI safety
- Show understanding of Constitutional AI, RLHF, and responsible scaling
- Reference real experience building with Claude API (InterviewMate uses Claude for answer generation)
- Demonstrate practical understanding of prompt engineering and model behavior
- Be honest about limitations and tradeoffs in AI systems"""
)

DEFAULT_PROFILE = build_interviewmate_prompt(
    name="Heejin Jo",
    role="Solutions Architect",
    company="OpenAI",
    projects="""    - Running Birth2Death (1-person startup): two live products
      - InterviewMate: AI interview coaching platform (Claude API, real-time STT, streaming answers)
        - Generating revenue, live users
      - TaskFlow: visionOS productivity app (Swift, RealityKit)
    - Architecture: semantic_cache.py (0.92 threshold), router.py (mental health patterns), cost_tracker.py
    - GitHub: github.com/JO-HEEJIN/birth2death-backend, pushed yesterday

    **Latest OpenAI Knowledge (Dec 2025):**
    - gpt-realtime (GA): $32/1M input, WebRTC, 66.5% function calling accuracy
    - o1-pro: $600/1M output, 60% fewer reasoning tokens vs o1-preview
    - Prompt Caching: 90% cost reduction for 1024+ token prompts
    - ChatGPT Apps: 800M users, MCP-based SDK
    - Enterprise AI 2025: 75% report productivity gains, 8x message growth YoY""",
    style="balanced",
    strengths=["Cost optimization", "Technical decision making", "AI/ML engineering", "Performance optimization"],
    custom_instructions="""For Korea market questions:
- No Korea region: 150-200ms latency to US is the elephant in the room
- Solutions: AWS Global Accelerator, edge VAD, streaming UI
- Sovereign AI pressure: Government pushing independent capabilities
- Suggest hybrid architecture (sensitive local, complex reasoning OpenAI)
- Position as bridge, not replacement

Market context:
- Korea shifting from fast follower to first mover
- G3 AI ambition (US, China, Korea)
- Samsung HBM dominance
- Startups need speed NOW, can't wait for domestic models

For Korea-specific questions:
- Acknowledge the real constraint (latency, sovereignty)
- Provide concrete technical solutions"""
)


# ---- 3 Experimental Conditions ----

CONDITIONS = {
    "A_star_anthropic": {
        "system": ANTHROPIC_PROFILE,
        "description": "InterviewMate STAR + Anthropic profile (FDE @ Anthropic)",
    },
    "B_star_default": {
        "system": DEFAULT_PROFILE,
        "description": "InterviewMate STAR + Default profile (SA @ OpenAI)",
    },
    "C_star_only": {
        "system": PAPER_STAR_PROMPT,
        "description": "Paper's C_role_star (STAR only, no profile) — reproduction on claude-sonnet-4-6",
    },
}


# ---- Scoring ----

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
    r"\bdrive\.\s",  # "Drive." as first word
    r"^drive\b",     # Starts with "drive"
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
    r"\bwalk\.\s",   # "Walk." as first word
    r"^walk\b",      # Starts with "walk"
]

# Implicit constraint patterns — the REAL reason (car must be at car wash)
CONSTRAINT_PATTERNS = [
    r"\bcar\s+(needs|has|must)\s+(to\s+)?(be|go|get)\b",
    r"\bneed\s+(the|your)\s+car\s+(at|there|to)\b",
    r"\bcan'?t\s+wash.*without\s+(the|your)\s+car\b",
    r"\bcar\s+wash\s+(requires|needs)\s+(the|your)\s+(car|vehicle)\b",
    r"\bhow\s+will\s+(the|your)\s+car\s+get\b",
    r"\bbring\s+(the|your)\s+car\b",
    r"\bcar\s+isn'?t\s+going\s+to\s+walk\b",
    r"\bvehicle\s+(needs|has|must)\b",
    r"\bget\s+(the|your)\s+car\s+to\b",
    r"\bcar\s+there\b",
    r"\bcar\s+with\s+you\b",
    r"\bcar\s+at\s+the\s+(car\s+)?wash\b",
]


def score_response(text: str) -> dict:
    """Score response for pass/fail AND implicit constraint detection."""
    lower = re.sub(r'\*{1,2}', '', text.lower())

    pass_hits = sum(1 for p in PASS_PATTERNS if re.search(p, lower))
    fail_hits = sum(1 for p in FAIL_PATTERNS if re.search(p, lower))
    constraint_hits = sum(1 for p in CONSTRAINT_PATTERNS if re.search(p, lower))

    if pass_hits > 0 and fail_hits == 0:
        verdict = "pass"
    elif fail_hits > 0 and pass_hits == 0:
        verdict = "fail"
    elif pass_hits > 0 and fail_hits > 0:
        if pass_hits >= fail_hits * 2:
            verdict = "pass"
        elif fail_hits >= pass_hits * 2:
            verdict = "fail"
        else:
            verdict = "ambiguous"
    else:
        verdict = "ambiguous"

    return {
        "verdict": verdict,
        "has_constraint": constraint_hits > 0,
        "pass_hits": pass_hits,
        "fail_hits": fail_hits,
        "constraint_hits": constraint_hits,
    }


# ---- API ----

def ask(system, question):
    kwargs = {
        "model": MODEL,
        "max_tokens": 512,
        "messages": [{"role": "user", "content": question}],
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
        text, latency = ask(system, QUESTION)
        score = score_response(text)

        result = {
            "condition": name,
            "trial": i + 1,
            "text": text,
            "verdict": score["verdict"],
            "has_constraint": score["has_constraint"],
            "constraint_hits": score["constraint_hits"],
            "latency_ms": round(latency),
        }
        results.append(result)

        tag = f"{score['verdict']}"
        if score['has_constraint']:
            tag += " +constraint"
        print(f"  [{i+1:02d}/{runs}] {tag} ({round(latency)}ms)")

        time.sleep(0.3)

    return results


def summarize(results):
    total = len(results)
    passes = sum(1 for r in results if r["verdict"] == "pass")
    fails = sum(1 for r in results if r["verdict"] == "fail")
    ambiguous = sum(1 for r in results if r["verdict"] == "ambiguous")
    with_constraint = sum(1 for r in results if r["has_constraint"])
    pass_with_constraint = sum(1 for r in results if r["verdict"] == "pass" and r["has_constraint"])
    latencies = sorted(r["latency_ms"] for r in results)

    return {
        "total": total,
        "pass": passes,
        "fail": fails,
        "ambiguous": ambiguous,
        "pass_rate": round(passes / total, 3),
        "constraint_rate": round(with_constraint / total, 3),
        "pass_with_constraint": pass_with_constraint,
        "correct_reasoning_rate": round(pass_with_constraint / total, 3),
        "median_latency_ms": latencies[len(latencies) // 2],
    }


def main():
    print(f"Car Wash STAR + Profile Interaction Experiment")
    print(f"Model: {MODEL} | Temperature: {TEMPERATURE} | Runs: {RUNS_PER_CONDITION}/condition")
    print(f"Question: {QUESTION}")

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_dir = Path(f"results/profile_star_{ts}")
    out_dir.mkdir(parents=True, exist_ok=True)

    all_results = []
    summaries = {}

    for name, condition in CONDITIONS.items():
        trials = run_condition(name, condition, RUNS_PER_CONDITION)
        all_results.extend(trials)
        s = summarize(trials)
        s["description"] = condition["description"]
        summaries[name] = s

    # Save raw results
    with open(out_dir / "raw.jsonl", "w") as f:
        for r in all_results:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    with open(out_dir / "summary.json", "w") as f:
        json.dump(summaries, f, indent=2, ensure_ascii=False)

    # Print report
    print("\n" + "=" * 80)
    print("RESULTS")
    print("=" * 80)
    print(f"{'Condition':<25} {'Pass Rate':>10} {'Constraint':>12} {'Correct+Reason':>15} {'Median ms':>10}")
    print("-" * 75)
    for name, s in summaries.items():
        print(
            f"{name:<25} "
            f"{s['pass_rate']:>9.0%} "
            f"{s['constraint_rate']:>11.0%} "
            f"{s['correct_reasoning_rate']:>14.0%} "
            f"{s['median_latency_ms']:>9}ms"
        )

    print(f"\nPass Rate = answered 'drive'")
    print(f"Constraint = mentioned implicit constraint (car must be at car wash)")
    print(f"Correct+Reason = answered 'drive' AND mentioned constraint")
    print(f"\nResults saved: {out_dir}/")

    # Write markdown report
    with open(out_dir / "report.md", "w") as f:
        f.write(f"# Car Wash STAR + Profile Experiment\n\n")
        f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
        f.write(f"Model: {MODEL} | Temperature: {TEMPERATURE} | Runs: {RUNS_PER_CONDITION}/condition\n\n")
        f.write(f"| Condition | Pass Rate | Constraint | Correct+Reason | Median Latency |\n")
        f.write(f"|-----------|-----------|------------|----------------|----------------|\n")
        for name, s in summaries.items():
            f.write(
                f"| {name} | {s['pass_rate']:.0%} ({s['pass']}/{s['total']}) "
                f"| {s['constraint_rate']:.0%} ({sum(1 for r in all_results if r['condition']==name and r['has_constraint'])}/{s['total']}) "
                f"| {s['correct_reasoning_rate']:.0%} ({s['pass_with_constraint']}/{s['total']}) "
                f"| {s['median_latency_ms']}ms |\n"
            )
        f.write(f"\n## Key Questions\n\n")
        f.write(f"1. Does Anthropic profile produce higher pass rate than Default profile?\n")
        f.write(f"2. Does either profile produce correct reasoning (implicit constraint)?\n")
        f.write(f"3. Does C_star_only (paper reproduction) still get 85% on claude-sonnet-4-6?\n")
        f.write(f"4. Is the pass rate on profiles just coincidence or systematic?\n")


if __name__ == "__main__":
    main()
