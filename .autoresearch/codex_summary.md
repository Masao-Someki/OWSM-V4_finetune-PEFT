# Wave Summary – exp_20260510_005403

**Why this config set**
- All prior runs (including debug-gate minimal configs) for every PEFT method candidate failed, most within seconds, with nonzero exit code and no metrics.
- The runs used up to 10 samples and up to 10 steps, so infra and PEFT init bugs are likely, not model convergence or resource issues.
- To move forward, we must resolve debug failure. This config reduces every axis even further — only 2 samples per split, only 6 max steps, and only 3 fast_dev_run steps. Remains on basic LoRA as minimum-repro baseline.

**Search-space coverage**
- This wave does not expand the PEFT axis further. Instead, it continues the smoke/debug gate until job script and batch setup with PEFT+speech data completes at least one (trivially) successful training batch.
- Does not open search on other axes (lr, optimizer, batch size, etc) until at least one run shows "SUCCEEDED".

**Checklist updates**
- No "done" promotion for new method candidates; all remain "done" for attempted sweeps, but stability is blocked at the debug/sanity test phase.
- This run checks the "minimal debug/sanity" checklist item to trace and unblock the cause of job failure.

**Next action**
- If this run succeeds, rerun 1–3 PEFT types (lora, adapter, ia3) with 2–10 samples per split in fast_dev_run/minimal steps to verify generality.
- If this run fails, carefully inspect logs, especially for YAML config errors, unexpected import failures, and shape mismatch at batch/data/model.
- No expansion of parameter space until this fails and is root-caused.
