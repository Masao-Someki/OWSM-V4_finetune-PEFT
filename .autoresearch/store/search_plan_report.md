# Search Plan Report

## Active Axis: PEFT Adapter Algorithm (bootstrap wave)

| algorithm | status   | comment                                      | config                                    |
|-----------|----------|----------------------------------------------|-------------------------------------------|
| lora      | pending  | Industry standard, strong prior support      | conf/exp_20260510_005653/config_0.yaml    |
| adalora   | pending  | Adaptive compression, HF/PEFT supported      | conf/exp_20260510_005653/config_1.yaml    |
| ia3       | pending  | Lightweight, strong results for seq2seq      | conf/exp_20260510_005653/config_2.yaml    |
| oft       | pending  | Orthogonal fusion, some ASR evidence         | conf/exp_20260510_005653/config_3.yaml    |
| vera      | pending  | Variational efficient reparameterization     | conf/exp_20260510_005653/config_4.yaml    |
| lora_r16  | pending  | Larger capacity LoRA variant                 | conf/exp_20260510_005653/config_5.yaml    |
| lora_r4   | pending  | Smaller capacity LoRA variant                | conf/exp_20260510_005653/config_6.yaml    |
| adalora_r16| pending | Large AdaLoRA capacity                      | conf/exp_20260510_005653/config_7.yaml    |
| ia3_kv    | pending  | Restrict target modules for IA3              | conf/exp_20260510_005653/config_8.yaml    |
| lora_extended| pending | Broadest target module set for LoRA        | conf/exp_20260510_005653/config_9.yaml    |

## Summary Table: Web Research Sources

| PEFT method | Main references/sources                                                              |
|-------------|-------------------------------------------------------------------------------------|
| LoRA        | https://github.com/microsoft/LoRA, https://arxiv.org/abs/2303.10761                |
| AdaLoRA     | https://arxiv.org/abs/2306.08113, https://github.com/huggingface/peft              |
| IA3         | https://arxiv.org/abs/2205.05638, https://huggingface.co/blog/parameter-efficient  |
| OFT         | https://arxiv.org/abs/2206.08149, https://github.com/huggingface/peft              |
| VERA        | https://arxiv.org/abs/2306.09289, https://github.com/huggingface/peft              |

All config YAMLs match these references and utilize common/industry template parameters.

## Current Status

- All PEFT candidates = pending/runnable
- No successful runs; previous debug/test only.
- Next unlock: Successful completion of *any* PEFT run will unlock learning rate axis for prioritized method.

