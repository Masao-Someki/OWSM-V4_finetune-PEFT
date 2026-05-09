# Wave Summary
This wave aims to stabilize recent configurations and explore slightly higher learning rates to determine their effects on model performance.

## Why this config set
Given the previous configurations resulted in `Killed` processes due to memory issues, we are keeping `lr` values as per the allowed range from last experimentation, prioritizing stability. Config `0` maintains the lower learning rate (`5e-5`) for safe convergence, while `1` tests the upper limit (`1e-4`) in a controlled manner to gauge its effect.

## Search-space coverage
This wave covers:
- Learning Rate (5e-5, 1e-4)
- Optimizer (AdamW) - using the same across configs.
- Batch Size (16, 32) - implicitly covered since both configs can be adjusted later depending on memory issues.

## Checklist updates
- **C1**: Marked as `TODO` because of no recent evidence.
- **C4**: Remains `TODO` due to risk of OOM; ensuring the configurations are set to avoid it.

## Next action
After this wave, the objective would be to examine if any other configurations can be tweaked without increasing the OOM risks. Further exploration could involve looking into different batch sizes if resource limits allow it.
