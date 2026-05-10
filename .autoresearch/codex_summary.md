# Wave Summary: Bootstrap PEFT Algorithm and Parameter Sweep

**Why this config set:**  
This is the initial bootstrap wave. No successful runs are yet recorded in `experiments.csv`. All previous attempts either failed or were debug/tests. The PEFT axis is clearly the most important first search space according to `prompt.txt` section 6, as evidenced in standard iterative ASR fine-tuning workflows. It also aligns with best-practice approaches (see web references below).  
We need to both test which adapter algorithm works best, and explore a representative spread of PEFT hyperparameters to ensure at least one config is functional.
We cover:  
- Multiple PEFT algorithms: LoRA, AdaLoRA, IA3, OFT, VERA (web search confirms all available and implemented for transformer ASR; see report).
- Key LoRA- or AdaLoRA-specific hyperparameters (r/alpha) are benchmarked at common values.
- Expanded target_modules (where meaningfully supported) to check breadth/stability.
- Sane baseline learning rate, copy from prior default (5e-5).
- Trainer/minimal pipeline settings remain default (for stability); controller variables not varied.

**Search-space coverage:**  
This wave fully covers the **PEFT adapter algorithm axis** and major practical hyperparameter brackets per the literature.  
Axes covered:
- Adapter/PEFT method: lora, adalora, ia3, oft, vera
- Critical method parameters: r/alpha @ 4/8/16, target_modules
Each method listed in Table 1 in the plan.  
**DEFERRED:** No variation in learning rate, optimizer, batch size, scheduler, etc. until minimally functional method is found.

**Checklist updates:**  
- [x] Search space axes match `prompt.txt` (see report).
- [x] Explicit candidate values for PEFT axis enumerated and now all PENDING.
- [ ] Strong functional/metric baseline established (deferred: until at least one config completes successfully).
- [ ] Other axes (learning rate, optimizer, etc.) deferred, will enumerate after at least 1 working baseline.
- [ ] Local stability remains unknown; this run may expose bugs with some types.

**Next action:**  
- If one or more configs complete successfully, move to sweep learning rate and/or optimizer for the best adapter.
- If all fail/stability, review logs, check implementation/target_module coverage, and run minimal smoke test for fastest/most conservative config variant.
- Continue checklist-driven progressive expansion (see roadmap in search_plan.md and report).

**Web research references:**
- [LoRA GitHub and documentation](https://github.com/microsoft/LoRA)
- [PEFT paper summary: Table and survey of methods](https://arxiv.org/abs/2303.10761)
- [Huggingface/peft supported methods](https://github.com/huggingface/peft)
- [Adapter methods for transformers - survey](https://arxiv.org/abs/2206.08149)

