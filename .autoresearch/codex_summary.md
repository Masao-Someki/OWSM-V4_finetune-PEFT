# Wave Summary

**Why this config set**: This wave focuses on a mixture of exploitation and slight exploration based on previous runs. Config 0 is a refinement of the best-performing Lora settings from prior experiments. Config 1 explores a different PEFT method for comparison, and Config 2 delves deeper into Adalora variations, intentionally using a lower learning rate to stabilize training.

**Search-space coverage**: The axes covered in this wave include:
- learning rate (5e-5 for Lora and ESPnet; reduced to 5e-6 for Adalora)
- PEFT method choices (Lora, ESPnet, Adalora)

**Checklist updates**: 
- C0 status remains `DOING` as no new evidence directly resolving prompt integrity has emerged.
- C1 is now `DOING`, backed by past run outcomes, suggesting configurations that need further examination.
- C2 moves to `DOING` with the inclusion of two variants (Lora and ESPnet) seeking to define the most effective PEFT method.

**Next action**: The subsequent wave should target a more focused exploration of learning rates and max_epochs to further optimize run stability, addressing memory concerns observed during earlier failures.
