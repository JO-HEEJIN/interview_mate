# Car Wash STAR + Profile Experiment

Date: 2026-03-07 23:41
Model: claude-sonnet-4-6 | Temperature: 0.7 | Runs: 20/condition

| Condition | Pass Rate | Constraint | Correct+Reason | Median Latency |
|-----------|-----------|------------|----------------|----------------|
| A_star_anthropic | 0% (0/20) | 0% (0/20) | 0% (0/20) | 3176ms |
| B_star_default | 30% (6/20) | 35% (7/20) | 10% (2/20) | 3337ms |
| C_star_only | 100% (20/20) | 100% (20/20) | 100% (20/20) | 7378ms |

## Key Questions

1. Does Anthropic profile produce higher pass rate than Default profile?
2. Does either profile produce correct reasoning (implicit constraint)?
3. Does C_star_only (paper reproduction) still get 85% on claude-sonnet-4-6?
4. Is the pass rate on profiles just coincidence or systematic?
