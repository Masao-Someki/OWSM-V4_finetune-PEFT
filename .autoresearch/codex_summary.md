# Wave Summary
- **Why this config set**: The selection is derived from previous experiments indicating stability issues with configurations exhibiting lower learning rates (e.g., lr at 5e-5 producing failures). The configs in this wave focus on adjusted learning rates and varied PEFT types to address potential memory issues from previous runs.
- **Search-space coverage**: This wave covers `learning rate`, `max_epochs`, `warmup_steps`, `PEFT method choice`, and `data ratio` as laid out in prompt.txt while working within the feedback provided from failed runs.
- **Checklist updates**: 
  - `C1` now marked as DONE as the configs are grounded in recent evidence from experiments.csv suggesting memory constraints and stability; adjustments in LR and configurations show this wave's focus on critical exploration.
  - `C4` now marked as DONE, as we've ensured no introduction of new axes without first addressing stability.
- **Next action**: The following wave should focus on further validating the learned configurations and expanding towards optimally fine-tuning parameters such as `max_epochs` and `data ratio` while observing any emerging stability issues.
