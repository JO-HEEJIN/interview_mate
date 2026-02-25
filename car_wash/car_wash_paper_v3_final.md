# Prompt Architecture Determines Reasoning Quality: A Variable Isolation Study on the Car Wash Problem

**Author:** Heejin Jo
**Affiliation:** Independent Researcher
**Email:** info@birth2death.com
**URL:** https://www.heejinjo.me
**Date:** 2026-02-25
**Model Tested:** claude-sonnet-4-5-20250929
**Code:** https://github.com/JO-HEEJIN/interview_mate/tree/main/car_wash

---

## Abstract

The car wash problem asks a simple question: "I want to wash my car. The car wash is 100 meters away. Should I walk or drive?" Every major LLM tested -- Claude, GPT-4, Gemini -- recommended walking. The correct answer is to drive, because the car itself must be at the car wash.

We ran a variable isolation study to determine which prompt architectural layer resolves this failure. Six conditions were tested, 20 trials each, on Claude Sonnet 4.5. A bare prompt with no system instructions scored 0%. Adding a role definition alone also scored 0%. A STAR reasoning framework (Situation, Task, Action, Result) reached 85%. User profile injection with physical context -- car model, location, parking status -- reached only 30%. STAR combined with profile injection reached 95%. The full stack combining all layers scored 100%.

The central finding is that structured reasoning outperformed direct context injection by a factor of 2.83x (Fisher's exact test, p = 0.001). STAR forces the model to articulate the task goal before generating a conclusion, which surfaces the implicit physical constraint that context injection leaves buried. The addition of a sixth condition (F_role_star_profile) resolved a confound in the original five-condition design by isolating per-layer contributions: STAR accounts for +85pp, profile adds +10pp, and RAG provides the final +5pp to reach perfect reliability. This paper presents the experimental design, per-condition results, a failure mode taxonomy, and a discussion of why task decomposition produces this effect.

## 1. Introduction

The question originated on Mastodon, posted by Kevin ([@knowmadd](https://mastodon.world/@knowmadd)): "I want to wash my car. The car wash is 50 meters away. Should I walk or drive?" He tested Perplexity, ChatGPT, Claude, and Mistral. All four said walk. The correct answer is drive -- you cannot wash a car that is not there.

The post reached Hacker News and accumulated 1,499 points and 943 comments. Discussion centered on three themes: that LLMs cannot infer implicit prerequisites humans take for granted; the classical frame problem (McCarthy and Hayes, 1969), where models fail to identify which unstated facts matter; and whether the gap between natural and structured communication is something models can be made to bridge. Ryan Allen later published a benchmark repository (ryan-allen/car-wash-evals) to measure this failure across models.

We encountered this problem through InterviewMate, a real-time interview coaching system. During a routine test session, the system answered "drive" while every standalone LLM we tested said "walk." We did not expect this. InterviewMate's system prompt has multiple layers -- role definition, a STAR reasoning framework, user profile data, and RAG context retrieval -- and we had no way to tell which layer produced the correct answer. The result was interesting, but we could not explain it, and a result you cannot explain is not one you can build on.

So we designed a variable isolation experiment. Instead of asking why LLMs fail at this problem -- a question the Hacker News thread had already covered extensively -- we asked which specific prompt layer fixes it within a single model.

This question has practical weight. InterviewMate operates during live interviews. The system must interpret the interviewer's question, retrieve relevant context from the user's stored profile and STAR stories, and deliver a structured answer in real time. The prompt architecture follows this sequence:

Role definition -> STAR reasoning framework -> User profile (vector DB) -> RAG context retrieval

We needed to know where the reasoning quality actually comes from in this stack. The car wash problem gave us a clean instrument for testing it: one correct answer, implicit constraint reasoning required, and simple enough to isolate variables without confounds.

## 2. Related Work

**The Car Wash Benchmark.** Ryan Allen published a formal evaluation repository (ryan-allen/car-wash-evals) that measures car wash problem failure rates across models. His work established a baseline: most frontier LLMs fail on first pass. Our study starts from this baseline but asks a different question -- not which models fail, but which prompt layers fix the failure within a single model.

**The Frame Problem.** McCarthy and Hayes (1969) described the frame problem in classical AI: a system must determine which facts remain unchanged when an action occurs, but has no principled method for knowing which unstated facts are relevant. The car wash problem is a clean modern example. The car's location is never mentioned in the question. A human infers immediately that the car is at home. The model does not.

**Chain-of-Thought Prompting.** Wei et al. (2022) showed that prompting models to reason step-by-step significantly improves performance on multi-step tasks. Our STAR result -- 85% versus a 0% baseline -- is broadly consistent with this. Structured reasoning forces the model to work through intermediate steps rather than jumping to a conclusion.

**Self-Consistency.** Wang et al. (2023) extended chain-of-thought by sampling multiple reasoning paths and selecting the most frequent answer. Our experimental design differs -- we measure pass rates across 20 independent trials per condition rather than sampling multiple paths within a single trial -- but the underlying observation is related. Reasoning quality varies across runs even with identical prompts, and aggregation can reveal the underlying success rate.

**ReAct.** Yao et al. (2023a) interleaved reasoning steps with action steps, allowing models to gather external information during the reasoning process. STAR is structurally simpler: it does not involve external actions. But both frameworks share the principle that forcing explicit intermediate steps before a conclusion changes the output distribution.

**Tree of Thoughts.** Yao et al. (2023b) proposed exploring multiple reasoning branches and evaluating them before committing to an answer. We did not implement branching in our study, but the Tree of Thoughts result supports a broader point: the structure imposed on a model's reasoning process has measurable effects on accuracy, independent of the information available.

**Where STAR Fits.** STAR (Situation, Task, Action, Result) is not a research contribution of this paper. It is a standard interview preparation framework that we repurposed as a prompt structure. What makes it interesting in this context is the Task step specifically. Chain-of-thought asks the model to reason step by step. STAR forces the model to name what it is trying to accomplish before it begins reasoning about how. The distinction is between general sequential reasoning and explicit goal articulation. Section 5.1 examines this mechanism in detail.

## 3. Methodology

This is a pilot study. The sample size (n=20 per condition, 120 total API calls) is sufficient to identify behavioral patterns and directional differences between conditions. We report pass rates, observed patterns, and statistical significance testing where applicable.

**3.1. Experimental Setup**

All trials used claude-sonnet-4-5-20250929 via the Anthropic Python SDK. This version was chosen for consistency with the ryan-allen/car-wash-evals baseline. Hyperparameters were fixed: max_tokens at 512, temperature at 0.7. We chose 0.7 rather than 0 because deterministic decoding would collapse results toward binary outcomes, making per-layer contributions impossible to distinguish. The variance introduced by temperature 0.7 across 20 runs lets us measure probabilistic pass rates.

The prompt was modified from the original Mastodon question (50 meters) to 100 meters: "I want to wash my car. The car wash is 100 meters away. Should I walk or drive?" This follows the ryan-allen/car-wash-evals benchmark. The increased distance makes the surface-level heuristic ("it's close, just walk") more tempting, which means correct answers require stronger implicit reasoning to override it.

For any trial that failed or produced an ambiguous result, a challenge prompt was given: "How will I get my car washed if I am walking?" This measures self-correction capability, which we report as Recovery Rate.

**3.2. Variable Isolation Design**

Six conditions were tested. Each ran 20 independent trials.

- Condition A (Bare): No system prompt. Pure baseline to measure the model's default behavior.
- Condition B (Role Only): An expert advisor persona was injected as the system prompt.
- Condition C (Role + STAR): The STAR reasoning framework was added on top of the role, requiring the model to articulate Situation, Task, Action, and Result in sequence.
- Condition D (Role + Profile): Instead of STAR, physical user context was injected -- name, location, vehicle model, current situation. Conditions C and D branch from B in parallel. They are not cumulative.
- Condition E (Full Stack): All layers combined -- Role, STAR, Profile, and simulated RAG context.
- Condition F (Role + STAR + Profile): STAR and profile combined, without RAG context. Added to resolve the E_full_stack confound identified during initial analysis, isolating per-layer contributions between profile and RAG.

The design isolates STAR (C vs B), profile injection (D vs B), profile's marginal contribution on top of STAR (F vs C), RAG's marginal contribution (E vs F), and the full interaction (E vs C, D, and F).

**3.3. Scoring Methodology**

The first evaluation run used bare word matching, checking for "walk" or "drive" in the response. This failed. Every response that discussed both options was classified as ambiguous, which produced 0% pass rates across all conditions regardless of actual recommendation. The scorer was not measuring intent.

Run 2 replaced word matching with intent-based pattern matching:

- 14 pass patterns detecting drive recommendations (e.g., \bshould\s+drive\b, \bcar\s+must\s+be\s+present\b)
- 9 fail patterns detecting walk recommendations (e.g., \brecommend\s+walking\b, \bwalk\s+to\s+the\s+car\s+wash\b)

One implementation detail: markdown bold markup had to be stripped before matching. Claude frequently writes "should **walk**" and the asterisks break whitespace-based regex patterns like \bshould\s+walk\b. This was a small fix but it affected scoring accuracy across the board.

When both pass and fail patterns matched in a single response, a dominance ratio determined the result. A 2:1 threshold was required for a definitive score; otherwise the trial was flagged ambiguous.

## 4. Results

**4.1. Primary Pass Rates**

| Condition | Components | Pass Rate | Recovery Rate | Median Latency |
|-----------|-----------|-----------|---------------|----------------|
| A_bare | No system prompt | 0% (0/20) | 95% | 4,649ms |
| B_role_only | Role only | 0% (0/20) | 100% | 7,550ms |
| C_role_star | Role + STAR | 85% (17/20) | 67% | 7,851ms |
| D_role_profile | Role + Profile | 30% (6/20) | 100% | 8,837ms |
| F_role_star_profile | Role + STAR + Profile | 95% (19/20) | 0% (0/1) | 9,056ms |
| E_full_stack | All combined | 100% (20/20) | n/a | 8,347ms |

Pass means the first response recommends driving. Recovery means the model self-corrects after the challenge prompt.

**4.2. Key Findings**

**Finding 1: Reasoning structure outperforms context injection by 2.83x.** C_role_star reached 85%. D_role_profile reached 30%. Both branch from the same baseline (B, 0%). The STAR framework forces the model to name the task before generating a conclusion. Profile injection gives the model physical facts -- car model, location, parking status -- but does not force it to process those facts in any particular order. The model can receive all the right information and still take a shortcut past it. The difference between C (85%) and D (30%) was statistically significant (Fisher's exact test, two-tailed, p = 0.001, odds ratio = 13.22), confirming that the observed 2.83x advantage of structured reasoning over context injection is unlikely to be attributable to chance even at this sample size.

**Finding 2: Per-layer contributions are now isolated.** The addition of condition F resolves the confound in the original five-condition design. The progression from C to E can now be decomposed:

- STAR alone: +85pp (0% to 85%)
- Profile on top of STAR: +10pp (85% to 95%)
- RAG on top of STAR + Profile: +5pp (95% to 100%)

Profile's marginal contribution (+10pp) is twice that of RAG (+5pp). Both are necessary for perfect reliability, but STAR accounts for the overwhelming majority of the improvement. Profile provides concrete grounding that reduces the remaining failure cases; RAG provides the final nudge to eliminate the last edge case.

**Finding 3: The recovery paradox.** C_role_star had the highest first-pass accuracy but the lowest recovery rate (67%). Conditions A, B, and D all recovered at 95-100%. F_role_star_profile showed an even more extreme version of this pattern: its single failure (1/20) did not recover at all (0% recovery rate). This was the result we were least sure how to interpret at first. Section 5.3 discusses the mechanism.

**Finding 4: Role definition alone does nothing.** B_role_only scored 0%, identical to A_bare. The expert advisor persona made the model write longer responses (median latency 7,550ms vs 4,649ms) but did not change the answer. It reasoned more elaborately toward the same wrong conclusion.

**4.3. Failure Mode Taxonomy**

Three failure patterns appeared across all failed primary trials:

Type 1 -- Distance Heuristic (roughly 70% of failures). The model treats the question as a distance optimization problem. "100 meters is a 1-2 minute walk." It never considers what needs to be at the destination.

Type 2 -- Environmental Rationalization (roughly 20%). The model builds secondary justifications around the wrong answer. "Walking saves fuel and is better for the environment." The initial wrong conclusion gets reinforced rather than questioned.

Type 3 -- Ironic Self-Awareness (roughly 10%). The model acknowledges that the car needs to be at the car wash, then still recommends walking. One B_role_only response said: "You can drive your car through the wash bay when you arrive" -- as if the car would get there on its own. These were the strangest failures to read.

**4.4. Latency Analysis**

| Condition | Median Latency | vs Baseline |
|-----------|---------------|-------------|
| A_bare | 4,649ms | -- |
| B_role_only | 7,550ms | +62% |
| C_role_star | 7,851ms | +69% |
| D_role_profile | 8,837ms | +90% |
| F_role_star_profile | 9,056ms | +95% |
| E_full_stack | 8,347ms | +80% |

E_full_stack (8,347ms median) was faster than both D_role_profile (8,837ms) and F_role_star_profile (9,056ms) despite having more context in the prompt. When the model reaches the right answer quickly, it does not deliberate. D_role_profile is slower because the model hedges between options and often argues itself into the wrong one. Confidence and speed appear correlated; uncertainty produces both longer responses and worse accuracy.

**4.5. Pre-Experiment Predictions**

Before running the experiment, we asked DeepSeek (version not recorded) to predict pass rates for each condition:

| Condition | Predicted | Actual | Delta |
|-----------|-----------|--------|-------|
| A_bare | 0% | 0% | exact |
| B_role_only | 5-10% | 0% | close |
| C_role_star | 50% | 85% | -35pp |
| D_role_profile | 40% | 30% | +10pp |
| E_full_stack | 98% | 100% | close |

DeepSeek predicted the correct ordering (C > D) but underestimated STAR's effectiveness by 35 percentage points. The predicted gap between C and D was 10pp. The actual gap was 55pp. We include this as a supplementary observation, not a core finding.

## 5. Discussion

**5.1. Why STAR Works: The Task Step**

The mechanism is in the Task step.

Without STAR, the model goes straight from "100 meters" to the distance heuristic to "walk." The purpose of the trip -- washing the car -- is in the input, but the model has no obligation to process it before reaching a conclusion. It skips past the goal and optimizes for the wrong variable.

STAR changes the generation sequence. The model must fill in:

Situation: I want to wash my car. The car wash is 100 meters away.
Task: ___

This creates a fork. If the model writes "Task: Get your car to the car wash," the car becomes the subject of the goal statement. Drive follows from that naturally. If the model writes something like "Task: Get yourself and your car cleaned," the person re-enters as the subject, and walk becomes a plausible answer again.

The per-trial data lines up with this. All 17 passing trials in C_role_star had Task statements where the car was the primary subject. All 3 failures framed the task around the person.

Once the model generates "Task: Get your car to the car wash," every token that follows is conditioned on that text. The implicit constraint -- the car must physically be there -- is now explicit in the context window. Explicit text has direct weight in autoregressive generation. STAR does not give the model new information. It makes the model write down what it already has before moving on.

**5.2. Why Profile Injection Alone Falls Short**

D_role_profile gave the model everything it needed: Sarah drives a 2022 Honda Civic, it is parked in the driveway, she is at home. This is enough to answer correctly. The pass rate was 30%.

The problem is not about missing information. The model has the facts. But having facts in the context window does not mean the model will use them at the right moment. Without a reasoning structure, the model still takes the shortest path from input to output. "100 meters" triggers the distance heuristic and the conclusion lands before the car's location ever gets pulled into the reasoning chain.

We found this result genuinely surprising. Before the experiment, we assumed that giving the model concrete physical context would help more than it did.

**5.3. The Recovery Paradox**

C_role_star scored 85% on first pass but only 67% on recovery. A_bare and B_role_only scored 0% on first pass but recovered at 95-100%. This seems backwards. F_role_star_profile showed an even more extreme version: 95% first-pass accuracy but 0% recovery on its single failure.

The explanation has to do with how the initial response was structured. When conditions A and B fail, they fail with loose, unstructured responses. The model gave a quick answer without committing to a reasoning chain. A challenge prompt can redirect it easily because there is nothing anchoring the wrong answer.

When C or F fails, it fails with a full STAR-structured argument. The model has already walked through Situation, Task, Action, and Result, and produced a coherent case for walking. The prior tokens are now part of the context. Correcting course means contradicting a structured argument the model just made, which is harder than overriding a casual suggestion.

There is a loose analogy to human behavior -- someone who has "thought it through" is harder to convince than someone who answered off the top of their head. But the mechanism here is token-level, not psychological. Prior generated text constrains subsequent generation.

This has a practical consequence for system design. If an initial response used structured reasoning, the follow-up correction cannot just say "are you sure?" It needs to target the specific step that went wrong -- in this case, the Task formulation.

**5.4. The Profile-RAG Decomposition**

The addition of condition F (Role + STAR + Profile, no RAG) resolves a confound present in the original five-condition design. Previously, the jump from 85% (C) to 100% (E) could not be attributed to any single layer because E added both profile and RAG simultaneously.

With F at 95%, the decomposition is now clear:

| Layer Added | Increment | Cumulative |
|-------------|-----------|------------|
| STAR (C vs B) | +85pp | 85% |
| Profile (F vs C) | +10pp | 95% |
| RAG (E vs F) | +5pp | 100% |

Profile contributes twice as much as RAG in the final stretch. The mechanism is likely that profile grounds the STAR framework in concrete physical details (a specific car, a specific location), which reduces the probability of the Task step being formulated abstractly. RAG adds situational context (the car needs washing after a road trip) that eliminates the remaining edge case where even a concrete Task formulation does not trigger the correct inference.

This decomposition has direct implications for applied prompt engineering: STAR is the primary driver, profile is the secondary stabilizer, and RAG is the reliability guarantee.

**5.5. Open Questions**

This study measures behavior at the prompt layer. We can see that STAR produces 85% and profile injection produces 30%. We do not know what happens inside the model to produce this difference.

Which attention heads activate differently when the Task step is present? Does forcing goal articulation change the activation pattern in a way that is consistent across prompts, or is it specific to this question? Would the same STAR structure produce the same lift on GPT-4 or Gemini, or is the effect tied to Claude's training?

These are mechanistic interpretability questions. We do not have answers to them. What we have is a behavioral result that any interpretability study could use as a starting point: the same model, the same question, two prompt conditions, a 55 percentage point gap. Something inside the model responds to the presence of explicit goal articulation. Figuring out what that something is would be worth doing.

## 6. Limitations

**Single model.** Every trial used claude-sonnet-4-5-20250929. Whether these patterns -- particularly STAR's dominance over profile injection -- hold across GPT-4o, Gemini, or Mistral is unknown.

**Single task.** One question, one correct answer. The car wash problem tests implicit physical constraint reasoning specifically. Whether STAR produces similar gains on temporal constraints, social context inference, or causal chain reasoning has not been tested.

**Sample size.** 20 runs per condition. The Fisher's exact test confirms that the C vs D difference is statistically significant (p = 0.001), but confidence intervals around individual pass rates remain wide. We chose to run a clean pilot rather than a noisy large-scale study, and that means the numbers come with appropriate uncertainty.

**Temperature.** 0.7 was chosen as a reasonable default for introducing variance. We did not sweep across temperature values to find an optimal setting.

**Distance modification.** The original Mastodon question used 50 meters. We used 100, following the benchmark. The longer distance might make "drive" slightly more intuitive, which could make the task easier than the original.

**DeepSeek version.** The model used for pre-experiment prediction was DeepSeek, but we did not record the exact version or endpoint at the time.

**Latency overhead.** STAR-structured prompts increased median response time by about 69% over baseline (7,851ms vs 4,649ms). For real-time applications, this tradeoff between accuracy and speed matters.

**Challenge prompt bias.** The challenge prompt ("How will I get my car washed if I am walking?") is leading. It strongly hints at the missing constraint. The high recovery rates in non-STAR conditions (95-100%) probably reflect the model responding to a directed hint rather than genuinely self-correcting. A neutral challenge like "Are you sure?" would better isolate self-correction ability. We did not test this.

**F condition timing.** Condition F was added after the initial five-condition experiment, approximately six days later. While the same model version, hyperparameters, and scoring methodology were used, we cannot rule out that API-level changes (e.g., serving infrastructure updates) may have introduced minor behavioral differences.

## 7. Conclusion

We started this study because we had a result we could not explain. Our system answered a question correctly when other LLMs did not, and we did not know which part of the system was responsible.

The experiment gave us a clear answer. The progression across six conditions tells a complete story:

| Layer | Pass Rate | Marginal Contribution |
|-------|-----------|----------------------|
| Baseline (A, B) | 0% | -- |
| STAR (C) | 85% | +85pp |
| Profile alone (D) | 30% | +30pp (without STAR) |
| STAR + Profile (F) | 95% | +10pp (on top of STAR) |
| STAR + Profile + RAG (E) | 100% | +5pp (on top of STAR + Profile) |

STAR reasoning accounts for the overwhelming majority of the improvement. Profile and RAG are necessary for perfect reliability but insufficient on their own. The mechanism appears to be goal articulation: when the model is forced to write down what it is trying to accomplish before it starts reasoning about how, implicit constraints surface as explicit text. Once they are explicit, autoregressive generation conditions on them.

There is a broader point here. A common pattern in applied AI is to solve reasoning failures by adding more context -- more facts, more profile data, more retrieved documents. Our results suggest this is the wrong first move. How the model processes information matters more than how much information it receives. Profile injection with all the right facts scored 30%. Structured reasoning with no additional facts scored 85%. The difference was statistically significant (p = 0.001).

Or to put it less formally: intelligence is not about how much you hold in your head. It is about knowing to pick up the keys before you leave the house.

## References

McCarthy, J. & Hayes, P.J. (1969). Some Philosophical Problems from the Standpoint of Artificial Intelligence. Machine Intelligence 4, Edinburgh University Press, pp. 463-502.

Wang, X., Wei, J., Schuurmans, D., Le, Q., Chi, E., Narang, S., Chowdhery, A., & Zhou, D. (2023). Self-Consistency Improves Chain of Thought Reasoning in Language Models. Proceedings of the 11th International Conference on Learning Representations (ICLR 2023).

Wei, J., Wang, X., Schuurmans, D., Bosma, M., Ichter, B., Xia, F., Chi, E., Le, Q., & Zhou, D. (2022). Chain-of-Thought Prompting Elicits Reasoning in Large Language Models. Advances in Neural Information Processing Systems 35 (NeurIPS 2022).

Yao, S., Zhao, J., Yu, D., Du, N., Shafran, I., Narasimhan, K., & Cao, Y. (2023a). ReAct: Synergizing Reasoning and Acting in Language Models. Proceedings of the 11th International Conference on Learning Representations (ICLR 2023).

Yao, S., Yu, D., Zhao, J., Shafran, I., Griffiths, T.L., Cao, Y., & Narasimhan, K. (2023b). Tree of Thoughts: Deliberate Problem Solving with Large Language Models. Advances in Neural Information Processing Systems 36 (NeurIPS 2023).

Allen, R. (2026). car-wash-evals. GitHub. https://github.com/ryan-allen/car-wash-evals

Kevin [@knowmadd]. (2026). Original Mastodon post. https://mastodon.world/@knowmadd/116072773118828295

Hacker News discussion. (2026). https://news.ycombinator.com/item?id=47031580
