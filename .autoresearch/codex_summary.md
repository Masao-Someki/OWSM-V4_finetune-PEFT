# Wave Summary: exp_20260509_235129

## Why this config set

- All PEFT methods in previous wave failed immediately (status=FAILED, exit_code=1, zero runtime, see experiments.csv).
- No evidence any specific PEFT method or hyperparameter is the root cause.
- All configs failed fast, including LoRA baseline, IA3, Adapter, Prefix, Adalora, OFT, and LoRA r2/r32 variants.
- The likely root cause is infrastructure (code/data/initialization incompatibility) rather than algorithm.
- Common debug-gate protocols (lightning, PyTorch, espnet) recommend a `fast_dev_run` or <10 steps as first triage.
- Therefore, a single minimal test config with LoRA (as archetype PEFT, minimal r/alpha/dropout, 3 steps) is used to trigger exactly where/what the error is.

## Search-space coverage

- Axis: PEFT Method. Diagnostic step only.
- Only LoRA tested in this step, as universal testbed for PEFT infra.
- **No true algorithmic search**—this is a troubleshooting/triage wave due to SYSTEMATIC FAILURE in all prior configs.

## Checklist updates

- Mark all previous PEFT method runs as `done` or `skipped` if tested (per prompt: only status update allowed), except this new one.
- Propose no new methods or hyperparams until error root cause is found.
- Checklist/progress is effectively paused at the lowest debug gate.

## Next action

- After this run: 
    - If FAILURE, collect full stack/error, update checklist as SYSTEMIC ERROR, and begin ablations (e.g., remove PEFT, try vanilla model).
    - If SUCCESS, repeat with r=8, full dropout, then adapter/ia3/prefix in debug mode to isolate which method/param breaks pipeline.
    - Only once at least one PEFT method passes debug gate, resume full search wave (max 10 per wave).

