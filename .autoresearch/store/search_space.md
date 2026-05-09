- [ ] Ensure all search space axes match `prompt.txt`.
- [ ] Enumerate explicit candidate values for each axis.

## Candidate Values

### peft parameters

| algorithm | done | comment | config |
| --- | -- | --- | --- |
| lora |   | Baseline performance |  |
| delora |   | Variants to explore from lora |  |
| adalora |   | Alternative approach to lora |  |

### Learning rate

| rate | done | comment | config |
| --- | -- | --- | --- |
| 1e-4 |   | Upper-bound test for learning rate |  |
| 5e-5 |   | Balanced learning rate |  |
| 2e-5 |   | Lower-bound test for learning rate |  |

## Next Steps

### Active Axis
- The current focus is on `peft parameters` and `learning rate`.

### Deferred Axes
- [ ] optimizer detail
- [ ] warmup_steps
- [ ] batch size
- [ ] max_epochs
