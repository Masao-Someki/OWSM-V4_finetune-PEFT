# Search Space Index

## Current wave: PEFT method family/type

| candidate   | comment                                               |
| ----------- | ----------------------------------------------------- |
| lora        | Default, most established PEFT baseline               |
| adalora     | Adaptive LoRA, often better with more params          |
| ia3         | Parameter-efficient scaler vector method              |
| oft         | Output-only focused fine-tuning                       |
| prefix      | Prefix-tuning, prominent for seq2seq transformers     |

## Web research findings

| method     | Short description                   | Reference/Source                                            |
| ---------- | ----------------------------------- | ----------------------------------------------------------- |
| lora       | Rank-decomposition, efficient tuning| https://arxiv.org/abs/2106.09685, HF PEFT docs              |
| adalora    | LoRA variant with adaptive rank     | https://arxiv.org/abs/2303.10512                            |
| ia3        | Vector-based scaling per attention  | https://arxiv.org/abs/2205.05638                            |
| oft        | Output-Focused Tuning matrix        | https://github.com/huggingface/peft/pull/409                |
| prefix     | Prefix-tuning for seq2seq/encoder-decoder | https://arxiv.org/abs/2101.00190                    |

Summary: This covers the main state-of-the-art and HF-PEFT-supported methods for large language and speech models. Source code and documentation confirm all are stable enough to merit a baseline test.

