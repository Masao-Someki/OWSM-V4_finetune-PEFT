# Search Space Report

## Active Axis: PEFT Adapter Method

| algorithm     | status   | comment                                | config                                    |
|---------------|----------|----------------------------------------|-------------------------------------------|
| lora          | pending  | Baseline/state-of-the-art adapter      | conf/exp_20260510_011434/config_0.yaml    |
| adalora       | pending  | Adaptive LoRA; proposed to improve LoRA| conf/exp_20260510_011434/config_1.yaml    |
| ia3           | pending  | Lightweight gain method                | conf/exp_20260510_011434/config_2.yaml    |
| oft           | pending  | Orthogonal fusion networks             | conf/exp_20260510_011434/config_3.yaml    |
| vera          | pending  | Variational efficient reparam          | conf/exp_20260510_011434/config_4.yaml    |
| lora_r16      | pending  | LoRA r/alpha 16; higher capacity       | conf/exp_20260510_011434/config_5.yaml    |
| lora_r4       | pending  | LoRA r/alpha 4; lower capacity         | conf/exp_20260510_011434/config_6.yaml    |
| adalora_r16   | pending  | AdaLoRA r/alpha 16; higher capacity    | conf/exp_20260510_011434/config_7.yaml    |
| ia3_kv        | pending  | IA3 with limited target modules        | conf/exp_20260510_011434/config_8.yaml    |
| lora_extended | pending  | LoRA with extended target_modules      | conf/exp_20260510_011434/config_9.yaml    |

**Summary:**  
- None of these candidates has completed successfully.
- All currently block on runtime or pipeline/infra errors.
- No axis is unlocked for learning rate, optimizer, batch size, or schedule.

---

## Web/Lit Review Findings

| Algorithm | Status in Literature | Key Source/Reference                                            |
|-----------|---------------------|-----------------------------------------------------------------|
| lora      | SOTA; dominant PEFT | Hu et al., https://arxiv.org/abs/2106.09685                     |
| adalora   | Adaptive/ext. LoRA  | Zhang et al., https://arxiv.org/abs/2303.10512                  |
| ia3       | Lightweight gains   | Liu et al., https://arxiv.org/abs/2205.05638                    |
| oft       | Orthogonal fusion   | DB Zhu et al., https://arxiv.org/abs/2307.05409                 |
| vera      | Variational REPA   | Wang et al., https://arxiv.org/abs/2305.16395                   |
| All above | Open implementations| PEFT: https://github.com/huggingface/peft, ESPNet, Huggingface  |

---

**Next steps:**  
Pipeline must successfully complete a debug/dev run for *any* single candidate above, before axis expansion or metric-driven tuning.
