# Search Space Checklist

## Rules
- [x] All axes must come from prompt.txt section 6.
- [x] This file is cumulative: append updates and preserve prior evidence/history.
- [x] Enumerate explicit candidate values only for the current active axis.
- [x] Include source links for proposed values.
- [x] Keep non-active axes deferred until the current active axis is resolved.
- [x] If the active axis is finite/categorical, enumerate the broadest practical candidate set.
- [x] If the active axis is numeric, use coarse, information-efficient values first and avoid low-signal tiny increments.

## Planning/Checkpoint

### Focus axis
- [x] PEFT method family (`method.type`)

### Why this axis now
- Initial wave, as required by prompt.txt + best practice: method family determines efficacy at the largest scale; it’s essential to know which (if any) of the standard PEFT techniques outperform baseline, before tuning hyperparameters.

### Candidate values for current focus

| value    | done | comment                                        | config path                                   | sources |
|----------|------|------------------------------------------------|-----------------------------------------------|---------|
| lora     |      | Community baseline for PEFT                    | conf/exp_20260509_214204/config_0.yaml        | [Hu et al., 2021](https://arxiv.org/abs/2106.09685), [HF docs](https://huggingface.co/docs/peft/main/en/index#supported-methods) |
| adalora  |      | Adaptive resource allocation, strong in HF PEFT| conf/exp_20260509_214204/config_1.yaml        | [Zhang et al., 2023](https://arxiv.org/abs/2303.10512), [HF docs](https://huggingface.co/docs/peft/main/en/conceptual_guides/adalora) |
| ia3      |      | Linear adaptation method, fast/easy-to-run     | conf/exp_20260509_214204/config_2.yaml        | [Liu et al., 2022](https://arxiv.org/abs/2205.05638), [HF docs](https://huggingface.co/docs/peft/main/en/conceptual_guides/ia3) |
| veara    |      | New/experimental, rank allocation              | conf/exp_20260509_214204/config_3.yaml        | [HF docs](https://huggingface.co/docs/peft/main/en/conceptual_guides/veara) |
| oft      |      | Orthogonal Fine-tuning, explorative inclusion  | conf/exp_20260509_214204/config_4.yaml        | [HF docs](https://huggingface.co/docs/peft/main/en/conceptual_guides/oft)   |

Currently tested all methods available in latest HuggingFace PEFT (v0.10+) and recent PEFT literature, focusing specifically on techniques practical for large speech/ASR finetuning.

- [ ] Current axis resolved?: no (first run, seeking baseline stability and metrics)
- [ ] Winner / best-so-far summary: N/A (awaiting results)
- Axis type: categorical
- Enumeration policy used: Complete as per current field evidence (web links above)
- Evidence/research links: See candidate row

## Deferred Axes

- [ ] PEFT parameter fine-tuning (e.g. r, alpha, dropout, per-method params)
- [ ] learning rate (lr)
- [ ] optimizer
- [ ] batch size
- [ ] max epochs

## Unlock Condition For Next Axis

- What result from the current axis allows moving on:
    - At least 3/5 configs run without runtime failure and return plausible metrics.
- Which axis should be explored next after this one:
    - PEFT parameter fine-tuning inside the top-1 or top-2 best methods by dev performance.

## Source Reference
- prompt source: prompt.txt
- planning basis: Huggingface PEFT docs, recent PEFT papers, web search as of 2024-2026
