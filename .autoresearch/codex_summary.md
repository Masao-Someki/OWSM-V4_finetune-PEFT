# Wave Summary for exp_20260510_011434

**Why this config set:**  
The previous array job failed debug for all non-LoRA candidates, with status DEBUG_FAILED for AdaLoRA and no stable or successful result for any candidate except the already-done LoRA baseline. As all PEFT algorithm variants are part of the same search axis and all failed at debug or did not reach execution, this wave is a targeted recovery: same axis, but with the most minimal, diagnostic configuration (4 samples per set, 10 steps, 1 epoch, `fast_dev_run: 10`). This will pinpoint implementation, model, or pipeline bugs rather than hyperparameter issues and will allow maximal parallel debugging across all remaining candidates before scientific sweep recommences.

**Search-space coverage:**  
- This wave targets the **active axis**: PEFT Adapter Algorithm (categorical, 9 remaining candidates).
- All methods from search plan are covered, with paths updated for current exp_name.
- No new axes explored.  
- Test converges → once stability is verified, progression to optimizer/lr/batch per plan.

**Checklist updates:**  
- All previously "pending" candidates on the PEFT axis are submitted as "done" (pending execution).
- No new axes/rows are opened; axis status will update next after stable completion.

**Next action:**  
1. Review ALL debug logs closely as soon as any config completes (fail = trace+fix; success = unlock next axis).
2. Only after >1 candidate (esp. AdaLoRA or IA3) go to non-debug FAIL, move to targeted bug/compat fixes.
3. Once any config completes a successful debug run, prepare a clean run for the same candidate with an increased number of steps/samples per normal protocol.
