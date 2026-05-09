# PEFT Search Space: Summary & Literature Table

## Active Axis: PEFT Family

| Method   | Config Path                                 | Notes                                                   | Literature/Source                                                            |
|----------|---------------------------------------------|---------------------------------------------------------|------------------------------------------------------------------------------|
| lora     | conf/exp_20260509_214204/config_0.yaml     | Community baseline, low-rank adapters                   | [Hu et al., 2021](https://arxiv.org/abs/2106.09685); [HF PEFT](https://huggingface.co/docs/peft/main/en/index#supported-methods) |
| adalora  | conf/exp_20260509_214204/config_1.yaml     | Adaptive scaling, more flexible than LoRA               | [Zhang et al., 2023](https://arxiv.org/abs/2303.10512); [HF Adalora](https://huggingface.co/docs/peft/main/en/conceptual_guides/adalora) |
| ia3      | conf/exp_20260509_214204/config_2.yaml     | Linear transform gating, parameter-efficient             | [Liu et al., 2022](https://arxiv.org/abs/2205.05638); [HF IA3](https://huggingface.co/docs/peft/main/en/conceptual_guides/ia3)        |
| veara    | conf/exp_20260509_214204/config_3.yaml     | Variational, efficient rank allocation                  | [HF VEARA](https://huggingface.co/docs/peft/main/en/conceptual_guides/veara)                                             |
| oft      | conf/exp_20260509_214204/config_4.yaml     | Orthogonal fine-tuning, orthogonal complements          | [HF OFT](https://huggingface.co/docs/peft/main/en/conceptual_guides/oft)                                                 |

## Candidate List (full planning.md)

Please see **store/planning.md** for the comprehensive candidate inventory.  
Current wave is a complete sweep of main PEFT algorithm families for ASR, as per [HuggingFace PEFT docs](https://huggingface.co/docs/peft/main/en/index#supported-methods) and surveyed 2024–2026 literature.

---

## Key Literature:

- **LoRA**: Hu et al., 2021 — [arXiv](https://arxiv.org/abs/2106.09685)
- **AdaLoRA**: Zhang et al., 2023 — [arXiv](https://arxiv.org/abs/2303.10512)
- **IA3**: Liu et al., 2022 — [arXiv](https://arxiv.org/abs/2205.05638)
- **HF PEFT Documentation**: [Main Supported Methods](https://huggingface.co/docs/peft/main/en/index#supported-methods)
- **Additional methods** (veara, oft): Supported as of HF PEFT 0.10

---

## Search Status

- All configs launched and run successfully for PEFT method family.
- Progressing to parameter-level fine-tuning for winner(s) next wave.
