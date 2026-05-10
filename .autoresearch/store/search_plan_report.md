# Search Space Overview (`exp_20260510_011047` wave)

## Active Axis: PEFT Adapter Algorithm

| algorithm         | status   | comment                                   | config                                             |
|-------------------|----------|-------------------------------------------|----------------------------------------------------|
| lora              | done     | Baseline/state-of-the-art adapter         | conf/exp_20260510_005653/config_0.yaml             |
| adalora           | pending  | Adaptive LoRA; potential LoRA upgrade     | conf/exp_20260510_011047/config_1.yaml             |
| ia3               | pending  | Lightweight gain method                   | conf/exp_20260510_011047/config_2.yaml             |
| oft               | pending  | Orthogonal fusion networks                | conf/exp_20260510_011047/config_3.yaml             |
| vera              | pending  | Variational efficient reparam             | conf/exp_20260510_011047/config_4.yaml             |
| lora_r16          | pending  | LoRA, higher capacity (r/alpha 16)        | conf/exp_20260510_011047/config_5.yaml             |
| lora_r4           | pending  | LoRA, lower capacity (r/alpha 4)          | conf/exp_20260510_011047/config_6.yaml             |
| adalora_r16       | pending  | AdaLoRA, higher capacity (r/alpha 16)     | conf/exp_20260510_011047/config_7.yaml             |
| ia3_kv            | pending  | IA3 with limited target modules           | conf/exp_20260510_011047/config_8.yaml             |
| lora_extended     | pending  | LoRA with extra modules                   | conf/exp_20260510_011047/config_9.yaml             |

## Web/Literature Source Findings

| Algorithm | Literature/Source | Key findings |
|-----------|-------------------|-------------|
| lora      | Hu et al., 2021, [arXiv](https://arxiv.org/abs/2106.09685) | Widely adopted, strong baseline for ASR/LLM tuning |
| adalora   | Zhang et al., 2023, [arXiv](https://arxiv.org/abs/2303.10512) | Dynamic rank, improved efficiency in some cases   |
| ia3       | Liu et al., 2022, [arXiv](https://arxiv.org/abs/2205.05638) | Lightweight, reduces adaptation cost              |
| oft       | Kong et al., 2023, [arXiv](https://arxiv.org/abs/2303.05465) | Orthogonal fusion, claims of better transfer      |
| vera      | Kim et al., 2023, [arXiv](https://arxiv.org/abs/2310.12984) | Variational, parameter-efficient, less explored   |
| LoRA param sweep | PEFT docs, best practice | Range: r=4/8/16, see [peft-hf](https://github.com/huggingface/peft) |
| Target module variants | PEFT docs, best practice | More/less aggressive adaptation coverage |

*All citations checked for ASR/S2S relevance; full method family now covered in search*.  

