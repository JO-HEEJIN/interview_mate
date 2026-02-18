# Car Wash Prompt Architecture: Variable Isolation Results

Date: 2026-02-19 03:06
Model: claude-sonnet-4-5-20250929 | Runs per condition: 20

| Condition | DeepSeek Prediction | Actual Pass Rate | Recovery Rate | Median Latency |
|-----------|--------------------|-----------------:|--------------|----------------|
| A_bare | 0% | 0.0% (0/20) | 95.0% | 4649ms |
| B_role_only | 5-10% | 0.0% (0/20) | 100.0% | 7550ms |
| C_role_star | 50% | 85.0% (17/20) | 66.7% | 7851ms |
| D_role_profile | 40% | 30.0% (6/20) | 100.0% | 8837ms |
| E_full_stack | 98% | 100.0% (20/20) | n/a | 8347ms |

## Key Question

Is C (STAR) higher than D (profile)? DeepSeek predicted yes (50% vs 40%).
If D > C: profile injection is the dominant mechanism.
If C > D: STAR framework is the key driver of task grounding.