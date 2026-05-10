# Search Space Index (Bootstrap, May 10, 2026)

## Current Axis: PEFT Method

| method   | status   | config path                             | rationale/source |
|----------|----------|-----------------------------------------|------------------|
| lora     | pending  | conf/exp_20260510_013346/config_0.yaml | LoRA baseline—transformer PEFT standard ([arXiv 2106.09685](https://arxiv.org/abs/2106.09685)) |
| adalora  | pending  | conf/exp_20260510_013346/config_1.yaml | Adaptive LoRA—parameter efficiency ([AdaLoRA paper](https://arxiv.org/abs/2303.10512)) |
| ia3      | pending  | conf/exp_20260510_013346/config_2.yaml | Lightweight gating ([IA³ paper](https://arxiv.org/abs/2205.05638)) |
| oft      | pending  | conf/exp_20260510_013346/config_3.yaml | Output Factorization Tuning ([OFT HuggingFace](https://github.com/huggingface/peft#oft)) |
| vera     | pending  | conf/exp_20260510_013346/config_4.yaml | Vector Representation Adapter ([VERA, see PEFT/HF docs](https://huggingface.co/docs/peft/main/en/package_reference/vera)) |

## Web-Research/Best-Practice Table

| Source/Link                                                        | Summary                              |
|--------------------------------------------------------------------|--------------------------------------|
| https://huggingface.co/docs/peft                                    | Supported methods, doc examples      |
| https://arxiv.org/abs/2106.09685                                   | LoRA: Encoder adaptation             |
| https://arxiv.org/abs/2303.10512                                   | AdaLoRA: Dynamic block adaptation    |
| https://arxiv.org/abs/2205.05638                                   | IA3: Gating multipliers              |
| https://github.com/huggingface/peft#oft                             | Output Factorization Tuning          |
| https://huggingface.co/docs/peft/main/en/package_reference/vera     | VERA: Efficient adaptation variant   |

- All sources recommend initial r/alpha values (8) for bootstrapping unless memory is prohibitive.
- Learning rate 5e-5 is default/favored for first PEFT method runs on T5/Transformer ASR (ESPnet, PEFT).
