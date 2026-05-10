# Search Space Report

## Active Axis: PEFT Adapter Algorithm

| algorithm       | status   | comment                                       | config                                 |
|-----------------|----------|-----------------------------------------------|----------------------------------------|
| lora            | done     | Baseline/state-of-the-art adapter             | conf/exp_20260510_005653/config_0.yaml |
| adalora         | pending  | Adaptive LoRA; attempts to improve over LoRA  | conf/exp_20260510_005653/config_1.yaml |
| ia3             | pending  | Lightweight, less intrusive                   | conf/exp_20260510_005653/config_2.yaml |
| oft             | pending  | Orthogonal fusion                            | conf/exp_20260510_005653/config_3.yaml |
| vera            | pending  | Newer, variational approach                  | conf/exp_20260510_005653/config_4.yaml |
| lora_r16        | pending  | LoRA r/alpha 16; higher capacity             | conf/exp_20260510_005653/config_5.yaml |
| lora_r4         | pending  | LoRA r/alpha 4; lower capacity               | conf/exp_20260510_005653/config_6.yaml |
| adalora_r16     | pending  | AdaLoRA r/alpha 16; higher capacity          | conf/exp_20260510_005653/config_7.yaml |
| ia3_kv          | pending  | IA3 (limited targets, key/val only)          | conf/exp_20260510_005653/config_8.yaml |
| lora_extended   | pending  | LoRA w/ extended target_modules              | conf/exp_20260510_005653/config_9.yaml |

## Web-Research/Source Reference

| Method      | Key Source/Reference                                         | Comment                                   |
|-------------|-------------------------------------------------------------|-------------------------------------------|
| LoRA        | https://arxiv.org/abs/2106.09685                            | Widely adopted baseline                   |
| AdaLoRA     | https://arxiv.org/abs/2303.10512                            | Adaptive; SOTA on many benchmarks         |
| IA3         | https://arxiv.org/abs/2205.05638, Huggingface PEFT docs     | Very low-parameter, stable                |
| OFT         | https://arxiv.org/abs/2303.00917                            | Newer orthogonal fusion, promising        |
| VERA        | https://arxiv.org/abs/2310.07703                            | Variational efficient PEFT                |
| Extended LoRA | GitHub/PEFT docs, LoRA paper supplements                  | Used for comparison in recent work        |

Summary: Candidates cover state-of-the-art PEFT literature for speech/ASR as per the latest reviews in Huggingface, ESPnet, and relevant arXiv sources.
