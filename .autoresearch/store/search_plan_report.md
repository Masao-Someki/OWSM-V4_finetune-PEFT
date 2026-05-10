# Search-Space Snapshot and Findings Summary

## Active Axis: PEFT Method (All candidates tried)
| algorithm     | status  | comment                            | config                                        |
|---------------|---------|------------------------------------|-----------------------------------------------|
| lora          | done    | Baseline, most cited, r=8          | conf/exp_20260509_222054/config_0.yaml        |
| adalora       | done    | Adaptive-rank, recent SOTA         | conf/exp_20260509_222054/config_4.yaml        |
| ia3           | done    | Lightweight gate-based PEFT        | conf/exp_20260509_222054/config_2.yaml        |
| adapter       | done    | Classic bottleneck adapters        | conf/exp_20260509_222054/config_1.yaml        |
| prefix_tuning | done    | Virtual tokens, S2S, low resource  | conf/exp_20260509_222054/config_3.yaml        |
| oft           | done    | Orthogonal Fusion, speech/S2S      | conf/exp_20260509_222054/config_5.yaml        |
| lora_r2       | done    | LoRA, low rank ablation            | conf/exp_20260509_222054/config_6.yaml        |
| lora_r32      | done    | LoRA, high rank ablation           | conf/exp_20260509_222054/config_7.yaml        |

**All PEFT method sweep configs ran, but all failed at debug-gate (see experiments.csv).**

---

## Web Research Source Highlights
| source  | key points |
| ------- | ---------- |
| HuggingFace PEFT docs<br>https://huggingface.co/docs/peft/index | All listed methods (LoRA, AdaLoRA, IA3, adapters, prefix, OFT) supported and appropriate for baselines. |
| ESPnet/PEFT speech repo docs<br>https://github.com/espnet/espnet | Mentions LoRA and OFT as first-line PEFT for S2S speech; recommends debug/test configs for infra, as done here. |
| LoRA/adapters survey<br>https://arxiv.org/abs/2303.05983 | Confirms broad empirical coverage with chosen candidates. |

---

## Current Coverage
Every major categorical method candidate attempted; next wave should address root cause of systematic debug/test failures, not additional PEFT variants.
