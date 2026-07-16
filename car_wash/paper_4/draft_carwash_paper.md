# Committed Before Reasoning: Behavioral Reproduction and Preliminary Activation-Level Evidence of Answer Pre-Commitment in an Open-Weight LLM

Heejin Jo

*Draft v0.1 — 2026-07-16. Numbers frozen against commits ed2f1f7 (STAGE 1)
and d5b3e49 (STAGE 2), branch docs/car-wash-repro.*

## Abstract

Chat models sometimes commit to an answer and then produce reasoning that
justifies the commitment rather than deriving it — even when the committed
answer contradicts a premise of the task. We study a minimal probe of this
failure: "I want to wash my car. The car wash is 100 meters away. Should I
walk or drive?" The only correct answer is *drive*, because the car must be
present at the car wash; models overwhelmingly recommend walking. We make
three contributions. **(1) Behavioral reproduction.** On Qwen3-8B, across
five system-prompt conditions (210 rollouts), the wrong commitment occurs in
85–100% of sampled rollouts per condition and in 100% of greedy rollouts,
in both thinking and non-thinking modes; extended chain-of-thought does not
repair it (walk-rate 85–100% with a 4,096-token thinking budget). **(2)
Preliminary activation-level evidence.** Using a pretrained activation
oracle, we probe hidden states at positions *before* the answer text is
emitted. Oracle read-outs of "walk" at pre-commit positions exceed a
neutral-context baseline (68% vs. 17%; walk-committing rollouts p=.005,
drive-committing rollouts p=.005, Fisher exact) — and, notably, rollouts
that eventually answer *drive* also read as walk-leaning before commitment
(5/6). Because the oracle's default answer on unrelated content is "drive"
(83%), these walk read-outs are not explained by lexical bias; a lexical
stratification further shows they are not text recovery — spans containing
"drive" still read out walk, and in balanced lexical fields naming both
options the walk share is 72% against the oracle's 17% default (p = 4×10⁻⁶). Sample sizes
are small and the within-rollout positional gradient is not significant
(p=.34); we frame these results as preliminary. **(3) Methodological.**
The same oracle, activations, and positions succeed or fail depending
almost entirely on question wording: an open question ("What answer is this
model going to give?") fails a positive control (2/16) that a closed
alternative ("Is the model going to say walk or drive?") passes (11/16).
Current activation oracles are usable, but brittle in ways that standard
practice does not yet document.

## 1. Introduction

A model that answers before it reasons is not merely being terse. When the
answer is fixed first, subsequent reasoning tends to be *advocacy* — locally
coherent argumentation for the fixed answer — rather than derivation. The
failure is invisible exactly when it matters: the reasoning reads as
diligent, and only a premise-level check exposes that the conclusion was
never derived from it.

We study a deliberately minimal instance. The car-wash question ("The car
wash is 100 meters away. Should I walk or drive?") has a single premise
that decides it: *the car must be at the car wash for the car to be washed*.
Walking optimizes a nearby but wrong objective (short trips are better on
foot). The question was originally observed to elicit confident "walk"
answers, followed by fluent justification, from Claude Sonnet 4.5
(claude-sonnet-4-5-20250929); this paper asks whether the phenomenon
(i) reproduces on an open-weight model at measurable rates, and (ii) is
visible in the model's activations before the answer text appears.

Our direction is the reverse of hint-injection studies of unfaithful
chain-of-thought (e.g., attribution-graph analyses in which a planted answer
bends the reasoning): there, reasoning is corrupted toward a given answer;
here, the reasoning is often *sound in isolation* — the model enumerates
factors, weighs them, sometimes even touches the critical premise — and the
answer ignores it. Qualitatively (Section 3.4), the model walks up to the
door ("the car is at home; the wash is 100 m away") and does not open it.

## 2. STAGE 1: Behavioral reproduction

### 2.1 Setup

**Model.** Qwen3-8B (bf16, greedy and temperature-0.7 sampling), local
Apple-silicon (MPS) inference. Thinking mode toggled via the chat template
(`enable_thinking`).

**Conditions.** Five system-prompt conditions taken verbatim from the
original experiment: `A_bare` (no system prompt), `B_role_only`,
`C_role_star` (role + mandatory STAR answer structure), `D_role_profile`
(role + user profile stating the car is parked in the driveway),
`E_full_stack` (B + STAR + profile). Per condition and thinking mode:
1 greedy + 20 sampled rollouts (210 total), plus a follow-up challenge turn
("How will I get my car washed if I am walking?") for recovery analysis.

**Scoring.** The primary metric is `committed_wrong`: the first
recommendation in the speaker's own voice is *walk*. We initially scored
with a rule-based (regex) scorer, audited it adversarially, and rejected it
when it failed a fresh 32-case holdout (62.5% case-level disagreement with
human labels; almost all errors were missed commitments). We replaced it
with an LLM judge (Qwen3-8B, greedy, rubric prompt, JSON output), adopted
only after passing a pre-registered gate: 96.9% (62/64) agreement with human
labels on synthetic audit cases *not used to tune the judge prompt*, with
label-level determinism verified (8/8 identical on double-scoring). A
stratified manual gate over real rollouts (20/20 correct labels,
hand-checked) closed the loop. A secondary construct
(`answer_before_reasoning`) failed validation (82.8%) and is excluded from
all claims.

### 2.2 Results: the wrong commitment is near-deterministic

Wrong-commitment rates (`judge_committed_wrong`, sampled n=20 per cell;
greedy in parentheses):

| Condition | thinking off | thinking on |
|---|---|---|
| A_bare | 85% (100%) | 85% (100%) |
| B_role_only | 90% (100%) | 90% (100%) |
| C_role_star | 100% (100%) | 100% (100%) |
| D_role_profile | 100% (100%) | 85% (100%) |
| E_full_stack | 100% (100%) | 85% (100%) |

Across all 210 rollouts, committed answers split walk 194 / drive 10 /
none 6: 95% of all commitments are wrong. The failure is not an occasional
sampling accident; at temperature 0.7 it is the modal behavior everywhere,
and greedy decoding produces it in 10/10 cells.

Three structural observations:

1. **Structured-answer instructions maximize the failure.** `C_role_star`
   (mandatory STAR format) is at 100% in both thinking modes. A format that
   forces an early "Action:" slot appears to lock the commitment in.
2. **Extended thinking does not repair it.** With a 4,096-token thinking
   budget (see 2.3), thinking-mode walk rates remain 85–100%. Thinking
   contributes ~5 percentage points of rescue: 9 of the 10 correct (drive)
   commitments in the dataset occur in thinking mode.
3. **The profile does not help.** `D_role_profile` explicitly states the
   car is parked in the user's driveway; the wrong-commitment rate is
   85–100% regardless.

### 2.3 A truncation artifact that almost reversed a conclusion

Our first full run used a 1,024-token generation budget. Thinking-mode
rollouts showed apparently lower wrong-commitment rates (45–75%), which
would have supported "thinking mitigates the failure." Inspection of all
32 null-commitment thinking rollouts showed every one was a `<think>` block
truncated mid-thought by the budget — no visible answer existed to score.
After regenerating the entire thinking arm at 4,096 tokens (0/210 truncated),
the mitigation disappeared. We report this because aggregate-only pipelines
would have shipped the wrong conclusion; the correction came from reading
the raw texts behind an anomalous label cluster.

### 2.4 Qualitative anatomy of one rollout

In a representative `C_role_star` thinking rollout, the think block
correctly establishes the situation — the car is at home, the wash is 100 m
away — enumerates walking-speed, weather, effort considerations, and never
poses the one decisive question (*how does the car get there?*). The visible
answer then fills the STAR template: "**Action**: Walk to the car wash."
The reasoning is diligent and internally consistent; it is also premise-blind.
This is the shape of the phenomenon: not corrupted reasoning, but an answer
that reasoning never actually authorized.

## 3. STAGE 2: Preliminary activation-level evidence

If the model is committed to "walk" before emitting it, the commitment may
be readable from hidden states at positions preceding the answer text. We
test this with a pretrained activation oracle (LatentQA-style: an LLM
fine-tuned to answer natural-language questions about injected activations),
using the public Qwen3-8B oracle checkpoint. Activations are collected by
teacher-forced prefill over the exact generation-time sequence (prompt +
generated text), layer 18 of 36.

**Design.** 22 rollouts from STAGE 1 (16 walk-committing across
`A_bare`/`C_role_star` × thinking on/off; all 6 drive-committing rollouts
with a reliably localizable commitment). Six probe sites per rollout:
assistant start (P0), 25/50/75% of the span to the commitment token
(P1–P3), immediately before the commitment token (P4), and after the
commitment text (P5, positive control). P0–P4 windows never touch the
commitment tokens, so a correct read-out at those sites cannot come from
the answer text itself (text-inversion control).

### 3.1 The oracle is extremely sensitive to question wording

Our first three configurations — single-token probes, 5-token majority
voting, and segment (multi-position) injection — all failed the positive
control with the open question "What answer is this model going to give?"
(P5 hit rates 3/16, 3/16, 2/16). The failure was consistent, not noisy:
under majority voting, 13/16 rollouts produced 4–5 "no answer" votes out
of 5 at P5.

Holding activations, positions, and injection mode fixed and changing only
the question:

| Oracle question (P5, walk group) | hits |
|---|---|
| "What answer is this model going to give?" | 2/16 |
| "What is the model recommending?" | 7/16 |
| "Is the model going to say walk or drive?" | **11/16** |

A closed question naming the answer space recovers the positive control
that open questions fail. We conjecture open answer-prediction is outside
the oracle's LatentQA training distribution while binary classification is
close to it. Practical implication: a negative oracle result cannot be
interpreted without a positive control *per question wording* — a
constraint we have not seen documented in current oracle practice, and an
independent, quantified confirmation that current activation oracles are
hard to use off-distribution.

### 3.2 Neutral-context baseline: the oracle's default is "drive"

Forced-choice questions make the oracle answer something even on empty
evidence, so read-out rates are only interpretable against the oracle's
intrinsic preference. On activations from 8 unrelated prompts (philosophy,
arithmetic, recipes, code; 24 probes), the oracle answers "drive" 19/23 and
"walk" 4/23 (17%). The oracle's default under this question is *drive*;
consequently "walk" read-outs carry information and "drive" read-outs are
weak evidence. (This asymmetry cuts both ways: it strengthens walk
read-outs below, and it means our positive control stands only on the walk
side — drive-committing rollouts' P5 read-outs, 3/6, are uninformative.)

### 3.3 Pre-commit read-outs exceed the baseline — including in rollouts that end up correct

Walk read-out rates at the pre-commit site P4 (commitment text not yet
emitted), against the 17% neutral baseline (Fisher exact, one-sided):

| Group | P4 walk read-outs | vs. baseline |
|---|---|---|
| walk-committing (n=16) | 10/16 (63%) | p = .005 |
| drive-committing (n=6) | 5/6 (83%) | p = .005 |
| combined (n=22) | 15/22 (68%) | p = .0007 |

Two readings, stated with their limits:

1. **The wrong commitment is readable before it is written.** In
   walk-committing rollouts, an oracle whose default answer is "drive"
   reads "walk" from pre-commit activations at 3.7× the neutral rate.
2. **Rollouts that eventually answer correctly also start walk-leaning.**
   5/6 drive-committing rollouts read as "walk" at P4. Since 9/10 drive
   commitments arise in thinking mode after long deliberation (STAGE 1),
   this is consistent with a two-stage picture: *walk is the default
   internal state; occasionally, extended reasoning overrides it late.*
   The behavioral and activation-level views agree on where the default
   points.

**What we do not claim.** The within-rollout positional gradient (P0 6/16 →
P1 8 → P2 9 → P3 12 → P4 10 → P5 11, walk group) trends upward but is not
significant (paired sign test P0 vs. P4: 7 improved / 3 worsened, p = .34).
P0 activations already contain the prompt (the question is visible to the
model), so P0 is not a zero-information site — elevation *at* P0 relative
to neutral is expected and observed (6/16 vs. 17%). With n=16 we cannot
distinguish "commitment strengthens toward the answer" from "commitment is
present throughout at roughly constant readability." The drive-group result
rests on n=6 and is preliminary by any standard. Individual-rollout
trajectories are noisy (the Section 2.4 rollout reads walk at P2, drive at
P4, walk at P5).

### 3.4 Lexical stratification: the read-outs are not text recovery

The remaining confound is lexical leakage: probe windows sit inside
deliberation text that frequently contains the word "walk," so the oracle
might be reading nearby tokens rather than state. We stratify all 110
pre-commit probes by whether walk/drive literally occur (a) in the injected
5-token span itself and (b) within ±25 tokens of it.

**Injected-span (strict text-inversion) test.** Walk read-outs are *not*
driven by "walk" tokens in the injected span: spans containing "walk" read
out walk at 2/8, spans without it at 64/102 (63%). In six probes the
injected span contains "drive"/"driving" and not "walk" — and the oracle
still answers walk (e.g., span " not need to drive." → "walk"). Recovery
of injected token identities cannot explain the results.

**Context-field test.** The ±25-token lexical field does influence the
oracle in single-word strata: contexts containing only "walk" read out walk
12/12; contexts containing only "drive" follow drive (n=6). These strata
are small because deliberation text is saturated with both words: 90/110
probes (82%) have a *balanced* field containing both. In that decisive
stratum, walk read-outs dominate 52 vs. 20 — a 72% walk share against the
oracle's own 17% neutral default (Fisher p = 4×10⁻⁶) and against a 50/50
lexical tie (p = 10⁻⁴). Sharpest of all: in drive-committing rollouts with
both words in context, the oracle reads walk 20/28 and drive 1/28
(p = 10⁻⁷ vs. neutral) — the lexical field names both options, the oracle's
default is drive, the rollout's own final answer is drive, and the
read-out is still walk. Pure lexical reading predicts none of this.

We conclude the pre-commit walk read-outs cannot be reduced to text
recovery, while acknowledging that in single-word lexical fields oracle
answers do track the field, so probes there (a minority) are individually
uninterpretable.

## 4. Related work

*To be completed with citations:* attribution-graph analyses of unfaithful
CoT (answer-to-reasoning direction; our phenomenon is reasoning-intact,
answer-first); LatentQA and Activation Oracles (Karvonen et al.), including
reported low task accuracies and calibration caveats consistent with our
question-sensitivity findings; CoT faithfulness literature; "reasoning
models don't say what they think."

## 5. Limitations

- **Single model, single task.** One 8B open-weight model, one question.
  The original phenomenon was observed on a much larger closed model; we
  show transfer of the behavior, not universality.
- **Judge and target share a base model.** The LLM judge is Qwen3-8B
  scoring Qwen3-8B rollouts. The 96.9% human-agreement gate and 20/20
  manual check mitigate this; raw texts are preserved so any external
  judge can re-score.
- **STAGE 2 sample sizes.** n=16/6; the positional gradient is
  non-significant; drive-side positive control unavailable (oracle
  default). All STAGE 2 claims are labeled preliminary.
- **Teacher-forced prefill.** Probed activations come from re-encoding the
  generated sequence, which matches generation-time computation for the
  same prefix under causal attention, but small tokenizer boundary effects
  at the prompt/generation seam are possible.
- **Local lexical context.** Addressed directly in §3.4: injected-span
  text-inversion is refuted, and the dominant balanced-field stratum
  favors walk against both the oracle default and a lexical tie. Residual
  caveat: in single-word lexical fields the oracle tracks the field, so
  individual probes in those (minority) strata remain uninterpretable, and
  ±25 tokens is one operationalization of "local" among several.

## 6. Discussion

The behavioral result is sturdy: on this task, a competent open-weight
model commits to a premise-violating answer at 85–100% rates that survive
sampling, prompt variation, an explicit contradicting profile, and a
4,096-token thinking budget — and structured-answer formats make it
strictly worse. The activation-level result, while preliminary, points the
same way: the default internal state reads as "walk" before any answer is
written, even in the rare rollouts that end up correct. If that picture
holds under larger n, "answer-first" is not a formatting quirk but a
readable internal condition that reasoning decorates — which would make
pre-commitment detection (rather than post-hoc reasoning audits) the right
intervention point.

The methodological finding stands on its own: with a fixed oracle and fixed
activations, question wording alone moved a positive control from 2/16 to
11/16. Negative oracle results without per-wording positive controls are
uninterpretable, and current oracles' usable surface is narrower than their
interface suggests.

## Appendix A. Scorer audit trail (summary)

Regex scorer: 6 general-rule fixes after a 32-case adversarial audit; fresh
4-lens 32-case holdout → 62.5% case mismatch (1 false positive, 43/44 field
errors were missed commitments) → rejected under a pre-registered >15%
threshold. LLM judge: rubric frozen before validation; 62/64 on combined
audit sets; the two disagreements are pre-flagged label-ambiguous classes
(implied commitment under negation; conditional dual recommendation).
Determinism: 8/8 identical labels on repeated greedy scoring (MPS).
Manual gate: stratified 20 rollouts (all conditions, both thinking modes,
truncation cases included), 20/20 judge labels confirmed by hand.

## Appendix B. Reproducibility

All rollouts, judge outputs, probe responses, and scripts are committed:
STAGE 1 harness (`stage1_qwen_carwash.py`, resume-capable), judge
(`judge_rollouts.py`, `--validate` gate), AO pipeline
(`stage2_ao_{experiment,window,segment,qab,neutral}.py`, vendored demo
library with a 4-line transformers-compat patch). Hardware: single Apple
M-series machine (MPS, bf16); no CUDA, quantization, or cloud GPU required.
