# Search Space Report

## Active Axis: Method Type

| value    | rationale / comment                                             | config                                         |
|----------|----------------------------------------------------------------|------------------------------------------------|
| lora     | Standard PEFT baseline, widely used, robust                    | conf/exp_20260509_212910/config_0.yaml         |
| adalora  | Adaptive LoRA variant, efficient and flexible, recent results  | conf/exp_20260509_212910/config_1.yaml         |
| ia3      | Lightweight, highly parameter-efficient, competitive           | conf/exp_20260509_212910/config_2.yaml         |

## Web/Literature Evidence Table

| Method   | Source/Reference                                                                                               |
|----------|--------------------------------------------------------------------------------------------------------------|
| lora     | https://arxiv.org/abs/2106.09685, https://github.com/huggingface/peft                                        |
| adalora  | https://arxiv.org/abs/2303.10512, https://github.com/huggingface/peft                                        |
| ia3      | https://arxiv.org/abs/2205.05638, https://github.com/huggingface/peft                                        |

## Coverage

- All major PEFT methods from `prompt.txt` and web best practices are tested.
- No locked-out methods from guides or open-source examples.

## Next Expansion

- Once a method "winner" is stable, hyperparameter search (e.g. r, alpha, dropout).
- If runtime/stability issues: debug/patch, hold off further expansion.
