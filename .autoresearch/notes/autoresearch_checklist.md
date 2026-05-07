# Autoresearch Checklist

Use this checklist to drive experiment planning.  
Codex must read this file and `experiments.csv` before proposing next configs.

## Rules
- Keep statuses up to date: `TODO`, `DOING`, `DONE`, `BLOCKED`.
- Prefer unresolved (`TODO`/`DOING`) items when selecting next wave.
- When an item becomes `DONE`, add a short evidence note with run ids.
- If evidence is conflicting, keep as `DOING` and specify what to test next.
- There is no fixed search order. Choose an adaptive order that improves narrowing speed:
  prioritize high-uncertainty + high-impact items, then shrink around winners.

## Checklist

| ID | Topic | Question | Status | Priority | Last update | Evidence / Notes |
|---|---|---|---|---|---|---|
| C0 | Smoke test policy | For pipeline verification wave, enforce `max_configs<=3`, `trainer.max_epochs=3`, `trainer.max_steps=100` | DOING | High | 2026-04-27 | Enforced in retry settings (`--max_configs 3 --quick_max_epochs 3 --quick_max_steps 100`) and default quick epoch cap updated to 3 in launcher scripts; execution blocked by Slurm controller connectivity before submission |
| C1 | PEFT family | Which PEFT family is best on current FLEURS objective? (`lora/espnet_lora/adalora/randlora/vblora/delora`) | TODO | High | - | - |
| C2 | LR | What LR range is robust for top PEFT families? | TODO | High | - | - |
| C3 | Epoch budget | What `trainer.max_epochs` is enough before overfit/plateau? | TODO | Medium | - | - |
| C4 | Warmup | What `scheduler.warmup_steps` works best with chosen LR/batch regime? | TODO | Medium | - | - |
| C5 | Data robustness | Do `dataset.ratio`, `time_apply_prob`, `text_prev_apply_prob` improve robustness? | TODO | Medium | - | - |
| C6 | Stability | Which settings reduce failure rate / debug failure risk? | DOING | High | 2026-04-27 | Root cause identified from debug logs: host-memory OOM kill (`exit_code=137`, Slurm `oom_kill`) under 8G request while loading `espnet/owsm_ctc_v4_1B`; raised default memory requests to 32G for debug and array launch paths, pending validation retry |

## Decision Policy
1. Each wave must target at least 2 checklist IDs.
2. Include at least one config for exploitation (best-known) and one for exploration (uncertain checklist item).
3. Do not expand search dimensions if unresolved failure/root-cause (`C6`) is blocking.
4. If `C0` is unresolved, run in smoke-test mode first and keep wave small/safe.

## Stop Condition Marker
- When Codex concludes the optimum is found, add this line in this file:
  - `OPTIMAL_FOUND: true`
- Also write `.autoresearch/stop.json` with:
  - `{"stop": true, "reason": "<short reason>"}`.
