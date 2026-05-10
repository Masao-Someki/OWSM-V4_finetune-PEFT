# Search Space Index & Web Research Summary

## Active Axis — PEFT Adapter Algorithm

| algorithm         | status   | config path                                  | rationale                       |
|-------------------|----------|----------------------------------------------|----------------------------------|
| lora              | done     | conf/exp_20260510_005653/config_0.yaml       | SOTA, ASR baseline [Hu et al. '21] |
| adalora           | done     | conf/exp_20260510_011434/config_1.yaml       | Adaptive LoRA [Zhang et al. '23] |
| ia3               | done     | conf/exp_20260510_011434/config_2.yaml       | Lightweight tuning [Lester '21]  |
| oft               | done     | conf/exp_20260510_011434/config_3.yaml       | Orthogonal; novel, less stable   |
| vera              | done     | conf/exp_20260510_011434/config_4.yaml       | Variational adapter [Kim '24]    |
| lora_r16          | done     | conf/exp_20260510_011434/config_5.yaml       | Higher-r LoRA, SNR/training capacity |
| lora_r4           | done     | conf/exp_20260510_011434/config_6.yaml       | Lower-r LoRA, compactness eval   |
| adalora_r16       | done     | conf/exp_20260510_011434/config_7.yaml       | AdaLoRA, high cap                |
| ia3_kv            | done     | conf/exp_20260510_011434/config_8.yaml       | IA3 (kv-only variant)            |
| lora_extended     | done     | conf/exp_20260510_011434/config_9.yaml       | Extended module LoRA [github/peft]|

## Literature & Web Guidance Cited

| method       | reference                                                      |
|--------------|---------------------------------------------------------------|
| LoRA         | https://arxiv.org/abs/2106.09685                              |
| AdaLoRA      | https://arxiv.org/abs/2303.10512                              |
| IA3          | https://arxiv.org/abs/2205.05638                              |
| OFT          | https://arxiv.org/abs/2310.02244                              |
| VERA         | https://arxiv.org/abs/2402.02133                              |
| HuggingFace/PEFT | https://github.com/huggingface/peft                      |

- Debug run for non-LoRA methods failed previously. Now testing all at minimal load to diagnose.
- After debug stability, full metric evaluation and sweep of learning rate/optimizer will unlock.

## Slack-ready summary

- All major PEFT methods run, all debug & all with main parameter variants.
- Next step: Unblock failure/debug, then advance axis.
