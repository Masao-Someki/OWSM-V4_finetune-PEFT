- [ ] Use web search to collect current best practices for this task/model family.
- [ ] Learning Rate
    - Candidate values: `5e-5, 1e-4`
    - Trial order: `1) 5e-5  2) 1e-4`
    - Stop condition: when OOM is encountered, revert to 5e-5.
    - Rationale: High learning rates may speed up convergence; however, excessive values can risk instability.
    - Sources: https://arxiv.org/abs/2003.03899

- [ ] Optimizer
    - Candidate values: `AdamW`
    - Trial order: `1) AdamW`
    - Stop condition: confirmed stability with this optimizer.
    - Rationale: Proven stability and performance on transformer-based models.
    - Sources: Official transformer documentation.

- [ ] Batch Size
    - Candidate values: `16, 32`
    - Trial order: `1) 16 2) 32`
    - Stop condition: if OOM is encountered, revert to 16.
    - Rationale: Smaller batch sizes tend to consume less memory.
    - Sources: https://openreview.net/pdf?id=H1bF3HQYVR

- [ ] Max Epochs
    - Candidate values: `2`
    - Trial order: `1) 2`
    - Stop condition: due to stability runs.
    - Rationale: Quick runs to ensure engagement without hitting instability.
    - Sources: ...

- [ ] Warmup Steps
    - Candidate values: `100`
    - Trial order: `1) 100`
    - Stop condition: confirm effectiveness.
    - Rationale: Sufficient warmup steps can improve convergence.
    - Sources: ...

- [ ] PEFT Method Choice
    - Candidate values: `adapter_like_method`
    - Trial order: `1) adapter_like_method`
    - Stop condition: when incorrect configurations emerge.
    - Rationale: Results show promise across similar tasks.
    - Sources: official PEFT library documentation.
