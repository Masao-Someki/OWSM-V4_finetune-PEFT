# Search Space Checklist

- [x] Ensure all search space axes match `prompt.txt`.
- [x] Enumerate explicit candidate values for each axis.

## Candidate Values

### PEFT Adapter Algorithm (Active)

| algorithm         | status   | comment                                    | config                                    |
|-------------------|----------|--------------------------------------------|-------------------------------------------|
| lora              | done     | Baseline/state-of-the-art adapter          | conf/exp_20260510_005653/config_0.yaml    |
| adalora           | pending  | Adaptive LoRA; proposed to improve LoRA    | conf/exp_20260510_011047/config_1.yaml    |
| ia3               | pending  | Lightweight gain method                    | conf/exp_20260510_011047/config_2.yaml    |
| oft               | pending  | Orthogonal fusion networks                 | conf/exp_20260510_011047/config_3.yaml    |
| vera              | pending  | Variational efficient reparam              | conf/exp_20260510_011047/config_4.yaml    |
| lora_r16          | pending  | LoRA r/alpha 16; higher capacity           | conf/exp_20260510_011047/config_5.yaml    |
| lora_r4           | pending  | LoRA r/alpha 4; lower capacity             | conf/exp_20260510_011047/config_6.yaml    |
| adalora_r16       | pending  | AdaLoRA r/alpha 16; higher capacity        | conf/exp_20260510_011047/config_7.yaml    |
| ia3_kv            | pending  | IA3 with limited target modules            | conf/exp_20260510_011047/config_8.yaml    |
| lora_extended     | pending  | LoRA with extended target_modules          | conf/exp_20260510_011047/config_9.yaml    |

Experimented all parameters?: no
Summary: All state-of-the-art PEFT algorithms for ASR enumerated with literature-supported parameter values; will move to optimizer/lr after first baseline.

### Learning rate
- Will be extended after all the experiments from PEFT axis have been finished.

### optimizer
- Will be extended after all the experiments from PEFT axis have been finished.

### warmup_steps
- Will be extended after all the experiments from PEFT axis have been finished.

### batch size
- Will be extended after all the experiments from PEFT axis have been finished.

### max_epochs
- Will be extended after all the experiments from PEFT axis have been finished.

