- [ ] Ensure all search space axes match `prompt.txt`.
- [ ] Enumerate explicit candidate values for each axis.

## Candidate Values

### Algorithm

| algorithm | done | comment | config |
| --- | -- | --- | --- |
| lora |   | Basic lora as baseline | conf/exp_20260509_204840/config_0.yaml |
| delora |   | Test variant of lora | conf/exp_20260509_204840/config_1.yaml |
| adalora |   | Adaptation of lora | conf/exp_20260509_204840/config_2.yaml |

### Learning rate
- Will be extended based on results from algorithm experiments.

### Optimizer
- Will be determined in future experiments after resolving performance of algorithms.

### Batch size 
- Will be investigated after algorithm results are available.

### Max epochs 
- Will be analyzed alongside optimization and algorithm performance.

## Unlock Condition For Next Axis
- What result from the current axis allows moving on: Outcomes from the proposed algorithms.
- Which axis should be explored next after this one: Learning rate, batch size, and max epochs can be tuned next based on algorithm results.
