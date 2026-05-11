import json
import re
from pathlib import Path
from typing import Any, List

from autostages.src.stages.abs_stage import AbsStage


class LoopEndStage(AbsStage):
    def __init__(self, store_path: Path = Path(".autosearch/store")):
        super().__init__(
            id="loop_end",
            description=(
                "Finalize one research loop after metrics collection.\n"
                "Decides whether search is exhausted and updates watcher_state."
            ),
            final_message="✅ Loop end decision complete.",
        )
        self.store_path = Path(store_path)

    def _is_search_space_exhausted(self) -> bool:
        search_plan = self.store_path / "search_plan.md"
        if not search_plan.exists():
            return False

        lines = search_plan.read_text(encoding="utf-8").splitlines()
        data_rows: list[list[str]] = []
        header_seen = False
        for line in lines:
            stripped = line.strip()
            if not stripped.startswith("|"):
                continue
            cols = [c.strip() for c in stripped.split("|")[1:-1]]
            if all(re.match(r"^-+$", c) or not c for c in cols):
                header_seen = True
                continue
            if not header_seen:
                continue
            data_rows.append(cols)

        if not data_rows:
            return False

        for cols in data_rows:
            row_text = " ".join(cols).lower()
            if "pending" in row_text or ("done" not in row_text and "skipped" not in row_text):
                return False
        return True

    def _read_exp_name(self) -> str:
        next_exp_name = self.store_path / "next_exp_name.txt"
        if next_exp_name.exists():
            value = next_exp_name.read_text(encoding="utf-8").strip()
            if value:
                return value

        watcher = self.store_path / "watcher_state.json"
        if watcher.exists():
            try:
                state = json.loads(watcher.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                return ""
            return str(state.get("exp_name", "")).strip()
        return ""

    def _write_watcher_state(self, state: dict[str, Any]) -> None:
        path = self.store_path / "watcher_state.json"
        path.write_text(json.dumps(state, indent=2), encoding="utf-8")

    def run_body(self, provider, messages: List[dict]) -> List[dict]:
        if self._is_search_space_exhausted():
            self._write_watcher_state({"phase": "IDLE"})
            print("✅ Search space exhausted → IDLE.")
            return messages

        exp_name = self._read_exp_name()
        if not exp_name:
            raise RuntimeError(
                "LoopEndStage could not determine exp_name from "
                "store/next_exp_name.txt or store/watcher_state.json"
            )

        self._write_watcher_state(
            {
                "phase": "EXPERIMENT_RUNNING",
                "array_job_id": "",
                "exp_name": exp_name,
                "last_main_sha": "",
            }
        )
        print(f"✅ Next wave: {exp_name} → EXPERIMENT_RUNNING.")
        return messages

    def evaluate_end_condition(self, runtime_dirs: dict[str, Any], messages: List[dict]) -> bool:
        state_path = self.store_path / "watcher_state.json"
        if not state_path.exists():
            return False
        try:
            state = json.loads(state_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return False

        phase = state.get("phase", "")
        if phase == "IDLE":
            return True
        if phase != "EXPERIMENT_RUNNING":
            return False

        exp_name = str(state.get("exp_name", "")).strip()
        return bool(exp_name)
