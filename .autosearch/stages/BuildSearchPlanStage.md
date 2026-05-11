# BuildSearchPlanStage

## Header
- Stage Name: `BuildSearchPlanStage`
- Stage Id: `build_search_plan`
- Previous Stage: `Start`
- Start Condition: `prompt.txt` exists at the repository root.
- End Condition: `.autosearch/store/search_plan.md` has been generated and `.autosearch/store/prompt_state.json` sha256 matches `prompt.txt`.
- On Success: `WavePlanStage`
- On Skip (cache hit): `WavePlanStage`
- Store Path: `self.store_path` resolves to `.autosearch/store/`.

## Behavior
1. Resolve provider/model.
2. Cache check using `prompt.txt` sha256 and `store/prompt_state.json`.
3. Build prompts from `prompt.txt`, config YAMLs, `experiments.csv`, and existing `search_plan.md`.
4. Call LLM and write `<file path=".autosearch/store/search_plan.md">` output.
5. Update `store/prompt_state.json`; initialize `store/bootstrap_done.json` if absent.
