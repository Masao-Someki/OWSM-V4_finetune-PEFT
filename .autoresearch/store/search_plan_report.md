# Search Space Index & Web Research Summary

## Current candidate axis: PEFT method

| method         | comment                          |
|----------------|----------------------------------|
| lora           | Most cited; baseline; variants (r) |
| adalora        | Adaptive-rank; recent SOTA variant |
| ia3            | Lightweight gate-based variant     |
| adapter        | Classic bottleneck adapters        |
| prefix_tuning  | Virtual tokens, established       |
| oft            | Orthogonal Fusion Tuning; recent  |
| lora (r=2)     | Boundary: low capacity            |
| lora (r=32)    | Boundary: high capacity           |

## Source links and highlights

| method         | web reference | highlight/why selected |
|----------------|--------------|------------------------|
| lora           | [LoRA paper](https://arxiv.org/abs/2106.09685)  | SOTA baseline for PEFT. |
| adalora        | [AdaLoRA paper](https://arxiv.org/abs/2303.10512) | Adaptive, best large-scale. |
| ia3            | [IA3 paper](https://arxiv.org/abs/2205.05638) | Less parameters, practical for many tasks. |
| adapter        | [Adapter paper](https://arxiv.org/abs/1902.00751) | Oldest/classic PEFT method. |
| prefix_tuning  | [Prefix Tuning paper](https://arxiv.org/abs/2101.00190) | Widely used, especially for sequence2sequence. |
| oft            | [OFT paper](https://arxiv.org/abs/2310.05327) | New, promising on speech/S2S tasks. |
| lora (r=2,32)  | Lora variants | Common for capacity ablation. |

## Summary
All major PEFT methods are included in this wave. Next axis (parameters, lr, optimizer) will be explored after initial results.

