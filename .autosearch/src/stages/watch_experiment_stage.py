import json
import subprocess
import time
from pathlib import Path
from typing import Any, List

from autostages.src.stages.abs_stage import AbsStage

TERMINAL_STATES = {"COMPLETED", "FAILED", "CANCELLED", "TIMEOUT", "NODE_FAIL"}
RUNNING_STATES = {"RUNNING", "PENDING"}
POLL_INTERVAL = 300  # 5 minutes


class WatchExperimentStage(AbsStage):
    def __init__(self, store_path: Path = Path(".autosearch/store")):
        super().__init__(
            id="watch_experiment",
            description=(
                "Monitor the submitted Slurm array job and wait for all tasks to reach\n"
                "a terminal state (COMPLETED / FAILED / CANCELLED / TIMEOUT / NODE_FAIL)."
            ),
            final_message="✅ All array job tasks have reached a terminal state.",
        )
        self.store_path = Path(store_path)

    def _load_watcher_state(self) -> dict:
        with open(self.store_path / "watcher_state.json", "r", encoding="utf-8") as f:
            return json.load(f)

    def _save_watcher_state(self, state: dict) -> None:
        with open(self.store_path / "watcher_state.json", "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2)

    def _load_max_stage_steps(self) -> int:
        config_path = self.store_path.parent / "config.json"
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
            return config.get("orchestration", {}).get("max_stage_steps", 72)
        except (OSError, json.JSONDecodeError):
            return 72

    def _get_job_states(self, array_job_id: str) -> dict[str, str]:
        result = subprocess.run(
            ["sacct", "-n", "-P", "-j", array_job_id, "--format=JobID,State"],
            capture_output=True,
            text=True,
        )
        task_states: dict[str, str] = {}
        for line in result.stdout.strip().splitlines():
            parts = line.strip().split("|")
            if len(parts) >= 2:
                job_id = parts[0].strip()
                raw_state = parts[1].strip()
                # Normalize "CANCELLED by 1234" → "CANCELLED"
                task_states[job_id] = raw_state.split()[0] if raw_state else raw_state
        return task_states

    def run_body(self, provider, messages: List[dict]) -> List[dict]:
        state = self._load_watcher_state()
        array_job_id = state.get("array_job_id", "")
        exp_name = state.get("exp_name", "unknown")

        if not array_job_id:
            print("❌ array_job_id is empty in watcher_state.json. Cannot watch experiment.")
            return messages

        max_stage_steps = self._load_max_stage_steps()
        print(f"Watching experiment: {exp_name} (job: {array_job_id})")
        print(f"Max poll attempts: {max_stage_steps} (~{max_stage_steps * POLL_INTERVAL // 3600}h)")

        final_states: dict[str, str] = {}
        poll_count = 0

        while poll_count < max_stage_steps:
            task_states = self._get_job_states(array_job_id)

            if not task_states:
                print(f"[Poll {poll_count + 1}/{max_stage_steps}] No task states returned from sacct, retrying...")
            else:
                n_running = sum(1 for s in task_states.values() if s in RUNNING_STATES)
                n_terminal = sum(1 for s in task_states.values() if s in TERMINAL_STATES)
                n_other = len(task_states) - n_running - n_terminal
                print(
                    f"[Poll {poll_count + 1}/{max_stage_steps}] "
                    f"Running/Pending: {n_running}, Terminal: {n_terminal}, Other: {n_other}"
                )

                if all(s in TERMINAL_STATES for s in task_states.values()):
                    final_states = task_states
                    break

            poll_count += 1
            if poll_count < max_stage_steps:
                print(f"  Next poll in {POLL_INTERVAL // 60} minutes...")
                time.sleep(POLL_INTERVAL)
        else:
            print(
                f"⚠️  Warning: Maximum poll count ({max_stage_steps}) reached without all tasks completing. "
                "Exiting forcefully."
            )
            final_states = self._get_job_states(array_job_id)

        tally: dict[str, int] = {}
        for s in final_states.values():
            tally[s] = tally.get(s, 0) + 1

        print("\n=== Job Completion Summary ===")
        for state_label, count in sorted(tally.items()):
            print(f"  {state_label}: {count}")
        print()

        state["phase"] = "COLLECTING_METRICS"
        self._save_watcher_state(state)
        print("Updated watcher_state.json phase → COLLECTING_METRICS.")

        messages.append({
            "role": "user",
            "content": (
                f"Experiment `{exp_name}` (job: {array_job_id}) has finished.\n"
                f"Final task state summary:\n{json.dumps(tally, indent=2)}"
            ),
        })

        return messages

    def evaluate_end_condition(self, runtime_dirs: dict[str, Any], messages: List[dict]) -> bool:
        state_file = self.store_path / "watcher_state.json"
        if not state_file.exists():
            return False
        try:
            with open(state_file, "r", encoding="utf-8") as f:
                state = json.load(f)
        except (OSError, json.JSONDecodeError):
            return False
        return state.get("phase") == "COLLECTING_METRICS"
