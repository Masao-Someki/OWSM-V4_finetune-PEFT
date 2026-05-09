- [ ] Ensure all search space axes match `prompt.txt`.
- [ ] Enumerate explicit candidate values for each axis.

## Candidate Values

### Method parameters

| algorithm | done | comment | config |
| --- | --- | --- | --- |
| method_A |  | Baseline exploration | conf/exp_20260509_205921/config_0.yaml |
| method_B |  | Alternative method    | conf/exp_20260509_205921/config_1.yaml |
| method_C |  | Exploring different parameters | conf/exp_20260509_205921/config_2.yaml |

### Notes (wave 2)
- We are in the initial phase of the search, so covering all primary method variants is mandatory before narrowing the search.
- No evidence yet from experiments.csv to indicate dysfunction or best performer.

### Current Focus

#### Focus axis
- [x] Method type (`method_A`, `method_B`, `method_C`)

#### Why this axis now
- Initial coverage is mandatory to ensure infrastructure and method implementations are correct.
- No prior result for any method; stability must be established for all.

#### Candidate values for current focus

| value     | done | comment             | config                                         |
|-----------|------|---------------------|------------------------------------------------|
| method_A  |      | Baseline exploration| conf/exp_20260509_211638/config_0.yaml         |
| method_B  |      | Alternative method  | conf/exp_20260509_211638/config_1.yaml         |
| method_C  |      | Explore diversity   | conf/exp_20260509_211638/config_2.yaml         |

Current axis resolved?: no
Winner / best-so-far summary: TBD after this wave completes
Axis type: categorical
Enumeration policy used: full set from prompt/web, 1:1 mapping to implemented configs
Evidence links: see conf/exp_20260509_205921/config_*.yaml (baseline variants), prompt.txt sec 6

#### Deferred Axes

- [ ] PEFT parameters
- [ ] Learning rate
- [ ] optimizer
- [ ] warmup_steps
- [ ] batch size
- [ ] max_epochs

#### Unlock Condition For Next Axis
- Upon collection of stable, complete metrics for each method, advance to the top-performing method and tune its primary hyperparameters.

#### Which axis next?
- Parameterization for the selected method, or explore PEFT hyperparameters.

#### Source Reference
- prompt source: `prompt.txt`
- format reference: `search_plan_human.md`

#### Accumulated Evidence
- First exploration run to substantiate metrics and stability; no prior run results in experiments.csv.
