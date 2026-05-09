# Wave Summary

## Why this config set

This is the first (bootstrap) wave for the project. No prior experiments are present (experiments.csv is empty). Thus, we are focusing on the **primary axis: PEFT method choice** using the core candidate PEFT methods discovered through web research and referenced in planning.md. Candidate methods are:
- **LoRA**: Standard strong baseline for PEFT ([PEFT paper](https://arxiv.org/abs/2106.09685), [HuggingFace PEFT](https://huggingface.co/docs/peft/index)).
- **AdaLoRA**: Adaptive LoRA variant, recent and widely benchmarked ([AdaLoRA paper](https://arxiv.org/abs/2303.10512)).
- **IA3**: Lightweight and fast well-known adapter ([IA3 paper](https://arxiv.org/abs/2205.05638)).
- **VERA**: Recent PEFT technique with promising results ([VERA repo](https://github.com/microsoft/VERA)).
- **OFT**: Output Feature Tuning, used in recent PEFT literature ([PEFT: A Survey](https://arxiv.org/abs/2309.07308)).

All five configs share common hyperparameters with LoRA-style models for parameters such as `r`, `alpha`, and `dropout` unless the method doesn't require them (e.g., IA3).

## Search-space coverage

- **Axis covered:** PEFT method (categorical)
- **Values:** lora, adalora, ia3, vera, oft
- All other axes remain at base defaults; the next wave will sweep the best method over additional axes.

## Checklist updates
- [x] PEFT method coverage: first exploratory round for all major PEFT types
- [ ] Peft parameters: pending
- [ ] Learning rate: pending
- [ ] Optimizer: pending
- [ ] Warmup steps: pending
- [ ] Batch size: pending
- [ ] Max epochs: pending

## Next action

Once results for all methods are available, shortlist the best method(s) and advance to exploring PEFT parameter sweeps for the best-performing one, per the roadmap. If instability or failure in any config, lock down and debug before expanding parameter search.
