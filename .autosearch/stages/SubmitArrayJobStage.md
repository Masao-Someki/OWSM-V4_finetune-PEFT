# SubmitArrayJobStage

## Header
- Stage Name: `SubmitArrayJobStage`
- Stage Id: `submit_array_job`
- Previous Stage: `DebugGateStage`
- Start Condition: Debug gate passed (COMPLETED) and `watcher_state.json` has `exp_name` + `effective_config_list`.
- End Condition: The array job has been submitted via sbatch and `array_job_id` is recorded in `watcher_state.json`.
- On Success: `WatchExperimentStage`
- Store Path: `self.store_path` resolves to `.autosearch/store/`.

## Behavior

### 1. Determine Array Range
1. Read `effective_config_list` (from `watcher_state.json`) and count usable config lines `n`.
2. Build array range `0-{n-1}` (optionally append `%{concurrency}` when configured).

### 2. Submit Array Job
1. Submit via `sbatch scripts/run-array.sh` (same style as debug stage: no explicit resource flags from this stage), with:
   - `--job-name {exp_name}`
   - `--array 0-{n-1}` (or `0-{n-1}%{concurrency}`)
   - `--exp_name {exp_name}`
   - `--config_list {effective_config_list}`
   - `--experiment_comment "[array-run]"`
2. Parse `array_job_id` from sbatch output; fail if parsing fails.
3. Copy `effective_config_list` to `.autoresearch/array_conf/{exp_name}/array_{array_job_id}.txt` for traceability.

### 3. Record State
1. Update `watcher_state.json`:
   ```json
   {
     "phase": "EXPERIMENT_RUNNING",
     "array_job_id": "{array_job_id}",
     "exp_name": "{exp_name}",
     "last_main_sha": ""
   }
   ```
2. Proceed via `On Success`.
