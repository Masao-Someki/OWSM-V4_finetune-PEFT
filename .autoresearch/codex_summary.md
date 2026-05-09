# Wave Summary
This wave consists of configs focused on optimizing various configurations for different methods (Lora, Espnet, Adalora) with adjustments in learning rates and parameters based on previous observations.

## Why this config set
Previous experiments did not yield useful metrics; hence, this wave provides a variety of adjustments in terms of parameter settings, especially focusing on stability and avoiding runtime errors.

## Search-space coverage
The wave covers the following axes:
- Learning Rate
- Method Choice
- Method Specific Parameters

## Checklist updates
- `C0`: Remains TODO since prompt.txt must be validated.
- `C1`: Targeting a wide array of configs linked to previous findings to maximize exploration.
- `C2`: This experiment incorporates both exploration (varied learning rates and methods) and exploitation (refining the parameters).
- `C3`: All involved axes are required as per the prompt.
- `C4`: By focusing on a limited number of configs, we mitigate stability risk.
- `C5`: Outputs are designed to follow reproducibility guidelines.

## Next action
Following this wave, the next actions should focus on gathering results to refine further exploration of effective learning rate ranges and more specific method parameters.
