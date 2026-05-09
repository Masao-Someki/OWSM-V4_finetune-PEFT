# Wave Summary
This wave aims to address the training stability concerns observed in the previous wave, focusing on dialing in effective configurations with known PEFT methods and careful adjustments of hyperparameters.

**Why this config set**: 
The choice of configurations is informed by the debug failures observed in `exp_20260509_011856`, where configurations did not successfully initiate due to potential memory constraints and instability. Maintaining a focus on key PEFT types that were previously shown to yield more stable results informs our configuration choices.

**Search-space coverage**: 
This wave explores:
- Learning rate (using `5e-5`, `1e-4`, `3e-5`).
- PEFT method choice (using `lora`, `espnet`, and `adalora`).

**Checklist updates**: 
- `C0`: Updated to DONE as the prompts are now complete and configurations have been generated correctly.
- `C1`: In progress as configs are based on previous failures, looking for improvements in WER.
- `C4`: Still TODO, as we are prioritizing debugging and stability given previous instability issues.

**Next action**: 
Plan to validate the configurations through successful debug runs, and once stability is confirmed, proceed to explore the maximum extent of the parameter space for further improvements on the batch size and epochs in subsequent waves.
