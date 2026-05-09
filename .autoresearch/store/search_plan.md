# Search Space Checklist

- [x] Ensure all search space axes match `prompt.txt`.
- [x] Enumerate explicit candidate values for each axis.

## Candidate Values

### Wave 1: PEFT method
**Why first**: Literature and prompt emphasize PEFT method as the most fundamental design decision; must establish a strong baseline before tuning any hyperparameters.

| candidate | status | comment | config | source |
| --- | --- | --- | --- | --- |
| lora | pending | Most common PEFT baseline, stable and widely supported | conf/exp_20260509_215758/config_0.yaml | [LoRA paper](https://arxiv.org/abs/2106.09685), [HuggingFace PEFT](https://huggingface.co/docs/peft/index) |
| adalora | pending | Adaptive LoRA variant, competitive in benchmarks | conf/exp_20260509_215758/config_1.yaml | [AdaLoRA paper](https://arxiv.org/abs/2303.10512) |
| ia3 | pending | Lightweight, parameter-efficient adapter | conf/exp_20260509_215758/config_2.yaml | [IA3 paper](https://arxiv.org/abs/2205.05638) |
| vera | pending | Newer, promising PEFT method | conf/exp_20260509_215758/config_3.yaml | [VERA repo](https://github.com/microsoft/VERA) |
| oft | pending | Output Feature Tuning, for completeness | conf/exp_20260509_215758/config_4.yaml | [PEFT Survey](https://arxiv.org/abs/2309.07308) |

**Unlock condition**: Complete all method trials and select the best observed performer(s) (based on WER/CER/validation loss evidence) for follow-up parameter search.

---

### Wave 2: PEFT hyperparameters (for winner from Wave 1)
**Why second**: Strong dependence of most PEFT methods (especially LoRA-family) on parameters `r`, `alpha`, and `dropout`. Each method could have distinct best parameters.

| candidate                 | status | comment | config | source |
|---------------------------|--------|---------|--------|--------|
| r: 4, 8, 16, 32           | pending | Coverage of small to moderate adaptation ranks |        | [LoRA/HF docs](https://huggingface.co/docs/peft/package_reference/lora) |
| alpha: 8, 16, 32, 64      | pending | Standard LoRA-scale factors |        | [LoRA/HF docs](https://huggingface.co/docs/peft/package_reference/lora) |
| dropout: 0.01, 0.05, 0.1  | pending | Literature baseline and common values |        | [PEFT survey](https://arxiv.org/abs/2309.07308) |

**Unlock condition**: Best method confirmed stable, then sweep parameters to optimize fine-grained performance.

---

### Wave 3: Learning rate

| candidate      | status | comment | config | source |
| -------------- | ------ | ------- | ------ | ------ |
| 1e-5           | pending | Small, conservative |        | [HF transformers docs](https://huggingface.co/docs/transformers/v4.30.0/en/main_classes/trainer#transformers.TrainingArguments) |
| 5e-5           | pending | Typical for PEFT |        | |
| 1e-4           | pending | Baseline (currently in template) |        | |
| 5e-4           | pending | For learning-rate robustness |        | |

**Unlock:** Winner from prior wave, best validated `r/alpha/dropout`, then LR sweep.

---

### Wave 4: Optimizer

| candidate | status | comment | config | source |
| --- | --- | --- | --- | --- |
| adamw | pending | Baseline, default for transformers | | [HF default](https://huggingface.co/docs/transformers/v4.30.0/en/main_classes/optimizer_schedules#transformers.AdamW) |
| adam | pending | Without weight decay | | |
| adamw8bit | pending | Low memory variant | | [bitsandbytes](https://github.com/TimDettmers/bitsandbytes) |

**Unlock:** Best method/param/lr setting found; now robustify to optimizer choice.

---

### Wave 5: Warmup steps

| candidate | status | comment | config | source |
| --- | --- | --- | --- | --- |
| 0 | pending | No warmup | | |
| 100 | pending | Short warmup | | |
| 1000 | pending | Default (transformers) | | |
| 5000 | pending | Large warmup | | |

**Unlock:** Only after optimizer/lr/method baselines are stable.

---

### Wave 6: Batch size

| candidate  | status | comment | config | source |
| ---------- | ------ | ------- | ------ | ------ |
| 2          | pending | Baseline, fits on most GPUs | | |
| 4          | pending | Used in initial default and common setups | | |
| 8          | pending | For scale | | |

**Unlock:** Only after prior learning-rate/warmup/optimizer stability.

---

### Wave 7: Max epochs

| candidate | status | comment | config | source |
| --- | --- | --- | --- | --- |
| 1   | pending | Early stopping check | | |
| 2   | pending | Short run | | |
| 5   | pending | Common for typical PEFT | | |
| 10  | pending | Full-length adaptation | | |

**Unlock:** Final run for best configuration.

