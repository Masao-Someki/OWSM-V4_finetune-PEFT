# Error Analysis Prompt Template (Generalized)

Use this when the latest wave has failures.

## Goal
Identify root causes and propose the minimum safe next step.

## Inputs to Review
- `.autoresearch/store/latest_error.log`
- `.autoresearch/store/latest_status.json`
- `.autoresearch/store/latest_metrics.json`
- Relevant rows in `.autoresearch/store/experiments.csv`

## Output Expectations
- Failure taxonomy (what failed, where, how often)
- Most likely root cause(s) with supporting evidence
- Immediate mitigations for the next wave
- Whether to run a small safety-validation wave before full expansion

## Constraints
- Do not broaden search axes until blocking stability issues are controlled.
- Keep recommendations consistent with root `prompt.txt` constraints.
