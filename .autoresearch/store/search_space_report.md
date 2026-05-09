# Search Space Report

## Current Sequential Decision

| item | value |
| --- | --- |
| resolved axis | PEFT method choice |
| winner so far | lora |
| next active axis | LoRA parameter presets |
| deferred next axis | learning rate |

## Completed Method Comparison

| method | wer | cer | result |
| --- | --- | --- | --- |
| lora | 0.214 | 0.109 | best |
| adalora | 0.227 | 0.117 | worse than lora |
| delora | 0.241 | 0.126 | worse than lora |

## Active LoRA Preset Candidates

| preset | comment |
| --- | --- |
| `r=4, alpha=8, dropout=0.0` | low-capacity baseline |
| `r=8, alpha=16, dropout=0.0` | standard baseline |
| `r=8, alpha=16, dropout=0.05` | standard with light dropout |
| `r=16, alpha=32, dropout=0.05` | higher-capacity coarse jump |
| `r=16, alpha=32, dropout=0.1` | higher-capacity with stronger regularization |

## Sources

- LoRA paper: https://arxiv.org/abs/2106.09685
- Hugging Face PEFT docs: https://huggingface.co/docs/peft/index
