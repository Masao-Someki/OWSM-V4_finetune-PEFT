# Wave Summary: exp_20260509_222054 (Bootstrap)

## Why this config set:
- This is the initialization ("bootstrap") wave—no reliable prior results in experiments.csv.
- All main PEFT method types likely supported/feasible with the code base are included, based on web research and current SOTA/official docs: LoRA, Adalora, IA3, Adapter, Prefix tuning, OFT and LoRA scale variants.
- LoRA is included at baseline, very low (r=2), and high rank (r=32) settings to check for under- and over-capacity in this backbone.
- Adalora is included for adaptive/auto-rank, which is widely cited as outperforming LoRA in some settings ([Ding et al., 2023](https://arxiv.org/abs/2303.10512)).
- OFT is included as a baseline orthogonal PEFT method that is used in recent speech/ASR finetune papers.
- Prefix tuning is included as it is an established baseline for transformer PEFT, especially in speech/seq2seq.
- Adapter is included as a classic PEFT baseline.
- This set covers all high-level method types suggested by prompt.txt and by the latest literature.
- Parameters such as batch size, epochs, optimizer are held at template-safe values (base_recipe_template), focusing the wave on method axis only.

## Search-space coverage:
- Covers the full categorical PEFT "method" axis.
- Candidate methods: LoRA, Adalora, IA3, Adapter, Prefix tuning, OFT, and 2 additional LoRA ranks for boundary check.
- All method types listed in planning.md, matching prompt.txt section 6.

## Checklist updates:
- [x] Enumerated all PEFT method candidates (methods axis: LoRA variants, Adalora, IA3, Adapter, Prefix tuning, OFT).
- [x] Submitted initial configs for all plausible PEFT method types.
- [ ] Remaining: Peft parameters, learning rate, optimizer, warmup_steps, batch size, max_epochs will be explored only after best method is clear.

## Next action:
- Wait for metrics from this bootstrap wave.
- Advance to a parameter or learning-rate sweep on the best performing method(s).
- If multiple methods are close, next wave may bifurcate into deeper parameter search for top 2–3 candidates.
- If none converge or evidence of instability, rerun LoRA/Adapter with shorter epoch/batch to debug.

## Web research references:
- [LoRA: https://arxiv.org/abs/2106.09685](https://arxiv.org/abs/2106.09685) (baseline, popularity)
- [Adalora: https://arxiv.org/abs/2303.10512](https://arxiv.org/abs/2303.10512) (adaptive rank)
- [IA3: https://arxiv.org/abs/2205.05638](https://arxiv.org/abs/2205.05638) (lightweight fine-tune)
- [Prefix Tuning: https://arxiv.org/abs/2101.00190](https://arxiv.org/abs/2101.00190)
- [Adapter: https://arxiv.org/abs/1902.00751](https://arxiv.org/abs/1902.00751)
- [OFT: https://arxiv.org/abs/2310.05327](https://arxiv.org/abs/2310.05327) (speech/ASR PEFT)

