# Autoresearch Checklist

Use this checklist to drive wave planning and execution.
Codex must read this file, `prompt.txt`, and `experiments.csv` before proposing next configs.

## Source of Truth
- Search space and hard constraints must come from `prompt.txt`.
- If this checklist conflicts with `prompt.txt`, follow `prompt.txt`.
- This checklist tracks progress and decision quality; it should not redefine search ranges.

## Rules
- Keep statuses up to date: `TODO`, `DOING`, `DONE`, `BLOCKED`.
- Prefer unresolved (`TODO`/`DOING`) items when selecting the next wave.
- When an item becomes `DONE`, add short evidence with run ids from `experiments.csv`.
- If evidence is conflicting, keep as `DOING` and write what to test next.
- Keep entries reusable across projects; avoid task-specific constants here.

## Checklist

| ID | Topic | Question | Status | Priority | Last update | Evidence / Notes |
|---|---|---|---|---|---|---|
| C0 | Input integrity | Is `prompt.txt` complete and internally consistent for this wave? | TODO | High | - | Confirm objective, constraints, output contract, and max_configs are filled |
| C1 | Evidence use | Are next configs grounded in recent evidence from `experiments.csv`? | TODO | High | - | Reference best/worst runs and unresolved failures |
| C2 | Exploit vs Explore | Does the wave include both exploitation and exploration per `prompt.txt` policy? | TODO | High | - | State which config belongs to which role |
| C3 | Axis coverage | Does the wave cover required comparison axes from `prompt.txt` without unnecessary expansion? | TODO | Medium | - | List covered axes and intentionally deferred axes |
| C4 | Stability risk | Are known runtime/resource risks controlled before broadening search? | TODO | High | - | If blocked, run minimal safe validation first |
| C5 | Reproducibility | Are outputs reproducible and contract-compliant (`conf/`, `array.txt`, `next_exp_name.txt`, summary)? | TODO | Medium | - | Validate file paths and formatting rules before submit |

## Decision Policy
1. Each wave should target at least 2 unresolved checklist IDs.
2. Keep one config for exploitation and one for exploration unless `prompt.txt` says otherwise.
3. Do not introduce new axes when stability is unresolved.
4. If `C0` or `C4` is unresolved, prefer a smaller/safe wave.

## Stop Condition Marker
- When optimum is judged reached, add:
  - `OPTIMAL_FOUND: true`
- Also write `.autoresearch/store/stop.json`:
  - `{"stop": true, "reason": "<short reason>"}`.
