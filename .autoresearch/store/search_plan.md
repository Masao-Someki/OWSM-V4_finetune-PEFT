# Search Space Checklist

- [ ] All axes must come from prompt.txt section 6.
- [ ] This file is cumulative: append updates and preserve prior evidence/history.
- [ ] Enumerate explicit candidate values only for the current active axis.
- [ ] Include source links for proposed values.
- [ ] Keep non-active axes deferred until the current active axis is resolved.
- [ ] If the active axis is finite/categorical, enumerate the broadest practical candidate set.
- [ ] If the active axis is numeric, use coarse, information-efficient values first and avoid low-signal tiny increments.

## Sequential Policy

- [ ] Choose one current focus axis.
- [ ] Run only the minimum set of experiments needed to resolve that axis.
- [ ] After resolving the current axis, update this file and choose the next focus axis.

---

## Current Focus (Wave 2: 2026-05-09 update)

### Focus axis
- [x] Method type (`lora`, `adalora`, `ia3`)

### Why this axis now
- No experiment results yet (experiments.csv empty).
- All PEFT methods and infrastructure must be validated for stability, compatibility, and any major effectiveness differences before fine-tuning hyperparameters.
- This axis is categorical with three widely-cited, validated PEFT methods via recent literature and HF-PEFT repo support.

### Candidate values for current focus

| value    | done | comment                                    | config                                         |
|----------|------|--------------------------------------------|------------------------------------------------|
| lora     |      | Standard, robust PEFT baseline             | conf/exp_20260509_213942/config_0.yaml         |
| adalora  |      | Adaptive LoRA, lighter/flexible            | conf/exp_20260509_213942/config_1.yaml         |
| ia3      |      | Competitive and very parameter-efficient   | conf/exp_20260509_213942/config_2.yaml         |

- Current axis resolved?: no
- Winner / best-so-far: TBD after actual metrics for all three
- Axis type: categorical (broadest practical set supported at runtime)
- Enumeration policy: "exhaust all major PEFT methods most often cited + supported by current runtime/libraries."
- Evidence links:
    - LoRA: https://arxiv.org/abs/2106.09685, https://github.com/huggingface/peft
    - AdaLoRA: https://arxiv.org/abs/2303.10512, https://github.com/huggingface/peft
    - IA3: https://arxiv.org/abs/2205.05638, https://github.com/huggingface/peft

---

## Deferred Axes

- [ ] PEFT method parameters (r, alpha, dropout, other)
- [ ] Learning rate
- [ ] optimizer
- [ ] warmup_steps
- [ ] batch size
- [ ] max_epochs

---

## Unlock Condition For Next Axis

- When all three main methods run successfully and give stable metrics, proceed to hyperparameter tuning for the best (single) method.
    - If any method fails or is unstable, debug and rerun the broken config(s) before tuning.
    - After all stable: advance to tuning parameters such as r, alpha, etc. for the top performer.

- Next axis after this: "PEFT method parameters" for the selected best method (i.e., r, alpha, dropout, etc.).

---

## Source Reference

- prompt source: `prompt.txt`
- format reference: `search_plan_human.md`

## Accumulated Evidence

Wave 1-2: No experiment results; exhaustively covering the main method type axis for method/infrastructure stability before tuning finer hyperparameters.
