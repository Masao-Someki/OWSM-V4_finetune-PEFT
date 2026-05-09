# Search Strategy Checklist (Generated)

This file is auto-generated from repository-root `prompt.txt`.
Prompt SHA256: `ea80bd3608500d60c5c9c633a78972cbb276090c73f2340f4353b5101c11c691`

## Interpretation Policy
- Follow constraints from `prompt.txt` first.
- If this file conflicts with `prompt.txt`, prioritize `prompt.txt`.
- Use `.autoresearch/notes/` and `experiments.csv` for evidence/prioritization.

## Execution Checklist (top-down)
- [ ] 1. Preflight
  - [ ] Confirm all base configs in `prompt.txt` exist.
  - [ ] Confirm debug gate policy (`yes/no`) from `prompt.txt`.
  - [ ] Confirm trial budget (max configs).
- [ ] 2. Stability-first smoke (small)
  - [ ] Start from conservative learning rate and small epoch/step budget.
  - [ ] Validate OOM/instability before broader search.
- [ ] 3. Primary axis sweep (coarse)
  - [ ] Prioritize `learning rate` and `optimizer` first.
  - [ ] Keep architecture/method-specific params conservative while selecting optimizer/LR region.
- [ ] 4. Secondary axis sweep (coarse)
  - [ ] Tune `batch size`, `warmup_steps`, `max_epochs` around stable region.
- [ ] 5. Method-family compare
  - [ ] Compare candidate adaptation/model method families under the best shared hyperparameter region.
- [ ] 6. Method-specific parameter refine
  - [ ] For top 1-2 method families, tune family-specific parameters.
- [ ] 7. Local parameter search around current best
  - [ ] Narrow around best config and run small neighborhood search.

## Research-Backed Candidate Values (to fill before wave planning)
- [ ] Use web search to collect current best practices for this task/model family.
- [ ] Prefer primary sources: official docs, papers, and strong reproduction reports.
- [ ] Record source links and short rationale for each proposed value range.
- [ ] If a known heuristic exists (example: pretrained LR scaling conventions), include it explicitly.
- [ ] For each axis from `prompt.txt`, add:
  - [ ] candidate values/ranges
  - [ ] search order (what to try first, second, ...)
  - [ ] stop/expand condition

### Required Web-Research Outputs
- [ ] `learning rate`: candidate ranges + ordering + heuristic basis
- [ ] `optimizer`: candidate set + ordering
- [ ] `batch size`, `warmup_steps`, `max_epochs`: safe-to-aggressive ordering
- [ ] `method family`: full candidate list from official docs and/or recent references
- [ ] `method-specific parameters`: family-specific knobs and ranges

## Practical Wave Policy
- Wave 1: stability-first + minimum viable comparison set.
- Wave 2: coarse search on highest-impact axes.
- Wave 3: method-family breadth check (based on web-collected full list).
- Wave 4+: local parameter search around the best method/config.

## prompt.txt (current)
```text
# AutoResearch Input Form (Simple)

Write only this form. Keep it short.
This file is the source of truth for planning the next wave.

How to fill:
- Replace `WRITE_HERE`.
- If unsure, use the suggested default.
- Keep bullets concise.

---

## Required (Fill these)

1) Goal for this wave
- What do you want to improve most?
- Write: Improve Portuguese ASR quality (validation WER) for OWSM PEFT finetuning.

2) Most important metric
- Which metric should decide success?
- Write: validation WER (Portuguese split)

3) Number of trials in this wave
- How many configs to run in the main wave.
- Write: 10

4) Current concern
- What is the main risk now?
- Write: training instability and occasional memory-related failures when expanding search too quickly.

5) Base configs
- List the base config files the planner is allowed to expand for this wave.
- Write:
  - conf/owsm_peft_lora_basic.yaml
  - conf/owsm_peft_espnet.yaml
  - conf/owsm_peft_adalora.yaml

6) What to explore in this wave (axes, not values)
- List the tuning axes you want to explore.
- Do NOT write numeric candidate values here.
- The planner will propose concrete value ranges when generating search space.
- Write:
  - learning rate
  - optimizer
  - batch size
  - max_epochs
  - warmup_steps
  - PEFT method choice (please check all method available on PEFT library)
  - Best PEFT parameter set for each of the PEFT method, such as ranks, etc.

7) Debug gate required
- Should we run a small debug job first, and only run the full parallel wave if debug passes?
- Write: yes/no
- Suggested default: yes

---

## Don'ts (Do not do in this wave)

A) Hard prohibitions
- Write explicit things the planner must not do.
- Write:
  - do not use lr above WRITE_HERE
  - do not increase training budget beyond WRITE_HERE
  - do not introduce new axes beyond WRITE_HERE

B) Forbidden combinations
- Write combinations that are not allowed.
- Write:
  - WRITE_HERE

---

## References (Optional but recommended)

- Add URLs, papers, docs, or notes the planner should consider.
- The planner should use these as guidance, while still obeying this form.

A) URLs
- WRITE_HERE

B) Papers / reports
- WRITE_HERE

C) Local files in this repo
- WRITE_HERE

---
```
