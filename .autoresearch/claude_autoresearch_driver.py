#!/usr/bin/env python3
"""
Claude API driver invoked from GitHub Actions.

Reads autoresearch state, asks Claude to propose the next experiment wave,
then commits and pushes generated files on a new branch.

File writes are returned as <file path="...">content</file> blocks and parsed
via regex.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--repo-root", default=".")
    p.add_argument("--prompts-dir", default=".autoresearch/prompts")
    p.add_argument("--csv-path", default=".autoresearch/store/experiments.csv")
    p.add_argument("--autoresearch-dir", default=".autoresearch")
    p.add_argument("--model", default="claude-opus-4-7")
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

def sync_search_space_from_root_prompt(repo_root: Path, prompts_dir: Path) -> None:
    """
    Generate `.autoresearch/prompts/search_space.md` from repo-root `prompt.txt`.
    """
    root_prompt_path = repo_root / "prompt.txt"
    out_path = prompts_dir / "search_space.md"
    prompts_dir.mkdir(parents=True, exist_ok=True)

    if root_prompt_path.exists():
        root_prompt = root_prompt_path.read_text(encoding="utf-8", errors="replace").strip()
    else:
        root_prompt = "(prompt.txt not found at repository root)"

    generated = f"""# Search Space Snapshot (Generated)

This file is auto-generated from repository-root `prompt.txt`.
Generated at: {now_iso()}

## Interpretation Policy
- Follow search-space definitions and hard constraints from `prompt.txt`.
- If this file conflicts with `prompt.txt`, prioritize `prompt.txt`.
- Use `.autoresearch/notes/` and `experiments.csv` for evidence and prioritization only.

## prompt.txt (current)
```text
{root_prompt}
```
"""
    out_path.write_text(generated, encoding="utf-8")


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

    return f"""You are the experiment planner for OWSM PEFT autoresearch.
Your goal is to find the best PEFT method and hyperparameters for FLEURS ASR by proposing the next experiment wave.

## Search Space Policy (MUST follow)
{search_space}

## Output Format
All file writes MUST use this exact XML tag format:

<file path="conf/exp_20260429_123456/config_0.yaml">
defaults:
  - ../../owsm_peft_lora_basic

lr: 5e-5
exp_tag: exp_20260429_123456_lora_lr5e-5

peft:
  type: lora
  r: 8
  lora_alpha: 8
  lora_dropout: 0.05
  task_type: seq_2_seq_lm
  target_modules: ["linear_q", "linear_k", "linear_v", "linear_out", "w_1", "w_2"]
</file>

<file path="array_conf/exp_20260429_123456/array.txt">
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
- `array_conf/{{next_exp_name}}/array.txt` — one config path per line
- `.autoresearch/store/next_exp_name.txt` — REQUIRED: single line, the next_exp_name value
- `.autoresearch/codex_summary.md` — your summary of this wave
- `.autoresearch/notes/autoresearch_checklist.md` — update statuses only
- `.autoresearch/notes/autoresearch_findings.md` — append new entry only
- `tests/test_config_load.py` — update parametrized config list if new test cases needed
- `tests/test_search_space.py` — update if needed

## Files You Must NOT Edit
- `conf/default.yaml`, `conf/dataset.yaml`, `conf/inference.yaml`, `conf/metrics.yaml`
- `conf/owsm_peft_*.yaml` (templates — use as defaults targets)
- `experiments.csv`, `src/`, `scripts/`, `run.py`, `pixi.toml`
- `exp/`, `dump/`, `data/`, `secrets/`, `.env`, `keys/`

## Config Format Rules
Each config in `conf/{{next_exp_name}}/` must:
1. Use `defaults: [- ../../<peft_template>]` to inherit from a PEFT template
2. Set `lr`, `peft.type`, and at minimum override the fields being tested
3. Use `exp_tag: {{next_exp_name}}_<descriptor>` (unique per config)
4. NOT set `exp_dir` (inherited from default.yaml via exp_tag)

## array.txt Format
One relative path per line (from repo root), no blank lines, no comments:
```
conf/exp_X/config_0.yaml
conf/exp_X/config_1.yaml
```

## Test Update Policy
If you add configs to a new exp_name directory, the tests auto-discover them via `conf/exp_*/*.yaml` glob.
You only need to manually edit tests if you need to add specific test logic for new PEFT types.

## Checklist Policy
- Prioritize C0 if DOING: max 3 configs, trainer.max_epochs≤3, trainer.max_steps≤100
- Do not expand to new axes while C6 (stability) is DOING
- Mark items DONE only when you have concrete metric evidence

{system_extra}
"""


def build_user_prompt(
    repo_root: Path,
    autoresearch_dir: Path,
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

    return f"""## Task

Plan and write the next experiment wave.

**next_exp_name**: `{next_exp_name}`
**max_configs**: {max_configs}
**mode**: `{mode}`
**timestamp**: {now_iso()}

---
{mode_section}
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
2. `.autoresearch/array_conf/{next_exp_name}/array.txt` — list of those config paths
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


# ---------------------------------------------------------------------------
# File operation parsing
# ---------------------------------------------------------------------------

FILE_TAG_RE = re.compile(
    r'<file\s+path=["\']([^"\']+)["\']>(.*?)</file>',
    re.DOTALL,
)

ALLOWED_PREFIXES = (
    "conf/exp_",
    ".autoresearch/array_conf/",
    ".autoresearch/",
    ".autoresearch/notes/",
    "tests/",
)


def apply_file_operations(response_text: str, repo_root: Path) -> list[str]:
    written: list[str] = []
    for m in FILE_TAG_RE.finditer(response_text):
        rel_path = m.group(1).strip()
        content = m.group(2)
        if content.startswith("\n"):
            content = content[1:]

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


def commit_to_branch(repo_root: Path, next_exp_name: str, written_files: list[str]) -> str:
    branch = f"autoresearch/{next_exp_name}"
    run_git("checkout", "-b", branch, cwd=repo_root)
    run_git("add", "--", *written_files, cwd=repo_root)
    _, diff = run_git("diff", "--cached", "--name-only", cwd=repo_root, check=False)
    if not diff.strip():
        print("[WARN] nothing staged after add")
        run_git("checkout", "-", cwd=repo_root, check=False)
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

    try:
        import anthropic
    except ImportError:
        print("[ERROR] anthropic package not installed. Run: pip install anthropic")
        return 1

    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        print("[ERROR] ANTHROPIC_API_KEY not set")
        return 1

    client = anthropic.Anthropic(api_key=api_key)

    sync_search_space_from_root_prompt(repo_root, prompts_dir)
    system_prompt = build_system_prompt(repo_root, prompts_dir)
    user_prompt = build_user_prompt(
        repo_root, autoresearch_dir, csv_path, args.max_configs, next_exp_name, mode
    )

    print(f"[INFO] calling Claude API: model={args.model} mode={mode} next_exp_name={next_exp_name}")
    try_notify("AutoResearch: Wave Planning Started", [
        f"- model: `{args.model}`",
        f"- mode: `{mode}`",
        f"- next_exp_name: `{next_exp_name}`",
        f"- max_configs: `{args.max_configs}`",
    ])

    try:
        message = client.messages.create(
            model=args.model,
            max_tokens=args.max_tokens,
            system=[
                {
                    "type": "text",
                    "text": system_prompt,
                    "cache_control": {"type": "ephemeral"},
                }
            ],
            messages=[{"role": "user", "content": user_prompt}],
        )
    except Exception as e:
        print(f"[ERROR] Claude API call failed: {e}", file=sys.stderr)
        try_notify("AutoResearch: Claude API Failed", [f"- error: `{str(e)[:200]}`"])
        return 1

    response_text = message.content[0].text
    tokens_in = message.usage.input_tokens
    tokens_out = message.usage.output_tokens
    print(f"[INFO] Claude response: {len(response_text)} chars "
          f"(in={tokens_in} out={tokens_out})")

    # Runtime state is kept under .autoresearch/store (prompts/ is template-only).
    (store_dir / "last_response.txt").write_text(response_text, encoding="utf-8")
    # Keep writing to the legacy location for backward compatibility.
    (prompts_dir / "last_response.txt").write_text(response_text, encoding="utf-8")

    # Apply file operations from model output.
    written = apply_file_operations(response_text, repo_root)

    if not written:
        print("[ERROR] Claude wrote no files. Check .autoresearch/store/last_response.txt")
        try_notify("AutoResearch: No Files Written", [
            "- Claude response produced no <file> tags",
            "- See .autoresearch/store/last_response.txt",
        ])
        return 1

    # Verify next_exp_name output.
    next_exp_name_path = autoresearch_dir / "store" / "next_exp_name.txt"
    if not next_exp_name_path.exists():
        print("[ERROR] .autoresearch/store/next_exp_name.txt not written by Claude")
        return 1
    confirmed_exp_name = next_exp_name_path.read_text().strip()

    # Verify array.txt.
    array_txt = repo_root / ".autoresearch" / "array_conf" / confirmed_exp_name / "array.txt"
    if not array_txt.exists():
        print(f"[ERROR] array.txt not found: {array_txt}")
        return 1

    bootstrap_marker_path = store_dir / "bootstrap_done.json"
    bootstrap_marker_path.write_text(json.dumps({
        "done": True,
        "mode": mode,
        "updated_at": now_iso(),
        "exp_name": confirmed_exp_name,
    }, indent=2), encoding="utf-8")
    written.append(".autoresearch/store/bootstrap_done.json")

    # Create branch and push.
    try:
        branch = commit_to_branch(repo_root, confirmed_exp_name, written)
    except Exception as e:
        print(f"[ERROR] git branch/commit failed: {e}", file=sys.stderr)
        try_notify("AutoResearch: Git Commit Failed", [f"- error: `{str(e)[:200]}`"])
        return 1

    if not branch:
        print("[ERROR] branch creation failed (nothing to commit)")
        return 1

    # Write next_branch for the GitHub Actions PR creation step.
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
