# Search Space Checklist

- [ ] Ensure all search space axes match `prompt.txt`.
- [ ] Enumerate explicit candidate values for each axis.

## Candidate Values

### peft parameters

| algorithm | done | comment | config |
| --- | -- | --- | --- |
| lora |  | Initial baseline | |
| delora |  | To be explored | |
| adalora |  | To be explored | |

## Learning Rate Candidates
The following learning rate candidates are proposed for this wave, each influencing the model's update steps:

| lr       | done | comment | config |
| -------- | ---- | ------- | ----- |
| 1e-5     |      | Starting point for exploration | |
| 2e-5     |      | Small increments for fine tuning | |
| 3e-5     |      | Continuing to modulate the learning pace | |
| 5e-5     |      | Mid-range approach to evaluate impacts | |
| 1e-4     |      | Boundary check for maximum learning rate | |

### Experimental Focus
- Current active axis: `lr`
- Frozen axes: `method`, `batch size`, `warmup_steps`, etc.

- [ ] Current axis resolved? No
- [ ] Winner / best-so-far summary: None yet
- [ ] Axis type: `numeric`
- [ ] Enumeration policy used: Coarse, information-efficient.

## Evidence links:
- Learning rates and their effects: [Towards Data Science](https://towardsdatascience.com/learning-rate-and-its-impact-on-training-a-deep-neural-network-9c4d1b1e8fe2)
- Lora method fundamentals: [Research paper on PEFT](https://arxiv.org/pdf/2008.05175.pdf)
