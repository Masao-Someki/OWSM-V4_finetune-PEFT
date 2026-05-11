import json
import os
import re
import subprocess
import urllib.request
from pathlib import Path
from typing import Any, List

from autostages.src.stages.abs_stage import AbsStage


def _run_cmd(cmd: list[str], check: bool = True) -> str:
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if check and proc.returncode != 0:
        raise RuntimeError(f"Command failed: {' '.join(cmd)}\n{proc.stderr.strip()}")
    return proc.stdout.strip()


def _tail_text(text: str, max_chars: int) -> str:
    return text[-max_chars:] if len(text) > max_chars else text


def _parse_file_blocks(text: str) -> list[tuple[str, str]]:
    pattern = re.compile(r'<file\s+path="([^"]+)">\s*(.*?)\s*</file>', re.DOTALL)
    return [(m.group(1).strip(), m.group(2)) for m in pattern.finditer(text)]


class BugfixStage(AbsStage):
    def __init__(self):
        super().__init__(
            id="bugfix",
            description="Propose and apply a minimal bugfix from the latest debug failure log.",
            final_message="✅ Bugfix stage complete.",
        )
        self.store_path = Path(".autosearch/store")
        self.store_path.mkdir(parents=True, exist_ok=True)

    def _resolve_failure_dir(self) -> Path:
        candidates = [Path("failure_logs"), Path(".autoresearch/failure_logs")]
        for p in candidates:
            if p.exists() and p.is_dir():
                return p
        return candidates[0]

    def _resolve_provider_name(self) -> str:
        model_txt = self.cache_path / "model.txt"
        if model_txt.exists():
            return model_txt.read_text(encoding="utf-8").strip()

        options = ["openai", "claude", "codex", "claude_code", "gemini"]
        prompt = (
            "Choose bugfix provider:\n"
            "- openai\n- claude\n- codex\n- claude_code\n- gemini\n"
            "Type one option exactly."
        )
        while True:
            choice = self.get_user_input(prompt).strip()
            if choice in options:
                model_txt.write_text(choice, encoding="utf-8")
                return choice
            print(f"❌ Invalid provider: {choice}")

    def _resolve_model_name(self, provider_name: str) -> str:
        config_path = Path(".autosearch/config.json")
        if not config_path.exists():
            raise RuntimeError("Missing .autosearch/config.json")
        config = json.loads(config_path.read_text(encoding="utf-8"))
        model_name = config.get("models", {}).get(provider_name)
        if not model_name:
            raise RuntimeError(f"Missing models.{provider_name} in .autosearch/config.json")
        return str(model_name)

    def _call_llm(self, provider: Any, messages: List[dict], provider_name: str, model_name: str) -> str:
        chat = getattr(provider, "chat")
        for kwargs in (
            {"provider": provider_name, "model": model_name},
            {"model": model_name},
            {"provider_name": provider_name, "model_name": model_name},
            {},
        ):
            try:
                return chat(messages, **kwargs)
            except TypeError:
                continue
        return chat(messages)

    def run_body(self, provider, messages: List[dict]) -> List[dict]:
        status_path = self.store_path / "latest_status.json"
        failure_dir = self._resolve_failure_dir()

        if not status_path.exists():
            print("Skip: latest_status.json not found.")
            return messages

        latest_status = json.loads(status_path.read_text(encoding="utf-8"))
        log_files = sorted(failure_dir.glob("*.log"), key=lambda p: p.stat().st_mtime, reverse=True) if failure_dir.exists() else []
        if latest_status.get("status") != "DEBUG_FAILED" or not log_files:
            print("Skip: start condition not met.")
            return messages

        latest_log_path = log_files[0]
        latest_log = latest_log_path.read_text(encoding="utf-8", errors="replace")
        latest_log_tail = _tail_text(latest_log, 4000)

        provider_name = self._resolve_provider_name()
        model_name = self._resolve_model_name(provider_name)

        bugfix_prompt = (
            "You are fixing a failed debug run.\n"
            "Identify the root cause and provide the minimal safe fix.\n"
            "Do not propose a new wave.\n"
            "Do not modify state files such as store/search_plan.md or store/next_exp_name.txt.\n"
            "Output all file edits as XML blocks only:\n"
            '<file path="relative/path.py">...full file content...</file>\n'
            "You may use web search if needed.\n\n"
            "latest_status.json:\n"
            f"{json.dumps(latest_status, ensure_ascii=False, indent=2)}\n\n"
            f"latest failure log ({latest_log_path}):\n{latest_log_tail}\n"
        )

        llm_messages = messages + [{"role": "user", "content": bugfix_prompt}]
        response = self._call_llm(provider, llm_messages, provider_name, model_name)
        (self.cache_path / "last_response.txt").write_text(response, encoding="utf-8")
        messages.append({"role": "user", "content": bugfix_prompt})
        messages.append({"role": getattr(provider, "assistant_name", "assistant"), "content": response})

        blocks = _parse_file_blocks(response)
        if not blocks:
            raise RuntimeError("No <file path=...> blocks found in bugfix response.")

        allowed_roots = ("conf/", "src/", "scripts/", "tests/")
        written_files: list[str] = []
        invalid_paths: list[str] = []
        for rel_path, content in blocks:
            rp = rel_path.strip().lstrip("./")
            if rp == "run.py" or any(rp.startswith(root) for root in allowed_roots):
                target = Path(rp)
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(content, encoding="utf-8")
                written_files.append(rp)
            else:
                invalid_paths.append(rel_path)

        if invalid_paths:
            print("⚠️ Skipped disallowed paths:")
            for p in invalid_paths:
                print(f"- {p}")
            raise RuntimeError("Bugfix response included disallowed file paths.")

        if not written_files:
            raise RuntimeError("No files were written.")

        _run_cmd(["git", "add", *written_files])
        _run_cmd(["git", "commit", "-m", "autoresearch: bugfix failed debug config"])

        recent = _run_cmd(["git", "log", "-n", "5", "--pretty=%s"])
        if "autoresearch: bugfix" not in recent:
            raise RuntimeError("Bugfix commit verification failed.")

        latest_status["status"] = "BUGFIX_PROPOSED"
        status_path.write_text(json.dumps(latest_status, ensure_ascii=False, indent=2), encoding="utf-8")

        if failure_dir.exists():
            for p in failure_dir.glob("*.log"):
                p.unlink()

        watcher_path = self.store_path / "watcher_state.json"
        if watcher_path.exists():
            watcher = json.loads(watcher_path.read_text(encoding="utf-8"))
            watcher["phase"] = "EXPERIMENT_RUNNING"
            watcher["array_job_id"] = None
            watcher_path.write_text(json.dumps(watcher, ensure_ascii=False, indent=2), encoding="utf-8")

        git_add_targets = [str(failure_dir), str(status_path)]
        if watcher_path.exists():
            git_add_targets.append(str(watcher_path))
        _run_cmd(["git", "add", *git_add_targets])
        _run_cmd(["git", "commit", "-m", "autoresearch: clear bugfix failure logs"])

        diff_text = _run_cmd(["git", "diff", "HEAD~1", "--", *written_files], check=False)
        diff_tail = _tail_text(diff_text, 3000)

        slack_prompt = (
            "Create a Slack plain-text summary.\n"
            "Requirements:\n"
            "- 1-2 sentences on what failed (root cause)\n"
            "- bullet points of changed files and what changed\n"
            "- <= 10 lines total\n"
            "- no code blocks, use inline backticks only\n\n"
            f"failure log (tail):\n{latest_log_tail}\n\n"
            f"diff (tail):\n{diff_tail}\n"
        )
        slack_messages = messages + [{"role": "user", "content": slack_prompt}]
        slack_summary = self._call_llm(provider, slack_messages, provider_name, model_name).strip()

        webhook = os.environ.get("SLACK_WEBHOOK_URL", "").strip()
        payload_text = f"🔧 *AutoResearch Bugfix*\n{slack_summary}"
        if webhook:
            try:
                req = urllib.request.Request(
                    webhook,
                    data=json.dumps({"text": payload_text}).encode("utf-8"),
                    headers={"Content-Type": "application/json"},
                    method="POST",
                )
                with urllib.request.urlopen(req, timeout=10):
                    pass
            except Exception as e:
                print(f"⚠️ Slack notification failed: {e}")
        else:
            print(payload_text)

        return messages

    def evaluate_end_condition(self, runtime_dirs: dict[str, Any], messages: List[dict]) -> bool:
        status_path = self.store_path / "latest_status.json"
        if not status_path.exists():
            return False

        try:
            status = json.loads(status_path.read_text(encoding="utf-8"))
        except Exception:
            return False
        if status.get("status") != "BUGFIX_PROPOSED":
            return False

        failure_dir = self._resolve_failure_dir()
        if failure_dir.exists() and any(failure_dir.glob("*.log")):
            return False

        try:
            recent = _run_cmd(["git", "log", "-n", "20", "--pretty=%s"], check=False)
        except Exception:
            return False

        has_bugfix_commit = "autoresearch: bugfix" in recent
        has_clear_logs_commit = "autoresearch: clear bugfix failure logs" in recent
        return has_bugfix_commit and has_clear_logs_commit
