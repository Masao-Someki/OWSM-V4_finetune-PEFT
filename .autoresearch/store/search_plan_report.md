# Search Space Status Report

## Active Axis: Method type (PEFT method)
All runs set all method params equal (`r=8`, `alpha=16`, `dropout=0.05`).

| method   | included? | rationale/source                        | config                                       |
|----------|-----------|-----------------------------------------|----------------------------------------------|
| lora     | Yes       | Baseline, widely supported (HF PEFT, arXiv 2106.09685) | conf/exp_20260509_213942/config_0.yaml       |
| adalora  | Yes       | Adaptive/efficient; commonly cited (arXiv 2303.10512)  | conf/exp_20260509_213942/config_1.yaml       |
| ia3      | Yes       | Efficient, recent SOTA method (arXiv 2205.05638)       | conf/exp_20260509_213942/config_2.yaml       |

All three are cited in: 
- https://github.com/huggingface/peft
- LoRA: https://arxiv.org/abs/2106.09685
- AdaLoRA: https://arxiv.org/abs/2303.10512
- IA3: https://arxiv.org/abs/2205.05638

## Deferred Axes
- PEFT parameters (`r`, `alpha`, `dropout`)
- learning rate
- optimizer
- warmup_steps
- batch size
- max_epochs

## Next-unlock Condition
- Need stable runs for all three method types. After stability, proceed to tuning PEFT hyperparameters for the best performer.


## Web Research Table

| Method   | Summary                                                  | Key Source(s)                       |
|----------|----------------------------------------------------------|-------------------------------------|
| lora     | Low-rank adapters, scalable, widely used, high support   | arXiv 2106.09685, HF PEFT docs      |
| adalora  | Adaptive, automatically tunes budget per-layer, flexible | arXiv 2303.10512, HF PEFT docs      |
| ia3      | Efficient, gate-based, strong for some language tasks    | arXiv 2205.05638, HF PEFT docs      |

