# Search Space Checklist

## Rules
- [ ] All axes must come from `prompt.txt` section 6.
- [ ] This file is cumulative: append updates and preserve prior evidence/history.
- [ ] Enumerate explicit candidate values only for the current active axis.
- [ ] Include source links for proposed values.
- [ ] Keep non-active axes deferred until the current active axis is resolved.
- [ ] If the active axis is finite/categorical, enumerate the broadest practical candidate set.
- [ ] If the active axis is numeric, use coarse, information-efficient values first and avoid low-signal tiny increments.

## Sequential Policy
- [ ] Choose one current focus axis.
- [ ] Run only the minimum set of experiments needed to resolve that axis.
- [ ] After resolving the current axis, update this file and choose the next focus axis.

## Current Focus

### Focus axis
- [ ] `WRITE_CURRENT_AXIS_HERE`

### Why this axis now
- [ ] Evidence from prior runs / web research:

### Candidate values for current focus

| value | done | comment | config |
| --- | --- | --- | --- |
| candidate_1 |  | baseline / low risk |  |
| candidate_2 |  | evidence-backed comparison |  |
| candidate_3 |  | boundary / exploration |  |

- [ ] Current axis resolved?: yes/no
- [ ] Winner / best-so-far summary:
- [ ] Axis type: `categorical` / `numeric`
- [ ] Enumeration policy used:
- [ ] If `categorical`: note that the list aims to be as complete as practical.
- [ ] If `numeric`: note the coarse search logic (for example logarithmic or bracketed spacing).
- [ ] Evidence links:

## Deferred Axes

<!-- List axes from prompt.txt section 6 that are NOT the current focus -->
- [ ] axis_B
- [ ] axis_C
- [ ] axis_D

## Unlock Condition For Next Axis
- [ ] What result from the current axis allows moving on:
- [ ] Which axis should be explored next after this one:

## Source Reference
- prompt source: `prompt.txt`
- format reference: `search_space_human.md`
