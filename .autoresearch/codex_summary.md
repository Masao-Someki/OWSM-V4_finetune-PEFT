# Wave Summary — exp_20260509_214931

## Why this config set

- The C0 (stability/smoketest) wave was submitted for the 5 major PEFT method families supported, and all configs ran without failure (per checklist status) and returned plausible, valid metrics.
- There are **no runtime or stability faults** blocking progression to effectiveness comparison; thus, the experiment proceeds to effectiveness ranking for the main PEFT axis.
- The config set exactly matches the methods described in the previous planning wave and directly maps to the best-practice axes in HuggingFace PEFT as of 2024–2026.
- No new configs are needed: this is an evaluation wave to establish which method(s) are most promising, using the configs already executed.

## Search-space coverage

- **Axis covered this wave**: PEFT method (lora, adalora, ia3, veara, oft)
- These comprise the **full candidate list** for practical, mainstream, ASR-supported PEFT methods as enumerated in store/planning.md.
- All axes below (parameter fine-tuning, lr, optimizer, etc.) are **locked** until a primary method is selected.

## Checklist updates

- **Method effectiveness (metric):** Now actionable, since valid metric results are returned.
- **Initial search/done, C0/smoke/done:** Previously completed.
- **Parameter exploration (winner-only), hyperparam/final:** Still locked as per roadmap.
- No failed runs; all methods produced outputs.

## Next action

- **Immediate:** Analyze the returned metrics and update the effectiveness ranking among the 5 PEFT methods. Select the best-1 or best-2 methods by dev performance (e.g., loss, CER, WER).
- **Next wave:** Advance to PEFT parameter fine-tuning for the top method(s) (e.g. adjust `r`, `alpha`, `dropout`); enumerate candidate values for those axes, using web research for sensible bounds.
- Plan an array covering 2–3 parameter combinations for the chosen method(s), as permitted by run quotas and evidence.

**End of summary.**
