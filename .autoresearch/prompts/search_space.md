# OWSM PEFT Autoresearch Search Space

This file defines the allowed experiment search space for Codex.
Do not propose configs outside this scope unless explicitly justified.
Track progress in `notes/autoresearch_checklist.md` and `notes/autoresearch_findings.md`.

## Objective
- Determine the best PEFT method and robust hyperparameters for FLEURS ASR.
- Prioritize stable improvement on validation metrics and low failure rate.

## Primary Axes
1. PEFT method family (from existing templates)
- `conf/owsm_peft_lora_basic.yaml`
- `conf/owsm_peft_espnet.yaml`
- `conf/owsm_peft_adalora.yaml`
- `conf/owsm_peft_randlora.yaml`
- `conf/owsm_peft_vblora.yaml`
- `conf/owsm_peft_delora.yaml`

2. Learning rate (`lr`)
- Coarse sweep: `1e-5, 3e-5, 5e-5, 1e-4, 2e-4`
- Fine sweep near best region: include up/down one step around winner.

3. Trainer budget (`trainer.max_epochs`, optional `trainer.max_steps`)
- `max_epochs`: `1, 2, 4, 6`
- For fast debug only, keep small `max_steps` via existing debug scripts.
- For full runs, avoid overly aggressive `max_steps` overrides unless needed.

4. Scheduler / warmup
- Default scheduler class remains `espnet2.schedulers.warmup_lr.WarmupLR`.
- Sweep `scheduler.warmup_steps`:
  - coarse: `1000, 3000, 6000, 10000`
  - fine: centered around best coarse value.

5. Data-related robustness / augmentation proxy (via dataset + preprocessor config)
- `dataset.train[*].dataset.ratio`: `0.25, 0.5, 1.0` (for ablation/curriculum checks)
- `dataset.preprocessor.time_apply_prob`: `0.0, 0.25, 0.5, 0.75`
- `dataset.preprocessor.text_prev_apply_prob`: `0.0, 0.25, 0.5, 0.75`
- Keep `fleurs_subsets=all` as baseline unless a subset study is intentional.

## Method-specific Suggested Ranges
- LoRA (`type=lora`): `r in {8,16,32}`, `lora_alpha in {8,16,32}`, `lora_dropout in {0.0,0.05,0.1}`
- ESPnet LoRA (`type=espnet_lora`): `rank in {8,16,32}`, `alpha in {8,16,32}`, `dropout_rate in {0.0,0.05,0.1}`
- AdaLoRA: `init_r in {8,12,16}`, `target_r in {4,8,12}`, keep `target_r <= init_r`
- RandLoRA: `r in {16,32,64}`, `randlora_dropout in {0.0,0.05,0.1}`
- VBLoRA: `r in {2,4,8}`, `topk in {1,2,4}`, `vblora_dropout in {0.0,0.05}`
- DeLoRA: baseline only first; expand only after at least one stable run.

## Wave Policy
1. Early waves: broad but shallow across method families.
2. Mid waves: focus top 2 families and tune LR/warmup/epochs.
3. Late waves: narrow local search around best config and verify reproducibility.

## Hard Constraints
- Max configs per wave must respect caller-provided limit (`max_configs`).
- Each wave must include:
  - at least one exploitation config (best-so-far neighborhood),
  - at least one exploration config (new axis combination),
  - clear rationale tied to `experiments.csv`.
- Always run debug-first flow before full submission.
