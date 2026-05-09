# Research Roadmap

## Rules
- [ ] All axes come from `prompt.txt` section 6; all candidates come from `store/planning.md`.
- [ ] This file is a full multi-wave roadmap — ALL axes and ALL candidates must appear.
- [ ] Each wave targets one axis. List every candidate for that axis (not just the active wave's subset).
- [ ] Mark candidates as done/pending/skipped based on experiments.csv evidence.
- [ ] Include unlock condition between waves.
- [ ] For numeric axes: coarse, high-information values first (e.g. log scale).
- [ ] Update each run: mark progress, add findings, adjust future wave order if evidence warrants.

## Roadmap

### Wave 1: <axis name>
**Why first**: <rationale>

| candidate | status | comment | config |
| --- | --- | --- | --- |
| candidate_A |  | baseline | |
| candidate_B |  | | |
| ... (all candidates from planning.md) | | | |

**Unlock condition**: <what result moves us to Wave 2>

---

### Wave 2: <axis name>
**Why second**: <rationale>

| candidate | status | comment | config |
| --- | --- | --- | --- |
| ... | | | |

**Unlock condition**: <what result moves us to Wave 3>

---

### Wave N: <remaining axes ...>

## Source Reference
- prompt source: `prompt.txt`
- candidate inventory: `store/planning.md`
- format reference: `search_plan_human.md`
