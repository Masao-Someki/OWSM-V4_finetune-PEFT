# Wave Summary

## Why this config set
- Bootstrap wave: No prior experiments in experiments.csv, so exploration must cover all practically supported PEFT methods as the first baseline.
- All PEFT methods enumerated in planning.md are included here: LORA (baseline/best-supported), AdaLoRA (adaptive LoRA), IA3 (scaling vectors), OFT (Output-Focused Tuning), and Prefix Tuning.
- Parameter values are based on standard/official defaults for each method in ASR/transformer large-model community use (see links below).
- All configs use lr=5e-5 as a safe and established PEFT learning rate; other main axes (dataset, model) fixed to prompt defaults.

## Search-space coverage
- Current axis: "PEFT method family/type". Candidates: lora, adalora, ia3, oft, prefix.
- Other axes (PEFT-specific parameters, learning rate, optimizer, warmup, batch size, max_epochs) deferred until method is chosen.

## Checklist updates
- [x] Initialize: method-family categorical axis coverage started.
- [ ] PEFT-specific param/ablation coverage — pending later waves.
- [ ] Stability check, debug, and smoke test to be run with this set.

## Next action
- Run/debug this batch. Compare validation metric (CER/WER).
- If all finish without failure, move to PEFT-parameter ablation for the best-performing method(s).
- If instability arises with any method, try simplified configs or reduce parameter values locally.

## Web research summary
- PEFT method support for speech/ASR: based on [HuggingFace PEFT docs](https://huggingface.co/docs/peft/index), [LoRA paper](https://arxiv.org/abs/2106.09685), [AdaLoRA](https://arxiv.org/abs/2303.10512), [IA3 in PEFT](https://arxiv.org/abs/2205.05638), OFT [source](https://github.com/huggingface/peft/pull/409) and prefix tuning [paper](https://arxiv.org/abs/2101.00190).
- Common best-practice hyperparameters: r=8, alpha=16 for LoRA/AdaLoRA, prefix_length=30 for prefix, dropout=0.05 standard in community for regularization.

