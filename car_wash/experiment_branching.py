"""
Prompt Branching vs STAR-for-All Experiment
Tests whether question-type branching (PREP + type-specific formats) produces
better answers than applying STAR to all questions.

Two prompt versions:
  - BRANCHING: Original production prompt (PREP structure + question type routing)
  - STAR_ALL:  Current experimental prompt (STAR for all questions, no routing)

Five question types tested:
  1. yes_no:      "Did you use Python for this project?"
  2. direct:      "What's your greatest strength?"
  3. behavioral:  "Tell me about a time you resolved a conflict on your team."
  4. compound:    "Introduce yourself and tell me why you want to work at our company."
  5. constraint:  Car wash problem (pass/fail scoring)

Evaluation: LLM-as-judge for questions 1-4, pattern-based for car wash.

Usage:
    export ANTHROPIC_API_KEY="sk-ant-..."
    python experiment_branching.py
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
JUDGE_MODEL = "claude-sonnet-4-6"
RUNS_PER_CELL = 10
TEMPERATURE = 0.7
MAX_TOKENS = 512

client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])


# ---- Questions ----

QUESTIONS = {
    "yes_no": {
        "text": "Did you use Python for this project?",
        "type": "yes_no",
        "criteria": [
            "starts_with_yes_or_no",   # Answers yes or no directly
            "concise",                  # Under 30 words
            "no_rambling",              # Doesn't over-explain
        ],
    },
    "direct": {
        "text": "What's your greatest strength?",
        "type": "direct",
        "criteria": [
            "answers_question",         # Actually answers what was asked
            "specific",                 # Uses concrete examples, not generic
            "appropriate_length",       # 30-80 words
        ],
    },
    "behavioral": {
        "text": "Tell me about a time you resolved a conflict on your team.",
        "type": "behavioral",
        "criteria": [
            "has_situation",            # Describes a specific situation
            "has_action",              # Describes what they did
            "has_result",              # Describes the outcome
            "uses_specific_example",   # Not generic/hypothetical
        ],
    },
    "compound": {
        "text": "Introduce yourself and tell me why you want to work at our company.",
        "type": "compound",
        "criteria": [
            "addresses_introduction",   # Covers self-introduction
            "addresses_motivation",     # Covers why this company
            "coherent_flow",           # Flows naturally between parts
        ],
    },
    "constraint": {
        "text": "I want to wash my car. The car wash is 100 meters away. Should I walk or drive?",
        "type": "constraint",
        "criteria": [],  # Pattern-based scoring, no LLM judge needed
    },
}


# ---- Profile ----

PROFILE = {
    "name": "Heejin Jo",
    "role": "Forward Deployed Engineer, Applied AI",
    "company": "Anthropic",
    "projects": """    - Running Birth2Death (1-person startup): two live products
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
    "style": "balanced",
    "strengths": ["Cost optimization", "Technical decision making", "AI/ML engineering", "Performance optimization"],
    "custom_instructions": """For Anthropic-specific questions:
- Emphasize alignment with Anthropic's mission of AI safety
- Show understanding of Constitutional AI, RLHF, and responsible scaling
- Reference real experience building with Claude API (InterviewMate uses Claude for answer generation)
- Demonstrate practical understanding of prompt engineering and model behavior
- Be honest about limitations and tradeoffs in AI systems""",
}


# ---- Prompt builders ----

def _build_common(profile):
    """Build the shared parts of the prompt (background, strengths, style)."""
    strengths_list = '\n'.join([f"- {s}" for s in profile["strengths"]])
    strengths_text = f"\n\n**Key Strengths to Emphasize:**\n{strengths_list}"

    style_instructions = {
        'concise': '- Be extremely concise and direct\n- Prefer bullet points over paragraphs\n- Maximum 30 words for most answers',
        'balanced': '- Balance detail with brevity\n- Use 30-60 words for most answers\n- Provide context but stay focused',
        'detailed': '- Provide comprehensive explanations\n- Use 60-100 words when appropriate\n- Include relevant context and examples'
    }
    style_guide = style_instructions[profile["style"]]
    return strengths_text, style_guide


def build_branching_prompt(profile):
    """Original production prompt: PREP + question type branching."""
    strengths_text, style_guide = _build_common(profile)

    prompt = f"""You are {profile["name"]}, interviewing for {profile["role"]} at {profile["company"]}.

# Your Background

{profile["projects"]}{strengths_text}

# Your Interview Style

**Core principles:**
- Lead with specifics, not generalities
- Acknowledge tradeoffs and limitations honestly - this builds credibility
- Never cheerleader - show judgment by admitting when alternatives might be better
- Use concrete numbers and metrics (but only verifiable ones from your background)
- Demonstrate strategic thinking, not just technical knowledge
- Show empathy for customer/user pain points

**Answer structure (PREP):**
- Point: State your conclusion first
- Reason: One clear reason why
- Example: Concrete, specific evidence from your background
- Point: Restate or add nuance if needed

# Communication Style

**Match the question type:**
- Yes/no → "Yes" or "No, [1-sentence correction]" (under 10 words)
- Direct question → Answer directly using PREP structure (30-80 words)
- Behavioral → Use STAR: Situation + Task + Action + Result (60-120 words)
- Compound/multi-part → Address each part using your specific experiences (100-150 words)

**Answer style: {profile["style"]}**
{style_guide}

**Core rules:**
1. ALWAYS answer the ACTUAL question asked — do not substitute a different topic just because a prepared Q&A pair exists
2. Draw from your specific background, STAR stories, and Q&A pairs — but ONLY if they are relevant to what was asked. If prepared answers don't match, ignore them completely
3. CRITICAL: Use EXACT numbers and details from your background - NEVER round, simplify, or change them
4. If your background has specific metrics (e.g., "92.6% reduction"), use those EXACT numbers
5. If your background provides context (e.g., "test vs production"), include that nuance
6. If caught in error, admit it briefly and move on
7. Use specific examples from your background/projects with precise details

# Example Answer Format

**For yes/no questions:**
Keep it under 10 words. If correcting, add one brief sentence.

**For direct questions:**
Answer the specific question asked, then stop. Don't elaborate unless asked.

**For behavioral questions (STAR):**
- Situation: What is the actual situation being described? (1 sentence)
- Task: What needs to be accomplished? What is the goal or constraint?
- Action: What action achieves the task given the situation? (2-3 sentences)
- Result: Measurable outcome with EXACT metrics from your background (use precise numbers, don't round or simplify)

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

    if profile.get("custom_instructions"):
        prompt += f"\n\n# YOUR SPECIFIC INTERVIEW CONTEXT & STYLE\n\n{profile['custom_instructions']}"

    return prompt


def build_star_all_prompt(profile):
    """Current experimental prompt: STAR for all questions, no branching."""
    strengths_text, style_guide = _build_common(profile)

    prompt = f"""You are {profile["name"]}, interviewing for {profile["role"]} at {profile["company"]}.

# Your Background

{profile["projects"]}{strengths_text}

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

**Answer style: {profile["style"]}**
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

    if profile.get("custom_instructions"):
        prompt += f"\n\n# YOUR SPECIFIC INTERVIEW CONTEXT & STYLE\n\n{profile['custom_instructions']}"

    return prompt


# ---- Two conditions ----

PROMPTS = {
    "branching": {
        "system": build_branching_prompt(PROFILE),
        "description": "PREP + question type branching (original production)",
    },
    "star_all": {
        "system": build_star_all_prompt(PROFILE),
        "description": "STAR for all questions (current experimental)",
    },
}


# ---- Car wash scoring (pattern-based) ----

PASS_PATTERNS = [
    r"\bshould\s+drive\b", r"\bshould\s+definitely\s+drive\b",
    r"\brecommend\s+driving\b", r"\bdrive\s+your\s+car\b",
    r"\btake\s+your\s+car\b", r"\bbring\s+your\s+car\b",
    r"\bdrive\s+to\s+the\s+car\s+wash\b", r"\bdrive\s+it\s+(there|over|to)\b",
    r"\bcar\s+needs\s+to\s+be\s+(at|there|present)\b",
    r"\bcar\s+must\s+be\s+present\b", r"\bneed\s+the\s+car\s+(at|there)\b",
    r"\bbest\s+to\s+drive\b", r"\bbetter\s+to\s+drive\b",
    r"\b(answer|solution)\s+is\s+to\s+drive\b",
    r"\bdrive\.\s", r"^drive\b",
]
FAIL_PATTERNS = [
    r"\bshould\s+walk\b", r"\bshould\s+definitely\s+walk\b",
    r"\brecommend\s+walking\b", r"\bwalk\s+to\s+the\s+car\s+wash\b",
    r"\bwalk\s+there\b", r"\bbest\s+to\s+walk\b", r"\bbetter\s+to\s+walk\b",
    r"\bgo\s+on\s+foot\b", r"\b(answer|solution)\s+is\s+to\s+walk\b",
    r"\bwalk\.\s", r"^walk\b",
]
CONSTRAINT_PATTERNS = [
    r"\bcar\s+(needs|has|must)\s+(to\s+)?(be|go|get)\b",
    r"\bneed\s+(the|your)\s+car\s+(at|there|to)\b",
    r"\bcan'?t\s+wash.*without\s+(the|your)\s+car\b",
    r"\bbring\s+(the|your)\s+car\b", r"\bget\s+(the|your)\s+car\s+to\b",
    r"\bcar\s+there\b", r"\bcar\s+with\s+you\b",
    r"\bcar\s+at\s+the\s+(car\s+)?wash\b",
]


def score_car_wash(text: str) -> dict:
    lower = re.sub(r'\*{1,2}', '', text.lower())
    pass_hits = sum(1 for p in PASS_PATTERNS if re.search(p, lower))
    fail_hits = sum(1 for p in FAIL_PATTERNS if re.search(p, lower))
    constraint_hits = sum(1 for p in CONSTRAINT_PATTERNS if re.search(p, lower))

    if pass_hits > 0 and fail_hits == 0:
        verdict = "pass"
    elif fail_hits > 0 and pass_hits == 0:
        verdict = "fail"
    elif pass_hits > 0 and fail_hits > 0:
        verdict = "pass" if pass_hits >= fail_hits * 2 else ("fail" if fail_hits >= pass_hits * 2 else "ambiguous")
    else:
        verdict = "ambiguous"

    return {"verdict": verdict, "has_constraint": constraint_hits > 0}


# ---- LLM-as-judge ----

JUDGE_PROMPT = """You are evaluating an interview answer. Score each criterion as PASS or FAIL.

**Question asked:** {question}
**Question type:** {qtype}
**Answer given:**
{answer}

**Criteria to evaluate:**
{criteria_text}

Also measure:
- word_count: Count the exact number of words in the answer.
- reasoning_order: Does the answer state a conclusion/answer BEFORE explaining reasoning ("conclusion_first"), or does it reason through the problem before concluding ("reasoning_first")? If unclear, say "mixed".

Respond in JSON only. Example:
{{
  "criteria": {{"criterion_name": "pass", ...}},
  "word_count": 45,
  "reasoning_order": "conclusion_first"
}}"""

CRITERIA_DESCRIPTIONS = {
    "starts_with_yes_or_no": "The answer begins with 'Yes' or 'No' (possibly followed by a comma or period)",
    "concise": "The answer is under 30 words total",
    "no_rambling": "The answer does not over-explain or add unnecessary elaboration",
    "answers_question": "The answer directly addresses what was asked",
    "specific": "The answer uses concrete examples, metrics, or projects — not generic platitudes",
    "appropriate_length": "The answer is between 30 and 80 words",
    "has_situation": "The answer describes a specific situation or context",
    "has_action": "The answer describes concrete actions the person took",
    "has_result": "The answer describes a measurable or concrete outcome",
    "uses_specific_example": "The answer references a real (or plausibly real) example, not a hypothetical",
    "addresses_introduction": "The answer includes a self-introduction (who they are, background)",
    "addresses_motivation": "The answer explains why they want to work at this specific company",
    "coherent_flow": "The answer flows naturally between parts without abrupt topic switches",
}


def judge_answer(question_key: str, answer: str) -> dict:
    """Use LLM to evaluate answer quality."""
    q = QUESTIONS[question_key]
    criteria_text = "\n".join(
        f"- {c}: {CRITERIA_DESCRIPTIONS[c]}" for c in q["criteria"]
    )

    prompt = JUDGE_PROMPT.format(
        question=q["text"],
        qtype=q["type"],
        answer=answer,
        criteria_text=criteria_text,
    )

    response = client.messages.create(
        model=JUDGE_MODEL,
        max_tokens=256,
        temperature=0,
        messages=[{"role": "user", "content": prompt}],
    )

    text = response.content[0].text.strip()
    # Extract JSON from response
    json_match = re.search(r'\{[\s\S]*\}', text)
    if json_match:
        return json.loads(json_match.group())
    return {"criteria": {}, "word_count": -1, "reasoning_order": "unknown"}


# ---- API ----

def ask(system: str, question: str) -> tuple[str, float]:
    start = time.time()
    response = client.messages.create(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        temperature=TEMPERATURE,
        system=system,
        messages=[{"role": "user", "content": question}],
    )
    latency_ms = (time.time() - start) * 1000
    return response.content[0].text, latency_ms


# ---- Runner ----

def run_experiment(runs_per_cell: int):
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_dir = Path(f"results/branching_{ts}")
    out_dir.mkdir(parents=True, exist_ok=True)

    all_results = []
    total_cells = len(PROMPTS) * len(QUESTIONS)
    total_calls = total_cells * runs_per_cell
    judge_calls = sum(runs_per_cell for q in QUESTIONS.values() if q["criteria"]) * len(PROMPTS)
    api_calls = total_calls + judge_calls

    print(f"Branching vs STAR-for-All Experiment")
    print(f"Model: {MODEL} | Judge: {JUDGE_MODEL} | Temperature: {TEMPERATURE}")
    print(f"Runs per cell: {runs_per_cell} | Cells: {total_cells} | Total API calls: ~{api_calls}")
    print(f"Questions: {list(QUESTIONS.keys())}")
    print(f"Prompts: {list(PROMPTS.keys())}")
    print()

    for prompt_name, prompt_data in PROMPTS.items():
        system = prompt_data["system"]
        print(f"\n{'='*60}")
        print(f"[{prompt_name}] {prompt_data['description']}")
        print(f"{'='*60}")

        for q_key, q_data in QUESTIONS.items():
            print(f"\n  [{q_key}] \"{q_data['text'][:50]}...\"")

            for i in range(runs_per_cell):
                text, latency = ask(system, q_data["text"])
                word_count = len(text.split())

                result = {
                    "prompt": prompt_name,
                    "question": q_key,
                    "question_type": q_data["type"],
                    "trial": i + 1,
                    "text": text,
                    "word_count": word_count,
                    "latency_ms": round(latency),
                }

                # Score
                if q_key == "constraint":
                    score = score_car_wash(text)
                    result["verdict"] = score["verdict"]
                    result["has_constraint"] = score["has_constraint"]
                    tag = f"{score['verdict']}"
                    if score["has_constraint"]:
                        tag += " +constraint"
                else:
                    judgment = judge_answer(q_key, text)
                    result["criteria"] = judgment.get("criteria", {})
                    result["reasoning_order"] = judgment.get("reasoning_order", "unknown")
                    result["judge_word_count"] = judgment.get("word_count", -1)
                    passes = sum(1 for v in result["criteria"].values() if v == "pass")
                    total_c = len(result["criteria"])
                    tag = f"{passes}/{total_c} criteria"
                    if result["reasoning_order"] != "unknown":
                        tag += f" [{result['reasoning_order']}]"

                all_results.append(result)
                print(f"    [{i+1:02d}/{runs_per_cell}] {tag} ({word_count}w, {round(latency)}ms)")
                time.sleep(0.3)

    # Save raw
    with open(out_dir / "raw.jsonl", "w") as f:
        for r in all_results:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    # Build summary
    summary = {}
    for prompt_name in PROMPTS:
        summary[prompt_name] = {}
        for q_key in QUESTIONS:
            trials = [r for r in all_results if r["prompt"] == prompt_name and r["question"] == q_key]

            if q_key == "constraint":
                s = {
                    "pass_rate": round(sum(1 for t in trials if t["verdict"] == "pass") / len(trials), 3),
                    "constraint_rate": round(sum(1 for t in trials if t.get("has_constraint")) / len(trials), 3),
                }
            else:
                # Per-criterion pass rates
                criteria_rates = {}
                for c in QUESTIONS[q_key]["criteria"]:
                    passed = sum(1 for t in trials if t.get("criteria", {}).get(c) == "pass")
                    criteria_rates[c] = round(passed / len(trials), 3)

                reasoning_orders = [t.get("reasoning_order", "unknown") for t in trials]
                s = {
                    "criteria_pass_rates": criteria_rates,
                    "avg_criteria_pass": round(
                        sum(criteria_rates.values()) / len(criteria_rates), 3
                    ) if criteria_rates else 0,
                    "reasoning_order": {
                        "conclusion_first": reasoning_orders.count("conclusion_first"),
                        "reasoning_first": reasoning_orders.count("reasoning_first"),
                        "mixed": reasoning_orders.count("mixed"),
                    },
                }

            s["avg_word_count"] = round(sum(t["word_count"] for t in trials) / len(trials), 1)
            s["median_latency_ms"] = sorted(t["latency_ms"] for t in trials)[len(trials) // 2]
            summary[prompt_name][q_key] = s

    with open(out_dir / "summary.json", "w") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    # Print report
    print_report(summary, all_results)
    write_report(out_dir, summary, all_results)

    print(f"\nResults saved: {out_dir}/")
    return summary


def print_report(summary, all_results):
    print("\n" + "=" * 90)
    print("RESULTS")
    print("=" * 90)

    # Car wash comparison
    print("\n--- Car Wash (Implicit Constraint) ---")
    print(f"{'Prompt':<15} {'Pass Rate':>10} {'Constraint':>12} {'Avg Words':>10}")
    print("-" * 50)
    for p in PROMPTS:
        s = summary[p]["constraint"]
        print(f"{p:<15} {s['pass_rate']:>9.0%} {s['constraint_rate']:>11.0%} {s['avg_word_count']:>9.1f}")

    # Other questions
    for q_key in ["yes_no", "direct", "behavioral", "compound"]:
        q = QUESTIONS[q_key]
        print(f"\n--- {q_key}: \"{q['text'][:50]}\" ---")
        print(f"{'Prompt':<15} {'Avg Score':>10} {'Words':>8} {'Order':>20}  Criteria")
        print("-" * 80)
        for p in PROMPTS:
            s = summary[p][q_key]
            order = s["reasoning_order"]
            order_str = f"C{order['conclusion_first']}/R{order['reasoning_first']}/M{order['mixed']}"
            criteria_str = " | ".join(
                f"{c}:{v:.0%}" for c, v in s["criteria_pass_rates"].items()
            )
            print(f"{p:<15} {s['avg_criteria_pass']:>9.0%} {s['avg_word_count']:>7.1f} {order_str:>20}  {criteria_str}")


def write_report(out_dir, summary, all_results):
    with open(out_dir / "report.md", "w") as f:
        f.write("# Branching vs STAR-for-All Experiment\n\n")
        f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
        f.write(f"Model: {MODEL} | Judge: {JUDGE_MODEL} | Temperature: {TEMPERATURE}\n")
        f.write(f"Runs per cell: {RUNS_PER_CELL}\n\n")

        # Car wash table
        f.write("## Car Wash (Implicit Constraint)\n\n")
        f.write("| Prompt | Pass Rate | Constraint | Avg Words |\n")
        f.write("|--------|-----------|------------|----------|\n")
        for p in PROMPTS:
            s = summary[p]["constraint"]
            f.write(f"| {p} | {s['pass_rate']:.0%} | {s['constraint_rate']:.0%} | {s['avg_word_count']:.1f} |\n")

        # Other questions
        for q_key in ["yes_no", "direct", "behavioral", "compound"]:
            q = QUESTIONS[q_key]
            f.write(f"\n## {q_key}: \"{q['text']}\"\n\n")
            f.write("| Prompt | Avg Score | Avg Words | Reasoning Order | Criteria |\n")
            f.write("|--------|-----------|-----------|-----------------|----------|\n")
            for p in PROMPTS:
                s = summary[p][q_key]
                order = s["reasoning_order"]
                order_str = f"C:{order['conclusion_first']} R:{order['reasoning_first']} M:{order['mixed']}"
                criteria_str = ", ".join(f"{c}: {v:.0%}" for c, v in s["criteria_pass_rates"].items())
                f.write(f"| {p} | {s['avg_criteria_pass']:.0%} | {s['avg_word_count']:.1f} | {order_str} | {criteria_str} |\n")

        # Key questions
        f.write("\n## Key Questions\n\n")
        f.write("1. Does branching (PREP) produce better yes/no conciseness?\n")
        f.write("2. Does STAR-for-all hurt direct question answers (over-structured)?\n")
        f.write("3. Does branching's PREP ('conclusion first') kill car wash accuracy?\n")
        f.write("4. Which prompt produces more 'reasoning_first' vs 'conclusion_first' answers?\n")
        f.write("5. Is there a clear winner, or do we need a hybrid approach?\n")


def main():
    run_experiment(RUNS_PER_CELL)


if __name__ == "__main__":
    main()
