#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import subprocess
import sys
import tempfile
from pathlib import Path


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Run a short training sanity check with temporary trainer overrides."
    )
    p.add_argument(
        "--base-config",
        default="conf/owsm_peft_lora_basic.yaml",
        help="Base training config path.",
    )
    p.add_argument(
        "--fast-dev-run",
        type=int,
        default=10,
        help="trainer.fast_dev_run override.",
    )
    p.add_argument(
        "--max-steps",
        type=int,
        default=100,
        help="trainer.max_steps override (iteration count).",
    )
    p.add_argument(
        "--max-epochs",
        type=int,
        default=2,
        help="trainer.max_epochs override.",
    )
    p.add_argument(
        "--stages",
        default="train",
        help="Stages to run (space-separated string passed to run.py).",
    )
    return p


def build_override_config_text(base_cfg_name: str, args: argparse.Namespace) -> str:
    return f"""defaults:
  - {base_cfg_name}

exp_tag: test_run_fd{args.fast_dev_run}_s{args.max_steps}_e{args.max_epochs}
num_device: 1
num_nodes: 1

trainer:
  fast_dev_run: {args.fast_dev_run}
  max_steps: {args.max_steps}
  max_epochs: {args.max_epochs}
"""


def main() -> int:
    args = build_parser().parse_args()
    repo_root = Path(__file__).resolve().parents[1]
    base_cfg = (repo_root / args.base_config).resolve()
    if not base_cfg.exists():
        print(f"[ERROR] base config not found: {base_cfg}", file=sys.stderr)
        return 2

    conf_dir = repo_root / "conf"
    base_cfg_name = base_cfg.name
    override_text = build_override_config_text(base_cfg_name=base_cfg_name, args=args)

    tmp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".yaml",
            prefix="tmp_test_run_",
            dir=conf_dir,
            delete=False,
        ) as tf:
            tf.write(override_text)
            tmp_path = Path(tf.name)

        cmd = [
            "bash",
            "-lc",
            f". ./scripts/path.sh && python run.py --stages {args.stages} --train_config {tmp_path}",
        ]
        print(f"[INFO] running: {' '.join(cmd)}")
        proc = subprocess.run(cmd, cwd=repo_root, env=os.environ.copy())
        if proc.returncode != 0:
            print(
                f"[FAIL] test run failed with exit code {proc.returncode}",
                file=sys.stderr,
            )
            return proc.returncode

        print("[PASS] test run finished without errors")
        return 0
    finally:
        if tmp_path is not None and tmp_path.exists():
            tmp_path.unlink()


if __name__ == "__main__":
    raise SystemExit(main())
