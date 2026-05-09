#!/usr/bin/env python3
"""
ChatGPT API driver invoked from GitHub Actions.

Reads autoresearch state, asks ChatGPT to propose the next experiment wave,
then commits and pushes generated files on a new branch.

File writes are returned as <file path="...">content</file> blocks and parsed
via regex.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--repo-root", default=".")
    p.add_argument("--prompts-dir", default=".autoresearch/prompts")
    p.add_argument("--csv-path", default="experiments.csv")
    p.add_argument("--autoresearch-dir", default=".autoresearch")
    p.add_argument("--model", default="gpt-4o-mini")
    p.add_argument("--model-research", default="")
    p.add_argument("--model-bugfix", default="")
    p.add_argument("--model-prompt-refresh", default="")
    p.add_argument("--mode", choices=["auto", "bootstrap", "iterative"], default="auto")
    p.add_argument("--max-configs", type=int, default=10)
    p.add_argument("--max-tokens", type=int, default=8192)
    return p.parse_args()


def now_iso() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def read_file_safe(path: Path, max_chars: int = 8000) -> str:
    if not path.exists():
        return f"(file not found: {path.name})"
    text = path.read_text(encoding="utf-8", errors="replace")
    if len(text) > max_chars:
        text = "...(truncated)...\n" + text[-max_chars:]
    return text


def read_csv_tail(csv_path: Path, n_rows: int = 20) -> str:
    if not csv_path.exists() or csv_path.stat().st_size == 0:
        return "(empty)"
    lines = csv_path.read_text(encoding="utf-8", errors="replace").splitlines()
    if len(lines) <= 1:
        return "(empty)"
    header = lines[0]
    tail = lines[max(1, len(lines) - n_rows):]
    return "\n".join([header] + tail)


# ---------------------------------------------------------------------------
# Prompt building
# ---------------------------------------------------------------------------

def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sync_search_space_from_root_prompt(repo_root: Path, prompts_dir: Path, prompt_text: str) -> bool:
    """
    Generate `.autoresearch/prompts/search_space.md` from repo-root `prompt.txt`.
    """
    out_path = prompts_dir / "search_space.md"
    prompts_dir.mkdir(parents=True, exist_ok=True)
    prompt_hash = _sha256_text(prompt_text)

    generated = f"""# Search Strategy Checklist (Generated)

This file is auto-generated from repository-root `prompt.txt`.
Prompt SHA256: `{prompt_hash}`

## Interpretation Policy
- Follow constraints from `prompt.txt` first.
- If this file conflicts with `prompt.txt`, prioritize `prompt.txt`.
- Use `.autoresearch/notes/` and `experiments.csv` for evidence/prioritization.

## Execution Checklist (top-down)
- [ ] 1. Preflight
  - [ ] Confirm all base configs in `prompt.txt` exist.
  - [ ] Confirm debug gate policy (`yes/no`) from `prompt.txt`.
  - [ ] Confirm trial budget (max configs).
- [ ] 2. Stability-first smoke (small)
  - [ ] Start from conservative learning rate and small epoch/step budget.
  - [ ] Validate OOM/instability before broader search.
- [ ] 3. Primary axis sweep (coarse)
  - [ ] Prioritize `learning rate` and `optimizer` first.
  - [ ] Keep architecture/method-specific params conservative while selecting optimizer/LR region.
- [ ] 4. Secondary axis sweep (coarse)
  - [ ] Tune `batch size`, `warmup_steps`, `max_epochs` around stable region.
- [ ] 5. Method-family compare
  - [ ] Compare candidate adaptation/model method families under the best shared hyperparameter region.
- [ ] 6. Method-specific parameter refine
  - [ ] For top 1-2 method families, tune family-specific parameters.
- [ ] 7. Local parameter search around current best
  - [ ] Narrow around best config and run small neighborhood search.

## Research-Backed Candidate Values (to fill before wave planning)
- [ ] Use web search to collect current best practices for this task/model family.
- [ ] Prefer primary sources: official docs, papers, and strong reproduction reports.
- [ ] Record source links and short rationale for each proposed value range.
- [ ] If a known heuristic exists (example: pretrained LR scaling conventions), include it explicitly.
- [ ] For each axis from `prompt.txt`, add:
  - [ ] candidate values/ranges
  - [ ] search order (what to try first, second, ...)
  - [ ] stop/expand condition

### Required Web-Research Outputs
- [ ] `learning rate`: candidate ranges + ordering + heuristic basis
- [ ] `optimizer`: candidate set + ordering
- [ ] `batch size`, `warmup_steps`, `max_epochs`: safe-to-aggressive ordering
- [ ] `method family`: full candidate list from official docs and/or recent references
- [ ] `method-specific parameters`: family-specific knobs and ranges

## Practical Wave Policy
- Wave 1: stability-first + minimum viable comparison set.
- Wave 2: coarse search on highest-impact axes.
- Wave 3: method-family breadth check (based on web-collected full list).
- Wave 4+: local parameter search around the best method/config.

## prompt.txt (current)
```text
{prompt_text}
```
"""
    before = out_path.read_text(encoding="utf-8", errors="replace") if out_path.exists() else ""
    if before == generated:
        return False
    out_path.write_text(generated, encoding="utf-8")
    return True


def detect_and_apply_prompt_updates(
    repo_root: Path,
    prompts_dir: Path,
    store_dir: Path,
) -> tuple[bool, list[str]]:
    written: list[str] = []
    root_prompt_path = repo_root / "prompt.txt"
    if root_prompt_path.exists():
        prompt_text = root_prompt_path.read_text(encoding="utf-8", errors="replace").strip()
    else:
        prompt_text = "(prompt.txt not found at repository root)"

    prompt_hash = _sha256_text(prompt_text)
    state_path = store_dir / "prompt_state.json"
    prev_hash = ""
    if state_path.exists():
        try:
            prev_hash = json.loads(state_path.read_text(encoding="utf-8")).get("prompt_sha256", "")
        except Exception:
            prev_hash = ""

    prompt_changed = bool(prev_hash and prev_hash != prompt_hash)
    first_seen = not bool(prev_hash)

    if sync_search_space_from_root_prompt(repo_root, prompts_dir, prompt_text):
        written.append(".autoresearch/prompts/search_space.md")

    update_ctx_path = store_dir / "prompt_update_context.md"
    if prompt_changed:
        findings_path = repo_root / ".autoresearch" / "notes" / "autoresearch_findings.md"
        findings_path.parent.mkdir(parents=True, exist_ok=True)
        existing = findings_path.read_text(encoding="utf-8", errors="replace") if findings_path.exists() else ""
        entry = (
            f"\n## Wave Prep Note ({now_iso()})\n"
            f"- type: prompt_txt_updated\n"
            f"- action: refresh search space and notes before next wave planning\n"
            f"- prompt_sha256: `{prompt_hash}`\n"
        )
        findings_path.write_text(existing.rstrip() + "\n" + entry, encoding="utf-8")
        written.append(".autoresearch/notes/autoresearch_findings.md")
        update_ctx_path.write_text(
            (
                "prompt.txt was manually updated since the last planning run.\n"
                f"- previous_sha256: `{prev_hash}`\n"
                f"- current_sha256: `{prompt_hash}`\n"
                "- Treat this as an intentional search-space/policy update.\n"
                "- Re-baseline notes/checklist interpretation before proposing configs.\n"
            ),
            encoding="utf-8",
        )
    else:
        update_ctx_path.write_text(
            (
                "prompt.txt did not change since the last planning run.\n"
                f"- current_sha256: `{prompt_hash}`\n"
                f"- first_seen: `{first_seen}`\n"
            ),
            encoding="utf-8",
        )
    written.append(".autoresearch/store/prompt_update_context.md")

    state_path.write_text(json.dumps({
        "prompt_sha256": prompt_hash,
        "updated_at": now_iso(),
    }, indent=2, ensure_ascii=False), encoding="utf-8")
    written.append(".autoresearch/store/prompt_state.json")
    return prompt_changed, written


def build_system_prompt(repo_root: Path, prompts_dir: Path) -> str:
    search_space = read_file_safe(prompts_dir / "search_space.md")
    system_md = prompts_dir / "system.md"
    system_txt = prompts_dir / "system.txt"
    if system_md.exists():
        system_extra = read_file_safe(system_md)
    elif system_txt.exists():
        system_extra = read_file_safe(system_txt)
    else:
        system_extra = ""

    return f"""You are the experiment planner for iterative autoresearch.
Your goal is to propose the next experiment wave to improve the target metric defined in `prompt.txt`.

## Search Space Policy (MUST follow)
{search_space}

## Output Format
All file writes MUST use this exact XML tag format:

<file path="conf/exp_20260429_123456/config_0.yaml">
defaults:
  - ../base_recipe_template

lr: 5e-5
exp_tag: exp_20260429_123456_variant_a

method:
  type: adapter_like_method
  param_a: 8
  param_b: 0.05
</file>

<file path=".autoresearch/array_conf.txt">
conf/exp_20260429_123456/config_0.yaml
conf/exp_20260429_123456/config_1.yaml
</file>

<file path=".autoresearch/store/next_exp_name.txt">exp_20260429_123456</file>

<file path=".autoresearch/codex_summary.md">
# Wave Summary
...
</file>

Do NOT include `</file>` anywhere inside file content.

## Files You May Write
- `conf/{{next_exp_name}}/` — new YAML configs (create directory)
- `conf/` — shared configs when needed for bug fixes or feature updates
- `.autoresearch/array_conf.txt` — one config path per line (overwrite each wave)
- `.autoresearch/store/next_exp_name.txt` — REQUIRED: single line, the next_exp_name value
- `.autoresearch/codex_summary.md` — your summary of this wave
- `.autoresearch/notes/autoresearch_checklist.md` — update statuses only
- `.autoresearch/notes/autoresearch_findings.md` — append new entry only
- `src/` — code changes for bug fixes, model implementation, and pipeline updates
- `scripts/` — launcher/runtime bug fixes when needed
- `tests/test_config_load.py` — update parametrized config list if new test cases needed
- `tests/test_search_space.py` — update if needed

## Files You Must NOT Edit
- `exp/`, `dump/`, `data/`, `secrets/`, `.env`, `keys/`

## Config Format Rules
Each config in `conf/{{next_exp_name}}/` must:
1. Use `defaults: [- ../<template_stem>]` to inherit from a template under `conf/`
2. Set primary tuning fields (for example `lr`, method type, or equivalent) and override the fields being tested
3. Use `exp_tag: {{next_exp_name}}_<descriptor>` (unique per config)
4. NOT set `exp_dir` (inherited from default.yaml via exp_tag)

## array_conf.txt Format
One relative path per line (from repo root), no blank lines, no comments:
```
conf/exp_X/config_0.yaml
conf/exp_X/config_1.yaml
```

## Test Update Policy
If you add configs to a new exp_name directory, the tests auto-discover them via `conf/exp_*/*.yaml` glob.
You only need to manually edit tests if you add new validation logic for new method families/types.

## Checklist Policy
- Prioritize C0 if DOING: max 3 configs, trainer.max_epochs≤3, trainer.max_steps≤100
- Do not expand to new axes while C6 (stability) is DOING
- Mark items DONE only when you have concrete metric evidence

{system_extra}
"""


def build_user_prompt(
    repo_root: Path,
    autoresearch_dir: Path,
    prompts_dir: Path,
    csv_path: Path,
    max_configs: int,
    next_exp_name: str,
    mode: str,
) -> str:
    store_dir = autoresearch_dir / "store"
    next_goal = read_file_safe(store_dir / "next_goal.md")
    latest_metrics = read_file_safe(store_dir / "latest_metrics.json")
    latest_status = read_file_safe(store_dir / "latest_status.json")
    latest_error = read_file_safe(store_dir / "latest_error.log", max_chars=3000)
    checklist = read_file_safe(repo_root / ".autoresearch" / "notes" / "autoresearch_checklist.md")
    findings = read_file_safe(repo_root / ".autoresearch" / "notes" / "autoresearch_findings.md", max_chars=4000)
    csv_text = read_csv_tail(csv_path, n_rows=20)

    has_errors = (store_dir / "latest_error.log").exists() and \
                 (store_dir / "latest_error.log").stat().st_size > 0

    prompt_md = read_file_safe(prompts_dir / "prompt.md") if (prompts_dir / "prompt.md").exists() else ""
    followup_md = read_file_safe(prompts_dir / "followup.md") if (prompts_dir / "followup.md").exists() else ""
    error_md = read_file_safe(prompts_dir / "error.md") if (prompts_dir / "error.md").exists() else ""
    prompt_update_context = read_file_safe(store_dir / "prompt_update_context.md", max_chars=2000)

    error_section = ""
    if has_errors:
        error_section = f"""
## latest_error.log (failures detected — diagnose first)
```
{latest_error}
```
"""

    mode_section = ""
    if mode == "bootstrap":
        mode_section = """
## Mode
Bootstrap mode (first wave initialization).
- Assume no reliable prior wave results.
- Build a conservative first wave from root `prompt.txt`.
- If needed, initialize missing `.autoresearch/notes/` files with minimal reusable content.
"""
    else:
        mode_section = """
## Mode
Iterative mode (wave 2+).
- Use latest metrics/errors/checklist evidence to refine direction.
- Prioritize debugging and stability first when failures exist.
"""

    template_section = ""
    if has_errors and error_md:
        template_section = f"""
## Template Focus
Use this error-handling template as the primary instruction:
{error_md}
"""
    elif mode == "iterative" and followup_md:
        template_section = f"""
## Template Focus
Use this follow-up template as the primary instruction:
{followup_md}
"""
    elif prompt_md:
        template_section = f"""
## Template Focus
Use this base planning template as the primary instruction:
{prompt_md}
"""

    return f"""## Task

Plan and write the next experiment wave.

**next_exp_name**: `{next_exp_name}`
**max_configs**: {max_configs}
**mode**: `{mode}`
**timestamp**: {now_iso()}

---
{mode_section}
---
{template_section}
---

## prompt_update_context.md
{prompt_update_context}

---

## next_goal.md
{next_goal}

---

## latest_metrics.json
```json
{latest_metrics}
```

---

## latest_status.json
```json
{latest_status}
```
{error_section}
---

## autoresearch_checklist.md (current state)
{checklist}

---

## autoresearch_findings.md (recent entries)
{findings}

---

## experiments.csv (header + last 20 rows)
```
{csv_text}
```

---

## Required Output

You MUST write these files (use `<file path="...">...</file>` format):

1. `conf/{next_exp_name}/config_N.yaml` — one per proposed config (max {max_configs})
2. `.autoresearch/array_conf.txt` — list of those config paths
3. `.autoresearch/store/next_exp_name.txt` — must contain exactly: `{next_exp_name}`
4. `.autoresearch/codex_summary.md` — your rationale and wave summary

Include these sections in codex_summary.md:
- **Why this config set**: evidence from experiments.csv
- **Search-space coverage**: which axes this wave covers
- **Checklist updates**: which IDs change status and why
- **Next action**: what the wave after this should target
"""


def resolve_mode(args_mode: str, store_dir: Path) -> str:
    if args_mode in {"bootstrap", "iterative"}:
        return args_mode
    marker = store_dir / "bootstrap_done.json"
    return "iterative" if marker.exists() else "bootstrap"


def has_recent_errors(store_dir: Path) -> bool:
    err = store_dir / "latest_error.log"
    return err.exists() and err.stat().st_size > 0


def select_model(
    args: argparse.Namespace,
    prompt_changed: bool,
    has_errors: bool,
) -> tuple[str, str]:
    model_research = args.model_research.strip() or args.model
    model_bugfix = args.model_bugfix.strip() or model_research
    model_prompt_refresh = args.model_prompt_refresh.strip() or model_research

    if has_errors:
        return model_bugfix, "bugfix"
    if prompt_changed:
        return model_prompt_refresh, "prompt_refresh"
    return model_research, "research"


# ---------------------------------------------------------------------------
# File operation parsing
# ---------------------------------------------------------------------------

FILE_TAG_RE = re.compile(
    r'<file\s+path=["\']([^"\']+)["\']>(.*?)</file>',
    re.DOTALL,
)

ALLOWED_PREFIXES = (
    "conf/exp_",
    "conf/",
    "array_conf/",
    ".autoresearch/array_conf/",
    ".autoresearch/",
    ".autoresearch/notes/",
    "src/",
    "scripts/",
    "run.py",
    "pixi.toml",
    "tests/",
)


def apply_file_operations(response_text: str, repo_root: Path) -> list[str]:
    written: list[str] = []
    for m in FILE_TAG_RE.finditer(response_text):
        rel_path = m.group(1).strip()
        content = m.group(2)
        if content.startswith("\n"):
            content = content[1:]

        # Backward compatibility: accept legacy array_conf/<exp>/array.txt and remap it.
        if rel_path.startswith("array_conf/"):
            rel_path = f".autoresearch/{rel_path}"

        if not any(rel_path.startswith(p) for p in ALLOWED_PREFIXES):
            print(f"[WARN] skipping disallowed path: {rel_path}")
            continue

        # Prevent directory traversal.
        target = (repo_root / rel_path).resolve()
        if not str(target).startswith(str(repo_root)):
            print(f"[WARN] skipping path outside repo: {rel_path}")
            continue

        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        written.append(rel_path)
        print(f"[INFO] wrote: {rel_path} ({len(content)} chars)")

    return written


def normalize_array_conf_file(repo_root: Path, written: list[str], exp_name: str) -> list[str]:
    """Prefer flat .autoresearch/array_conf.txt and clean old per-exp list if present."""
    canonical = repo_root / ".autoresearch" / "array_conf.txt"
    legacy = repo_root / ".autoresearch" / "array_conf" / exp_name / "array.txt"

    if canonical.exists():
        # If both exist, remove legacy to avoid stale references.
        if legacy.exists():
            legacy.unlink()
        if ".autoresearch/array_conf.txt" not in written:
            written.append(".autoresearch/array_conf.txt")
        return written

    if legacy.exists():
        canonical.parent.mkdir(parents=True, exist_ok=True)
        canonical.write_text(legacy.read_text(encoding="utf-8"), encoding="utf-8")
        legacy.unlink()
        if ".autoresearch/array_conf.txt" not in written:
            written.append(".autoresearch/array_conf.txt")
        return written

    return written


# ---------------------------------------------------------------------------
# Git operations
# ---------------------------------------------------------------------------

def run_git(*args: str, cwd: Path, check: bool = True) -> tuple[int, str]:
    r = subprocess.run(
        ["git"] + list(args),
        cwd=str(cwd), capture_output=True, text=True, check=False,
    )
    if check and r.returncode != 0:
        raise RuntimeError(f"git {args[0]} failed: {r.stderr.strip()}")
    return r.returncode, r.stdout.strip()


def commit_to_current_branch(repo_root: Path, next_exp_name: str, written_files: list[str]) -> str:
    _, branch = run_git("rev-parse", "--abbrev-ref", "HEAD", cwd=repo_root)
    branch = branch.strip()
    run_git("add", "--", *written_files, cwd=repo_root)
    _, diff = run_git("diff", "--cached", "--name-only", cwd=repo_root, check=False)
    if not diff.strip():
        print("[WARN] nothing staged after add")
        return ""
    run_git(
        "-c", "user.name=autoresearch-bot",
        "-c", "user.email=autoresearch-bot@users.noreply.github.com",
        "commit", "-m", f"autoresearch: propose {next_exp_name}",
        cwd=repo_root,
    )
    run_git("push", "origin", branch, cwd=repo_root)
    return branch


# ---------------------------------------------------------------------------
# Slack helper (best-effort)
# ---------------------------------------------------------------------------

def try_notify(title: str, lines: list[str]) -> None:
    try:
        from src.slack_notify import format_status_message, post_slack_message
        post_slack_message(text=format_status_message(title=title, body_lines=lines))
    except Exception:
        pass


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    args = parse_args()
    repo_root = Path(args.repo_root).resolve()
    prompts_dir = (repo_root / args.prompts_dir).resolve()
    autoresearch_dir = (repo_root / args.autoresearch_dir).resolve()
    csv_path = (repo_root / args.csv_path).resolve()
    store_dir = (autoresearch_dir / "store").resolve()
    store_dir.mkdir(parents=True, exist_ok=True)
    mode = resolve_mode(args.mode, store_dir)

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    next_exp_name = f"exp_{ts}"

    api_key = os.environ.get("OPENAI_API_KEY", "")
    if not api_key:
        print("[ERROR] OPENAI_API_KEY not set")
        return 1

    prompt_changed, prewritten = detect_and_apply_prompt_updates(repo_root, prompts_dir, store_dir)
    has_errors = has_recent_errors(store_dir)
    selected_model, model_reason = select_model(args, prompt_changed=prompt_changed, has_errors=has_errors)
    if prompt_changed:
        print("[INFO] prompt.txt changed since last run; refreshed search space and notes before planning.")
    system_prompt = build_system_prompt(repo_root, prompts_dir)
    user_prompt = build_user_prompt(
        repo_root, autoresearch_dir, prompts_dir, csv_path, args.max_configs, next_exp_name, mode
    )

    print(
        f"[INFO] calling ChatGPT API: model={selected_model} reason={model_reason} "
        f"mode={mode} next_exp_name={next_exp_name}"
    )
    try_notify("AutoResearch: Wave Planning Started", [
        f"- model: `{selected_model}`",
        f"- model_reason: `{model_reason}`",
        f"- mode: `{mode}`",
        f"- next_exp_name: `{next_exp_name}`",
        f"- max_configs: `{args.max_configs}`",
    ])

    try:
        payload = {
            "model": selected_model,
            "max_output_tokens": args.max_tokens,
            "input": [
                {
                    "role": "system",
                    "content": [{"type": "input_text", "text": system_prompt}],
                },
                {
                    "role": "user",
                    "content": [{"type": "input_text", "text": user_prompt}],
                },
            ],
        }
        req = urllib.request.Request(
            "https://api.openai.com/v1/responses",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        with urllib.request.urlopen(req) as res:
            body = json.loads(res.read().decode("utf-8"))
    except Exception as e:
        print(f"[ERROR] ChatGPT API call failed: {e}", file=sys.stderr)
        try_notify("AutoResearch: ChatGPT API Failed", [f"- error: `{str(e)[:200]}`"])
        return 1

    response_text = (body.get("output_text") or "").strip()
    if not response_text:
        parts: list[str] = []
        for item in body.get("output", []):
            for content in item.get("content", []):
                if content.get("type") == "output_text":
                    t = (content.get("text") or "").strip()
                    if t:
                        parts.append(t)
        response_text = "\n".join(parts).strip()
    usage = body.get("usage", {}) if isinstance(body, dict) else {}
    tokens_in = usage.get("input_tokens", 0)
    tokens_out = usage.get("output_tokens", 0)
    print(f"[INFO] ChatGPT response: {len(response_text)} chars "
          f"(in={tokens_in} out={tokens_out})")

    # Runtime state is kept under .autoresearch/store (prompts/ is template-only).
    (store_dir / "last_response.txt").write_text(response_text, encoding="utf-8")
    # Keep writing to the legacy location for backward compatibility.
    (prompts_dir / "last_response.txt").write_text(response_text, encoding="utf-8")

    # Apply file operations from model output.
    written = prewritten + apply_file_operations(response_text, repo_root)

    if not written:
        print("[ERROR] ChatGPT wrote no files. Check .autoresearch/store/last_response.txt")
        try_notify("AutoResearch: No Files Written", [
            "- ChatGPT response produced no <file> tags",
            "- See .autoresearch/store/last_response.txt",
        ])
        return 1

    # Verify next_exp_name output.
    next_exp_name_path = autoresearch_dir / "store" / "next_exp_name.txt"
    if not next_exp_name_path.exists():
        print("[ERROR] .autoresearch/store/next_exp_name.txt not written by planner")
        return 1
    confirmed_exp_name = next_exp_name_path.read_text().strip()

    written = normalize_array_conf_file(repo_root, written, confirmed_exp_name)

    # Verify array config list (new flat file first, then legacy fallback).
    array_txt = repo_root / ".autoresearch" / "array_conf.txt"
    if not array_txt.exists():
        array_txt = repo_root / ".autoresearch" / "array_conf" / confirmed_exp_name / "array.txt"
    if not array_txt.exists():
        print("[ERROR] array config list not found (.autoresearch/array_conf.txt or legacy path)")
        return 1

    bootstrap_marker_path = store_dir / "bootstrap_done.json"
    bootstrap_marker_path.write_text(json.dumps({
        "done": True,
        "mode": mode,
        "updated_at": now_iso(),
        "exp_name": confirmed_exp_name,
    }, indent=2), encoding="utf-8")
    written.append(".autoresearch/store/bootstrap_done.json")

    # Commit and push on the current branch.
    try:
        branch = commit_to_current_branch(repo_root, confirmed_exp_name, written)
    except Exception as e:
        print(f"[ERROR] git branch/commit failed: {e}", file=sys.stderr)
        try_notify("AutoResearch: Git Commit Failed", [f"- error: `{str(e)[:200]}`"])
        return 1

    if not branch:
        print("[ERROR] branch creation failed (nothing to commit)")
        return 1

    # Keep writing next_branch for compatibility with external tooling.
    (autoresearch_dir / "store" / "next_branch.txt").write_text(branch)
    print(f"[INFO] done. branch={branch} exp_name={confirmed_exp_name}")

    try_notify("AutoResearch: Wave Proposed", [
        f"- branch: `{branch}`",
        f"- exp_name: `{confirmed_exp_name}`",
        f"- files_written: `{len(written)}`",
        f"- tokens: `in={tokens_in} out={tokens_out}`",
    ])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
