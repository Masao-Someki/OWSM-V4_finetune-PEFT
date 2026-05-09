#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import fcntl
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List

from src.slack_notify import format_status_message, post_slack_message


FIELDS: List[str] = [
    "run_uid",
    "status",
    "created_at",
    "start_time",
    "end_time",
    "duration_sec",
    "exit_code",
    "exp_name",
    "experiment_comment",
    "stages",
    "config_list",
    "train_config_path",
    "infer_config_path",
    "measure_config_path",
    "base_config",
    "runtime_config",
    "exp_tag",
    "exp_dir",
    "model_tag",
    "learning_rate",
    "peft_type",
    "peft_detail",
    "optimizer_detail",
    "scheduler_detail",
    "trainer_detail",
    "model_init_detail",
    "trainer_max_epochs",
    "trainer_max_steps",
    "trainer_accumulate_grad_batches",
    "trainer_gradient_clip_val",
    "trainer_precision",
    "trainer_fast_dev_run",
    "seed",
    "num_device",
    "num_nodes",
    "slurm_job_name",
    "slurm_job_id",
    "slurm_array_job_id",
    "slurm_array_task_id",
    "hostname",
    "cuda_visible_devices",
    "command",
    "wer",
    "cer",
]


def now_iso() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Upsert experiment tracking rows in CSV.")
    p.add_argument("--mode", choices=["start", "finish"], required=True)
    p.add_argument("--csv-path", default="experiments.csv")
    p.add_argument("--lock-path", default=".autoresearch/store/experiments.csv.lock")
    p.add_argument("--run-uid", required=True)
    p.add_argument("--exit-code", type=int, default=None)

    for f in FIELDS:
        if f in {"run_uid", "status", "created_at", "start_time", "end_time", "duration_sec", "exit_code"}:
            continue
        p.add_argument(f"--{f.replace('_', '-')}", default=None)
    return p.parse_args()


def load_config_values(runtime_config: str | None) -> Dict[str, str]:
    if not runtime_config:
        return {}

    cfg_path = Path(runtime_config)
    if not cfg_path.exists():
        return {}

    try:
        from espnet3.utils.config_utils import load_config_with_defaults
        from omegaconf import OmegaConf
        cfg = load_config_with_defaults(cfg_path)
        cfg = OmegaConf.to_container(cfg, resolve=True)
    except Exception:
        try:
            from omegaconf import OmegaConf
            cfg = OmegaConf.load(cfg_path)
            cfg = OmegaConf.to_container(cfg, resolve=True)
        except Exception:
            return {}

    def g(path, default=""):
        cur = cfg
        for k in path.split("."):
            if not isinstance(cur, dict) or k not in cur:
                return default
            cur = cur[k]
        return cur

    def compact(v) -> str:
        try:
            return json.dumps(v, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        except Exception:
            return str(v)

    peft_value = g("model.peft", "")
    if isinstance(peft_value, dict):
        peft_type = str(peft_value.get("type", ""))
    else:
        peft_type = str(peft_value)

    model_init = g("model", {})
    if isinstance(model_init, dict):
        model_init = {k: v for k, v in model_init.items() if k != "_target_"}

    trainer_cfg = g("trainer", {})
    optimizer_cfg = g("optimizer", {})
    scheduler_cfg = g("scheduler", {})

    return {
        "exp_tag": str(g("exp_tag", "")),
        "exp_dir": str(g("exp_dir", "")),
        "model_tag": str(g("model.model_tag", "")),
        "learning_rate": str(g("lr", "")),
        "peft_type": peft_type,
        "peft_detail": compact(peft_value),
        "optimizer_detail": compact(optimizer_cfg),
        "scheduler_detail": compact(scheduler_cfg),
        "trainer_detail": compact(trainer_cfg),
        "model_init_detail": compact(model_init),
        "trainer_max_epochs": str(g("trainer.max_epochs", "")),
        "trainer_max_steps": str(g("trainer.max_steps", "")),
        "trainer_accumulate_grad_batches": str(g("trainer.accumulate_grad_batches", "")),
        "trainer_gradient_clip_val": str(g("trainer.gradient_clip_val", "")),
        "trainer_precision": str(g("trainer.precision", "")),
        "trainer_fast_dev_run": str(g("trainer.fast_dev_run", "")),
        "seed": str(g("seed", "")),
        "num_device": str(g("num_device", "")),
        "num_nodes": str(g("num_nodes", "")),
    }


def read_rows(path: Path) -> List[Dict[str, str]]:
    if not path.exists() or path.stat().st_size == 0:
        return []
    with path.open("r", newline="") as f:
        reader = csv.DictReader(f)
        return [{k: (v if v is not None else "") for k, v in row.items()} for row in reader]


def write_rows(path: Path, rows: List[Dict[str, str]]) -> None:
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row.get(k, "") for k in FIELDS})


def upsert_row(rows: List[Dict[str, str]], run_uid: str) -> Dict[str, str]:
    for r in rows:
        if r.get("run_uid") == run_uid:
            return r
    row = {k: "" for k in FIELDS}
    row["run_uid"] = run_uid
    rows.append(row)
    return row


def compute_duration_sec(start_time: str, end_time: str) -> str:
    if not start_time or not end_time:
        return ""
    try:
        s = datetime.fromisoformat(start_time)
        e = datetime.fromisoformat(end_time)
        return str(int((e - s).total_seconds()))
    except Exception:
        return ""


def main() -> int:
    args = parse_args()
    csv_path = Path(args.csv_path)
    csv_path.parent.mkdir(parents=True, exist_ok=True)

    lock_path = Path(args.lock_path)
    lock_path.parent.mkdir(parents=True, exist_ok=True)

    with lock_path.open("a+") as lockf:
        fcntl.flock(lockf, fcntl.LOCK_EX)
        rows = read_rows(csv_path)
        row = upsert_row(rows, args.run_uid)

        if not row.get("created_at"):
            row["created_at"] = now_iso()

        for f in FIELDS:
            if f in {"run_uid", "status", "created_at", "start_time", "end_time", "duration_sec", "exit_code"}:
                continue
            val = getattr(args, f, None)
            if val is not None and str(val) != "":
                row[f] = str(val)

        cfg_values = load_config_values(getattr(args, "runtime_config", None))
        for k, v in cfg_values.items():
            if v != "":
                row[k] = v

        if args.mode == "start":
            row["status"] = "RUNNING"
            row["start_time"] = now_iso()
            row["exit_code"] = ""
            row["end_time"] = ""
            row["duration_sec"] = ""
        else:
            end = now_iso()
            row["end_time"] = end
            code = 0 if args.exit_code is None else int(args.exit_code)
            row["exit_code"] = str(code)
            row["status"] = "COMPLETED" if code == 0 else "FAILED"
            row["duration_sec"] = compute_duration_sec(row.get("start_time", ""), end)

        write_rows(csv_path, rows)
        running_count = sum(1 for r in rows if r.get("status", "").strip() == "RUNNING")
        fcntl.flock(lockf, fcntl.LOCK_UN)

    title = f"Experiment {row['status']}"
    job_name = row.get("slurm_job_name", "").strip()
    exp_comment = row.get("experiment_comment", "").strip().lower()
    if job_name.endswith("_debug") or "[debug" in exp_comment:
        run_type = "debug"
    elif "[array-run]" in exp_comment or row.get("slurm_array_job_id", "").strip():
        run_type = "array"
    else:
        run_type = "run"
    body_lines = [
        f"- exp_name: `{row.get('exp_name', '')}`",
        f"- run_type: `{run_type}`",
        f"- slurm_job_name: `{job_name}`",
        f"- run_uid: `{row.get('run_uid', '')}`",
        f"- base_config: `{row.get('base_config', '')}`",
        f"- running_now: `{running_count}`",
    ]
    if row.get("status") != "RUNNING":
        body_lines.append(f"- exit_code: `{row.get('exit_code', '')}`")
        body_lines.append(f"- duration_sec: `{row.get('duration_sec', '')}`")
    post_slack_message(text=format_status_message(title=title, body_lines=body_lines))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
