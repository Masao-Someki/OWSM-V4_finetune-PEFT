# Search Space Checklist

## Candidate Values

### PEFT Algorithm

| algorithm | done | comment | config |
| --- | --- | --- | --- |
| lora | pending | strong baseline; widely used | conf/exp_20260510_013346/config_0.yaml |
| adalora | pending | adapts rank; very parameter-efficient | conf/exp_20260510_013346/config_1.yaml |
| ia3 | pending | lightweight gating | conf/exp_20260510_013346/config_2.yaml |
| oft | pending | output factorization tuning | conf/exp_20260510_013346/config_3.yaml |
| vera | pending | vector representation adapter | conf/exp_20260510_013346/config_4.yaml |

Experimented all algorithms?: no

Summary:
No PEFT method has yet run to completion. This wave compares all canonical, practical PEFT methods in this setting using equal/fair hyperparameters to establish the baseline winner and identify any immediate incompatibility/stability risks.

### PEFT hyperparameters
- Will be extended after all the experiments from PEFT methods (above) have been finished.

### Learning rate
- Will be extended after all the experiments from PEFT methods have been finished.

### optimizer
- Will be extended after all the experiments from PEFT methods have been finished.

### warmup_steps
- Will be extended after all the experiments from PEFT methods have been finished.

### batch size
- Will be extended after all the experiments from PEFT methods have been finished.

### max_epochs
- Will be extended after all the experiments from PEFT methods have been finished.
