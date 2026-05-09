# Wave Summary
This wave aims to ensure stability first before undergoing broader exploration of parameters. Due to the instability issues in the prior experiment, we are enforcing a smaller batch of configurations focusing on learning rate, method choice, and memory adjustments.

**Why this config set**: Evidence from prior runs indicated high memory usage leading to failures. Each configuration aims to balance the learning rate and ranks in accordance with the identified parameters from the PEFT library.

**Search-space coverage**: This wave covers:
- Learning rate
- Optimizer and method choices
- PEFT-specific parameters

**Checklist updates**:
- `C0`: Updated to TODO as `prompt.txt` is confirmed.
- `C1`: Updated to TODO as we are using configurations that were tested in the last wave.
- `C2`: Updated to TODO as we aim for a mix of exploitation (narrowing down successful parameters) and exploration (testing variations in rank and methods).

**Next action**: If stability is assured, the next wave will focus on fine-tuning remaining hyperparameters, such as batch size and epochs, based on the observations from this set of results.
