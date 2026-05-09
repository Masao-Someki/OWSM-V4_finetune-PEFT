# Wave Summary
This wave aims to stabilize training and improve validation WER for Portuguese ASR using diverse PEFT methods. 

## Why this config set
Three configurations were chosen to explore small adjustments around previous findings, addressing known instabilities. The focus is on decreasing the learning rate and adjusting PEFT parameters to maintain training stability, responding to recent debug failures.

## Search-space coverage
- Learning Rate: Adjusting the learning rates across configurations (1e-5, 2e-5, 3e-5) to find the optimal rate.
- PEFT Methods: Exploring different PEFT methods including LoRA, AdaLoRA, and ESPnet.
- Other hyperparameters: Testing dropout and alpha values.

## Checklist updates
- C0: Marked as DONE after confirming `prompt.txt` aligns.
- C4: Marked as DONE by limiting memory requests, ensuring stability was prioritized.

## Next action
Future waves should focus on further exploring learning rates and other axes if stability is validated. If successful outcomes are achieved, attempts to broaden the search for hyperparameters may begin.
