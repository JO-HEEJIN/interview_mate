# Branching vs STAR-for-All Experiment

Date: 2026-03-08 02:03
Model: claude-sonnet-4-6 | Judge: claude-sonnet-4-6 | Temperature: 0.7
Runs per cell: 10

## Car Wash (Implicit Constraint)

| Prompt | Pass Rate | Constraint | Avg Words |
|--------|-----------|------------|----------|
| branching | 50% | 40% | 17.2 |
| star_all | 10% | 0% | 49.4 |

## yes_no: "Did you use Python for this project?"

| Prompt | Avg Score | Avg Words | Reasoning Order | Criteria |
|--------|-----------|-----------|-----------------|----------|
| branching | 67% | 15.6 | C:10 R:0 M:0 | starts_with_yes_or_no: 100%, concise: 50%, no_rambling: 50% |
| star_all | 33% | 42.0 | C:10 R:0 M:0 | starts_with_yes_or_no: 100%, concise: 0%, no_rambling: 0% |

## direct: "What's your greatest strength?"

| Prompt | Avg Score | Avg Words | Reasoning Order | Criteria |
|--------|-----------|-----------|-----------------|----------|
| branching | 77% | 75.1 | C:10 R:0 M:0 | answers_question: 100%, specific: 100%, appropriate_length: 30% |
| star_all | 87% | 75.3 | C:10 R:0 M:0 | answers_question: 100%, specific: 100%, appropriate_length: 60% |

## behavioral: "Tell me about a time you resolved a conflict on your team."

| Prompt | Avg Score | Avg Words | Reasoning Order | Criteria |
|--------|-----------|-----------|-----------------|----------|
| branching | 100% | 172.3 | C:1 R:5 M:4 | has_situation: 100%, has_action: 100%, has_result: 100%, uses_specific_example: 100% |
| star_all | 95% | 150.6 | C:6 R:1 M:3 | has_situation: 100%, has_action: 100%, has_result: 80%, uses_specific_example: 100% |

## compound: "Introduce yourself and tell me why you want to work at our company."

| Prompt | Avg Score | Avg Words | Reasoning Order | Criteria |
|--------|-----------|-----------|-----------------|----------|
| branching | 100% | 188.3 | C:8 R:0 M:2 | addresses_introduction: 100%, addresses_motivation: 100%, coherent_flow: 100% |
| star_all | 100% | 192.8 | C:9 R:0 M:1 | addresses_introduction: 100%, addresses_motivation: 100%, coherent_flow: 100% |

## Key Questions

1. Does branching (PREP) produce better yes/no conciseness?
2. Does STAR-for-all hurt direct question answers (over-structured)?
3. Does branching's PREP ('conclusion first') kill car wash accuracy?
4. Which prompt produces more 'reasoning_first' vs 'conclusion_first' answers?
5. Is there a clear winner, or do we need a hybrid approach?
