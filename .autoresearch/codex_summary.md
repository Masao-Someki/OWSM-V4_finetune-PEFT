# Wave Summary

**Why this config set**: 
This first wave includes configurations that span different PEFT methods (LoRA, ESPnet, and AdaLoRA) to test a range of approaches with different parameter settings. The learning rates and parameters were selected conservatively to minimize the risk of training instability.

**Search-space coverage**: 
This wave covers the following axes:
- Learning rate
- Max epochs
- Warmup steps
- PEFT method choice
- Data ratio

**Checklist updates**: 
- C0: updated to DONE; the configurations are now defined correctly.
- C4: marked as TODO; we will monitor stability as we execute these initial runs.

**Next action**: 
The next wave should continue monitoring stability while expanding the search around successful configurations from this wave. Target further exploration into learning rate and max epochs for selected methods based on preliminary results.
