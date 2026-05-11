import json
import shutil
import subprocess
import time
from pathlib import Path
from typing import Any, List

from autostages.src.stages.abs_stage import AbsStage


class DebugGateStage(AbsStage):
    def __init__(self, exp_name: str | None = None, max_configs: int = 10):
        super().__init__(
            id="debug_gate",
            description=(
                "Submit a single debug job to verify the experiment config before full array submission.\n"
                "Polls for completion and checks the final Slurm state."
            ),
            final_message="Debug gate evaluation complete.",
        )
        self.exp_name = (exp_name or "").strip()
        self.max_configs = max_configs
        self.store_path = Path(".autosearch/store")
        self.debug_job_id: str | None = None
        self.debug_state: str | None = None
        self.effective_config_list: Path | None = None

    def _update_watcher_state_for_submit(self) -> None:
        if self.effective_config_list is None:
            raise RuntimeError("effective_config_list is not prepared.")
        self.store_path.mkdir(parents=True, exist_ok=True)
        watcher_state_path = self.store_path / "watcher_state.json"
        state: dict[str, Any] = {}
        if watcher_state_path.exists():
            try:
                state = json.loads(watcher_state_path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                state = {}
        state["exp_name"] = self.exp_name
        state["effective_config_list"] = str(self.effective_config_list)
        watcher_state_path.write_text(json.dumps(state, indent=2), encoding="utf-8")

    def _resolve_exp_name(self) -> str:
        if self.exp_name:
            return self.exp_name

        candidates = [
            Path(".autosearch/store/watcher_state.json"),
            Path(".autoresearch/store/bootstrap_done.json"),
        ]
        for path in candidates:
            if not path.exists():
                continue
            try:
                payload = json.loads(path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                continue
            value = str(payload.get("exp_name", "")).strip()
            if value:
                self.exp_name = value
                return self.exp_name

        text_candidate = Path(".autoresearch/store/next_exp_name.txt")
        if text_candidate.exists():
            value = text_candidate.read_text(encoding="utf-8").strip()
            if value:
                self.exp_name = value
                return self.exp_name

        raise RuntimeError(
            "DebugGateStage could not resolve exp_name from "
            ".autosearch/store/watcher_state.json, "
            ".autoresearch/store/bootstrap_done.json, or "
            ".autoresearch/store/next_exp_name.txt"
        )

    def run_body(self, provider, messages: List[dict]) -> List[dict]:
        self._resolve_exp_name()

        # Step 1: Prepare config list
        base_config_list_path = self.store_path / "effective_config_list.txt"
        raw_lines = base_config_list_path.read_text(encoding="utf-8").splitlines()
        configs = [l for l in raw_lines if l.strip() and not l.strip().startswith("#")]

        if len(configs) > self.max_configs:
            configs = configs[: self.max_configs]
            limited_dir = self.store_path / "effective_config_list"
            limited_dir.mkdir(parents=True, exist_ok=True)
            limited_path = limited_dir / f"{self.exp_name}_limited.txt"
            limited_path.write_text("\n".join(configs) + "\n", encoding="utf-8")
            self.effective_config_list = limited_path
            print(f"Config list truncated to {self.max_configs} entries → {limited_path}")
        else:
            self.effective_config_list = base_config_list_path
        self._update_watcher_state_for_submit()

        Path(f"logs/{self.exp_name}").mkdir(parents=True, exist_ok=True)
        Path(f"conf/{self.exp_name}/generated").mkdir(parents=True, exist_ok=True)

        # Step 2: Submit debug job (no explicit resource flags)
        sbatch_cmd = [
            "sbatch",
            "scripts/run-array.sh",
            "--exp_name", self.exp_name,
            "--config_list", self.effective_config_list,
            "--task_id", "0",
            "--quick_train", "true",
            "--quick_fast_dev_run", "10",
            "--quick_max_steps", "100",
            "--quick_max_epochs", "2",
            "--experiment_comment", "[debug-gate]",
        ]

        result = subprocess.run(sbatch_cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"sbatch failed:\n{result.stderr}")
            return False

        output = result.stdout.strip()
        parts = output.split()
        if not parts or not parts[-1].isdigit():
            print(f"Failed to parse job ID from sbatch output: {output!r}")
            return False

        self.debug_job_id = parts[-1]
        print(f"Debug job submitted: {self.debug_job_id}")

        # Step 3: Poll until job disappears from squeue
        print("Polling for debug job completion...")
        while True:
            poll = subprocess.run(
                ["squeue", "-h", "-j", self.debug_job_id],
                capture_output=True, text=True,
            )
            if not poll.stdout.strip():
                break
            time.sleep(5)

        # Step 4: Check final state via sacct
        sacct = subprocess.run(
            ["sacct", "-n", "-P", "-j", self.debug_job_id, "--format=State"],
            capture_output=True, text=True,
        )
        states = [s.strip() for s in sacct.stdout.strip().splitlines() if s.strip()]
        self.debug_state = states[0] if states else "UNKNOWN"

        if self.debug_state == "COMPLETED":
            print(f"Debug job {self.debug_job_id} completed successfully.")
            messages.append({
                "role": "user",
                "content": (
                    f"Debug gate passed for experiment `{self.exp_name}`.\n"
                    f"Effective config list: `{self.effective_config_list}`.\n"
                    "Proceeding to full array job submission."
                ),
            })
            return messages

        # Failure path
        log_src = Path(f"logs/{self.exp_name}/debug_{self.debug_job_id}.log")
        failure_dir = Path(".autoresearch/failure_logs")
        failure_dir.mkdir(parents=True, exist_ok=True)
        log_dst = failure_dir / f"debug_{self.debug_job_id}.log"
        if log_src.exists():
            shutil.copy2(log_src, log_dst)

        self.store_path.mkdir(parents=True, exist_ok=True)
        status = {
            "exp_name": self.exp_name,
            "debug_job_id": self.debug_job_id,
            "status": "DEBUG_FAILED",
            "debug_state": self.debug_state,
        }
        (self.store_path / "latest_status.json").write_text(
            json.dumps(status, indent=2), encoding="utf-8"
        )

        subprocess.run([
            "git", "add",
            str(self.store_path / "latest_status.json"),
            str(failure_dir),
            "experiments.csv",
        ])
        subprocess.run([
            "git", "commit", "-m",
            f"autoresearch: debug failed {self.exp_name} ({self.debug_job_id})",
        ])

        print(f"Debug job {self.debug_job_id} failed with state: {self.debug_state}")
        messages.append({
            "role": "user",
            "content": (
                f"Debug gate FAILED for experiment `{self.exp_name}`.\n"
                f"Job ID: {self.debug_job_id}, state: {self.debug_state}.\n"
                f"Failure log saved to: {log_dst}.\n"
                "Proceeding to bugfix stage."
            ),
        })
        return messages

    def evaluate_end_condition(self, runtime_dirs: dict[str, Any], messages: List[dict]) -> bool:
        # Not yet run
        if self.debug_job_id is None or self.debug_state is None:
            return False

        if self.debug_state == "COMPLETED":
            return True

        # Failure path is complete when the failure log exists on disk
        failure_log = Path(f".autoresearch/failure_logs/debug_{self.debug_job_id}.log")
        if failure_log.exists():
            return True

        # Fallback: latest_status.json records DEBUG_FAILED for this job
        status_path = self.store_path / "latest_status.json"
        if status_path.exists():
            try:
                status = json.loads(status_path.read_text(encoding="utf-8"))
                if (
                    status.get("debug_job_id") == self.debug_job_id
                    and status.get("status") == "DEBUG_FAILED"
                ):
                    return True
            except (json.JSONDecodeError, KeyError):
                pass

        return False
