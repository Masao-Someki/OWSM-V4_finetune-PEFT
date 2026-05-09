# Search Space Checklist

## Candidate Values

### PEFT method

| algorithm     | status  | comment                            | config                                        | source |
|---------------|---------|------------------------------------|-----------------------------------------------|--------|
| lora          | done    | Baseline, most cited, r=8          | conf/exp_20260509_222054/config_0.yaml        |        |
| adalora       | done    | Adaptive-rank, recent SOTA         | conf/exp_20260509_222054/config_4.yaml        |        |
| ia3           | done    | Lightweight gate-based PEFT        | conf/exp_20260509_222054/config_2.yaml        |        |
| adapter       | done    | Classic bottleneck adapters        | conf/exp_20260509_222054/config_1.yaml        |        |
| prefix_tuning | done    | Virtual tokens, S2S, low resource  | conf/exp_20260509_222054/config_3.yaml        |        |
| oft           | done    | Orthogonal Fusion, speech/S2S      | conf/exp_20260509_222054/config_5.yaml        |        |
| lora_r2       | done    | LoRA, low rank ablation            | conf/exp_20260509_222054/config_6.yaml        |        |
| lora_r32      | done    | LoRA, high rank ablation           | conf/exp_20260509_222054/config_7.yaml        |        |
