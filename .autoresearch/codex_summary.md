# Wave Summary

## Why this config set
- **No prior experiment results available** (`experiments.csv` is empty).
- The axis "method type" (categorical: `lora`, `adalora`, `ia3`) must be validated for compatibility, basic stability, and basic task suitability.
- This config set directly explores all three prominent PEFT methods widely cited in literature, matching the planned/focused axes in the search plan.
- Parameters (r, alpha, dropout) are kept constant, so only method-level differences are assessed per policy to minimize moving parts.

## Search-space coverage
- **This wave actively covers:** `method type` (PEFT method: `lora`, `adalora`, `ia3`)
- **Deferred axes:** PEFT parameters (`r`, `alpha`, `dropout`), optimizer, learning rate, warmup_steps, batch size, and max_epochs—per the sequential policy.

## Checklist updates
- Confirms all stability and execution for LoRA, AdaLoRA, and IA3 under a shared config.
- Directly impacts: 
    - `Needs to validate effectiveness of methods in configurations`
    - `Stability and performance metrics to be assessed`
- Both items are advanced by this run, as results are essential before tuning further.

## Next action
- **If all three runs are stable:** Proceed to parameter/hyperparameter tuning (start with `r`, `alpha`, `dropout`) for the best-performing method.
- **If any run fails:** Debug/patch infra or method errors (broken method or config), then rerun only the broken ones until all three methods are stable.
- **Concrete next axis:** `PEFT method parameters` (hyperparameters for the best method).

