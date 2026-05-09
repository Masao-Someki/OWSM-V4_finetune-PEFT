# Research Roadmap

## Rules
- All axes come from prompt.txt section 6; all candidates come from store/planning.md.
- This file is a full multi-wave roadmap — ALL axes and ALL candidates must appear.
- Every wave MUST use a markdown table for candidates (no bullet lists, no prose-only).
- Each wave targets one axis. List every candidate for that axis from planning.md.
- Mark candidates as done/pending/skipped based on experiments.csv evidence.
- Include unlock condition between each wave.
- For numeric axes: coarse, high-information values first (e.g. log scale).
- Update each run: mark progress, add findings, adjust future wave order if evidence warrants.

## Roadmap

### Wave 1: PEFT method family/type
**Why first**: Method family provides the largest effect on transferability and parameter count. Literature and HF PEFT docs show initial family choice determines subsequent hyperparameter ablations.

| candidate   | status   | comment                                                  | config | source                                   |
| ----------- | -------- | -------------------------------------------------------- | ------ | ----------------------------------------- |
| lora        | pending  | Default PEFT baseline                                   | conf/exp_20260509_220815/config_0.yaml | planning.md, HF docs           |
| adalora     | pending  | Adaptive LoRA (higher flex, more recent)                | conf/exp_20260509_220815/config_1.yaml | planning.md, AdaLoRA paper     |
| ia3         | pending  | Very efficient per-gate vector scaling                  | conf/exp_20260509_220815/config_2.yaml | planning.md, IA3 paper         |
| oft         | pending  | Output-only fine-tuning, new PEFT approach              | conf/exp_20260509_220815/config_3.yaml | planning.md, OFT PR            |
| prefix      | pending  | Prefix-tuning (popular for seq2seq/encoder-decoder)     | conf/exp_20260509_220815/config_4.yaml | planning.md, Prefix Tuning paper|

**Unlock condition**: All methods run, and at least one finishes successfully (valid loss/metric available). If any method fails, rerun with safer settings or minimal epoch for that method.

---

### Wave 2: PEFT-specific parameter ablation (per-method best; e.g., LoRA r/alpha, Prefix-length)
**Why second**: Once best initial method is identified, fine-tuning its micro-hyperparameters has highest impact.

| candidate        | status   | comment                                 | config | source |
| ---------------- | -------- | --------------------------------------- | ------ | ------ |
| lora: r=4        | pending  | Lower-rank baseline                     |        | planning.md |
| lora: r=8        | pending  | Standard                                |        | planning.md |
| lora: r=16       | pending  | Higher expressive power                 |        | planning.md |
| adalora: r=(auto)| pending  | Adaptive rank, let model adjust         |        | planning.md |
| prefix: prefix_length=10| pending | Small prefix (fewer params)     |        | planning.md |
| prefix: prefix_length=30| pending | Literature std.                    |        | planning.md |
| prefix: prefix_length=60| pending | Large prefix                        |        | planning.md |

**Unlock condition**: Best method from Wave 1 is clear (either by metric or stability).

---

### Wave 3: Learning rate tuning (method family fixed)
**Why third**: Once family/hyperparams set, learning rate yields biggest remaining performance swings.

| candidate | status   | comment         | config | source |
| --------- | -------- | --------------- | ------ | ------ |
| 1e-4      | pending  | Common upper end |        |  |
| 5e-5      | pending  | Literature std.  |        |  |
| 1e-5      | pending  | Lower/stable     |        |  |

**Unlock condition**: Best method and PEFT-param regime found.

---

### Wave 4: Optimizer
**Why fourth**: Once lr and method are stable, optimizer affects convergence-quality tradeoff (AdamW, Adam, etc).

| candidate | status   | comment               | config | source |
| --------- | -------- | --------------------- | ------ | ------ |
| adamw     | pending  | Default/best practice |        |  |
| adam      | pending  | Simpler, sometimes stabler |   |  |

**Unlock condition**: At least two LRs are tested with best-performing method.

---

### Wave 5: warmup_steps
**Why fifth**: Only important when learning rate/optimizer are tuned; safeset: 0, 1000, 6000.

| candidate | status   | comment           | config | source |
| --------- | -------- | ----------------- | ------ | ------ |
| 0         | pending  | No warmup         |        |      |
| 1000      | pending  | Short warmup      |        |      |
| 6000      | pending  | Long (default)    |        |      |

**Unlock condition**: Learning rate/optimizer combo stable for >2 runs.

---

### Wave 6: batch size
**Why sixth**: Batch size tradeoff for compute/memory/regularization.

| candidate | status   | comment               | config | source |
| --------- | -------- | --------------------- | ------ | ------ |
| 2         | pending  | Min size (stability)  |        |      |
| 4         | pending  | Default               |        |      |
| 8         | pending  | Push throughput       |        |      |

**Unlock condition**: Model/optimizer stable at two batch sizes.

---

### Wave 7: max_epochs
**Why seventh**: Larger epoch only after method/learning hyperparams tuned.

| candidate | status   | comment           | config | source |
| --------- | -------- | ----------------- | ------ | ------ |
| 1         | pending  | Fast debug        |        |      |
| 2         | pending  | Literature std.   |        |      |
| 5         | pending  | For full learning |        |      |

**Unlock condition**: Stability and capacity established.

---

## Source Reference
- prompt.txt
- planning.md
- web research (links in codex_summary.md)

