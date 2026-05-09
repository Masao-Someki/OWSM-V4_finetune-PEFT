# Search Space Checklist

- [x] Ensure all search space axes match `prompt.txt`.
- [x] Enumerate explicit candidate values for each axis.

## Candidate Values

### PEFT Method Choice

| method   | done | comment                          | config                                  |
|----------|------|----------------------------------|-----------------------------------------|
| lora     |      | Baseline PEFT method             | conf/exp_20260509_194955/config_0.yaml |
| delora   |      | Variant of lora                  | conf/exp_20260509_194955/config_1.yaml |
| adalora  |      | Adaptive method exploration       | conf/exp_20260509_194955/config_2.yaml |

- As this is the first experimental wave, understanding which PEFT method performs best will illuminate next paths.

## Next Steps

- **Unlock Condition**: Success with the current methods will guide towards determining learning rates and optimizers in the next wave.
