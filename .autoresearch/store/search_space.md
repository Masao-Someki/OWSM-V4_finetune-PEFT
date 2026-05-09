# Search Space Checklist (Active)
- [ ] All axes come from prompt.txt section 6
- [ ] Enumerated explicit candidate values per axis
- [ ] Source links included for proposed values
- [ ] Sequential policy enforced: finish Phase 1 before expanding other axes
- [ ] Do not expand non-Phase1 axes until Phase 1 winner is selected

prompt source: prompt.txt (sha256=c68f12dfd28b449466bf89750f5c1531c7e46c83c1da1090090a4bd02acde137)

## Sequential Policy
- Phase 1: Compare method/algorithm families (PEFT variants). Select a winner under matched training budgets.
- Phase 2+: Expand remaining axes one at a time in order (learning rate → optimizer → batch size → max_epochs → warmup_steps → PEFT parameter refinements).
- Non-Phase1 axes are listed but deferred until Phase 1 completion.

## Phase 1: Method / Algorithm Family

| algorithm        | done | comment                               | config                                      |
| ---              | ---  | ---                                   | ---                                         |
| baseline_from_prompt (lora) |      | LoRA baseline under tight budget       | conf/exp_20260509_191301/config_0.yaml     |
| candidate_1 (adalora)       |      | Adaptive LoRA ranks (same budget)      |                                            |
| candidate_2 (ia3)           |      | Multiplicative adapters                 |                                            |
| candidate_3 (prefix_tuning) |      | Soft prefix parameters only             |                                            |

- [ ] Experimented all method-family candidates?: no
- [ ] Phase 1 winner summary (why this method won): TBD after successful runs
- [ ] Evidence links:
  - LoRA (Hu et al., 2021): https://arxiv.org/abs/2106.09685
  - HF PEFT overview: https://huggingface.co/docs/peft/index
  - AdaLoRA (Zhang et al., 2023): https://arxiv.org/abs/2303.10512
  - IA3 (Liu et al., 2022): https://arxiv.org/abs/2205.05638
  - Prefix-tuning (Li & Liang, 2021): https://arxiv.org/abs/2101.00190

## Phase 2+: Axis-by-Axis Expansion (Deferred until Phase 1 complete)

Note: The following axes and candidate values are defined per prompt.txt section 6, but expansion will only proceed after Phase 1 winner selection. Trial orders prioritize low-risk defaults first and follow evidence-backed ranges.

### Axis: learning rate
- [ ] Candidate values:
  - [1e-5, 2e-5, 5e-5, 1e-4, 2e-4]
- [ ] Trial order:
  - Start near 2e-4 (commonly strong for PEFT/QLoRA), then 1e-4, then smaller LRs if instability spikes.
- [ ] Fixed settings for fair comparison:
  - Keep method (Phase 1 winner), batch_size, max_epochs/steps, optimizer fixed.
- [ ] Expand condition:
  - If top-2 LRs are within 0.5% metric difference, add midpoints (e.g., 7.5e-5, 1.5e-4).
- [ ] Stop condition:
  - No improvement after 2 consecutive bracket refinements or plateau across 3 LRs.
- [ ] Sources:
  - QLoRA: https://arxiv.org/abs/2305.14314 (used 2e-4 frequently)
  - HF PEFT guide: https://huggingface.co/docs/peft/index

### Axis: optimizer
- [ ] Candidate values:
  - ["adamw", "adamw_torch", "adafactor"]
- [ ] Trial order:
  - adamw → adamw_torch → adafactor (only if memory constrained or very long seqs)
- [ ] Fixed settings for fair comparison:
  - Keep LR from prior best, others fixed.
- [ ] Expand condition:
  - If instability observed, try adafactor at same LR.
- [ ] Stop condition:
  - If optimizer swap yields <0.3% improvement across 2 runs.
- [ ] Sources:
  - HF Transformers training: https://huggingface.co/docs/transformers/main/en/training
  - Adafactor paper: https://arxiv.org/abs/1804.04235

### Axis: batch size
- [ ] Candidate values:
  - [1, 2, 4, 8]
- [ ] Trial order:
  - Start at 1 (stability baseline), then 2 → 4 → 8 as resources allow.
- [ ] Fixed settings for fair comparison:
  - Keep effective training steps constant (adjust epochs/steps if needed).
- [ ] Expand condition:
  - If metric improves with larger batches and no OOMs.
- [ ] Stop condition:
  - First OOM or no gain after 1 step up.
- [ ] Sources:
  - QLoRA/PEFT resource practices: https://arxiv.org/abs/2305.14314

### Axis: max_epochs
- [ ] Candidate values:
  - [1, 3, 5]
- [ ] Trial order:
  - Start from 1 (smoke), then 3, then 5 if not overfitting.
- [ ] Fixed settings for fair comparison:
  - Keep LR/warmup fixed; same method and optimizer.
- [ ] Expand condition:
  - If validation still improving at end of shorter run.
- [ ] Stop condition:
  - Early plateau or overfitting indication.
- [ ] Sources:
  - HF training tips: https://huggingface.co/docs/transformers/main/en/training

### Axis: warmup_steps
- [ ] Candidate values:
  - Absolute: [0, 50, 100, 500] or ratio: [0%, 3%, 5% of total steps]
- [ ] Trial order:
  - 0 → small (50/3%) → moderate (100/5%)
- [ ] Fixed settings for fair comparison:
  - Keep LR and method fixed; same steps.
- [ ] Expand condition:
  - If loss spikes at start or optimizer instability.
- [ ] Stop condition:
  - No improvement after 2 increments.
- [ ] Sources:
  - Scheduler/warmup guidance: https://huggingface.co/docs/transformers/main/en/training

### Axis: PEFT method choice (HF PEFT-supported)
- [ ] Candidate values:
  - ["lora", "adalora", "ia3", "prefix_tuning", "prompt_tuning", "p_tuning"]
- [ ] Trial order:
  - lora (baseline) → adalora → ia3 → prefix_tuning → prompt_tuning/p_tuning (if applicable)
- [ ] Fixed settings for fair comparison:
  - Same LR, batch size, steps/epochs, optimizer.
- [ ] Expand condition:
  - If a non-LoRA method beats LoRA by >0.5%, add one more confirmatory run.
- [ ] Stop condition:
  - Winner stable across 2 seeds (if seeding policy exists).
- [ ] Sources:
  - HF PEFT docs: https://huggingface.co/docs/peft/index

### Axis: Best PEFT parameter set for each method
- [ ] Candidate values:
  - LoRA: r ∈ [4, 8, 16], alpha ∈ [8, 16, 32], dropout ∈ [0.0, 0.05, 0.1]
  - AdaLoRA: init_r ∈ [8, 16], target_r ∈ [8, 16], orth_reg_weight ∈ [0.5, 1.0]
  - IA3: per-layer activation gating enabled; no rank; consider dropout ∈ [0.0, 0.05]
  - Prefix/Prompt/P-Tuning: prefix_length ∈ [10, 20, 50]; dropout ∈ [0.0, 0.1]
- [ ] Trial order:
  - Start with LoRA r=8, alpha=16, dropout=0.05; adjust r first (memory/perf), then alpha, then dropout.
- [ ] Fixed settings for fair comparison:
  - Use Phase 1 winner method; keep LR/optimizer/batch constant.
- [ ] Expand condition:
  - If increasing r gives clear gains without OOM, continue; otherwise back off.
- [ ] Stop condition:
  - Diminishing returns across 2 parameter increments.
- [ ] Sources:
  - LoRA: https://arxiv.org/abs/2106.09685
  - AdaLoRA: https://arxiv.org/abs/2303.10512
  - IA3: https://arxiv.org/abs/2205.05638
  - Prefix-tuning: https://arxiv.org/abs/2101.00190

## Notes
- This wave executes only the LoRA baseline (smoke) due to prior DEBUG_FAILED. Other axes remain defined but inactive to comply with the sequential policy.
- After Phase 1 stability is confirmed and at least two method families are benchmarked, proceed to declare a Phase 1 winner before expanding additional axes.

