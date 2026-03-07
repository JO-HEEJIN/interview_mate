# Branching vs STAR-for-All Experiment

Date: 2026-03-08 02:14
Model: claude-sonnet-4-6 | Judge: claude-sonnet-4-6 | Temperature: 0.7
Runs per cell: 10

## Car Wash (Implicit Constraint)

| Prompt | Pass Rate | Constraint | Avg Words |
|--------|-----------|------------|----------|
| branching | 40% | 20% | 20.3 |
| star_all | 10% | 10% | 47.3 |

## yes_no: "Did you use Python for this project?"

| Prompt | Avg Score | Avg Words | Reasoning Order | Criteria |
|--------|-----------|-----------|-----------------|----------|
| branching | 100% | 15.0 | C:10 R:0 M:0 | starts_with_yes_or_no: 100%, concise: 100%, no_rambling: 100% |
| star_all | 33% | 43.0 | C:10 R:0 M:0 | starts_with_yes_or_no: 100%, concise: 0%, no_rambling: 0% |

## direct: "What's your greatest strength?"

| Prompt | Avg Score | Avg Words | Reasoning Order | Criteria |
|--------|-----------|-----------|-----------------|----------|
| branching | 87% | 71.0 | C:10 R:0 M:0 | answers_question: 100%, specific: 100%, appropriate_length: 60% |
| star_all | 90% | 70.0 | C:10 R:0 M:0 | answers_question: 100%, specific: 100%, appropriate_length: 70% |

## behavioral: "Tell me about a time you resolved a conflict on your team."

| Prompt | Avg Score | Avg Words | Reasoning Order | Criteria |
|--------|-----------|-----------|-----------------|----------|
| branching | 100% | 171.6 | C:2 R:5 M:3 | has_situation: 100%, has_action: 100%, has_result: 100%, uses_specific_example: 100% |
| star_all | 88% | 124.3 | C:5 R:0 M:5 | has_situation: 100%, has_action: 100%, has_result: 50%, uses_specific_example: 100% |

## compound: "Introduce yourself and tell me why you want to work at our company."

| Prompt | Avg Score | Avg Words | Reasoning Order | Criteria |
|--------|-----------|-----------|-----------------|----------|
| branching | 100% | 175.5 | C:8 R:0 M:2 | addresses_introduction: 100%, addresses_motivation: 100%, coherent_flow: 100% |
| star_all | 100% | 202.9 | C:10 R:0 M:0 | addresses_introduction: 100%, addresses_motivation: 100%, coherent_flow: 100% |

## Key Questions

1. Does branching (PREP) produce better yes/no conciseness?
2. Does STAR-for-all hurt direct question answers (over-structured)?
3. Does branching's PREP ('conclusion first') kill car wash accuracy?
4. Which prompt produces more 'reasoning_first' vs 'conclusion_first' answers?
5. Is there a clear winner, or do we need a hybrid approach?
