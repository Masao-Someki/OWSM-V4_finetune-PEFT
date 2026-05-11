# LoopEndStage

## Header
- Stage Name: `LoopEndStage`
- Stage Id: `loop_end`
- Previous Stage: `CollectMetricsStage`
- Start Condition: Metrics collection is complete for the current loop.
- End Condition: decision is made from `store/search_plan.md` whether to finish search or continue with next wave planning.
- On Success: `WavePlanStage` (continue search)
- On Failure: `End` (search exhausted)
- Store Path: `self.store_path` resolves to `.autosearch/store/`.

## Behavior
1. Parse `store/search_plan.md` and detect exhaustion (`done`/`skipped` only).
2. If exhausted, keep the workflow ending path.
3. If not exhausted, route to next wave planning.
4. Transition outcome:
   - continue => `On Success` to `WavePlanStage`
   - exhausted => `On Failure` to `End`
