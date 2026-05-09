# Findings Log

## 2026-05-09T21:42:04Z — Bootstrap initialization

- Planned and launched a 5-way sweep across core PEFT families: lora, adalora, ia3, veara, oft.
- All inherit the same core configuration except for `method.type` to maximize comparability.
- This will reveal if any method is nonfunctional (runtime/fitting error) and, for those that work, provide preliminary metric comparability for the ASR task.
- All other sweep axes (LR, optimizer, etc.) are locked; no exploration here in this round.
- Web research confirms these families cover the major supported PEFT algorithms as of 2024–2026 for large-model ASR.
- Next step: if all stable, begin method-specific or parameter-specific finetuning.
