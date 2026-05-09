# Search Space Checklist

## Rules
- [ ] All axes must come from `prompt.txt` section 6.
- [ ] Enumerate explicit candidate values for each axis.
- [ ] Include source links for proposed values.
- [ ] Do not expand non-Phase1 axes before Phase1 completion.

## Sequential Policy
- [ ] Phase 1 (method/algorithm family comparison) must finish first.
- [ ] Phase 2+ starts only after Phase 1 is marked complete.
- [ ] After Phase 1, expand remaining axes sequentially (one axis focus per step).

## Phase 1: Method / Algorithm Family

| algorithm | done | comment | config |
| --- | --- | --- | --- |
| baseline_from_prompt |  | baseline |  |
| candidate_1 |  | from docs/papers |  |
| candidate_2 |  | from docs/papers |  |
| candidate_3 |  | from docs/papers |  |

- [ ] Experimented all method-family candidates?: yes/no
- [ ] Phase 1 winner summary (why this method won):
- [ ] Evidence links:

## Phase 2+: Axis-by-Axis Expansion (Sequential)

### Axis: learning rate
- [ ] Candidate values: 
- [ ] Trial order: 
- [ ] Fixed settings for fair comparison:
- [ ] Expand condition:
- [ ] Stop condition:
- [ ] Sources:

### Axis: optimizer
- [ ] Candidate values: 
- [ ] Trial order: 
- [ ] Fixed settings for fair comparison:
- [ ] Expand condition:
- [ ] Stop condition:
- [ ] Sources:

### Axis: batch size
- [ ] Candidate values: 
- [ ] Trial order: 
- [ ] Fixed settings for fair comparison:
- [ ] Expand condition:
- [ ] Stop condition:
- [ ] Sources:

### Axis: max_epochs
- [ ] Candidate values: 
- [ ] Trial order: 
- [ ] Fixed settings for fair comparison:
- [ ] Expand condition:
- [ ] Stop condition:
- [ ] Sources:

### Axis: warmup_steps
- [ ] Candidate values: 
- [ ] Trial order: 
- [ ] Fixed settings for fair comparison:
- [ ] Expand condition:
- [ ] Stop condition:
- [ ] Sources:

### Axis: PEFT method choice (please check all method available on PEFT library)
- [ ] Candidate values: 
- [ ] Trial order: 
- [ ] Fixed settings for fair comparison:
- [ ] Expand condition:
- [ ] Stop condition:
- [ ] Sources:

### Axis: Best PEFT parameter set for each of the PEFT method, such as ranks, etc.
- [ ] Candidate values: 
- [ ] Trial order: 
- [ ] Fixed settings for fair comparison:
- [ ] Expand condition:
- [ ] Stop condition:
- [ ] Sources:

## Source Reference
- prompt source: `prompt.txt`
- format reference: `search_space_human.md`
