# stages/build_search_plan_stage.py
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, List

from autostages.src.stages.abs_stage import AbsStage
from autostages.src.utils import run_with_spinner


class BuildSearchPlanStage(AbsStage):
    PROVIDER_CHOICES = [
        ("openai", "OpenAI API", "models.openai_api"),
        ("claude", "Anthropic API", "models.claude_api"),
        ("codex", "Codex CLI", "models.codex_cli"),
        ("claude_code", "Claude Code CLI", "models.claude_cli"),
        ("gemini", "Google Gemini API", "models.google_api"),
    ]

    def __init__(self, store_path: Path = Path(".autosearch/store")):
        super().__init__(
            id="build_search_plan",
            description=(
                "Build a comprehensive multi-wave search plan for PEFT experiments.\n"
                "The plan guides which configurations to try in each experimental wave."
            ),
            final_message="✅ Search plan successfully generated.",
        )
        self.store_path = Path(store_path)
        self.store_path.mkdir(parents=True, exist_ok=True)

    def _sha256_file(self, path: Path) -> str:
        return hashlib.sha256(path.read_bytes()).hexdigest()

    def _resolve_provider_name(self) -> str:
        model_file = self.cache_path / "model.txt"
        if model_file.exists():
            return model_file.read_text(encoding="utf-8").strip()

        print("Select a provider for this stage:")
        for i, (key, label, module) in enumerate(self.PROVIDER_CHOICES, 1):
            print(f"  [{i}] {key} — {label} ({module})")

        keys = [c[0] for c in self.PROVIDER_CHOICES]
        while True:
            raw = input("Enter number or provider name: ").strip()
            if raw.isdigit() and 1 <= int(raw) <= len(keys):
                selected = keys[int(raw) - 1]
            elif raw in keys:
                selected = raw
            else:
                print(f"Invalid choice. Enter 1–{len(keys)} or one of {keys}.")
                continue
            model_file.write_text(selected, encoding="utf-8")
            return selected

    def _load_model_name(self, provider_name: str) -> str:
        config_path = Path(".autosearch/config.json")
        if not config_path.exists():
            return ""
        try:
            config = json.loads(config_path.read_text(encoding="utf-8"))
            return config.get("models", {}).get(provider_name, "")
        except (json.JSONDecodeError, KeyError):
            return ""

    def _read_safe(self, path: Path, last_n_lines: int = None) -> str:
        if not path.exists():
            return ""
        text = path.read_text(encoding="utf-8")
        if last_n_lines is not None:
            lines = text.splitlines()
            text = "\n".join(lines[-last_n_lines:])
        return text

    def _is_cache_hit(self, prompt_sha: str) -> bool:
        state_path = self.store_path / "prompt_state.json"
        plan_path = self.store_path / "search_plan.md"
        if not state_path.exists() or not plan_path.exists():
            return False
        try:
            state = json.loads(state_path.read_text(encoding="utf-8"))
            return state.get("prompt_sha256") == prompt_sha
        except (json.JSONDecodeError, KeyError):
            return False

    def _build_system_prompt(self) -> str:
        return (
            "You are a research assistant building a comprehensive multi-wave experiment roadmap\n"
            "for PEFT (Parameter-Efficient Fine-Tuning) methods applied to a speech recognition model.\n\n"
            "Your task:\n"
            "1. Use web search to fetch ALL available PEFT method names from the official HuggingFace PEFT library.\n"
            "   - Primary source: https://huggingface.co/docs/peft/package_reference/peft_types\n"
            "   - Also check: https://github.com/huggingface/peft (README, SUPPORTED_MODELS)\n"
            "   - List EVERY PeftType enum value (LORA, LOHA, LOKR, ADALORA, IA3, VERA, OFT, BOFT, LOFTQ,\n"
            "     FOURIERFT, HRA, VBLORA, RANDLORA, DELORA, ESPNET_LORA, ...). Do NOT stop early.\n"
            "2. For each method, determine compatibility with encoder-decoder (seq2seq) models.\n"
            "3. Structure the search into sequential waves — one exploration axis per wave.\n"
            "4. Enumerate EXPLICIT candidate values (not generic ranges) for the Wave 1 axis only;\n"
            "   keep all other waves deferred.\n"
            "5. For numeric axes: use coarse log-scale values (e.g. 1e-5, 5e-5, 1e-4) not dense sweeps.\n\n"
            "Output ONLY one <file> block:\n"
            '<file path=".autosearch/store/search_plan.md">...</file>\n'
            "No other text."
        )

    def _build_user_prompt(self) -> str:
        prompt_txt = self._read_safe(Path("prompt.txt"))
        default_yaml = self._read_safe(Path("conf/default.yaml"))
        peft_yaml = self._read_safe(Path("conf/owsm_peft_lora_basic.yaml"))
        search_plan_human = self._read_safe(Path(".autosearch/resources/search_plan_human.md"))

        experiments_csv = self._read_safe(Path("experiments.csv"), last_n_lines=30)
        if not experiments_csv:
            experiments_csv = self._read_safe(
                Path(".autoresearch/store/experiments.csv"), last_n_lines=30
            )

        existing_plan = self._read_safe(self.store_path / "search_plan.md")
        if existing_plan:
            existing_section = (
                "## Existing search_plan.md (extend this — do not discard prior findings)\n"
                + existing_plan
            )
        else:
            existing_section = ""

        output_format = (
            '<file path=".autosearch/store/search_plan.md">\n'
            "# Research Roadmap\n\n"
            "## Wave 1: PEFT Method Family\n"
            "**Why first**: Establishing which method is stable and compatible is prerequisite for all\n"
            "hyperparameter tuning.\n"
            "**Current focus**: YES\n\n"
            "| candidate | status | comment | config | source |\n"
            "| --- | --- | --- | --- | --- |\n"
            "| lora | pending | seq2seq compatible; strong baseline | | https://... |\n"
            "| ... | | | | |\n\n"
            "**Unlock condition**: At least one method completes without crash or OOM; fix the best-WER\n"
            "method for Wave 2.\n\n"
            "---\n\n"
            "## Wave 2: PEFT Hyperparameters (rank, alpha, dropout)\n"
            "**Why second**: ...\n"
            "**Current focus**: NO — deferred until Wave 1 is resolved.\n\n"
            "**Deferred until Wave 1 is resolved.**\n\n"
            "---\n"
            "</file>"
        )

        parts = [
            "Build a comprehensive multi-wave research roadmap from the inputs below.\n",
            "## prompt.txt (goals, metric, axes to explore)",
            prompt_txt,
            "## conf/default.yaml (base config format and available fields)",
            default_yaml,
            "## conf/owsm_peft_lora_basic.yaml (PEFT config example)",
            peft_yaml,
            "## .autosearch/resources/search_plan_human.md (format reference — use this table structure)",
            search_plan_human,
            "## experiments.csv (evidence so far — last 30 rows)",
            experiments_csv,
        ]
        if existing_section:
            parts.append(existing_section)

        parts += [
            "## Instructions\n",
            "### Wave structure",
            "Arrange axes in this order (one axis per wave):",
            "1. Wave 1 — PEFT method family (categorical): test ALL compatible methods first.",
            "2. Wave 2 — Best method's hyperparams (rank, alpha, dropout, target_modules): deferred.",
            "3. Wave 3 — Learning rate (log-scale): deferred.",
            "4. Wave 4 — Optimizer (AdamW, AdaFactor, SGD, ...): deferred.",
            "5. Wave 5 — Warmup steps: deferred.",
            "6. Wave 6 — Batch size / max_epochs: deferred.",
            "Add more waves if prompt.txt section 6 lists additional axes.\n",
            "### Wave 1 requirements (CURRENT FOCUS)",
            "- Fetch the full PeftType enum from https://huggingface.co/docs/peft/package_reference/peft_types",
            "- For EVERY method found, write one table row:",
            "  | candidate | status | comment | config | source |",
            "  - candidate: exact method name (lowercase, as used in config `peft.type`)",
            "  - status: `pending` (or `done` / `skipped` if experiments.csv has evidence)",
            "  - comment: 1-line note on seq2seq compatibility + brief rationale",
            "  - config: leave empty (filled after experiments run)",
            "  - source: URL to official docs or paper",
            "- Mark any method NOT compatible with encoder-decoder as `skipped` with reason.",
            "- Prioritize: standard LoRA family first, then regularization-based, then exotic.\n",
            "### Deferred waves",
            "For Waves 2–6, write only the wave heading and:",
            '"**Deferred until Wave N-1 is resolved.**"',
            "Do NOT enumerate candidate values for deferred waves yet.\n",
            "### Unlock conditions",
            "After each wave table, write:",
            "**Unlock condition**: <what result allows moving to next wave>\n",
            "### Output format (MUST follow exactly)",
            output_format,
        ]

        return "\n\n".join(p for p in parts if p)

    def _parse_file_block(self, response: str, file_path: str) -> str | None:
        pattern = rf'<file\s+path="{re.escape(file_path)}">(.*?)</file>'
        match = re.search(pattern, response, re.DOTALL)
        return match.group(1).strip() if match else None

    def _write_state_files(self, prompt_sha: str) -> None:
        now = datetime.now(timezone.utc).isoformat()
        (self.store_path / "prompt_state.json").write_text(
            json.dumps({"prompt_sha256": prompt_sha, "updated_at": now}, indent=2),
            encoding="utf-8",
        )
        bootstrap_path = self.store_path / "bootstrap_done.json"
        if not bootstrap_path.exists():
            bootstrap_path.write_text(
                json.dumps({"done": False, "updated_at": now}, indent=2),
                encoding="utf-8",
            )

    def run_body(self, provider, messages: List[dict]) -> List[dict]:
        prompt_path = Path("prompt.txt")
        if not prompt_path.exists():
            print("❌ prompt.txt not found at repository root. Cannot proceed.")
            return messages

        provider_name = self._resolve_provider_name()
        model_name = self._load_model_name(provider_name)
        if model_name:
            print(f"Using model: {model_name} ({provider_name})")

        prompt_sha = self._sha256_file(prompt_path)
        if self._is_cache_hit(prompt_sha):
            print(f"✅ Cache hit: search_plan.md is up-to-date (sha256={prompt_sha[:8]}...).")
            return messages

        system_prompt = self._build_system_prompt()
        user_prompt = self._build_user_prompt()

        llm_messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        response = run_with_spinner(
            provider.chat,
            (llm_messages,),
            "Generating search plan via LLM...",
        )

        (self.cache_path / "last_response.txt").write_text(response, encoding="utf-8")

        plan_content = self._parse_file_block(response, ".autosearch/store/search_plan.md")
        if plan_content is None:
            print("⚠️  Could not parse <file path=\".autosearch/store/search_plan.md\"> block.")
            print("Raw response saved to cache. Please check last_response.txt.")
            return messages

        (self.store_path / "search_plan.md").write_text(plan_content, encoding="utf-8")
        self._write_state_files(prompt_sha)

        messages.append({"role": "user", "content": user_prompt})
        messages.append({"role": provider.assistant_name, "content": response})
        return messages

    def evaluate_end_condition(self, runtime_dirs: dict[str, Any], messages: List[dict]) -> bool:
        prompt_path = Path("prompt.txt")
        if not prompt_path.exists():
            return False

        search_plan_path = self.store_path / "search_plan.md"
        if not search_plan_path.exists() or search_plan_path.stat().st_size == 0:
            return False

        state_path = self.store_path / "prompt_state.json"
        if not state_path.exists():
            return False

        try:
            state = json.loads(state_path.read_text(encoding="utf-8"))
            stored_sha = state.get("prompt_sha256", "")
            if not stored_sha:
                return False
            actual_sha = hashlib.sha256(prompt_path.read_bytes()).hexdigest()
            return stored_sha == actual_sha
        except (json.JSONDecodeError, KeyError, OSError):
            return False
