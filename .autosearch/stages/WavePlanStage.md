# WavePlanStage

## Header
- Stage Name: `WavePlanStage`
- Stage Id: `wave_plan`
- Previous Stage: `BuildSearchPlanStage` or `LoopEndStage`
- Start Condition: planning context exists (`store/search_plan.md`, and when iterative, latest metrics/goal are present).
- End Condition: Next-wave artifacts are generated and committed (`store/next_exp_name.txt`, `store/effective_config_list.txt`, configs).
- On Success: `DebugGateStage`
- Store Path: `self.store_path` resolves to `.autosearch/store/`.

## Behavior
1. Resolve provider/model from cache/config.
2. Determine mode (`bootstrap` or `iterative`) and update prompt state files.
3. Build planning prompt from `next_goal.md`, `findings.md`, `experiments.csv`, `search_plan.md`.
4. If unclear, inspect repository files (especially `.autosearch/`, `conf/`, `src/`) and return complete output in one response.
5. Parse `<file path="...">` blocks and write only allowed paths.
6. Require both `store/next_exp_name.txt` and `store/effective_config_list.txt`; fail if missing.
7. Reconcile status labels in `search_plan.md` and `search_plan_report.md` from `experiments.csv`.
8. Write `store/bootstrap_done.json` and commit `autoresearch: propose {next_exp_name}`.

Note: If response parsing fails or no files are written, this stage raises an error.
