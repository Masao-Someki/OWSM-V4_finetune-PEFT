# Wave Summary for exp_20260510_012658

## Why this config set

**Evidence from experiments.csv**:  
- Across all recent waves (exp_20260509_* and exp_20260510_*), every config attempting a debug run **failed**.  
- All algorithm variants (lora, adalora, ia3, oft, vera and their parameterizations) have unresolved stability or runtime errors.
- No config has completed a successful run long enough to measure core metrics, making functional correctness and pipeline debug the immediate gating concern.

**Current status**:
- The prior wave (exp_20260510_011434) attempted a wide method sweep, each with `fast_dev_run: 10` and highly restricted data sizes (`max_samples_per_subset_{split}: 4`), yet all FAILED.
- No evidence exists for metric quality or correctness, indicating a fundamental implementation or environment problem across all methods.

## Search-space coverage

- **Primary axis**: Only PEFT algorithm/method—**all tested candidates failed**.
- No other axes (learning rate, optimizer, etc.) are unlocked or justified yet.

## Checklist updates

- *Stability* checklist items remain **DOING**—no config is marked successful.
- All PEFT candidates remain "pending"/unresolved, as no config completed or produced metric evidence.

## Next action

- **Focus remains on minimal debug runs for all candidate PEFT methods**.
- No expansion along other search axes (lr, optimizer, etc.) is warranted until a baseline run completes successfully.
- Diagnostic action for the next wave: further minimize or instrument for error output, and/or test infrastructure details (dataset access/paths, CUDA and model loading, etc.).
- If possible, isolate the method with fewest customizations for the next test (e.g. vanilla LoRA), and further reduce data/batch/max_steps until *any* completion signal is achieved. Also consider logging or runtime config options to capture stack trace or error information.

