# Wave Summary: exp_20260510_011047

## Why this config set
The prior debug wave (`exp_20260509_222054`) **failed all candidates at debug-gate** (exit code 1, rapid failures, no metrics produced). Since the PEFT axis is active and only the LoRA baseline was attempted, the current wave proceeds by running the remaining major PEFT adapter algorithms enumerated (adalora, ia3, oft, vera, LoRA variants, and extended targets) under minimal, debug-like runtime settings. Fast failure indicates either (a) code/config integration issues or (b) method-level incompatibilities, not model convergence. Therefore, to isolate which method or set of settings—if any—passes a minimal runtime check, this wave takes each config from the active PEFT search space and checks its runnability with minimal steps.

## Search-space coverage
- **Axis**: PEFT Adapter Algorithm
- **Configs in this wave**: All remaining pending candidates from search_plan.md—adalora, ia3, oft, vera, LoRA with r=4/r=16, adalora r16, ia3 limited, lora extended.
- **Other axes**: Held, per roadmap (no evidence justifying expansion with current consistent debug failures).

## Checklist updates
- Items related to PEFT adapter baseline, "all major PEFT methods run to debug completion," will be marked pending->done for any config that passes fast_dev_run=10 to completion.
- Stability and debug-gate checklist items remain **open/DOING** until one config completes at least the debug phase.

## Next action
- If any config runs successfully to debug completion, examine log and partial metrics for runtime/stability, then proceed to metrics collection with the same config(s).
- If *all* fail, conduct a debugging triage on model construction, peft target modules, and source/model versions; consider using a pure LoRA config or reducing to a minimal backbone w/o PEFT for isolating issues.

