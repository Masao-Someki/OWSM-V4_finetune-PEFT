# CollectMetricsStage

## Header
- Stage Name: `CollectMetricsStage`
- Stage Id: `collect_metrics`
- Previous Stage: `WatchExperimentStage`
- Start Condition: All array tasks reached terminal states and `watcher_state.json` phase is `COLLECTING_METRICS`.
- End Condition: `store/latest_metrics.json` has been updated and changes are committed.
- On Success: `LoopEndStage`
- Store Path: `self.store_path` resolves to `.autosearch/store/`.

## Behavior
1. Read `exp_name` and `array_job_id` from `watcher_state.json`.
2. Run `.autoresearch/collect_metrics.py` and write `store/latest_metrics.json`.
3. Update `store/latest_status.json` and `store/next_goal.md`.
4. `git add` + `git commit -m "autoresearch: collect metrics {exp_name} ({array_job_id})"`.
5. Set `watcher_state.json` phase to `WAVE_PLANNING`.

Note: This stage does not run `git push`.
