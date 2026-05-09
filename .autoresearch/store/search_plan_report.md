# Search Space Report (exp_20260509_214204 — Bootstrap)

## Active axis: PEFT method family

| method   | status | config path                                   | summary rationale                | source link                                                                              |
|----------|--------|-----------------------------------------------|----------------------------------|------------------------------------------------------------------------------------------|
| lora     | planned| conf/exp_20260509_214204/config_0.yaml        | Industry baseline, PEFT standard | [Hu et al., 2021](https://arxiv.org/abs/2106.09685), [HF PEFT](https://huggingface.co/docs/peft/main/en/index#supported-methods) |
| adalora  | planned| conf/exp_20260509_214204/config_1.yaml        | Adaptive/pruned, strong in PEFT  | [Zhang et al., 2023](https://arxiv.org/abs/2303.10512), [HF PEFT](https://huggingface.co/docs/peft/main/en/conceptual_guides/adalora) |
| ia3      | planned| conf/exp_20260509_214204/config_2.yaml        | Lightweight/efficient adaptation | [Liu et al., 2022](https://arxiv.org/abs/2205.05638), [HF PEFT](https://huggingface.co/docs/peft/main/en/conceptual_guides/ia3)    |
| veara    | planned| conf/exp_20260509_214204/config_3.yaml        | Rank-allocation method (new)     | [HF Docs](https://huggingface.co/docs/peft/main/en/conceptual_guides/veara)               |
| oft      | planned| conf/exp_20260509_214204/config_4.yaml        | Orthogonal, emerging in PEFT     | [HF Docs](https://huggingface.co/docs/peft/main/en/conceptual_guides/oft)                 |

## Key web-research sources tabulated

| source                        | relevance    | notes                                                         |
|-------------------------------|--------------|---------------------------------------------------------------|
| Hu et al., 2021 (LoRA)        | core         | PEFT original/baseline                                        |
| Zhang et al., 2023 (AdaLoRA)  | high         | Adaptive PEFT in recent libraries                             |
| Liu et al., 2022 (IA3)        | high         | Efficient/orthogonal adaptation, esp. for large model ASR     |
| HF PEFT docs                  | essential    | Enumerates all available & supported PEFT method families     |

## Next: unlock parameter fine-tuning inside winner method(s) after stability/metric review.
