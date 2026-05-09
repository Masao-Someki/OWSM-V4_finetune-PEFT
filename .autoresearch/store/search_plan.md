# Search Space Checklist

## Candidate Values

### PEFT method

| algorithm     | status  | comment                            | config                                        | source |
|---------------|---------|------------------------------------|-----------------------------------------------|--------|
| lora          | pending | Baseline, most cited, r=8          |                                               |        |
| adalora       | pending | Adaptive-rank, recent SOTA         |                                               |        |
| ia3           | pending | Lightweight gate-based PEFT        |                                               |        |
| adapter       | pending | Classic bottleneck adapters        |                                               |        |
| prefix_tuning | pending | Virtual tokens, S2S, low resource  |                                               |        |
| oft           | pending | Orthogonal Fusion, speech/S2S       |                                               |        |
| lora_r2       | pending | LoRA, low rank ablation            |                                               |        |
| lora_r32      | pending | LoRA, high rank ablation           |                                               |        |

Experimented all methods?: no

---

### Peft parameters

(will enumerate after PEFT method finishes)

---

### Learning rate

(will enumerate after best PEFT method selected)

---

### optimizer

(will enumerate after best PEFT and parameter combo)

---

### warmup_steps

(will enumerate after best PEFT and optimizer combo)

---

### batch size

(will enumerate after best PEFT and optimizer combo)

---

### max_epochs

(will enumerate after best PEFT and optimizer combo)

