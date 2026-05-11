import json
import re
import shutil
import subprocess
from pathlib import Path
from typing import Any, List

from autostages.src.stages.abs_stage import AbsStage


class SubmitArrayJobStage(AbsStage):
    def __init__(self, store_path: Path = Path(".autosearch/store")):
        super().__init__(
            id="submit_array_job",
            description=(
                "Submit the full experiment array job via sbatch.\n"
                "Reads the effective config list written by DebugGateStage,\n"
                "submits the Slurm array job, and records the job ID in watcher_state.json."
            ),
            final_message="✅ Array job submitted and watcher state recorded.",
        )
        self.store_path = Path(store_path)

    def _load_watcher_state(self) -> dict:
        state_path = self.store_path / "watcher_state.json"
        with state_path.open() as f:
            return json.load(f)

    def _save_watcher_state(self, state: dict) -> None:
        state_path = self.store_path / "watcher_state.json"
        state_path.write_text(json.dumps(state, indent=2))

    def run_body(self, provider, messages: List[dict]) -> List[dict]:
        # Load orchestration config
        config_path = Path(".autosearch/config.json")
        with config_path.open() as f:
            config = json.load(f)
        slurm = config.get("orchestration", {}).get("slurm", {})

        # Read exp_name and effective_config_list from state written by DebugGateStage
        state = self._load_watcher_state()
        exp_name = state["exp_name"]
        effective_config_list = Path(state["effective_config_list"])

        if not effective_config_list.exists():
            print(f"❌ effective_config_list not found: {effective_config_list}")
            return False

        # Count non-empty lines to determine array range
        lines = [l.strip() for l in effective_config_list.read_text().splitlines() if l.strip()]
        n = len(lines)
        if n == 0:
            print("❌ effective_config_list is empty — nothing to submit.")
            return False

        array_range = f"0-{n - 1}"
        concurrency = slurm.get("concurrency")
        if concurrency:
            array_range += f"%{concurrency}"

        # Ensure log directory exists
        log_dir = Path(f"logs/{exp_name}")
        log_dir.mkdir(parents=True, exist_ok=True)

        # Build sbatch command
        cmd = [
            "sbatch",
            f"--job-name={exp_name}",
            f"--array={array_range}",
        ]

        cmd += [
            "scripts/run-array.sh",
            "--exp_name", exp_name,
            "--config_list", str(effective_config_list),
            "--experiment_comment", "[array-run]",
        ]

        print(f"\nSubmitting: {' '.join(cmd)}\n")
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            print(f"❌ sbatch failed (exit {result.returncode}):\n{result.stderr}")
            return False

        match = re.search(r"Submitted batch job (\d+)", result.stdout)
        if not match:
            print(f"❌ Could not parse array_job_id from sbatch output:\n{result.stdout}")
            return False

        array_job_id = match.group(1)
        print(f"✅ Submitted array job: {array_job_id}  ({n} tasks, range {array_range})")

        # Archive config list for traceability
        tracking_dir = Path(f".autoresearch/array_conf/{exp_name}")
        tracking_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy(effective_config_list, tracking_dir / f"array_{array_job_id}.txt")

        # Record state
        self._save_watcher_state({
            "phase": "EXPERIMENT_RUNNING",
            "array_job_id": array_job_id,
            "exp_name": exp_name,
            "last_main_sha": "",
        })

        messages.append({
            "role": "user",
            "content": (
                f"Array job submitted successfully.\n"
                f"- exp_name: {exp_name}\n"
                f"- array_job_id: {array_job_id}\n"
                f"- array_range: {array_range}\n"
                f"- tasks: {n}\n"
                f"- config_list: {effective_config_list}\n"
                f"- watcher_state.json updated → phase=EXPERIMENT_RUNNING"
            ),
        })
        return messages

    def evaluate_end_condition(self, runtime_dirs: dict[str, Any], messages: List[dict]) -> bool:
        state_path = self.store_path / "watcher_state.json"
        if not state_path.exists():
            return False
        try:
            with state_path.open() as f:
                state = json.load(f)
        except (json.JSONDecodeError, OSError):
            return False

        return (
            state.get("phase") == "EXPERIMENT_RUNNING"
            and bool(str(state.get("array_job_id", "")).strip())
        )
