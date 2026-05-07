#!/usr/bin/env python3
"""
Autoresearch watcher — called by check_and_submit.slurm.

State machine:
  RESEARCH_RUNNING            → poll sacct every 1min → on complete: collect metrics, git push → WAITING_FOR_RESEARCH_UPDATE
  WAITING_FOR_RESEARCH_UPDATE → poll git fetch every 1min → on new commit: git pull, sbatch next → RESEARCH_RUNNING
  IDLE                 → do nothing, do not resubmit (manual restart required)
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from src.slack_notify import format_status_message, post_slack_message

STATE_PATH = REPO_ROOT / ".autoresearch" / "watcher_state.json"
WATCH_LOG_PATH = REPO_ROOT / ".autoresearch" / "watcher_commit_check.log"
RESUBMIT_DELAY_SEC = 60  # 1分
PHASE_RESEARCH_RUNNING = "RESEARCH_RUNNING"
PHASE_WAITING_FOR_RESEARCH_UPDATE = "WAITING_FOR_RESEARCH_UPDATE"
PHASE_IDLE = "IDLE"

# Backward-compat aliases
LEGACY_PHASE_MAP = {
    "EXPERIMENT_RUNNING": PHASE_RESEARCH_RUNNING,
    "WAITING_FOR_PR_MERGE": PHASE_WAITING_FOR_RESEARCH_UPDATE,
}

TERMINAL_STATES = {
    "COMPLETED", "FAILED", "CANCELLED", "TIMEOUT",
    "NODE_FAIL", "OUT_OF_MEMORY", "PREEMPTED",
    "BOOT_FAIL", "DEADLINE", "REVOKED",
}


def now_iso() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def append_watch_log(message: str) -> None:
    WATCH_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with WATCH_LOG_PATH.open("a", encoding="utf-8") as f:
        f.write(f"{now_iso()} {message}\n")


# ---------------------------------------------------------------------------
# State I/O
# ---------------------------------------------------------------------------

def load_state() -> dict:
    if not STATE_PATH.exists():
        return {"phase": "IDLE"}
    try:
        return json.loads(STATE_PATH.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"[WARN] failed to load watcher_state.json: {e}", file=sys.stderr)
        return {"phase": "IDLE"}


def save_state(state: dict) -> None:
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    state["phase_updated_at"] = now_iso()
    STATE_PATH.write_text(json.dumps(state, indent=2, ensure_ascii=False))


def normalize_phase(phase: str) -> str:
    return LEGACY_PHASE_MAP.get(phase, phase)


# ---------------------------------------------------------------------------
# Slurm helpers
# ---------------------------------------------------------------------------

def run_cmd(args: list[str], **kwargs) -> tuple[int, str, str]:
    try:
        r = subprocess.run(args, capture_output=True, text=True, check=False, **kwargs)
        return r.returncode, r.stdout.strip(), r.stderr.strip()
    except FileNotFoundError:
        return 127, "", f"{args[0]}: command not found"


def query_array_states(array_job_id: str) -> dict[str, str]:
    """sacct で array_job_id の全タスク状態を返す。{job_id_task: state}"""
    rc, out, _ = run_cmd([
        "sacct", "-n", "-P", "-j", array_job_id,
        "--format=JobIDRaw,State",
    ])
    states: dict[str, str] = {}
    if rc != 0 or not out:
        return states
    for line in out.splitlines():
        parts = line.split("|")
        if len(parts) < 2:
            continue
        jid = parts[0].strip()
        state = parts[1].strip().split()[0].split("+")[0].upper()
        if "_" in jid:  # array task (e.g., 17915098_0)
            states[jid] = state
    return states


def all_terminal(states: dict[str, str]) -> bool:
    return bool(states) and all(s in TERMINAL_STATES for s in states.values())


# ---------------------------------------------------------------------------
# Git helpers
# ---------------------------------------------------------------------------

def git(*args, check: bool = True) -> tuple[int, str]:
    rc, out, err = run_cmd(["git", "-C", str(REPO_ROOT)] + list(args))
    if check and rc != 0:
        print(f"[ERROR] git {' '.join(args)} failed: {err}", file=sys.stderr)
        raise RuntimeError(f"git {args[0]} failed (rc={rc}): {err}")
    return rc, out


def current_main_sha() -> str:
    _, sha = git("rev-parse", "origin/main")
    return sha.strip()


def has_new_commits(last_sha: str) -> bool:
    git("fetch", "origin", check=False)
    new_sha = current_main_sha()
    return new_sha != last_sha


def git_push_results(exp_name: str = "") -> None:
    """
    実験結果を main へ push。

    Pushed:
      .autoresearch/   — state files (metrics JSON, error log, next_goal, etc.)
      experiments.csv  — run metadata with wer/cer
      results/{exp_name}/ — eval metrics, eval CSV, train log tails, error log tails
      notes/           — checklist / findings (変更があれば)

    NOT pushed:
      exp/             — gitignore 済み (checkpoints 含む)
      logs/            — gitignore 済み (raw Slurm logs)
    """
    git("add",
        ".autoresearch/watcher_state.json",
        ".autoresearch/latest_status.json",
        ".autoresearch/latest_metrics.json",
        ".autoresearch/latest_error.log",
        ".autoresearch/next_goal.md",
        "experiments.csv",
        check=False)

    git("add", ".autoresearch/notes/", check=False)

    # results/{exp_name}/ を追加（存在する場合）
    if exp_name:
        results_dir = REPO_ROOT / ".autoresearch" / "results" / exp_name
        if results_dir.exists():
            git("add", f".autoresearch/results/{exp_name}/", check=False)
            print(f"[INFO] staging results/{exp_name}/")

    _, diff = git("diff", "--cached", "--name-only", check=False)
    if not diff.strip():
        print("[INFO] nothing to commit, skipping push")
        return

    staged_files = diff.strip().splitlines()
    print(f"[INFO] staging {len(staged_files)} files")

    git(
        "-c", "user.name=autoresearch-watcher",
        "-c", "user.email=autoresearch-watcher@cluster",
        "commit", "-m", f"autoresearch: results {now_iso()}"
    )
    git("push", "origin", "main")
    print("[INFO] git push done")


# ---------------------------------------------------------------------------
# Metrics collection
# ---------------------------------------------------------------------------

def collect_metrics(exp_name: str, array_job_id: str) -> dict:
    rc, out, err = run_cmd([
        sys.executable, str(REPO_ROOT / ".autoresearch" / "collect_metrics.py"),
        "--exp-name", exp_name,
        "--array-job-id", array_job_id,
        "--csv-path", str(REPO_ROOT / ".autoresearch" / "experiments.csv"),
        "--output", str(REPO_ROOT / ".autoresearch" / "latest_metrics.json"),
        "--error-output", str(REPO_ROOT / ".autoresearch" / "latest_error.log"),
    ], cwd=str(REPO_ROOT))
    if rc != 0:
        print(f"[WARN] collect_metrics failed (rc={rc}): {err}", file=sys.stderr)
        return {}
    print(out)
    metrics_path = REPO_ROOT / ".autoresearch" / "latest_metrics.json"
    if metrics_path.exists():
        try:
            return json.loads(metrics_path.read_text())
        except Exception:
            pass
    return {}


def write_latest_status(exp_name: str, array_job_id: str, task_states: dict[str, str]) -> None:
    failed = [k for k, v in task_states.items() if v != "COMPLETED"]
    status = {
        "exp_name": exp_name,
        "array_job_id": array_job_id,
        "total_tasks": len(task_states),
        "completed": len(task_states) - len(failed),
        "failed": len(failed),
        "finished_at": now_iso(),
        "failed_task_ids": failed,
    }
    out = REPO_ROOT / ".autoresearch" / "latest_status.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(status, indent=2, ensure_ascii=False))


def write_next_goal(exp_name: str, array_job_id: str, metrics: dict) -> None:
    best_wer = metrics.get("best_wer")
    best_uid = metrics.get("best_run_uid", "")
    failed_count = metrics.get("failed_count", 0)

    content = (
        f"# Next Goal\n\n"
        f"- Previous wave: `{exp_name}` (array_job_id=`{array_job_id}`)\n"
        f"- Finished at: {now_iso()}\n"
        f"- Mode: slurm\n"
        f"- Max configs for next wave: 10\n\n"
        f"## Evidence from latest wave\n"
        f"- Best WER: `{best_wer}`\n"
        f"- Best run: `{best_uid}`\n"
        f"- Failed tasks: `{failed_count}`\n"
        f"- See `.autoresearch/latest_metrics.json` for full details.\n\n"
        f"## Instruction\n"
        f"1. Read `notes/autoresearch_checklist.md` and prioritize unresolved IDs.\n"
        f"2. Read `experiments.csv` and summarize completed/failed results.\n"
        f"3. Propose next wave within `prompts/search_space.md`.\n"
        f"4. If C0 is unresolved: max 3 configs, trainer.max_epochs≤3.\n"
        f"5. Write all output files using `<file path=\"...\">...</file>` format.\n"
    )
    (REPO_ROOT / ".autoresearch" / "next_goal.md").write_text(content)


# ---------------------------------------------------------------------------
# Submit next experiment
# ---------------------------------------------------------------------------

def submit_next_experiment(state: dict) -> Optional[str]:
    """
    .autoresearch/next_exp_name.txt を読んで array 投入。
    成功したら新しい array_job_id を返す。
    """
    next_exp_name_path = REPO_ROOT / ".autoresearch" / "next_exp_name.txt"
    if not next_exp_name_path.exists():
        print("[ERROR] .autoresearch/next_exp_name.txt not found after git pull")
        return None

    next_exp_name = next_exp_name_path.read_text().strip()
    if not next_exp_name:
        print("[ERROR] next_exp_name.txt is empty")
        return None

    config_list = REPO_ROOT / ".autoresearch" / "array_conf" / next_exp_name / "array.txt"
    if not config_list.exists():
        print(f"[ERROR] array.txt not found: {config_list}")
        return None

    lines = [
        l.strip() for l in config_list.read_text().splitlines()
        if l.strip() and not l.strip().startswith("#")
    ]
    if not lines:
        print(f"[ERROR] array.txt is empty: {config_list}")
        return None

    n = len(lines)
    array_range = f"0-{n - 1}"
    print(f"[INFO] submitting {next_exp_name}: {n} configs, range={array_range}")

    rc, out, err = run_cmd([
        "bash",
        str(REPO_ROOT / ".autoresearch" / "submit-array-with-debug.sh"),
        next_exp_name, array_range, str(config_list),  # .autoresearch/array_conf/ "0",
    ], cwd=str(REPO_ROOT))

    if rc != 0:
        print(f"[ERROR] submit failed (rc={rc}):\n{err}", file=sys.stderr)
        post_slack_message(text=format_status_message(
            title="Watcher: Submit Failed",
            body_lines=[
                f"- exp_name: `{next_exp_name}`",
                f"- exit_code: `{rc}`",
                f"- error: `{err[:200]}`",
            ],
        ))
        return None

    print(out)
    # "Submitted batch job 17915098" を解析
    new_array_job_id = ""
    for line in out.splitlines():
        if "Submitted batch job" in line:
            new_array_job_id = line.strip().split()[-1]
            break

    if not new_array_job_id:
        print("[WARN] could not parse array_job_id from sbatch output")
        return None

    state["array_job_id"] = new_array_job_id
    state["exp_name"] = next_exp_name
    state["phase"] = PHASE_RESEARCH_RUNNING
    state["submitted_at"] = now_iso()
    save_state(state)

    post_slack_message(text=format_status_message(
        title="Watcher: Next Experiment Submitted",
        body_lines=[
            f"- exp_name: `{next_exp_name}`",
            f"- array_job_id: `{new_array_job_id}`",
            f"- configs: `{n}`",
        ],
    ))
    return new_array_job_id


# ---------------------------------------------------------------------------
# Self-resubmit
# ---------------------------------------------------------------------------

def resubmit_self(delay_sec: int = RESUBMIT_DELAY_SEC) -> None:
    slurm_script = REPO_ROOT / ".autoresearch" / "check_and_submit.slurm"
    rc, out, err = run_cmd([
        "sbatch",
        f"--begin=now+{delay_sec}",
        str(slurm_script),
    ], cwd=str(REPO_ROOT))
    if rc != 0:
        print(f"[ERROR] resubmit failed (rc={rc}): {err}", file=sys.stderr)
    else:
        job_id = out.strip().split()[-1] if out else "?"
        print(f"[INFO] resubmitted self: job_id={job_id} delay={delay_sec}s")


# ---------------------------------------------------------------------------
# Main state machine
# ---------------------------------------------------------------------------

def handle_experiment_running(state: dict) -> None:
    array_job_id = state.get("array_job_id", "")
    exp_name = state.get("exp_name", "")

    if not array_job_id:
        print("[ERROR] array_job_id not set in watcher_state.json")
        resubmit_self()
        return

    task_states = query_array_states(array_job_id)
    if not task_states:
        print(f"[WARN] sacct returned no tasks for {array_job_id}. controller may be down.")
        resubmit_self()
        return

    if not all_terminal(task_states):
        running = [k for k, v in task_states.items() if v not in TERMINAL_STATES]
        print(f"[INFO] array {array_job_id} still running: {len(running)} tasks active")
        resubmit_self()
        return

    failed_count = sum(1 for v in task_states.values() if v != "COMPLETED")
    print(f"[INFO] array {array_job_id} complete. "
          f"total={len(task_states)} failed={failed_count}")
    post_slack_message(text=format_status_message(
        title="Watcher: Array Completed",
        body_lines=[
            f"- exp_name: `{exp_name}`",
            f"- array_job_id: `{array_job_id}`",
            f"- total: `{len(task_states)}`",
            f"- failed: `{failed_count}`",
        ],
    ))

    # 結果収集
    metrics = collect_metrics(exp_name, array_job_id)
    write_latest_status(exp_name, array_job_id, task_states)
    write_next_goal(exp_name, array_job_id, metrics)

    # mainのSHAを記録してからpush
    try:
        git("fetch", "origin", check=False)
        state["last_main_sha"] = current_main_sha()
    except Exception:
        state["last_main_sha"] = ""

    state["phase"] = PHASE_WAITING_FOR_RESEARCH_UPDATE
    save_state(state)

    try:
        git_push_results(exp_name=exp_name)
    except Exception as e:
        print(f"[ERROR] git push failed: {e}", file=sys.stderr)
        post_slack_message(text=format_status_message(
            title="Watcher: Git Push Failed",
            body_lines=[f"- error: `{str(e)[:200]}`"],
        ))

    post_slack_message(text=format_status_message(
        title="Watcher: Waiting for PR Merge",
        body_lines=[
            f"- exp_name: `{exp_name}`",
            f"- pushed results, GitHub Actions will create next wave PR",
        ],
    ))
    resubmit_self()


def handle_waiting_for_pr(state: dict) -> None:
    last_sha = state.get("last_main_sha", "")

    try:
        git("fetch", "origin", check=False)
        new_sha = current_main_sha()
    except Exception as e:
        print(f"[WARN] git fetch failed: {e}")
        append_watch_log(f"fetch_failed last_sha={last_sha[:8]} error={str(e)[:160]}")
        resubmit_self()
        return

    if new_sha == last_sha:
        print(f"[INFO] no new commits on main (sha={last_sha[:8]}). still waiting.")
        append_watch_log(f"no_new_commit sha={last_sha[:8]}")
        resubmit_self()
        return

    print(f"[INFO] new commits detected: {last_sha[:8]} → {new_sha[:8]}")
    append_watch_log(f"new_commit_detected from={last_sha[:8]} to={new_sha[:8]}")
    try:
        git("pull", "origin", "main")
    except Exception as e:
        print(f"[ERROR] git pull failed: {e}", file=sys.stderr)
        append_watch_log(f"pull_failed target_sha={new_sha[:8]} error={str(e)[:160]}")
        resubmit_self()
        return

    state["last_main_sha"] = new_sha
    save_state(state)

    new_array_job_id = submit_next_experiment(state)
    if not new_array_job_id:
        print("[WARN] submit failed. will retry on next tick.")
    resubmit_self()


def main() -> int:
    state = load_state()
    phase = normalize_phase(state.get("phase", PHASE_IDLE))
    if state.get("phase") != phase:
        state["phase"] = phase
        save_state(state)
    print(f"[INFO] watcher tick: phase={phase} time={now_iso()}")
    print(f"[INFO] state: {json.dumps(state)}")
    append_watch_log(
        f"tick phase={phase} exp={state.get('exp_name', '')} array_job_id={state.get('array_job_id', '')}"
    )

    post_slack_message(text=format_status_message(
        title=f"Watcher Tick: {phase}",
        body_lines=[
            f"- exp_name: `{state.get('exp_name', '')}`",
            f"- array_job_id: `{state.get('array_job_id', '')}`",
        ],
    ))

    if phase == PHASE_RESEARCH_RUNNING:
        handle_experiment_running(state)
    elif phase == PHASE_WAITING_FOR_RESEARCH_UPDATE:
        handle_waiting_for_pr(state)
    else:
        print(f"[INFO] phase={phase!r}: idle, not resubmitting.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
