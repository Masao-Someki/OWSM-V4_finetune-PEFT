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
  - [ ] Start from conservative values on highest-risk axes defined in `prompt.txt`.
  - [ ] Validate OOM/instability before broader search.
- [ ] 3. Primary axis sweep (coarse)
  - [ ] Choose initial high-impact axes only from `prompt.txt` section 6.
  - [ ] Keep method-specific params conservative while selecting stable regions.
- [ ] 4. Secondary axis sweep (coarse)
  - [ ] Expand to remaining axes from `prompt.txt` section 6 around stable regions.
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
- [ ] Build this section ONLY from axes listed in `prompt.txt` section 6.
- [ ] Do not add extra axes not present in `prompt.txt` unless explicitly allowed there.
- [ ] For each axis below, provide: candidates/range, trial order, rationale links, and stop/expand condition.
- [ ] `learning rate`
- [ ] `optimizer`
- [ ] `batch size`
- [ ] `max_epochs`
- [ ] `warmup_steps`
- [ ] `PEFT method choice (please check all method available on PEFT library)`
- [ ] `Best PEFT parameter set for each of the PEFT method, such as ranks, etc.`

### Axis Value Enumeration (must fill before planning)
#### Axis: `learning rate`
- [ ] Candidate values (explicit list): `v1`, `v2`, `v3`
- [ ] Trial order: `1) ... 2) ... 3) ...`
- [ ] Fixed/paired settings for fair comparison:
- [ ] Expand condition:
- [ ] Stop condition:
- [ ] Rationale (1-2 lines):
- [ ] Sources (URLs):

#### Axis: `optimizer`
- [ ] Candidate values (explicit list): `v1`, `v2`, `v3`
- [ ] Trial order: `1) ... 2) ... 3) ...`
- [ ] Fixed/paired settings for fair comparison:
- [ ] Expand condition:
- [ ] Stop condition:
- [ ] Rationale (1-2 lines):
- [ ] Sources (URLs):

#### Axis: `batch size`
- [ ] Candidate values (explicit list): `v1`, `v2`, `v3`
- [ ] Trial order: `1) ... 2) ... 3) ...`
- [ ] Fixed/paired settings for fair comparison:
- [ ] Expand condition:
- [ ] Stop condition:
- [ ] Rationale (1-2 lines):
- [ ] Sources (URLs):

#### Axis: `max_epochs`
- [ ] Candidate values (explicit list): `v1`, `v2`, `v3`
- [ ] Trial order: `1) ... 2) ... 3) ...`
- [ ] Fixed/paired settings for fair comparison:
- [ ] Expand condition:
- [ ] Stop condition:
- [ ] Rationale (1-2 lines):
- [ ] Sources (URLs):

#### Axis: `warmup_steps`
- [ ] Candidate values (explicit list): `v1`, `v2`, `v3`
- [ ] Trial order: `1) ... 2) ... 3) ...`
- [ ] Fixed/paired settings for fair comparison:
- [ ] Expand condition:
- [ ] Stop condition:
- [ ] Rationale (1-2 lines):
- [ ] Sources (URLs):

#### Axis: `PEFT method choice (please check all method available on PEFT library)`
- [ ] Candidate values (explicit list): `v1`, `v2`, `v3`
- [ ] Trial order: `1) ... 2) ... 3) ...`
- [ ] Fixed/paired settings for fair comparison:
- [ ] Expand condition:
- [ ] Stop condition:
- [ ] Rationale (1-2 lines):
- [ ] Sources (URLs):

#### Axis: `Best PEFT parameter set for each of the PEFT method, such as ranks, etc.`
- [ ] Candidate values (explicit list): `v1`, `v2`, `v3`
- [ ] Trial order: `1) ... 2) ... 3) ...`
- [ ] Fixed/paired settings for fair comparison:
- [ ] Expand condition:
- [ ] Stop condition:
- [ ] Rationale (1-2 lines):
- [ ] Sources (URLs):

## Practical Wave Policy
- Wave 1: stability-first + minimum viable comparison set.
- Wave 2: coarse search on high-impact axes from `prompt.txt`.
- Wave 3: method-family breadth check (based on web-collected full list).
- Wave 4+: local parameter search around the best method/config.

## Source Reference
- Source file: repository-root `prompt.txt`
- Prompt SHA256: `ea80bd3608500d60c5c9c633a78972cbb276090c73f2340f4353b5101c11c691`
- To inspect details, read `prompt.txt` directly (do not duplicate full text here).
