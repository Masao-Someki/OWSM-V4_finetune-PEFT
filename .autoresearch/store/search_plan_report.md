# Search Space Report (exp_20260509_211638)

## Current axis (active): Method type

| method    | description                 | config                                     |
|-----------|----------------------------|--------------------------------------------|
| method_A  | Baseline, established      | conf/exp_20260509_211638/config_0.yaml     |
| method_B  | Alternative, param shift   | conf/exp_20260509_211638/config_1.yaml     |
| method_C  | Different params, explore  | conf/exp_20260509_211638/config_2.yaml     |

*All three main methods covered in this wave.*

## Deferred axes

- PEFT parameters: Defer until method coverage is complete
- Learning rate: Defer
- optimizer: Defer
- warmup_steps: Defer
- batch size: Defer
- max_epochs: Defer

## Evidence and sources (web research summary)
- No run results (experiments.csv empty) — necessary baseline method check.
- See conf/exp_20260509_205921/ for initial template and prompt.txt for axis validity.

## Next Steps
- When metrics are available, select the most promising method or debug/skip broken ones.
- Unlock tuning of key hyperparameters for the best method.

Prepared for Slack or review: summarizes which methods are tried, rationale, and deferred search axes.
