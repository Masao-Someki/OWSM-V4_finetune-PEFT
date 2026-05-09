# Wave Summary

## Why this config set
This set is designed to refine conditions from the previous debug failures. Each configuration aims to adjust learning rates, explore varying PEFT methods, and manage dropout rates to ensure stability and performance improvements based on previous evidence. The choice of parameters is informed by maintenance of model integrity while searching for better WER outcomes, particularly in Portuguese ASR.

## Search-space coverage
This wave covers:
- learning rate
- PEFT method choice
- dropout rate
- max_epochs 

We ensure we are not expanding on any axes beyond those listed in `prompt.txt`, in response to the recent instability and debug failures.

## Checklist updates
- **C0**: Updated from `TODO` to `DONE` as the prompt has been reviewed and conforms to requirements.
- **C1**: In progress as we utilize evidence from the previous failures to inform this wave.
- **C4**: Updated from `TODO` to `DONE` since adjustments to configurations have been made to mitigate resource risks.

## Next action
The next wave should focus on continued exploration of configurations that provide worse-than-expected outcomes. Given the pending status on evidence utilization, I suggest iterating on the learning rates and PEFT method configurations, along with observing training stability under the new setups.
