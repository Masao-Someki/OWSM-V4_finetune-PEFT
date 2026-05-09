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
    p.add_argument("--model", default="gpt-4.1-mini")
    p.add_argument("--model-research", default="gpt-4.1")
    p.add_argument("--model-bugfix", default="")
    p.add_argument("--model-prompt-refresh", default="")
    p.add_argument("--model-search-plan", default="gpt-4.1")
    p.add_argument("--mode", choices=["auto", "bootstrap", "iterative"], default="auto")
    p.add_argument("--max-configs", type=int, default=10)
    p.add_argument("--max-tokens", type=int, default=8192)
    p.add_argument("--cache-dirs", nargs="*", default=["conf", "src"],
                   help="Directories to read and include as repo context in the system prompt.")
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


def compact_markdown_for_slack(path: Path, max_lines: int = 12, max_chars: int = 1800) -> list[str]:
    if not path.exists():
        return []
    text = path.read_text(encoding="utf-8", errors="replace")
    lines = [line.rstrip() for line in text.splitlines() if line.strip()]
    picked: list[str] = []
    total = 0
    for line in lines[:max_lines]:
        line = re.sub(r"^#+\s*", "", line)
        line = re.sub(r"\|", " | ", line)
        if total + len(line) > max_chars:
            break
        picked.append(f"- {line}")
        total += len(line)
    return picked


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
# Directory context
# ---------------------------------------------------------------------------

_CONTEXT_EXTS = {".yaml", ".py", ".sh", ".md", ".txt", ".toml"}


def read_dirs_as_context(repo_root: Path, dirs: list[str], max_chars: int = 20000) -> str:
    parts: list[str] = []
    total = 0
    for d in dirs:
        dpath = repo_root / d
        if not dpath.is_dir():
            continue
        for f in sorted(dpath.rglob("*")):
            if not f.is_file() or f.suffix not in _CONTEXT_EXTS:
                continue
            try:
                text = f.read_text(encoding="utf-8", errors="replace")
            except Exception:
                continue
            rel = f.relative_to(repo_root)
            entry = f"\n### {rel}\n```\n{text.rstrip()}\n```\n"
            if total + len(entry) > max_chars:
                parts.append(f"\n### (truncated — remaining files omitted)\n")
                return "# Repository Context\n" + "".join(parts)
            parts.append(entry)
            total += len(entry)
    if not parts:
        return ""
    return "# Repository Context\n" + "".join(parts)


# ---------------------------------------------------------------------------
# Prompt building
# ---------------------------------------------------------------------------

def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


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

    update_ctx_path = store_dir / "prompt_update_context.md"
    if prompt_changed:
        findings_path = store_dir / "findings.md"
        findings_path.parent.mkdir(parents=True, exist_ok=True)
        existing = findings_path.read_text(encoding="utf-8", errors="replace") if findings_path.exists() else ""
        entry = (
            f"\n## Wave Prep Note ({now_iso()})\n"
            f"- type: prompt_txt_updated\n"
            f"- action: refresh search space and notes before next wave planning\n"
            f"- prompt_sha256: `{prompt_hash}`\n"
        )
        findings_path.write_text(existing.rstrip() + "\n" + entry, encoding="utf-8")
        written.append(".autoresearch/store/findings.md")
        update_ctx_path.write_text(
            (
                "prompt.txt was manually updated since the last planning run.\n"
                f"- previous_sha256: `{prev_hash}`\n"
                f"- current_sha256: `{prompt_hash}`\n"
                "- Treat this as an intentional search-space/policy update.\n"
                "- Re-baseline notes/checklist interpretation before proposing configs.\n"
                "- Regenerate `.autoresearch/store/search_plan.md` in this run.\n"
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


def build_system_prompt(repo_root: Path, prompts_dir: Path, repo_context: str = "") -> str:
    search_plan = read_file_safe(prompts_dir / "search_plan.md")
    system_md = prompts_dir / "system.md"
    system_txt = prompts_dir / "system.txt"
    if system_md.exists():
        system_extra = read_file_safe(system_md)
    elif system_txt.exists():
        system_extra = read_file_safe(system_txt)
    else:
        system_extra = ""

    repo_context_section = f"\n{repo_context}\n" if repo_context else ""

    return f"""You are the experiment planner for iterative autoresearch.{repo_context_section}
Your goal is to propose the next experiment wave to improve the target metric defined in `prompt.txt`.

## Search Space Policy (MUST follow)
{search_plan}

## Search Space Authoring (MUST write each run)
- Use `.autoresearch/prompts/search_plan.md` as reference context/template.
- You must write `.autoresearch/store/search_plan.md` in this run.
- Build it from repository-root `prompt.txt` plus web research evidence.
- Choose one current focus axis from `prompt.txt` section 6.
- Enumerate explicit candidate values, trial order, and rationale links for that current focus axis only.
- Keep the remaining axes deferred until the current focus axis is resolved.
- If the active axis is finite/categorical, enumerate the broadest practical candidate set you can justify.
- If the active axis is numeric, choose coarse, information-efficient values first rather than dense low-signal increments.
- Prefer patterns like `1e-5, 5e-5, 1e-4` over `1e-5, 2e-5, 3e-5` unless prior evidence justifies local refinement.

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
- `.autoresearch/store/search_plan.md` — active search-space checklist and value enumeration for next research
- `.autoresearch/store/search_plan_report.md` — search-space index plus web-research results summary table
- `.autoresearch/store/checklist.md` — update statuses only
- `.autoresearch/store/findings.md` — append new entry only
- `src/` — code changes for bug fixes, model implementation, and pipeline updates
- `scripts/` — launcher/runtime bug fixes when needed
- `tests/test_config_load.py` — update parametrized config list if new test cases needed
- `tests/test_search_plan.py` — update if needed

## Files You Must NOT Edit
- `exp/`, `dump/`, `data/`, `secrets/`, `.env`, `keys/`

## CRITICAL: No Placeholder Names in Output
`search_plan_human.md` uses dummy names like `method_A`, `method_B`, `method_C` only to illustrate file format.
These are NOT real method names. NEVER write `method_A`, `method_B`, `method_C`, or any `method_*` placeholder into any config or search_plan.md.
All method names in output must be real names (e.g. `lora`, `adalora`, `ia3`, `vera`, `oft`) discovered via web search.

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
- Prioritize C0 if DOING: max 3 configs, use minimal training epochs/steps
- Do not expand to new axes while stability is unresolved
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
    checklist = read_file_safe(store_dir / "checklist.md")
    findings = read_file_safe(store_dir / "findings.md", max_chars=4000)
    csv_text = read_csv_tail(csv_path, n_rows=20)

    has_errors = (store_dir / "latest_error.log").exists() and \
                 (store_dir / "latest_error.log").stat().st_size > 0

    prompt_md = read_file_safe(prompts_dir / "prompt.md") if (prompts_dir / "prompt.md").exists() else ""
    followup_md = read_file_safe(prompts_dir / "followup.md") if (prompts_dir / "followup.md").exists() else ""
    error_md = read_file_safe(prompts_dir / "error.md") if (prompts_dir / "error.md").exists() else ""
    prompt_update_context = read_file_safe(store_dir / "prompt_update_context.md", max_chars=2000)
    human_search_plan = read_file_safe(prompts_dir / "search_plan_human.md", max_chars=12000)
    active_search_plan = read_file_safe(store_dir / "search_plan.md", max_chars=12000)

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

## store/checklist.md (current state)
{checklist}

---

## store/findings.md (recent entries)
{findings}

---

## experiments.csv (header + last 20 rows)
```
{csv_text}
```

---

## search_plan_human.md (format reference — structure only)
The names below (method_A, method_B, ...) are dummy placeholders for format illustration.
Do NOT use them in output. Use real method names discovered via web search.
{human_search_plan}

---

## active search_plan.md (append-only base)
{active_search_plan}

---

## Required Output

You MUST write these files (use `<file path="...">...</file>` format):

1. `conf/{next_exp_name}/config_N.yaml` — one per proposed config (max {max_configs})
2. `.autoresearch/array_conf.txt` — list of those config paths
3. `.autoresearch/store/next_exp_name.txt` — must contain exactly: `{next_exp_name}`
4. `.autoresearch/codex_summary.md` — your rationale and wave summary
5. `.autoresearch/store/search_plan.md` — regenerated from `prompt.txt` + web research (active file)
6. `.autoresearch/store/search_plan_report.md` — consolidated search-space index and research-results table

Include these sections in codex_summary.md:
- **Why this config set**: evidence from experiments.csv
- **Search-space coverage**: which axes this wave covers
- **Checklist updates**: which IDs change status and why
- **Next action**: what the wave after this should target

For `.autoresearch/store/search_plan.md`:
- Use checkboxes (`- [ ]`) for executable steps.
- Treat the existing `.autoresearch/store/search_plan.md` as append-only project memory.
- Preserve prior sections, prior findings, and prior candidate tables unless they are clearly superseded and explicitly marked as updated.
- Do not replace the whole file with a fresh short summary.
- Update by appending new observations, new candidate rows, new decisions, and new unlock conditions.
- Choose one active axis from `prompt.txt` section 6 and enumerate explicit candidate values only for that axis.
- Include trial order and source links for the active axis.
- Do not introduce extra axes unless explicitly allowed by `prompt.txt`.
- Follow the structure/style of `search_plan_human.md` as the primary format template.
- Use `.autoresearch/prompts/search_plan.md` as context baseline, then write improved content to `.autoresearch/store/search_plan.md`.
- Make the search space explicitly sequential:
  - Say why the current axis is the right one to resolve now.
  - Keep non-active axes as deferred placeholders only.
  - State what result unlocks the next axis and name that next axis.
- Candidate-value policy:
  - For finite/categorical axes, list the maximum practical candidate set, especially when the total set is small enough to enumerate.
  - For numeric axes, use coarse values that cover the plausible range efficiently; avoid dense adjacent values unless refining around evidence.

For `.autoresearch/store/search_plan_report.md`:
- Write a compact human-readable summary of the current search space.
- Include a table of the active axis candidates and a table summarizing web-research findings/sources.
- Make it suitable for pasting into Slack with minimal cleanup.
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
    model_search_plan = args.model_search_plan.strip() or model_prompt_refresh

    if has_errors:
        return model_bugfix, "bugfix"
    if prompt_changed:
        return model_search_plan, "search_plan"
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
        print("[INFO] prompt.txt changed since last run; refreshed prompt/update notes and will regenerate search_plan.")
    repo_context = read_dirs_as_context(repo_root, args.cache_dirs) if args.cache_dirs else ""
    if repo_context:
        print(f"[INFO] repo context loaded: {len(repo_context)} chars from {args.cache_dirs}")
    system_prompt = build_system_prompt(repo_root, prompts_dir, repo_context)
    user_prompt = build_user_prompt(
        repo_root, autoresearch_dir, prompts_dir, csv_path, args.max_configs, next_exp_name, mode
    )

    print(
        f"[INFO] calling OpenAI API: model={selected_model} reason={model_reason} "
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
        if model_reason in ("research", "search_plan"):
            payload["tools"] = [{"type": "web_search_preview"}]
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
        print(f"[ERROR] OpenAI API call failed: {e}", file=sys.stderr)
        try_notify("AutoResearch: OpenAI API Failed", [f"- error: `{str(e)[:200]}`"])
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
    print(f"[INFO] OpenAI response: {len(response_text)} chars "
          f"(in={tokens_in} out={tokens_out})")

    # Runtime state is kept under .autoresearch/store (prompts/ is template-only).
    (store_dir / "last_response.txt").write_text(response_text, encoding="utf-8")
    # Keep writing to the legacy location for backward compatibility.
    (prompts_dir / "last_response.txt").write_text(response_text, encoding="utf-8")

    # Apply file operations from model output.
    written = prewritten + apply_file_operations(response_text, repo_root)

    if not written:
        print("[ERROR] model wrote no files. Check .autoresearch/store/last_response.txt")
        try_notify("AutoResearch: No Files Written", [
            "- model response produced no <file> tags",
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
    ] + (
        ["- search_plan_report:"] +
        compact_markdown_for_slack(
            autoresearch_dir / "store" / "search_plan_report.md",
            max_lines=10,
            max_chars=1500,
        )
        if (autoresearch_dir / "store" / "search_plan_report.md").exists()
        else []
    ))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
