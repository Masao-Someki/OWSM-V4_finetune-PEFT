# Search Space Checklist

- [ ] Ensure all search space axes match `prompt.txt`.
- [ ] Enumerate explicit candidate values for each axis.

## Candidate Values

### PEFT method choice

| method  | done | comment                         | config |
| ------- | ---- | ------------------------------- | ------ |
| lora    | x    | Baseline: well-documented method | conf/exp_20260509_194113/config_0.yaml |
| adalora |      | Variation: exploring alternatives | conf/exp_20260509_194113/config_1.yaml |

Experimented all parameters?: no
Summary: The approach to experiment first with `lora` provides a grounded baseline, while `adalora` introduces boundary exploration.

### learning rate
- Will be extended after the PEFT methods have been validated.

### optimizer
- Will be extended after the PEFT methods have been validated.

### batch size
- Will be extended after the PEFT methods have been validated.

### max_epochs
- Will be extended after the PEFT methods have been validated.

### warmup_steps
- Will be extended after the PEFT methods have been validated.
