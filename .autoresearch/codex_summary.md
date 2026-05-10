# Wave Summary: First-Wave PEFT Method Bootstrap

## Why this config set

- **Prompt.txt** calls for an empirical comparison of strong PEFT baselines. The repository and planning.md mention LoRA, AdaLoRA, IA3, OFT, and VERA as canonical candidates for modern parameter-efficient fine-tuning (PEFT) on speech models.
- **Experiments.csv** shows only failed or debug-stage attempts—no methods yet show convergence. Thus, for true bootstrap, we must cover all leading contenders with basic, robust hyperparameters. All configs use a moderate r=8/oft_rank=8 and alpha=8, matching common PEFT best-practices for first iteration ([HuggingFace PEFT docs](https://huggingface.co/docs/peft), [LoRA original paper](https://arxiv.org/abs/2106.09685)).
- These methods are practical in espnet3 (assuming code and config support per planning.md/store) and are confirmed as available in the broader PEFT/transformer field: [GitHub - PEFT methods](https://github.com/huggingface/peft#supported-methods).
- We use the same learning rate and dropout parameters for fair empirical comparison.

## Search-space coverage

- **Active axis**: PEFT method (categorical: lora, adalora, ia3, oft, vera)
- **Fixed**: initial learning rate (5e-5), batch size, optimizer, steps, and all other settings as defined by prompt/store—per best practices for initial method comparison.
- **Deferred axes**: Per section 6 of prompt.txt, after baseline PEFT method is selected, search space will open on other axes (see search_plan.md for explicit candidate values).

## Checklist updates

- [x] Bootstrap first PEFT-method sweep
- [ ] Move to next axis (e.g., peft-specific params, learning-rate) after convergence/metrics review

## Next action

- If any method runs to successful loss/metrics completion (no crash or immediate NaN/exit), unlock per-method parameter and learning rate tuning next—start with the best empirical performer(s).
- If all crash, triage bug logs and retry with fallback minimal configs and small-rank values (see search_plan.md recommendations).
