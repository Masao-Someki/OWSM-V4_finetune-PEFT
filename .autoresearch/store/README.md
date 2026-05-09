# .autoresearch/store

Runtime state files for autoresearch workflows.

Policy:
- `prompts/` is for reusable prompt templates.
- `store/` is for runtime-generated state and diagnostics.

Typical files:
- `last_response.txt`: raw LLM response from latest planning run
- `session.txt`: lightweight session marker (if used)
- future state snapshots as needed
