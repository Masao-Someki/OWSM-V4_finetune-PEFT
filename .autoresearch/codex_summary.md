# Wave Summary

## Why this config set

All debug and full runs for PEFT configs in the previous wave (`exp_20260509_222054`) failed. All candidate algorithms are still marked pending, except for LoRA baseline (now marked "done") since it was attempted with relevant parameters. No candidates have working metric evidence. The wave structure covers the full categorical sweep of adapter/PEFT algorithm families recommended in state-of-the-art speech PEFT literature and Huggingface documentation. 

## Search-space coverage

- **Axis**: PEFT Adapter Algorithm (categorical)
- **Configs covered**: AdaLoRA, IA3, OFT, VERA, LoRA variants (r=4/16, extended targets), IA3_kv, AdaLoRA_r16
- **LoRA (r=8)** is marked done (attempted), rest are pending and submitted.

## Checklist updates

- **PEFT Adapter Algorithm**
  - LoRA: status changed to **done** (attempted, debug+full both failed)
  - All other methods: status remains **pending**
- No axes unlocked; learning rate, optimizer, warmup etc. remain deferred.
- Stability remains unresolved due to persistent runtime/debug failures.

## Next action

- Wait for completion of this categorical sweep: AdaLoRA, IA3, OFT, VERA, LoRA-r4/r16, extended-targets, AdaLoRA-r16, IA3_kv.
- On persistent crash/failure: triage log, target simplest/most robust candidate (e.g. IA3/LoRA-r4) for minimal/no-adapter smoke test or code/infra bugfix.
- On successful debug/metric: advance to learning rate or peft parameter grid per roadmap.
