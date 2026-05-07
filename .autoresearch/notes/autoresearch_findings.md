# Autoresearch Findings Log

Append one entry per wave after planning/execution attempt.

---

## Entry Template

### Wave
- timestamp:
- trigger: `exp_name=` `array_job_id=`
- planned_next_exp:
- mode:

### Checklist Coverage
- targeted_ids: (e.g. `C1,C2`)
- why_these_now:

### Experiments Added
- config_paths:
- key deltas vs previous best:
- submit_command:

### Outcomes Observed
- relevant_run_uids:
- metric_summary:
- failures:

### Conclusions By Checklist
- `C1`:
- `C2`:
- `C3`:
- `C4`:
- `C5`:
- `C6`:

### Next Action
- continue / narrow / fix-blocker:
- candidate axes for next wave:

---

### Wave
- timestamp: 2026-04-27T17:27:58-05:00
- trigger: `exp_name=exp_smoke3` `array_job_id=17915098`
- planned_next_exp: `exp_smoke3`
- mode: `slurm`

### Checklist Coverage
- targeted_ids: `C0,C6`
- why_these_now: C6 is blocking all expansion; C0 is still unresolved and must gate retries with strict smoke limits.

### Experiments Added
- config_paths:
  - `conf/owsm_peft_lora_basic.yaml`
  - `conf/owsm_peft_espnet.yaml`
  - `conf/owsm_peft_adalora.yaml`
- key deltas vs previous best: no search-space expansion; stability-only runtime fix (`mem 8G -> 32G`) and C0 smoke enforcement (`max_configs=3`, `quick_max_steps=100`, `quick_max_epochs=3`).
- submit_command: `bash scripts/submit-array-with-debug.sh exp_smoke3 0-2 array_conf/exp_smoke3/array_3.txt 0 --max_configs 3 --quick_train true --quick_fast_dev_run 10 --quick_max_steps 100 --quick_max_epochs 3`

### Outcomes Observed
- relevant_run_uids:
  - `17915098_0_exp_smoke3_owsm_peft_lora_basic_a0`
  - `17915039_0_exp_smoke3_owsm_peft_lora_basic_a0`
  - `17914613_0_exp_smoke3_owsm_peft_lora_basic_a0`
- metric_summary: no train metrics produced; process killed before first optimization step.
- failures:
  - Slurm debug logs show `Killed` + `Detected 1 oom_kill event` with `exit_code=137`.
  - New retry attempt blocked pre-run by infra error: `sbatch: Unable to contact slurm controller (connect failure)`.

### Conclusions By Checklist
- `C1`: no new evidence.
- `C2`: no new evidence.
- `C3`: no new evidence.
- `C4`: no new evidence.
- `C5`: no new evidence.
- `C6`: likely root cause is insufficient host memory request (8G) for model/materialization path; memory request increased to 32G in launcher defaults.

### Next Action
- continue / narrow / fix-blocker: fix-blocker; rerun exact debug-first command once Slurm control plane is reachable.
- candidate axes for next wave: keep same 3-config smoke set to validate stability first; only then resume C1/C2 exploration.
