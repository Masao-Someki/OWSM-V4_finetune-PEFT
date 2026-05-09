# Search Space Snapshot (Wave: exp_20260509_235129)

## Active Axis: PEFT Method

| algorithm     | status   | comment                           | config                                         |
|---------------|----------|-----------------------------------|------------------------------------------------|
| lora          | pending  | Baseline, most cited, r=8         | conf/exp_20260509_222054/config_0.yaml (FAILED)   |
| adalora       | pending  | Adaptive-rank, recent SOTA        | conf/exp_20260509_222054/config_4.yaml (FAILED)   |
| ia3           | pending  | Lightweight gate-based PEFT       | conf/exp_20260509_222054/config_2.yaml (FAILED)   |
| adapter       | pending  | Classic bottleneck adapters       | conf/exp_20260509_222054/config_1.yaml (FAILED)   |
| prefix_tuning | pending  | Virtual tokens, S2S, low resource | conf/exp_20260509_222054/config_3.yaml (FAILED)   |
| oft           | pending  | Orthogonal Fusion, ASR/S2S        | conf/exp_20260509_222054/config_5.yaml (FAILED)   |
| lora_r2       | pending  | LoRA, low-rank ablation           | conf/exp_20260509_222054/config_6.yaml (FAILED)   |
| lora_r32      | pending  | LoRA, high-rank ablation          | conf/exp_20260509_222054/config_7.yaml (FAILED)   |
| debug_lora    | pending  | Diagnosing all failures           | conf/exp_20260509_235129/config_0.yaml           |

All canonical methods above systematically failed (status=FAILED) at first step. Now using smallest possible LoRA config (r=4, alpha=8, 0 dropout, 3 steps) to elicit root error and trigger working pipeline.

## Web/Documentation Sources

| Method    | Citation/Link |
|-----------|---------------|
| LoRA      | https://arxiv.org/abs/2106.09685 |
| AdaLoRA   | https://github.com/jiachunfeng/Adalora |
| IA3       | https://arxiv.org/abs/2205.05638 |
| Adapter   | https://arxiv.org/abs/1902.00751 |
| PrefixTuning | https://arxiv.org/abs/2101.00190 |
| OFT       | https://arxiv.org/abs/2307.01949 |
| ESPnet PEFT | https://github.com/espnet/espnet/issues/4923 |

## Action Items

- DO NOT advance to new search axes before any PEFT candidate passes debug-gate.
- Collect/triage error-to-fix if this config fails again.

