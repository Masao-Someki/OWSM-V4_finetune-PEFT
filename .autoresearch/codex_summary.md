# Wave Summary

This wave focuses on refining configurations based on the failure of the previous wave, specifically addressing the training instability issues. 

## Why this config set
The previous experiments resulted in multiple debug failures likely due to inadequate memory allocation and inappropriate hyperparameters. By adjusting the learning rates and exploring different PEFT configurations (LORA, ESPnet, and ADALORA) close to the best known configurations, we aim to stabilize and improve performance.

## Search-space coverage
This wave explores:
- Learning rate
- PEFT method choice 

Each configuration utilizes a stable PEFT method while varying the learning rate, facilitating a focused exploration that adheres to the existing search space.

## Checklist updates
- C0: Status changed from TODO to DONE after confirming the prompt file's completeness.
- C1: Initial status set to TODO. The configurations are based on reviewed metrics from the last failed run to steer towards better performance.
- C4: Status set to DOING, with plans to run minimal tests and observe stability before broadening the search again.

## Next action
The next wave should target:
- Validating the stability of the training process with a narrow range of configurations.
- Reassessing the best-performing configurations and exploring options for a full-scale expansion once stability is confirmed.
