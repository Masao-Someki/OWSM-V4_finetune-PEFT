# Wave Summary: exp_20260509_214204 (Bootstrap)

## Why this config set

**Bootstrap mode**: With no prior runs (experiments.csv is empty) and following prompt.txt, begin with a method-family sweep of PEFT methods as published in recent literature and summarized in leading libraries, especially [PEFT by HuggingFace](https://huggingface.co/docs/peft/main/en/index#supported-methods), and referenced in up-to-date open source speech/ASR works.

We test key algorithmic axes:

- **lora**: The community standard/baseline for PEFT—well-supported with clear benchmarks in literature.
  - Source: [Hu et al., 2021](https://arxiv.org/abs/2106.09685)

- **adalora**: Adaptive extension for LoRA, impactful on several benchmarks.
  - Source: [Zhang et al., 2023](https://arxiv.org/abs/2303.10512), [Huggingface](https://huggingface.co/docs/peft/main/en/conceptual_guides/adalora)

- **ia3**: Linear adaptation method for improved efficiency.
  - Source: [Liu et al., 2022](https://arxiv.org/abs/2205.05638), [Huggingface](https://huggingface.co/docs/peft/main/en/conceptual_guides/ia3)

- **veara**: Recent rank allocation method, promising for some tasks but used less in ASR (exploratory inclusion).
  - Source: [PEFT docs](https://huggingface.co/docs/peft/main/en/conceptual_guides/veara)

- **oft**: Orthogonal Fine-tuning, representing a distinct adaptation route.
  - Source: [PEFT docs](https://huggingface.co/docs/peft/main/en/conceptual_guides/oft)

All other axes (optimizer, learning rate, batch size) are left at recommended defaults in the bootstrap sweep for clear baseline comparability per prompt and sequential policy.

## Search-space coverage

**This wave sweeps only the `method` (PEFT algorithm type) axis.**
- lora, adalora, ia3, veara, oft
- All with r/alpha/dropout same as original baseline (to lock control variables)

Deferred: Learning rate, optimizer, scheduler, and other hyperparameters (per sequential policy in prompt.txt).

## Checklist updates

- [x] Search space policy followed: All initial method axis values explored.
- [x] C0 (stability/smoketest): Should detect major runtime/model issues in at least 5 PEFT method families.
- [ ] Method effectiveness: Next—compare metrics to determine best families; only then unlock further axes.
- [ ] Hyperparameter range/exploration (LR/opt/etc.): Not started.

## Next action

**After this wave:**
- Review completion/stability for these 5 method configs.
- If all run successfully, compare dev/test metrics to select the top 1–2 for deeper per-method hyperparameter tuning (learning rate, LoRA parameters, etc.).
- If any fail (e.g. runtime or training errors), replace with fallback/baseline method for diagnostic next wave.
- Do not unlock learning rate or other axes until the method family winner(s) are known.
