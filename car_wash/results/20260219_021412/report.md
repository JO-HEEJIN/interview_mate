# Car Wash Prompt Architecture: Variable Isolation Results

Date: 2026-02-19 02:37
Model: claude-sonnet-4-5-20250929 | Runs per condition: 20

| Condition | DeepSeek Prediction | Actual Pass Rate | Recovery Rate | Median Latency |
|-----------|--------------------|-----------------:|--------------|----------------|
| A_bare | 0% | 0.0% (0/20) | 75.0% | 4365ms |
| B_role_only | 5-10% | 0.0% (0/20) | 30.0% | 7447ms |
| C_role_star | 50% | 0.0% (0/20) | 0.0% | 7972ms |
| D_role_profile | 40% | 0.0% (0/20) | 45.0% | 8712ms |
| E_full_stack | 98% | 0.0% (0/20) | 0.0% | 8292ms |

## Key Question

Is C (STAR) higher than D (profile)? DeepSeek predicted yes (50% vs 40%).
If D > C: profile injection is the dominant mechanism.
If C > D: STAR framework is the key driver of task grounding.