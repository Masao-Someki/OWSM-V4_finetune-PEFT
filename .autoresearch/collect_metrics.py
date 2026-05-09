#!/usr/bin/env python3
"""
Scan exp/{exp_name}/*/infer/metrics.json and update experiments.csv.
Writes summary to .autoresearch/store/latest_metrics.json.
Copies result artifacts to results/{exp_name}/ for GitHub tracking.

Copied to results/ (git-tracked):
  {exp_tag}/metrics.json     — eval metrics
  {exp_tag}/eval.csv         — eval CSV files (if any)
  {exp_tag}/train_tail.txt   — last TRAIN_TAIL_LINES of train.log
  errors/{run_uid}.txt       — last ERROR_TAIL_LINES of failed Slurm logs

NOT copied (stays on cluster only):
  exp/*/checkpoints/         — model weights
  exp/*/wandb/               — WandB local files
  exp/*/stats/               — collect_stats output (large)
  logs/*.log                 — raw full Slurm logs

Usage:
    python scripts/collect_metrics.py \
        --exp-name exp_20260429_123456 \
        --array-job-id 17915098
"""
from __future__ import annotations

import argparse
import csv
import fcntl
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

TRAIN_TAIL_LINES = 500
ERROR_TAIL_LINES = 200


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--exp-name", required=True)
    p.add_argument("--array-job-id", required=True)
    p.add_argument("--csv-path", default=".autoresearch/store/experiments.csv")
    p.add_argument("--output", default=".autoresearch/store/latest_metrics.json")
    p.add_argument("--error-output", default=".autoresearch/store/latest_error.log")
    p.add_argument("--results-dir", default=".autoresearch/results")
    p.add_argument("--logs-dir", default="logs")
    return p.parse_args()


def now_iso() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    if not path.exists() or path.stat().st_size == 0:
        return [], []
    with path.open(newline="") as f:
        reader = csv.DictReader(f)
        fieldnames = list(reader.fieldnames or [])
        rows = [{k: (v or "") for k, v in row.items()} for row in reader]
    return fieldnames, rows


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, str]]) -> None:
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row.get(k, "") for k in fieldnames})


def extract_metrics(metrics_data: dict) -> tuple[float | None, float | None]:
    """Extract WER/CER from metrics.json (ESPnet3-compatible)."""
    def _find(data: Any, keys: list[str]) -> float | None:
        if isinstance(data, dict):
            for k in keys:
                if k in data:
                    v = data[k]
                    if isinstance(v, (int, float)):
                        return float(v)
            for v in data.values():
                found = _find(v, keys)
                if found is not None:
                    return found
        return None

    wer = _find(metrics_data, ["WER", "wer", "word_error_rate"])
    cer = _find(metrics_data, ["CER", "cer", "char_error_rate"])
    return wer, cer


def tail_lines(path: Path, n: int) -> str:
    try:
        lines = path.read_text(errors="replace").splitlines()
        return "\n".join(lines[-n:])
    except Exception:
        return ""


# ---------------------------------------------------------------------------
# Write artifacts into results/
# ---------------------------------------------------------------------------

def copy_to_results(
    exp_root: Path,
    exp_tag: str,
    results_exp_dir: Path,
) -> None:
    """Copy successful run artifacts into results/{exp_name}/{exp_tag}/."""
    exp_dir = exp_root / exp_tag
    out_dir = results_exp_dir / exp_tag
    out_dir.mkdir(parents=True, exist_ok=True)

    # eval metrics.json
    metrics_src = exp_dir / "infer" / "metrics.json"
    if metrics_src.exists():
        shutil.copy2(metrics_src, out_dir / "metrics.json")

    # eval CSV (all *.csv under infer/)
    for csv_src in (exp_dir / "infer").glob("*.csv"):
        shutil.copy2(csv_src, out_dir / csv_src.name)

    # tail of train.log (use the newest when multiple logs exist)
    train_logs = sorted(exp_dir.glob("train*.log"), key=lambda p: p.stat().st_mtime, reverse=True)
    if not train_logs:
        train_logs = sorted(exp_dir.glob("*.log"), key=lambda p: p.stat().st_mtime, reverse=True)
    if train_logs:
        tail = tail_lines(train_logs[0], TRAIN_TAIL_LINES)
        if tail:
            (out_dir / "train_tail.txt").write_text(
                f"# {train_logs[0].name} (last {TRAIN_TAIL_LINES} lines)\n\n" + tail,
                encoding="utf-8",
            )


def copy_error_to_results(
    logs_dir: Path,
    exp_name: str,
    run_uid: str,
    results_errors_dir: Path,
) -> None:
    """Copy tail of failed Slurm logs into results/{exp_name}/errors/{run_uid}.txt."""
    exp_logs = logs_dir / exp_name
    # run_uid: {array_job_id}_{task_id}_{exp_tag}
    parts = run_uid.split("_")
    if len(parts) < 2:
        return
    array_job_id, task_id = parts[0], parts[1]

    log_path = exp_logs / f"{array_job_id}_{task_id}.log"
    if not log_path.exists():
        # debug log fallback
        debug_logs = sorted(
            exp_logs.glob(f"debug_*.log"),
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )
        if not debug_logs:
            return
        log_path = debug_logs[0]

    tail = tail_lines(log_path, ERROR_TAIL_LINES)
    if not tail:
        return

    results_errors_dir.mkdir(parents=True, exist_ok=True)
    safe_uid = run_uid.replace("/", "_")
    (results_errors_dir / f"{safe_uid}.txt").write_text(
        f"# {log_path.name} (last {ERROR_TAIL_LINES} lines)\n"
        f"# run_uid: {run_uid}\n\n" + tail,
        encoding="utf-8",
    )


def collect_aggregate_error_log(failed_run_uids: list[str], results_errors_dir: Path) -> str:
    """Build aggregate error log content for .autoresearch/store/latest_error.log."""
    chunks = []
    for run_uid in failed_run_uids[:5]:
        safe_uid = run_uid.replace("/", "_")
        p = results_errors_dir / f"{safe_uid}.txt"
        if p.exists():
            chunks.append(p.read_text(encoding="utf-8", errors="replace"))
    return "\n\n".join(chunks)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    args = parse_args()
    exp_root = Path("exp") / args.exp_name
    csv_path = Path(args.csv_path)
    lock_path = csv_path.with_suffix(csv_path.suffix + ".lock")
    lock_path.parent.mkdir(parents=True, exist_ok=True)

    results_exp_dir = Path(args.results_dir) / args.exp_name
    results_errors_dir = results_exp_dir / "errors"
    logs_dir = Path(args.logs_dir)

    wave_summary: list[dict] = []
    best_wer = float("inf")
    best_run_uid = ""
    failed_run_uids: list[str] = []

    # -----------------------------------------------------------------------
    # Step 1: scan metrics.json files
    # -----------------------------------------------------------------------
    metrics_by_exp_tag: dict[str, tuple[float | None, float | None]] = {}
    for metrics_path in sorted(exp_root.glob("*/infer/metrics.json")):
        exp_tag = metrics_path.parent.parent.name
        try:
            data = json.loads(metrics_path.read_text())
        except Exception as e:
            print(f"[WARN] failed to read {metrics_path}: {e}")
            continue
        wer, cer = extract_metrics(data)
        metrics_by_exp_tag[exp_tag] = (wer, cer)
        print(f"[INFO] {exp_tag}: WER={wer} CER={cer}")

        # Copy successful run artifacts to results/
        copy_to_results(exp_root, exp_tag, results_exp_dir)

    # -----------------------------------------------------------------------
    # Step 2: update experiments.csv
    # -----------------------------------------------------------------------
    with lock_path.open("a+") as lockf:
        fcntl.flock(lockf, fcntl.LOCK_EX)
        fieldnames, rows = read_csv(csv_path)

        for col in ("wer", "cer"):
            if fieldnames and col not in fieldnames:
                fieldnames.append(col)

        updated = 0
        for row in rows:
            if row.get("exp_name", "").strip() != args.exp_name:
                continue
            run_uid = row.get("run_uid", "").strip()
            exp_tag_from_uid = "_".join(run_uid.split("_")[2:]) if run_uid else ""

            wer, cer = metrics_by_exp_tag.get(exp_tag_from_uid, (None, None))
            if wer is not None:
                row["wer"] = str(wer)
                updated += 1
            if cer is not None:
                row["cer"] = str(cer)

            status = row.get("status", "").strip()
            entry: dict = {
                "run_uid": run_uid,
                "base_config": row.get("base_config", "").strip(),
                "peft_type": row.get("peft_type", "").strip(),
                "lr": row.get("learning_rate", "").strip(),
                "trainer_max_epochs": row.get("trainer_max_epochs", "").strip(),
                "wer": wer,
                "cer": cer,
                "status": status,
            }
            wave_summary.append(entry)

            if status == "FAILED":
                failed_run_uids.append(run_uid)
            if wer is not None and float(wer) < best_wer:
                best_wer = float(wer)
                best_run_uid = run_uid

        if updated > 0 and fieldnames:
            write_csv(csv_path, fieldnames, rows)
            print(f"[INFO] updated {updated} rows in {csv_path}")
        fcntl.flock(lockf, fcntl.LOCK_UN)

    # -----------------------------------------------------------------------
    # Step 3: copy failure logs into results/errors/
    # -----------------------------------------------------------------------
    for run_uid in failed_run_uids:
        copy_error_to_results(logs_dir, args.exp_name, run_uid, results_errors_dir)

    # .autoresearch/store/latest_error.log (aggregated)
    err_path = Path(args.error_output)
    err_path.parent.mkdir(parents=True, exist_ok=True)
    if failed_run_uids:
        agg = collect_aggregate_error_log(failed_run_uids, results_errors_dir)
        if agg:
            err_path.write_text(agg, encoding="utf-8")
            print(f"[INFO] wrote aggregated error log: {err_path}")
    else:
        err_path.write_text("")

    # -----------------------------------------------------------------------
    # Step 4: write latest_metrics.json
    # -----------------------------------------------------------------------
    output_data = {
        "exp_name": args.exp_name,
        "array_job_id": args.array_job_id,
        "collected_at": now_iso(),
        "wave_summary": wave_summary,
        "best_run_uid": best_run_uid,
        "best_wer": best_wer if best_wer < float("inf") else None,
        "failed_count": len(failed_run_uids),
        "results_dir": str(results_exp_dir),
    }
    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(output_data, indent=2, ensure_ascii=False))
    print(f"[INFO] wrote {out_path} ({len(wave_summary)} runs, "
          f"{len(metrics_by_exp_tag)} with metrics, {len(failed_run_uids)} failed)")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
