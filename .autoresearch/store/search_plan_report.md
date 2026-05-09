# Search Space Summary & Web Research Table

## Axis: PEFT method

| Method   | Description                              | Source                                                         |
|----------|------------------------------------------|----------------------------------------------------------------|
| lora     | Low-rank adaptation, canonical baseline  | [LoRA paper](https://arxiv.org/abs/2106.09685), [HF PEFT](https://huggingface.co/docs/peft/index) |
| adalora  | Adaptive LoRA (dynamic rank)             | [AdaLoRA paper](https://arxiv.org/abs/2303.10512)              |
| ia3      | Lightweight additive adaptation          | [IA3 paper](https://arxiv.org/abs/2205.05638)                  |
| vera     | Parameter-efficient, recent, fast        | [VERA repo](https://github.com/microsoft/VERA)                 |
| oft      | Output Feature Tuning                    | [PEFT Survey](https://arxiv.org/abs/2309.07308)                |

All above are supported in recent papers and/or the HuggingFace PEFT repo.

## Web References
| Name         | Key Takeaway                                                                                      | Source |
|--------------|--------------------------------------------------------------------------------------------------|--------|
| LoRA         | Most widely used PEFT adapter; easy to tune                                                      | [LoRA paper](https://arxiv.org/abs/2106.09685) |
| AdaLoRA      | Dynamic parameter budget allocation; strong results                                              | [AdaLoRA paper](https://arxiv.org/abs/2303.10512) |
| IA3          | Small, minimal-overhead, less expressive than LoRA but more stable                               | [IA3 paper](https://arxiv.org/abs/2205.05638) |
| VERA         | Fast inference, low adaptation cost; promising but not as widely benchmarked as LoRA/AdaLoRA     | [VERA repo](https://github.com/microsoft/VERA) |
| OFT          | Stable, less common, explored for coverage                                                       | [PEFT Survey](https://arxiv.org/abs/2309.07308) |

For configuration details and further tuning axes, see HuggingFace PEFT [docs](https://huggingface.co/docs/peft/index).
