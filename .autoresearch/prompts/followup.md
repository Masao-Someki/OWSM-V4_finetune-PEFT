# Follow-up Prompt Template (Generalized)

Use this when refining a previously proposed wave.

## Goal
Revise the plan using new evidence, reviewer feedback, or failed-run diagnostics.

## Instructions
- Keep the same `next_exp_name` unless explicitly asked to create a new wave.
- Minimize changes: modify only configs that need adjustment.
- Preserve valid outputs and formatting contracts.
- Explain exactly what changed and why.

## Required Checks
- `array.txt` paths match existing config files.
- Updated configs remain inside search space from root `prompt.txt`.
- Checklist and findings are updated only where justified by evidence.
