import json
import subprocess
from pathlib import Path
from typing import Any, List

from autostages.src.stages.abs_stage import AbsStage


class CollectMetricsStage(AbsStage):
    def __init__(self, store_path: Path = Path(".autosearch/store")):
        super().__init__(
            id="collect_metrics",
            description=(
                "Collect metrics from completed array job tasks,\n"
                "update state files, and commit results."
            ),
            final_message="✅ Metrics collected and committed.",
        )
        self.store_path = Path(store_path)
        self.store_path.mkdir(parents=True, exist_ok=True)

    def _read_watcher_state(self) -> dict:
        p = self.store_path / "watcher_state.json"
        if not p.exists():
            return {}
        return json.loads(p.read_text(encoding="utf-8"))

    def _write_watcher_state(self, data: dict) -> None:
        p = self.store_path / "watcher_state.json"
        p.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def _git(self, *args: str) -> subprocess.CompletedProcess:
        return subprocess.run(["git", *args], check=True, capture_output=True, text=True)

    def _build_next_goal(self, metrics: dict) -> str:
        best_wer = metrics.get("best_wer")
        best_run_uid = metrics.get("best_run_uid", "")
        failed_count = metrics.get("failed_count", 0)
        wave_summary = metrics.get("wave_summary", [])
        exp_name = metrics.get("exp_name", "")
        completed_count = sum(1 for r in wave_summary if r.get("wer") is not None)
        total_count = len(wave_summary)

        lines = [
            f"# Next Wave Goal — derived from {exp_name}\n",
            "## Summary",
            f"- Total runs: {total_count}",
            f"- Completed with metrics: {completed_count}",
            f"- Failed: {failed_count}",
        ]

        if best_wer is not None:
            lines.append(f"- Best WER: {best_wer:.4f} (run: {best_run_uid})")
        else:
            lines.append("- Best WER: N/A (no successful runs)")

        lines.append("\n## Direction")
        if failed_count == total_count:
            lines.append(
                "All runs failed. Investigate failure logs before proceeding. "
                "Consider adjusting memory limits, fixing config errors, or simplifying the search space."
            )
        elif best_wer is not None and best_wer < 0.3:
            lines.append(
                f"Good baseline achieved (WER={best_wer:.4f}). "
                "Next wave should explore hyperparameter tuning (learning rate, rank, alpha) "
                "around the best-performing configuration."
            )
        elif best_wer is not None:
            lines.append(
                f"Current best WER is {best_wer:.4f}. "
                "Next wave should explore alternative PEFT methods or adjust warmup/epoch settings "
                "to improve convergence."
            )
        else:
            lines.append(
                "No metrics collected yet. Verify that inference completed and metrics.json files exist."
            )

        if failed_count > 0:
            lines.append(
                f"\n{failed_count} run(s) failed. Review `.autoresearch/results/{exp_name}/errors/` "
                "and address root causes before the next wave."
            )

        return "\n".join(lines) + "\n"

    def run_body(self, provider, messages: List[dict]) -> List[dict]:
        # Step 1: read watcher state
        state = self._read_watcher_state()
        exp_name = state.get("exp_name", "")
        array_job_id = state.get("array_job_id", "")

        if not exp_name or not array_job_id:
            print("[CollectMetricsStage] Missing exp_name or array_job_id in watcher_state.json.")
            return messages

        print(f"[CollectMetricsStage] Collecting metrics for exp={exp_name}, job={array_job_id}")

        # Step 2: run collect_metrics.py
        result = subprocess.run(
            [
                "python", ".autoresearch/collect_metrics.py",
                "--exp-name", exp_name,
                "--array-job-id", str(array_job_id),
                "--output", str(self.store_path / "latest_metrics.json"),
                "--lock-path", str(self.store_path / "experiments.csv.lock"),
            ],
            capture_output=True, text=True,
        )
        print(result.stdout)
        if result.returncode != 0:
            print(f"[CollectMetricsStage] collect_metrics.py failed:\n{result.stderr}")
            return messages

        # Step 3: load latest_metrics.json for downstream state files
        latest_metrics_path = self.store_path / "latest_metrics.json"
        metrics: dict = {}
        if latest_metrics_path.exists():
            try:
                metrics = json.loads(latest_metrics_path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                pass

        # Write latest_status.json
        status_data = {
            "exp_name": exp_name,
            "array_job_id": str(array_job_id),
            "status": "COMPLETED",
        }
        (self.store_path / "latest_status.json").write_text(
            json.dumps(status_data, indent=2), encoding="utf-8"
        )

        # Write next_goal.md
        next_goal = self._build_next_goal(metrics)
        (self.store_path / "next_goal.md").write_text(next_goal, encoding="utf-8")

        # Step 4: git add and commit (no push)
        try:
            self._git(
                "add",
                "experiments.csv",
                str(self.store_path / "latest_metrics.json"),
                str(self.store_path / "latest_status.json"),
                str(self.store_path / "next_goal.md"),
                ".autoresearch/results/",
            )
            self._git(
                "commit",
                "-m", f"autoresearch: collect metrics {exp_name} ({array_job_id})",
            )
        except subprocess.CalledProcessError as e:
            print(f"[CollectMetricsStage] Git error: {e.stderr}")
            return messages

        # Step 5: transition to WAVE_PLANNING
        state["phase"] = "WAVE_PLANNING"
        self._write_watcher_state(state)

        return messages

    def evaluate_end_condition(self, runtime_dirs: dict[str, Any], messages: List[dict]) -> bool:
        # Require watcher_state.json to have transitioned to WAVE_PLANNING
        state_path = self.store_path / "watcher_state.json"
        if not state_path.exists():
            return False
        try:
            state = json.loads(state_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return False

        if state.get("phase") != "WAVE_PLANNING":
            return False

        exp_name = state.get("exp_name", "")
        array_job_id = str(state.get("array_job_id", ""))

        # latest_metrics.json must exist and match the current experiment
        metrics_path = self.store_path / "latest_metrics.json"
        if not metrics_path.exists():
            return False
        try:
            metrics = json.loads(metrics_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return False
        if metrics.get("exp_name") != exp_name:
            return False
        if str(metrics.get("array_job_id", "")) != array_job_id:
            return False

        # latest_status.json must show COMPLETED for this experiment
        status_path = self.store_path / "latest_status.json"
        if not status_path.exists():
            return False
        try:
            status = json.loads(status_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return False
        if status.get("status") != "COMPLETED":
            return False
        if status.get("exp_name") != exp_name:
            return False

        # next_goal.md must exist and be non-empty
        next_goal_path = self.store_path / "next_goal.md"
        if not next_goal_path.exists() or next_goal_path.stat().st_size == 0:
            return False

        # Confirm the collect-metrics commit exists in local git log
        expected_msg = f"autoresearch: collect metrics {exp_name} ({array_job_id})"
        try:
            log = subprocess.run(
                ["git", "log", "--oneline", "-30"],
                capture_output=True, text=True, check=True,
            )
            if expected_msg not in log.stdout:
                return False
        except subprocess.CalledProcessError:
            return False

        return True
