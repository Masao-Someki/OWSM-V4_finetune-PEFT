# Wave Summary

## Why this config set
The previous wave defined the conceptual baseline for method exploration without actual experiment results (no rows in experiments.csv). According to the project sequential policy and search plan, we must explicitly and independently cover all major method types to establish both stability and method effectiveness, before considering hyperparameter and fine-tuning axes. Here, we pick the three most broadly recognized parameter-efficient fine-tuning (PEFT) methods—`lora`, `adalora`, and `ia3`—as supported by current libraries and literature. Each config uses the same core hyperparameters for direct comparison.

## Search-space coverage
- Current axis: "method type" (categorical).
- Methods selected based on both project requirements and web best practices for PEFT.
- Covers three prominent PEFT algorithmic variants: LoRA, AdaLoRA, Ia3.
- All other axes (hyperparameters, dataset, optimizer, etc.) deferred until one stable, effective method is identified.

## Checklist updates
- [x] Initial wave planning completed (already complete).
- [/] Needs to validate effectiveness of methods in configurations: REMAINS INCOMPLETE, will be resolved by the results of this wave.
- [/] Stability and performance metrics to be assessed: REMAINS INCOMPLETE, dependent on wave execution.
- No item marked complete from new evidence (since experiments.csv is still empty).

## Next action
- After results for these three configs are available, the winning (or best-performing and stable) method will be chosen.
- The search will then proceed to optimize PEFT hyperparameters (e.g., r, alpha, dropout) for that method, as planned in the space.
- If failures occur, debugging/stability investigation becomes first priority before expansion.

## Additional
- Rationale for method values:
    - LoRA: Baseline/most widely adopted PEFT [https://arxiv.org/abs/2106.09685].
    - AdaLoRA: Adaptive, evidence of improved efficiency [https://arxiv.org/abs/2303.10512].
    - IA3: Simpler, competitive on multiple tasks [https://arxiv.org/abs/2205.05638].
