Wave Summary — exp_20260509_191301 (iterative, stability-first)

Why this config set
- Latest status shows DEBUG_FAILED on prior wave (exp_20260509_011856). With no rows in experiments.csv and no metrics produced, we must unblock stability before expanding search.
- We propose a single LoRA baseline smoke config (Phase 1 baseline_from_prompt) to validate runtime with minimal memory footprint and short duration:
  - batch_size=1 (minimize VRAM/RAM)
  - method.r=4 (smaller adapter rank than typical r=8 to further reduce memory)
  - max_epochs=1 and trainer.max_steps=60 to keep debug short
  - lr=2e-4, adamw, warmup_steps=10 (common PEFT defaults; safe for a smoke run)

Search-space coverage (from prompt.txt section 6)
- Phase 1 focus only: Method/Algorithm family = PEFT with LoRA as the baseline.
- We do not expand other axes (learning rate, optimizer, batch size, max_epochs, warmup_steps, PEFT parameter sweep) until Phase 1 stability is confirmed.
- Regenerated .autoresearch/store/search_space.md from the updated prompt.txt SHA and current web evidence; enumerates candidate values and trial order but marks non-Phase1 axes deferred.

What changed vs previous wave
- Narrowed to 1 config for debug-first gate due to DEBUG_FAILED.
- Reduced memory risk: batch_size -> 1; LoRA rank -> 4; steps -> 60.
- Regenerated the active search space after prompt.txt update (sha256=c68f12...).
- Added a shared base template (conf/base_recipe_template.yaml) so per-run configs can inherit minimal, consistent keys per repo contract.

Checklist updates
- C0 (Input integrity): DOING — prompt.txt changed; regenerated search space; validated that axes match section 6 and deferred non-Phase1 axes.
- C4 (Stability risk): DOING — single minimal smoke config with strict caps to pass debug and avoid OOM.
- C5 (Reproducibility): DOING — all paths are valid, array_conf points to existing config, exp_tag is unique; no exp_dir override.

Next action (if this debug passes)
- Continue Phase 1 method-family comparison:
  - Add AdaLoRA, IA3, and Prefix-Tuning baselines with matched training budget (same lr, steps, batch_size) to compare algorithm families fairly.
- Only after selecting a Phase 1 winner, expand the next axis (learning rate) around the winner’s best default, followed by optimizer and batch size per the sequential policy.

Run instructions (debug-first)
- Use the repo’s debug-first launcher as in prior waves (e.g., submit-array-with-debug.sh) with this single config:
  - conf/exp_20260509_191301/config_0.yaml
- Keep quick caps (fast_dev_run / quick_max_steps / quick_max_epochs) consistent with trainer.max_steps set here to avoid overrides.

Evidence links (for defaults rationale; also embedded in search_space.md)
- LoRA paper (Hu et al., 2021): https://arxiv.org/abs/2106.09685
- HF PEFT docs (methods & usage): https://huggingface.co/docs/peft/index
- AdaLoRA (Zhang et al., 2023): https://arxiv.org/abs/2303.10512
- IA3 (Liu et al., 2022): https://arxiv.org/abs/2205.05638
- QLoRA (Dettmers et al., 2023) for PEFT LR/batch guidance: https://arxiv.org/abs/2305.14314
- HF Opt/Training tips (warmup, schedulers): https://huggingface.co/docs/transformers/main/en/training

