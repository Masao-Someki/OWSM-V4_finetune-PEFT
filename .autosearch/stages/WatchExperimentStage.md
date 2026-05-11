# WatchExperimentStage

## Header
- Stage Name: `WatchExperimentStage`
- Stage Id: `watch_experiment`
- Previous Stage: `SubmitArrayJobStage`
- Start Condition: `watcher_state.json` phase is `EXPERIMENT_RUNNING` and `array_job_id` is set.
- End Condition: All tasks in the array job have reached a terminal state (COMPLETED / FAILED / CANCELLED / TIMEOUT).
- On Success: `CollectMetricsStage`
- Store Path: `self.store_path` resolves to `.autosearch/store/` — use this attribute to access all `store/` files referenced in this document.

## Behavior

### 1. Load State
1. Read `watcher_state.json` and extract `array_job_id` and `exp_name`.
2. If `array_job_id` is empty, exit with an error.

### 2. Poll for All Tasks Completion
1. Every 5 minutes, run the following:
   1. Run `sacct -n -P -j {array_job_id} --format=JobID,State` to get the state of each task.
   2. If all tasks are in a terminal state (COMPLETED / FAILED / CANCELLED / TIMEOUT / NODE_FAIL), break out of the loop.
   3. If any tasks are still RUNNING or PENDING, wait until the next poll.
2. If the maximum poll count (`max_stage_steps` from `.autosearch/config.json` under `orchestration.max_stage_steps`) is reached, emit a warning log and exit forcefully.

### 3. Record Completion Summary
1. Tally the final state of each task (count of COMPLETED / FAILED / other) and print to stdout.
2. Update `watcher_state.json` phase to `COLLECTING_METRICS`.
3. Proceed via `On Success`.
