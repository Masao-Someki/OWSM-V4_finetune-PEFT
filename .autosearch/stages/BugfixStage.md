# BugfixStage

## Header
- Stage Name: `BugfixStage`
- Stage Id: `bugfix`
- Previous Stage: `DebugGateStage`
- Start Condition: `store/latest_status.json` has `status == "DEBUG_FAILED"` and failure logs exist.
- End Condition: bugfix commits exist, failure logs are cleared, and status is `BUGFIX_PROPOSED`.
- On Success: `DebugGateStage` (retry same `exp_name`)
- Store Path: `self.store_path` resolves to `.autosearch/store/`.

## Behavior
1. Read latest failure context from status + failure log.
2. Ask LLM for minimal safe fix and parse `<file path="...">` edits.
3. Apply allowed-file edits, commit bugfix.
4. Update status, clear failure logs, commit cleanup.
5. Optionally send Slack summary.

Note: This stage does not run `git push`.
