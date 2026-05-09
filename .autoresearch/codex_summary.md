# Wave Summary
This wave aims to improve Portuguese ASR quality by exploring the PEFT configurations around known issues from the previous runs. It adopts a debug-first approach to ensure stability during model training.

### Why this config set
Given the need to address the recent issues of memory and training instability encountered in the previous wave, we have focused on configs that optimize both parameters and computational efficiency. Configurations have been selected based on previous evidence suggesting potential success in reducing validation WER.

### Search-space coverage
This wave covers the following axes defined in `prompt.txt`:
- learning rate
- max_epochs
- warmup_steps
- PEFT method choice
- data ratio

### Checklist updates
- C0: marked as DONE as all necessary parameters and constraints for config generation are defined.
- C1: marked as TODO as there are still no complete recent experiment results available to reference.
- C4: marked as TO DO since we are still validating the training stability due to memory issues.

### Next action
The subsequent wave should aim to resolve C1 by incorporating results from these configurations. This will require evaluation of the experiments to identify valid next steps based on collected metrics.
