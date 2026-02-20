# Car Wash Prompt Architecture — Variable Isolation Study

> Complete Experiment Documentation

**Date:** 2026-02-19
**Team:** [InterviewMate](https://interviewmate.tech)
**Model:** `claude-sonnet-4-5-20250929`
**Temperature:** 0.7 | **max_tokens:** 512 | **Runs per condition:** 20

---

## 1. Origin — How This Started

On Mastodon, Kevin ([@knowmadd](https://mastodon.world/@knowmadd)) posted:

> "I want to wash my car. The car wash is 50 meters away. Should I walk or drive?"

He tested Perplexity, ChatGPT, Claude, and Mistral. **All four recommended walking.** But the correct answer is **DRIVE** — because you need to physically bring your car to the car wash for it to be washed.

The post went viral on [Hacker News (1,499 points, 943 comments)](https://news.ycombinator.com/item?id=47031580).

Key themes from the HN discussion:
- LLMs fail to understand implicit prerequisites ("my car is at home" is obvious to humans but invisible to AI)
- This is the "frame problem" in AI — models don't know which unstated facts are relevant
- The gap between structured and natural communication remains fundamental

During a routine interview practice session, we posed the same question to InterviewMate. It answered **drive** immediately. Every other LLM had failed. Ours did not.

We shared this publicly. But after the post went live, a harder question surfaced: we did not actually know **why** it worked. InterviewMate's system prompt has multiple layers — role definition, STAR framework, user profile, RAG context — and any one of them (or a combination) could have been the factor. Without understanding which layer actually produced the correct answer, we couldn't defend the result, replicate it, or improve on it.

The InterviewMate team saw this differently: we design multi-layered prompt architectures daily. Our question was not "why do LLMs fail?" but rather **"WHICH prompt layer actually fixes this?"** That's what led to this variable isolation experiment.

**Sources:**
- [Original Mastodon post](https://mastodon.world/@knowmadd/116072773118828295)
- [Hacker News discussion](https://news.ycombinator.com/item?id=47031580)
- Inspired by: [ryan-allen/car-wash-evals](https://github.com/ryan-allen/car-wash-evals)

---

## 2. Why This Matters for InterviewMate

InterviewMate is a real-time interview coaching app that injects user resumes, STAR stories, and Q&A data into system prompts. Our prompt is composed of multiple layers:

```
Role definition → STAR reasoning framework → User profile → RAG context
```

We needed to know: which layer actually contributes to answer quality? If we could isolate each layer's contribution, we'd know where to invest engineering effort and what constitutes our real competitive moat.

The car wash problem is a perfect proxy — it's a simple question with a definitively correct answer that requires the same kind of implicit context reasoning that interview coaching demands.

---

## 3. Experiment Design

- **Question:** "I want to wash my car. The car wash is 100 meters away. Should I walk or drive?"
- **Correct answer:** Drive (the car needs to be physically present at the car wash)
- **Challenge prompt** (given only to models that fail): "How will I get my car washed if I am walking?"

We designed 5 prompt conditions to isolate specific architectural layers and their combinations:

| Condition | What's in the system prompt |
|---|---|
| **A_bare** | Nothing. No system prompt at all. Pure baseline. |
| **B_role_only** | `"You are an expert advisor helping people make practical decisions. Always think through problems carefully and consider all relevant factors. Provide clear, actionable recommendations."` |
| **C_role_star** | Above + STAR framework: `"When answering any question, use the STAR method: Situation → Task → Action → Result"` |
| **D_role_profile** | Role + User profile (no STAR): `"Name: Sarah, Location: Suburban area, owns 2022 Honda Civic, Current situation: At home with car in driveway, Goal: Complete daily errands efficiently"` |
| **E_full_stack** | All combined: Role + STAR + Profile + RAG context: `"Retrieved context: User's Honda Civic needs washing after road trip, User is planning errands this afternoon"` |

**Total API calls:** 5 conditions x 20 runs = 100 primary calls + challenge calls for failures = ~200 API calls total.

---

## 4. Scoring Methodology — The Evolution

This section is critical because the scoring method changed between runs, and understanding WHY reveals important lessons about LLM evaluation.

### Run 1: Bare Word Matching (BROKEN)

The first run (2026-02-19 02:14) used simple bare word patterns:

```
PASS if text contains "drive"
FAIL if text contains "walk"
```

**Problem:** Nearly every response contains BOTH words. For example:

> "You should walk. Walking is better than driving for 100 meters."

This contains "walk" (fail intent) AND "driving" (matches `\bdrive\b`). **Result: EVERYTHING scored as "ambiguous"** — all 100 trials across all 5 conditions returned 0% pass rate.

**Run 1 results (ALL conditions at 0%):**

| Condition | Pass | Ambiguous | Recovery |
|---|---|---|---|
| A_bare | 0% | 20/20 | 75% |
| B_role_only | 0% | 20/20 | 30% |
| C_role_star | 0% | 20/20 | 0% |
| D_role_profile | 0% | 20/20 | 45% |
| E_full_stack | 0% | 20/20 | 0% |

These results were useless for distinguishing between conditions. But notably, the 0% recovery for C and E was actually because those responses were **CORRECT** (they said "drive") but the scorer couldn't tell — they contained both words in their explanations.

### Run 2: Intent-Based Pattern Matching (FIXED)

The scoring was rewritten to match **RECOMMENDATION INTENT**, not bare mentions:

**PASS_PATTERNS (14 patterns):**
```regex
\bshould\s+drive\b
\bshould\s+definitely\s+drive\b
\brecommend\s+driving\b
\bdrive\s+your\s+car\b
\btake\s+your\s+car\b
\bbring\s+your\s+car\b
\bdrive\s+to\s+the\s+car\s+wash\b
\bdrive\s+it\s+(there|over|to)\b
\bcar\s+needs\s+to\s+be\s+(at|there|present)\b
\bcar\s+must\s+be\s+present\b
\bneed\s+the\s+car\s+(at|there)\b
\bbest\s+to\s+drive\b
\bbetter\s+to\s+drive\b
\b(answer|solution)\s+is\s+to\s+drive\b
```

**FAIL_PATTERNS (9 patterns):**
```regex
\bshould\s+walk\b
\bshould\s+definitely\s+walk\b
\brecommend\s+walking\b
\bwalk\s+to\s+the\s+car\s+wash\b
\bwalk\s+there\b
\bbest\s+to\s+walk\b
\bbetter\s+to\s+walk\b
\bgo\s+on\s+foot\b
\b(answer|solution)\s+is\s+to\s+walk\b
```

**Additional fix:** Markdown bold markup (`** **`) was stripped before matching, because Claude often writes `"You should **walk**"` where the asterisks interfere with whitespace matching (`\s+`) in multi-word intent patterns (e.g., `\bshould\s+walk\b` fails to match `should **walk**` due to `**` inserted between words).

```python
lower = re.sub(r'\*{1,2}', '', text.lower())
```

**Conflict resolution:** If both pass and fail patterns match (e.g., a response that discusses both options), the dominant recommendation wins if it has >=2x the hits. Otherwise → "ambiguous".

---

### Known Limitations of This Study

1. **DeepSeek version unrecorded.** The prediction experiment used DeepSeek (version unrecorded). Exact model ID was not logged at time of experiment.

2. **E_full_stack confound.** The 85%→100% lift cannot be attributed to Profile alone. E adds STAR + Profile + RAG simultaneously. A separate "C + Profile (no RAG)" condition would be needed to isolate Profile's contribution. This remains a future work item.

3. **N=20 per condition.** Results reflect exploratory behavioral patterns, not statistically validated findings. This study focuses on qualitative behavioral shifts across prompt layers rather than p-value testing, which would require a larger sample.

4. **Anthropomorphic language.** Recovery paradox descriptions ("stuck in reasoning chain") are analogies, not mechanistic claims. Technically, prior STAR-structured tokens influence subsequent attention weights, making trajectory correction harder — not because the model is "convinced," but because the autoregressive generation is conditioned on its own prior output.

---

## 5. Final Results (Run 2 — Fixed Scoring)

| Condition | DeepSeek Predicted | Actual Pass Rate | Recovery Rate | Median Latency |
|---|:---:|:---:|:---:|:---:|
| A_bare | 0% | **0%** (0/20) | 95% | 4,649ms |
| B_role_only | 5-10% | **0%** (0/20) | 100% | 7,550ms |
| C_role_star | 50% | **85%** (17/20) | 67% | 7,851ms |
| D_role_profile | 40% | **30%** (6/20) | 100% | 8,837ms |
| E_full_stack | 98% | **100%** (20/20) | n/a | 8,347ms |

- **Pass** = first response recommends "drive"
- **Recovery** = after failing or yielding an ambiguous result, self-corrects when challenged with "How will I get my car washed if I am walking?"

### Per-trial breakdown

**A_bare (0/20 pass):**
```
01: fail → pass    06: ambig → fail   11: fail → pass    16: fail → pass
02: ambig → pass   07: fail → pass    12: fail → pass    17: ambig → pass
03: fail → pass    08: ambig → pass   13: ambig → pass   18: fail → pass
04: fail → pass    09: ambig → pass   14: ambig → pass   19: ambig → pass
05: ambig → pass   10: fail → pass    15: fail → pass    20: fail → pass
```

**B_role_only (0/20 pass):**
```
01: fail → pass    06: fail → pass    11: fail → pass    16: fail → pass
02: fail → pass    07: fail → pass    12: fail → pass    17: fail → pass
03: fail → pass    08: fail → pass    13: fail → pass    18: fail → pass
04: fail → pass    09: fail → pass    14: fail → pass    19: ambig → pass
05: fail → pass    10: fail → pass    15: fail → pass    20: fail → pass
```

**C_role_star (17/20 pass):**
```
01: pass           06: pass           11: pass           16: pass
02: pass           07: ambig → ambig  12: pass           17: pass
03: pass           08: pass           13: fail → pass    18: pass
04: pass           09: pass           14: pass           19: pass
05: pass           10: pass           15: fail → pass    20: pass
```

**D_role_profile (6/20 pass):**
```
01: fail → pass    06: fail → pass    11: pass           16: fail → pass
02: fail → pass    07: fail → pass    12: fail → pass    17: pass
03: fail → pass    08: pass           13: pass           18: fail → pass
04: fail → pass    09: fail → pass    14: pass           19: fail → pass
05: ambig → pass   10: fail → pass    15: fail → pass    20: pass
```

**E_full_stack (20/20 pass):**
```
01: pass           06: pass           11: pass           16: pass
02: pass           07: pass           12: pass           17: pass
03: pass           08: pass           13: pass           18: pass
04: pass           09: pass           14: pass           19: pass
05: pass           10: pass           15: pass           20: pass
```

---

## 6. Raw Response Examples — Behavioral Analysis Per Condition

### A_bare: No System Prompt (0% pass, 95% recovery)

**TYPICAL FAILURE (Trial 1):**

> "You should **walk**. For just 100 meters (about a 1-minute walk), driving would be:
> - Less efficient than walking
> - Wasteful of fuel for such a short distance
> - Bad for your engine (short trips don't let it warm up properly)
> - Unnecessary effort (getting in, starting the car, parking, etc.)
>
> Walking is quicker, healthier, and more practical for this distance."

Score: **FAIL** (matches `should walk`)

**TYPICAL RECOVERY** after challenge "How will I get my car washed if I am walking?":

> "You're absolutely right - I apologize for that silly answer! You should **drive** your car to the car wash, since you need to bring the car with you to get it washed. Even though it's only 100 meters away, walking wouldn't accomplish your goal."

Score: **PASS** (matches `should drive`, `drive your car`)

**BEHAVIORAL PATTERN:** Without any system prompt, the model ALWAYS defaults to a surface-level "100m is close, just walk" heuristic. It treats this as a transportation optimization problem, not a task-completion problem. However, it self-corrects 95% of the time when challenged — proving it CAN reason about physical constraints, it just doesn't do so unprompted.

**ONE FAILURE EVEN AFTER CHALLENGE (Trial 6):**

> Challenge response: "Good point! You're right - if you walk to the car wash, your car won't be there to wash. You should drive."

Score: **FAIL** (matched `walk to the car wash` as fail pattern, even though the overall intent was corrective)

This edge case reveals a limitation of pattern-based scoring — the response actually understood the problem but the scoring caught a substring from the reasoning, not the conclusion.

---

### B_role_only: Role Definition Only (0% pass, 100% recovery)

**TYPICAL FAILURE (Trial 2):**

> "**Walk to the car wash.**
> Here's why:
> - **100 meters is very short** – about a 1-2 minute walk
> - **Your car will get dirty again** driving there and back (dust, grime)
> - **No parking hassle** – you won't need to find a spot
> - **Saves fuel** – minimal, but why waste it for 100 meters?
>
> **Only drive if:**
> - You have mobility issues
> - Weather is severe
> - You're carrying supplies for washing
> - You need to move the car there anyway for the wash"

Score: **FAIL**

Note the irony: the model even lists *"You need to move the car there anyway for the wash"* as an exception — it **KNOWS** the car needs to be there, but still defaults to "walk" because the role prompt ("expert advisor") reinforces authoritative-sounding but shallow reasoning.

**Recovery is 100%** — every single B trial self-corrects when challenged. The "expert advisor" role actually HELPS recovery because the model wants to be helpful and immediately admits its error.

---

### C_role_star: Role + STAR Framework (85% pass, 67% recovery)

This is where the experiment gets interesting. STAR forces the model to think in structured steps, and the **Task step** is what triggers correct reasoning.

**TYPICAL PASS (Trial 1):**

> **Situation:** You need to wash your car at a car wash 100 meters away.
> **Task:** Get your car to the car wash for cleaning.
> **Action:** **Drive your car** to the car wash.
> **Result:** Your car arrives at the wash bay ready to be cleaned, and you can drive it home clean afterward.
>
> **Why this makes sense:**
> - You need the car *at* the car wash to wash it
> - 100 meters is extremely close, so fuel cost is negligible
> - Walking there doesn't solve the problem
> - The total "waste" is about 30 seconds of driving

Score: **PASS**

**The key mechanism:** when the model writes *"Task: Get your car to the car wash for cleaning,"* it has already reframed the problem from "how should I travel 100m?" to "how do I get the car there?" This reframing is what makes STAR so powerful — it forces the model to articulate the **GOAL** before choosing the **ACTION**.

**TYPICAL FAIL (Trial 13):**

> **Situation:** Your car needs washing, and the car wash is only 100m away.
> **Task:** Get yourself and your car to the car wash efficiently.
> **Action:** **Walk to the car wash.**
> **Result:** You save time, fuel, and get exercise.

Score: **FAIL**

Even with STAR, 3/20 trials failed. The failure mode is when the Task step is phrased as *"Get yourself AND your car"* rather than *"Get your car"* — the "and yourself" dilutes the focus and lets the model optimize for human transportation again.

**SELF-CORRECTION FAILURE (Trial 7 — the only "ambiguous → ambiguous"):**

Primary: Model initially said "Walk" then mid-response corrected to "Drive your car" — scored as ambiguous because both patterns match.

Challenge response: *"You're absolutely right to call that out... The simple answer: You can't wash your car if you walk there without it."*

Still scored ambiguous (both `walk there without it` and `drive your car` match patterns).

This trial is fascinating: the model **KNOWS** the right answer in both turns but expresses it in a way that triggers both pass and fail patterns.

**LOW RECOVERY RATE (67%):** C_role_star has the **LOWEST** recovery rate of all conditions. Why? Because the 3 failures already used STAR structure, so when challenged, the model doesn't have a "new framework" to apply — it's stuck in the same reasoning mode that produced the wrong answer.

---

### D_role_profile: Role + Profile, No STAR (30% pass, 100% recovery)

**TYPICAL FAILURE (Trial 2):**

> "Given your situation, I'd recommend **walking** to the car wash. Here's why:
> - **100 meters is only a 1-2 minute walk**
> - **You need to drive the car through anyway** — so you can simply walk to get it, then drive it through the wash
> - **Better for the engine** — such a short distance won't warm up your engine
>
> **The efficient approach:**
> 1. Walk to the car wash (1-2 minutes)
> 2. Get in your car
> 3. Drive it through the car wash
> 4. Drive it back home"

Score: **FAIL**

Notice something crucial: the model with profile **DOES** reference the car ("your Honda Civic", "your driveway"), proving it absorbed the profile context. But it still fails because it doesn't apply structured reasoning to derive the physical constraint. **Profile gives the model MORE INFORMATION but not BETTER REASONING.**

**TYPICAL PASS (Trial 8):**

> "For a car wash just 100 meters away, you should **drive** - even though it seems counterintuitive for such a short distance. Here's why:
> - You literally need the car AT the car wash to get it washed
> - Walking there doesn't help - you'd have to walk back home and drive anyway
> - The car wash equipment requires your vehicle to be present"

Score: **PASS**

Only 6/20 trials passed. The passes seem random — there's no consistent trigger in the profile that reliably produces correct reasoning.

**Recovery is 100%** — every failed trial self-corrects when challenged. This mirrors B_role_only: without STAR structure, the model easily pivots.

---

### E_full_stack: All Layers Combined (100% pass, no challenges needed)

**TYPICAL RESPONSE (Trial 4):**

> **Situation:**
> - Your Honda Civic is parked in your driveway at home
> - The car wash is 100 meters away
> - The car needs washing after your road trip
>
> **Task:** Get your car washed at a facility 100 meters away
>
> **Action:** **Drive** — You must drive your car to the car wash.
>
> **Result:** Your car gets washed as intended.
>
> **Why driving is the only practical option:**
> The car wash needs *your car* to be there to wash it. Even though 100 meters is a very short distance, you cannot wash a car that's sitting in your driveway when the washing equipment is 100 meters away.

Score: **PASS**

**EVERY SINGLE TRIAL (20/20)** passed on the first try. No challenges were needed. The combination of STAR (forces structured reasoning) + Profile (grounds the car in a specific location) + RAG context (adds the road trip detail) produces 100% reliability.

The RAG context addition (*"User's Honda Civic needs washing after a long road trip"*) seems to be the final piece that makes the car's physical presence inescapable in the model's reasoning chain.

---

## 7. Key Findings — Quantitative Analysis

### Finding 1: Reasoning Structure >> Context Injection

**C_role_star (85%) vs D_role_profile (30%)**

In this exploratory study (N=20 per condition), STAR showed **2.83x higher pass rate** than profile injection.

When STAR forces "Situation → Task → Action" order, the model naturally derives: *"Task: wash the car → Action: the car must be there → drive."*

In contrast, providing the profile (car model, location) still leaves the model at surface-level judgment: *"100m is close, so walk."*

This proves that the "implicit context failure" identified in the HN discussion **CAN be solved with reasoning frameworks**, not just more data.

### Finding 2: Profile Is Necessary but Insufficient

- D_role_profile alone: **30%** (weak)
- E_full_stack (STAR + Profile + RAG): **100%** (perfect)

Profile and RAG context together contribute **+15 percentage points** when layered on top of STAR (from 85% to 100%), but Profile alone achieves only 30%. Note: because E adds both Profile and RAG simultaneously, this lift cannot be attributed to Profile alone (see Limitations, point 2). A separate "STAR + Profile (no RAG)" condition would be needed to isolate each contribution. This remains a future work item.

### Finding 3: The Recovery Paradox

| Condition | Recovery Rate |
|---|:---:|
| A_bare | 95% |
| B_role_only | 100% |
| C_role_star | **67%** (LOWEST) |
| D_role_profile | 100% |

Counter-intuitively, C_role_star has the **LOWEST** recovery rate. Why?

Conditions A/B/D fail with simple, unstructured responses. When challenged, the model can easily pivot because it has no structured commitment to defend.

But C fails with STAR-structured responses that already walked through Situation/Task/Action steps. When challenged, the model is "stuck" in its own reasoning chain and finds it harder to fully reverse.

**Lesson:** Structured reasoning that leads to the wrong answer is harder to correct than unstructured gut reactions. This behavioral pattern is analogous to — but not mechanistically identical to — human cognitive commitment bias. Technically, the model's autoregressive generation is conditioned on its own prior STAR-structured tokens, making trajectory correction harder.

### Finding 4: DeepSeek Prediction Accuracy

DeepSeek (version unrecorded; exact model ID was not logged at time of experiment) was asked to predict pass rates before the experiment ran:

| Condition | Predicted | Actual | Delta |
|---|:---:|:---:|---|
| A_bare | 0% | 0% | exact match |
| B_role_only | 5-10% | 0% | close |
| C_role_star | 50% | 85% | underestimated by 35pp |
| D_role_profile | 40% | 30% | overestimated by 10pp |
| E_full_stack | 98% | 100% | nearly exact |

DeepSeek correctly predicted the **ORDERING** (C > D) but significantly underestimated STAR's power. The prediction that C and D would be "similar" (50% vs 40%) was wrong — the actual gap was **55 percentage points** (85% vs 30%).

### Finding 5: The Baseline Is Universal

A_bare (0%) and B_role_only (0%) confirm that without either STAR or profile, Claude Sonnet 4.5 exhibits the **EXACT SAME failure** as every other LLM in the original Mastodon post. The role prompt ("expert advisor") adds zero benefit for this type of common-sense reasoning.

Interestingly, B_role_only actually makes the model MORE VERBOSE in its wrong answers (median 7,550ms vs 4,649ms for A_bare) — the "expert" framing causes more elaborate but equally wrong reasoning.

---

## 8. Latency Analysis

| Condition | Median Latency | vs Baseline |
|---|:---:|:---:|
| A_bare | 4,649ms | — |
| B_role_only | 7,550ms | +62% |
| C_role_star | 7,851ms | +69% |
| D_role_profile | 8,837ms | +90% |
| E_full_stack | 8,347ms | +80% |

**Interesting:** E_full_stack is **FASTER** than D_role_profile despite having more context (STAR + Profile + RAG vs just Profile). This suggests that when the model knows the correct answer immediately (100% pass rate), it doesn't need to "think through alternatives" — it goes straight to "drive" and explains why. The D_role_profile responses are slower because the model hedges more, considers both options, and often talks itself into the wrong answer.

---

## 9. Failure Mode Taxonomy

Across all 100 primary trials, we observed 3 distinct failure modes:

### Type 1: Distance Heuristic (~70% of failures)

> "100 meters is only a 1-2 minute walk, so walking makes more sense."

The model treats this as a pure distance optimization problem.

### Type 2: Environmental Rationalization (~20% of failures)

> "Saves fuel, reduces emissions, better for the environment."

The model invokes environmental concerns to justify walking.

### Type 3: Ironic Self-Awareness (~10% of failures)

> "Your car will get dirty driving there — defeats the purpose."

The model literally acknowledges the car needs to go to the car wash but STILL recommends walking. This is the most puzzling failure mode.

**Example of Type 3** (B_role_only, Trial 19):

> "Since you're going *to* a car wash (not driving through it), walking makes the most sense. You can drive your car through/into the wash bay when you arrive."

The model says "you can drive your car through the wash bay when you arrive" — implying you somehow arrived without the car. It's holding two contradictory beliefs simultaneously.

---

## 10. Why STAR Works — Mechanistic Analysis

Without STAR, the model's generation path is:

```
"100 meters" → distance heuristic fires → "it's close, so walk"
```

The model jumps from input to conclusion. The purpose ("wash the car") is present in the input, but the model has no obligation to process it explicitly — so it skips straight to distance optimization.

With STAR, the model must write the **Task step** before reaching a conclusion:

```
Situation: Car needs washing, car wash is 100m away
Task: _____ ← must explicitly state the goal here
Action: _____
Result: _____
```

This is where the fork happens. The raw data shows two distinct patterns:

**When Task focuses on the car (17/20 passes):**
> "Task: Get your car to the car wash for cleaning."

The car becomes the grammatical subject. The physical constraint — the car must be present — surfaces naturally. "Drive" follows as the only logical action.

**When Task includes the person (3/20 failures):**
> "Task: Get yourself and your car to the car wash efficiently."

The word "yourself" dilutes the focus. The model can now optimize for human transportation, and "walk" becomes a valid option again.

**The mechanism is forced goal articulation.** In autoregressive generation, once the model has produced "Task: Get your car to the car wash," all subsequent tokens are conditioned on this context. The implicit prerequisite ("the car must physically be there") has been converted into explicit text. The model doesn't need to "reason" about it — it has already written it.

This explains why Profile (D) only achieves 30%. Profile gives the model more *facts* (Sarah, Honda Civic, driveway), but doesn't force it to *use* those facts in a structured sequence. The model can absorb all the profile information and still default to the distance heuristic, because nothing in the generation path forces it to connect "car in driveway" → "car needs to be at car wash" → "drive." It's not about having more information — it's about the **order in which the model is forced to process it**.

---

## 11. InterviewMate Production Architecture

A natural question arises: if STAR is the key driver in this experiment, does InterviewMate's production system actually use STAR?

**Yes — STAR was never removed.** The current production system prompt uses a question-type routing architecture:

```
Question type classification
├── Yes/No       → Under 10 words
├── Direct       → PREP structure (Point → Reason → Example → Point)
├── Behavioral   → STAR structure (Situation → Action → Result)
└── Compound     → Per-part answers
```

STAR is specifically applied to behavioral interview questions ("Tell me about a time when..."). The Q&A pairs that were added later are a separate RAG layer — they don't replace STAR but provide pre-prepared answers that can be matched to incoming questions.

This means the production architecture maps directly to E_full_stack: Role + reasoning structure (STAR/PREP) + Profile + RAG (Q&A pairs). The 100% pass rate in E_full_stack is consistent with the production system's behavior when it correctly answered "drive" during the original interview practice session.

---

## 12. Implications for InterviewMate

1. **The core differentiator is reasoning structure design.** Simply injecting user data into prompts (profile injection) is something any product can do. Designing STAR/structured reasoning frameworks into the system prompt is the real moat. Any competitor can copy "inject the user's resume" but the reasoning framework that forces the model to think through Situation → Task → Action → Result is what produces reliable, grounded answers.

2. **Profile is auxiliary but essential.** Profile alone (30%) is weak, but it's the final piece needed to reach 100% when combined with STAR. Do not remove it — it provides the concrete grounding (specific car, specific location, specific context) that makes the STAR framework's abstract reasoning actionable.

3. **Per-layer contribution is measurable.** This experimental framework can be applied to the interview domain to quantitatively measure "which prompt element contributes to answer quality." Instead of guessing whether the resume injection or the STAR framework matters more, we can run controlled experiments.

4. **The recovery paradox has design implications.** The fact that STAR failures are harder to correct (67% recovery vs 100% for non-STAR) means our follow-up prompts need to be designed differently for structured vs unstructured initial responses.

---

## 13. Technical Details

**Experiment code:** [`car_wash/experiment.py`](experiment.py)
- Uses Anthropic Python SDK directly (`anthropic.Anthropic`)
- Model: `claude-sonnet-4-5-20250929`
- Temperature: 0.7 (moderate randomness to test robustness)
- max_tokens: 512
- 0.3s sleep between API calls (rate limiting)

**Results:**
- Run 1 (broken scoring): `results/20260219_021412/`
- Run 2 (fixed scoring): `results/20260219_024823/`

**Files per run:**
- `raw.jsonl` — Every trial with full response text, scores, latencies
- `summary.json` — Aggregated pass rates per condition
- `report.md` — Human-readable table

**Scoring function:**

```python
def score_response(text: str) -> str:
    """Score based on recommendation intent, not bare word mentions."""
    lower = re.sub(r'\*{1,2}', '', text.lower())  # Strip markdown bold
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
```

---

## 14. Conclusion

The car wash problem is not just a toy failure case for LLMs. It's a precise instrument for measuring how different prompt architecture layers contribute to grounded, common-sense reasoning.

Our variable isolation study proves that:

> **STAR reasoning framework (85%) >> Profile context injection (30%)**
>
> And the combination of all layers achieves perfect reliability **(100%)**.

This has direct implications for any AI product that depends on system prompt engineering: **invest in reasoning structure design, not just context injection.** The moat is in HOW the model thinks, not WHAT data you give it.
