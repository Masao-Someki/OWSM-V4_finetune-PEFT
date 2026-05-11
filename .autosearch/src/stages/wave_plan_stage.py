import csv
import hashlib
import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, List

from autostages.src.stages.abs_stage import AbsStage
from autostages.src.utils import run_with_spinner


class WavePlanStage(AbsStage):
    _ALLOWED_PATH_PREFIXES = (
        "conf/exp_",
        "conf/",
        ".autoresearch/",
        ".autoresearch/notes/",
        "src/",
        "scripts/",
        "run.py",
        "tests/",
    )
    _PROVIDER_KEY_MAP = {
        "openai": "openai_api",
        "claude": "claude_api",
        "codex": "codex_cli",
        "claude_code": "claude_cli",
        "gemini": "google_api",
    }

    def __init__(self):
        super().__init__(
            id="wave_plan",
            description=(
                "Plan the next wave of experiments.\n"
                "Reads latest metrics and goal, then proposes new experiment configs via LLM."
            ),
            final_message="✅ Wave plan complete. Next experiment is prepared.",
        )
        self.store_path = Path(".autosearch/store")

    def _resolve_provider_name(self) -> str:
        cache_file = self.cache_path / "model.txt"
        if cache_file.exists():
            return cache_file.read_text(encoding="utf-8").strip()

        choices = list(self._PROVIDER_KEY_MAP.keys())
        print("Choose an LLM provider for wave planning:")
        for i, name in enumerate(choices, 1):
            print(f"  [{i}] {name}")

        while True:
            raw = input("Enter number (1-5): ").strip()
            if raw.isdigit() and 1 <= int(raw) <= len(choices):
                selected = choices[int(raw) - 1]
                cache_file.write_text(selected, encoding="utf-8")
                return selected
            print("  Invalid choice, try again.")

    def _resolve_model(self, provider_name: str) -> str:
        config_path = Path(".autosearch/config.json")
        if not config_path.exists():
            return ""
        try:
            config = json.loads(config_path.read_text(encoding="utf-8"))
            key = self._PROVIDER_KEY_MAP.get(provider_name, provider_name)
            return config.get("models", {}).get(key, "")
        except (json.JSONDecodeError, OSError):
            return ""

    def _determine_mode(self) -> tuple[str, bool]:
        bootstrap_marker = self.store_path / "bootstrap_done.json"
        mode = "bootstrap" if not bootstrap_marker.exists() else "iterative"

        prompt_path = Path("prompt.txt")
        prompt_sha = hashlib.sha256(prompt_path.read_bytes()).hexdigest() if prompt_path.exists() else ""

        prompt_state_path = self.store_path / "prompt_state.json"
        prompt_changed = False
        if prompt_state_path.exists():
            try:
                state = json.loads(prompt_state_path.read_text(encoding="utf-8"))
                prompt_changed = state.get("prompt_sha256", "") != prompt_sha
            except (json.JSONDecodeError, OSError):
                prompt_changed = True
        else:
            prompt_changed = bool(prompt_sha)

        update_ctx = self.store_path / "prompt_update_context.md"
        if prompt_changed:
            update_ctx.write_text(
                f"# Prompt Update Context\n\nPrompt changed (new sha256: {prompt_sha}).\n",
                encoding="utf-8",
            )
        else:
            update_ctx.write_text(
                f"# Prompt Update Context\n\nPrompt unchanged (sha256: {prompt_sha}).\n",
                encoding="utf-8",
            )

        prompt_state_path.write_text(
            json.dumps({"prompt_sha256": prompt_sha}, indent=2),
            encoding="utf-8",
        )
        return mode, prompt_changed

    def _build_user_prompt(self) -> str:
        parts: list[str] = []

        def _section(path: Path, label: str) -> None:
            if path.exists():
                parts.append(f"## {label}\n\n{path.read_text(encoding='utf-8')}\n")

        _section(self.store_path / "next_goal.md", "Next Goal")
        _section(self.store_path / "findings.md", "Findings")
        _section(Path("experiments.csv"), "Experiments CSV")
        _section(self.store_path / "search_plan.md", "Search Plan")
        _section(self.store_path / "prompt_update_context.md", "Prompt Update Context")

        parts.append(
            "Based on the above context, propose the next wave of experiments.\n"
            "If anything is unclear, inspect files in this repository before answering.\n"
            "In most cases, the necessary information is in `.autosearch/`, `conf/`, and `src/`.\n"
            "Think through the plan once and provide the complete output in a single response.\n"
            "Output all new or updated files using the format:\n"
            '<file path="path/to/file">content</file>\n\n'
            "Required outputs:\n"
            "- store/next_exp_name.txt  (the experiment name only, no extra whitespace)\n"
            "- store/effective_config_list.txt  (one config path per line)\n"
            "- conf/exp_<name>/config.yaml  (experiment config)\n"
        )
        return "\n".join(parts)

    def _parse_file_blocks(self, response: str) -> list[tuple[str, str]]:
        return re.findall(r'<file\s+path="([^"]+)">(.*?)</file>', response, re.DOTALL)

    def _is_allowed_path(self, path_str: str) -> bool:
        if path_str.startswith("store/") or path_str.startswith(".autosearch/store/"):
            return True
        return any(path_str.startswith(prefix) for prefix in self._ALLOWED_PATH_PREFIXES)

    def _write_files(self, file_blocks: list[tuple[str, str]]) -> list[Path]:
        repo_root = Path(".").resolve()
        written: list[Path] = []
        for path_str, content in file_blocks:
            if path_str.startswith("store/"):
                dest = self.store_path / path_str[len("store/"):]
            else:
                dest = Path(path_str)

            try:
                (repo_root / dest).resolve().relative_to(repo_root)
            except ValueError:
                print(f"⚠️  Skipping '{path_str}': path escapes repository root.")
                continue

            if not self._is_allowed_path(path_str):
                print(f"⚠️  Skipping '{path_str}': not in allowed path list.")
                continue

            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text(content.strip(), encoding="utf-8")
            written.append(dest)
            print(f"  Wrote: {dest}")
        return written

    def _reconcile_search_plan(self) -> None:
        experiments_csv = Path("experiments.csv")
        if not experiments_csv.exists():
            return

        status_map: dict[str, str] = {}
        with open(experiments_csv, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                status = row.get("status", "").strip()
                conf = (
                    row.get("config_path")
                    or row.get("conf")
                    or row.get("exp_name")
                    or ""
                ).strip()
                if conf and status:
                    status_map[conf] = status

        for plan_file in (
            self.store_path / "search_plan.md",
            self.store_path / "search_plan_report.md",
        ):
            if not plan_file.exists():
                continue
            lines = plan_file.read_text(encoding="utf-8").splitlines()
            updated: list[str] = []
            for line in lines:
                if line.strip().startswith("|"):
                    for conf, status in status_map.items():
                        if conf in line and "skipped" not in line:
                            line = re.sub(
                                r"\|\s*pending\s*\|",
                                f"| {status} |",
                                line,
                                flags=re.IGNORECASE,
                            )
                updated.append(line)
            plan_file.write_text("\n".join(updated), encoding="utf-8")

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
            if "pending" in row_text or (
                "done" not in row_text and "skipped" not in row_text
            ):
                return False
        return True

    def run_body(self, provider, messages: List[dict]) -> List[dict]:
        # Step 1: Resolve provider
        provider_name = self._resolve_provider_name()
        model = self._resolve_model(provider_name)
        if model:
            print(f"  Using provider={provider_name}, model={model}")
            if hasattr(provider, "model"):
                provider.model = model

        # Step 2: Determine mode
        mode, prompt_changed = self._determine_mode()
        print(f"  Mode: {mode}, prompt_changed: {prompt_changed}")

        # Step 3: Wave planning
        messages.append({"role": "user", "content": self._build_user_prompt()})
        response = run_with_spinner(
            provider.chat,
            (messages,),
            "Planning next experiment wave...",
        )
        messages.append({"role": provider.assistant_name, "content": response})
        (self.cache_path / "last_response.txt").write_text(response, encoding="utf-8")

        # Step 4: Write files
        file_blocks = self._parse_file_blocks(response)
        if not file_blocks:
            raise RuntimeError(
                "WavePlanStage failed: no <file path=\"...\"> blocks found in model response."
            )
        written_files = self._write_files(file_blocks)
        if not written_files:
            raise RuntimeError(
                "WavePlanStage failed: parsed file blocks but no files were written."
            )

        next_exp_name_path = self.store_path / "next_exp_name.txt"
        effective_config_list_path = self.store_path / "effective_config_list.txt"

        if not next_exp_name_path.exists():
            print("❌ store/next_exp_name.txt was not generated. Aborting.")
            return messages

        exp_name = next_exp_name_path.read_text(encoding="utf-8").strip()

        if not effective_config_list_path.exists():
            print("❌ store/effective_config_list.txt does not exist. Aborting.")
            return messages

        # Step 5: Reconcile search plan
        self._reconcile_search_plan()

        # Step 6: Write bootstrap marker
        bootstrap_marker = self.store_path / "bootstrap_done.json"
        bootstrap_marker.write_text(
            json.dumps(
                {
                    "done": True,
                    "mode": mode,
                    "updated_at": datetime.now(timezone.utc).isoformat(),
                    "exp_name": exp_name,
                },
                indent=2,
            ),
            encoding="utf-8",
        )
        written_files.extend([
            bootstrap_marker,
            self.store_path / "prompt_state.json",
            self.store_path / "prompt_update_context.md",
        ])

        # Step 7: Stage + commit only (no push)
        subprocess.run(["git", "add"] + [str(f) for f in written_files], check=True)
        subprocess.run(
            ["git", "commit", "-m", f"autoresearch: propose {exp_name}"],
            check=True,
        )

        return messages

    def evaluate_end_condition(self, runtime_dirs: dict[str, Any], messages: List[dict]) -> bool:
        # next_exp_name.txt must exist and be non-empty
        next_exp_name_path = self.store_path / "next_exp_name.txt"
        if not next_exp_name_path.exists():
            return False
        exp_name = next_exp_name_path.read_text(encoding="utf-8").strip()
        if not exp_name:
            return False

        # effective config list must exist
        if not (self.store_path / "effective_config_list.txt").exists():
            return False

        # bootstrap_done.json must exist with matching exp_name and done=true
        bootstrap_marker = self.store_path / "bootstrap_done.json"
        if not bootstrap_marker.exists():
            return False
        try:
            marker = json.loads(bootstrap_marker.read_text(encoding="utf-8"))
            if not marker.get("done"):
                return False
            if marker.get("exp_name") != exp_name:
                return False
        except (json.JSONDecodeError, OSError):
            return False

        # last git commit must reference the exp_name
        result = subprocess.run(
            ["git", "log", "-1", "--pretty=%s"],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            return False
        if exp_name not in result.stdout.strip():
            return False

        return True
