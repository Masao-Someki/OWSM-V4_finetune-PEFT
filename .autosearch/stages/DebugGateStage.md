# DebugGateStage

## Header
- Stage Name: `DebugGateStage`
- Stage Id: `debug_gate`
- Previous Stage: `WavePlanStage` or `BugfixStage`
- Start Condition: `store/effective_config_list.txt` exists and `exp_name` is determined.
- End Condition: Debug job is `COMPLETED` or failure log/status is saved.
- On Success: `SubmitArrayJobStage`
- On Failure: `BugfixStage`
- Store Path: `self.store_path` resolves to `.autosearch/store/`.

## Behavior
1. Read `store/effective_config_list.txt`, strip comments/blank lines, and apply `max_configs` cap if needed.
2. Save the effective list path into `watcher_state.json` as `effective_config_list` (with `exp_name`) for handoff.
3. Submit one debug job via `sbatch scripts/run-array.sh` (no explicit resource flags) with:
   - `--exp_name {exp_name}`
   - `--config_list {effective_config_list}`
   - `--task_id 0`
   - quick-run options for debug gate
4. Poll until completion and check final state via `sacct`.
5. On success, proceed to `SubmitArrayJobStage`.
6. On failure, save failure log + `store/latest_status.json`, then commit debug-failure metadata.

Note: This stage does not run `git push`.
