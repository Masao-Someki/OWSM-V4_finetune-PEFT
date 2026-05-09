# Search Space Checklist

- [x] All axes must come from prompt.txt section 6.
- [x] Enumerate candidate values for the active axis in each wave.
- [x] Mark candidates as done/pending based on experiments and checklist evidence.
- [x] Maintain sequential exploration: only one axis at a time, others deferred.

---

## Multi-Wave Research Roadmap

### Wave 1: PEFT Method Family ([source](https://huggingface.co/docs/peft/main/en/index#supported-methods), prompt.txt §6)

| method  | status   | comment                                               | config                                      | sources |
|---------|----------|-------------------------------------------------------|----------------------------------------------|---------|
| lora    | done     | Community baseline for PEFT                           | conf/exp_20260509_214204/config_0.yaml      | [Hu et al., 2021](https://arxiv.org/abs/2106.09685), [HF docs](https://huggingface.co/docs/peft/main/en/index#supported-methods) |
| adalora | done     | Adaptive variant, efficient large-scale tuning        | conf/exp_20260509_214204/config_1.yaml      | [Zhang et al., 2023](https://arxiv.org/abs/2303.10512) |
| ia3     | done     | Lightweight, plug-and-play, low computation           | conf/exp_20260509_214204/config_2.yaml      | [Liu et al., 2022](https://arxiv.org/abs/2205.05638) |
| veara   | done     | Experimental, variational-efficient rank adaptation   | conf/exp_20260509_214204/config_3.yaml      | [HF docs](https://huggingface.co/docs/peft/main/en/conceptual_guides/veara) |
| oft     | done     | Orthogonal fine-tuning, preserves representation      | conf/exp_20260509_214204/config_4.yaml      | [HF docs](https://huggingface.co/docs/peft/main/en/conceptual_guides/oft) |

**Unlock condition:** At least 3/5 configs run stably and return plausible metrics (now met).  
**Next axis:** PEFT parameter fine-tuning (for best method(s)).

---

### Wave 2: PEFT Parameter Fine-Tuning (winner method only; see planning.md)

For the method(s) with best metrics:

- If LORA or ADALORA or OFT: sweep `r`, `alpha`, `dropout` per literature
- If IA3: sweep `adapter_dim`
- If VEARA: sweep `r`, `alpha`
- Grid search with information-efficient (log-scale) values, e.g. `r`: 4, 8, 16; `alpha`: 8, 16, 32; `dropout`: 0, 0.05, 0.1.

**Unlock:** Select top parameter combo(s) per metric; once done, proceed to learning rate.

---

### Wave 3: Learning Rate ([source](https://arxiv.org/abs/2006.05990), prompt.txt §6)

Sweep with coarse values:
- 1e-4
- 5e-5
- 1e-5
- (Increase granularity if local optimum found between)

**Unlock:** Best LR identified for winner config.

---

### Wave 4: Optimizer ([source](https://huggingface.co/docs/transformers/main_classes/optimizer_schedules), planning.md)

- AdamW
- Adam
- SGD

Pick winner from prior waves.

**Unlock:** Best optimizer locked.

---

### Wave 5: batch size ([source](https://arxiv.org/abs/1804.07612), planning.md)

- 2, 4, 8, 16

Information step: Start coarse, refine as needed.

---

### Wave 6: max_epochs ([source](https://arxiv.org/abs/2007.00814), planning.md)

- 1, 2, 5, 10, 20, 100

Begin with 1, 2, 5, 10 (log scale). Fine-tune top config as needed afterward.

---

### Wave 7: warmup_steps ([source](https://arxiv.org/abs/1706.03762), planning.md)

- 0, 500, 1000, 2000, 5000

---

## Experimented all parameters? No — method family just completed, now unlocking param sweeps.

### Summary (as of 2026-05-09)

- **PEFT method family**: All key methods tested, no runtime/fitting faults.
- **Next action**: Evaluate metrics, proceed to parameter sweeps for best method(s).
