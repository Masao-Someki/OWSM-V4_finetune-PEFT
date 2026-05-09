# Wave Summary

## Why this config set
This wave introduces three new configurations focused on different PEFT methods: LoRA, ESPnet, and AdaLoRA. Each config explores varying learning rates and other hyperparameters. The intent is to establish a baseline performance for Portuguese ASR, leveraging the unique aspects of each method. Given we have no prior evidence from `experiments.csv`, we are adopting a conservative strategy for exploration.

## Search-space coverage
This wave covers the following axes:
- learning rate
- max_epochs (inferred as standard)
- warmup_steps (inferred as standard)
- PEFT method choice (lora, espnet, adalora)

## Checklist updates
- C0: DONE. The input from `prompt.txt` has been thoroughly confirmed and is consistent.
- C1: TODO. No previous evidence exists due to no prior experiments.
- C2: DONE. This wave includes both exploitation (with a conservative learning rate) and exploration (more aggressive learning rates in other configs).
- C4: DONE. The current wave cautiously limits configurations to avoid training instabilities.
- C3: TODO. Coverage extends into several axes, yet there remains a need to track further PEFT method explorations.

## Next action
- The subsequent wave should target C1 for evidence gathering from the current wave and aim for broader exploration of the PEFT methods based on the outcomes.
