# AutoResearch System Design

## 概要

clusterで実験 → 結果をGitHubへpush → GitHub Actions上のClaude/ChatGPTがconfig/codeを修正してPR作成 → CI通過でauto-merge → clusterが更新を検知して次の実験を投入、という自律研究ループ。

旧アーキテクチャ（login node常駐プロセス + `codex exec` CLI）を廃止し、以下に置き換える：

- **常駐プロセス廃止** → self-resubmit型 Slurm watcher job
- **Codex CLI廃止** → GitHub Actions上でClaude API (Anthropic SDK) を呼ぶ Python スクリプト

---

## 全体フロー

```
[Cluster]
  run_experiment.slurm (array job)
      ↓ 完了
  check_and_submit.slurm (watcher, self-resubmit)
      ↓ sacctで全タスク完了確認
      ↓ metrics.json 収集 → experiments.csv 更新
      ↓ .autoresearch/ 更新 (latest_metrics.json, next_goal.md, ...)
      ↓ git add/commit/push → origin/main

[GitHub Actions] (push trigger)
      ↓ .autoresearch/ を読む
      ↓ Claude API で次のconfig/code提案
      ↓ conf/{next_exp_name}/ と array_conf/{next_exp_name}/ を生成
      ↓ PR作成
      ↓ CI: test_config_load + test_search_plan (GPU不要)
      ↓ CI pass → auto-merge (squash)

[Cluster] (watcher, WAITING_FOR_PR_MERGE フェーズ)
      ↓ git fetch → 新コミット検知
      ↓ git pull
      ↓ array_conf/{next_exp_name}/ を読んで sbatch
      ↓ watcher_state.json を EXPERIMENT_RUNNING に更新して resubmit
```

---

## ディレクトリ構造

```
/
├── .autoresearch/                   # state interface (gitで管理)
│   ├── watcher_state.json           # watcherのフェーズ管理
│   ├── latest_status.json           # 直近array jobのステータス
│   ├── latest_metrics.json          # 直近実験のメトリクス (WER/CER)
│   ├── latest_error.log             # エラーログの抜粋
│   ├── next_goal.md                 # 次waveへの指示 (Claudeが読む)
│   └── codex_summary.md            # Claudeが書いた変更サマリー
│
├── .github/
│   └── workflows/
│       ├── autoresearch.yml         # push trigger → Claude → PR作成
│       └── ci.yml                   # PR trigger → config/search_plan test
│
├── scripts/
│   ├── check_and_submit.slurm      # [新規] watcher job (self-resubmit)
│   ├── collect_metrics.py          # [新規] metrics.json → experiments.csv
│   ├── run-array.sh                # [既存] 個別タスク実行
│   ├── submit-array-with-debug.sh  # [既存] debug gate + array投入
│   └── submit-local-with-debug.sh  # [既存] local実行
│
├── src/
│   ├── bin/
│   │   ├── autoresearch_driver.py  # [新規] Claude API呼び出し
│   │   └── autoresearch_loop.py           # [旧] 廃止予定
│   ├── experiments_csv.py          # [既存] CSV記録
│   └── slack_notify.py             # [既存] Slack通知
│
├── tests/
│   ├── test_config_load.py         # [新規] config loadingテスト (CI用)
│   └── test_search_plan.py        # [新規] search space validationテスト (CI用)
│
├── conf/
│   ├── default.yaml                # ベースconfig
│   ├── dataset.yaml
│   ├── inference.yaml
│   ├── metrics.yaml
│   ├── {base_template_1}.yaml     # レシピ側のベーステンプレート
│   ├── {base_template_2}.yaml
│   ├── ...
│   └── {exp_name}/                 # Claudeが生成する実験config群
│       ├── config_0.yaml
│       ├── config_1.yaml
│       └── ...
│
├── array_conf/
│   └── {exp_name}/
│       └── array.txt               # Claudeが生成するconfig listファイル
│
├── experiments.csv                 # 全実験メタデータ
├── notes/
│   ├── autoresearch_checklist.md  # C0〜C6 チェックリスト
│   └── autoresearch_findings.md   # waveごとの知見ログ
└── prompts/
    ├── search_plan.md             # 探索空間定義
    ├── prompt.txt                  # Claude用: 新セッション
    ├── followup.txt                # Claude用: 継続セッション
    └── error.txt                   # Claude用: エラー分析
```

---

## State Interface: `.autoresearch/`

### `watcher_state.json`

watcherのフェーズ管理。watcherはこれを読み書きして状態遷移する。

```json
{
  "phase": "EXPERIMENT_RUNNING",
  "array_job_id": "17915098",
  "exp_name": "exp_20260429_123456",
  "next_exp_name": "",
  "last_main_sha": "abc123def456",
  "submitted_at": "2026-04-29T12:00:00-05:00",
  "phase_updated_at": "2026-04-29T12:00:00-05:00"
}
```

- `phase`: `"EXPERIMENT_RUNNING"` | `"WAITING_FOR_PR_MERGE"` | `"IDLE"`
- `last_main_sha`: WAITING_FOR_PR_MERGE フェーズで新コミット検知に使う
- `next_exp_name`: GitHub Actionsが書き込む (Claudeが決めた次の実験名)

### `latest_status.json`

直近arrayの完了サマリー。GitHub Actionsが参照する。

```json
{
  "exp_name": "exp_20260429_123456",
  "array_job_id": "17915098",
  "total_tasks": 5,
  "completed": 4,
  "failed": 1,
  "finished_at": "2026-04-29T18:00:00-05:00",
  "failed_run_uids": ["17915098_2_exp_..._a2"]
}
```

### `latest_metrics.json`

直近waveの全実験メトリクス。GitHub ActionsのClaude promptに渡す。

```json
{
  "exp_name": "exp_20260429_123456",
  "wave_summary": [
    {
      "run_uid": "17915098_0_exp_..._a0",
      "base_config": "conf/{base_template}.yaml",
      "method_type": "method_a",
      "lr": "5e-5",
      "trainer_max_epochs": "3",
      "wer": 0.312,
      "cer": 0.187,
      "status": "COMPLETED"
    }
  ],
  "best_run_uid": "17915098_0_exp_..._a0",
  "best_wer": 0.312
}
```

### `latest_error.log`

失敗したタスクのログ末尾200行。GitHub Actionsのerrorプロンプトに埋め込む。

### `next_goal.md`

clusterが書き込み、Claudeが読む指示書。

```markdown
# Next Goal

- Previous wave: exp_20260429_123456 (array_job_id=17915098)
- Mode: slurm
- Max configs for next wave: 10
- Checklist priority: C1 (method-family comparison)

## Evidence from latest wave
- method_a: metric=...
- method_b: failed
- method_c: metric=...

## Instruction
Propose next wave targeting C1 and C2.
Do NOT expand beyond search_plan.md.
```

### `codex_summary.md`

Claudeが書き込む変更サマリー。人間が確認用に読む。

---

## Cluster Watcher Job

### `scripts/check_and_submit.slurm`

self-resubmit型のSlurmジョブ。CPUパーティションで十分（GPU不要）。

```bash
#!/bin/bash
#SBATCH --job-name=autoresearch_watcher
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=2
#SBATCH --mem=4G
#SBATCH --time=0:10:00          # 1回の実行は10分以内
#SBATCH --partition=cpu
#SBATCH --account=bbjs-delta-cpu
#SBATCH --output=logs/watcher/%j.log
#SBATCH --error=logs/watcher/%j.log

set -euo pipefail
cd "${SLURM_SUBMIT_DIR}"
. scripts/path.sh

python scripts/watcher.py
```

### `scripts/watcher.py`

watcherのメインロジック。`check_and_submit.slurm` から呼ばれる。

```python
#!/usr/bin/env python3
"""
Autoresearch watcher.
Reads .autoresearch/watcher_state.json, decides what to do, then resubmits itself.
"""
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent.resolve()
STATE_PATH = REPO_ROOT / ".autoresearch" / "watcher_state.json"
SLEEP_SEC = 300  # 5分後に再投入

def now_iso():
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")

def load_state() -> dict:
    if not STATE_PATH.exists():
        return {"phase": "IDLE"}
    return json.loads(STATE_PATH.read_text())

def save_state(state: dict):
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    state["phase_updated_at"] = now_iso()
    STATE_PATH.write_text(json.dumps(state, indent=2, ensure_ascii=False))

def resubmit_self(delay_sec: int = SLEEP_SEC):
    """delay_sec 後に自分自身をsbatchで再投入する。"""
    subprocess.run(
        ["sbatch", f"--begin=now+{delay_sec}", "scripts/check_and_submit.slurm"],
        check=True
    )

def all_tasks_terminal(array_job_id: str) -> tuple[bool, dict]:
    """
    sacct で array_job_id の全タスク状態を確認。
    戻り値: (全タスクterminalか, {task_id: state} の辞書)
    """
    result = subprocess.run(
        ["sacct", "-n", "-P", "-j", array_job_id,
         "--format=JobIDRaw,State,ExitCode"],
        capture_output=True, text=True
    )
    states = {}
    terminal = {"COMPLETED", "FAILED", "CANCELLED", "TIMEOUT",
                "NODE_FAIL", "OUT_OF_MEMORY", "PREEMPTED"}
    for line in result.stdout.splitlines():
        parts = line.split("|")
        if len(parts) < 3:
            continue
        jid, state, _ = parts[0].strip(), parts[1].strip().split()[0], parts[2].strip()
        if "_" in jid:  # array task (e.g., 12345_0)
            states[jid] = state
    if not states:
        return False, states
    return all(s in terminal for s in states.values()), states

def collect_metrics(exp_name: str, array_job_id: str) -> dict:
    """
    exp/{exp_name}/*/infer/metrics.json を探してまとめる。
    experiments.csv も更新する (collect_metrics.py に委譲)。
    """
    result = subprocess.run(
        ["python", "scripts/collect_metrics.py",
         "--exp-name", exp_name,
         "--array-job-id", array_job_id,
         "--csv-path", "experiments.csv",
         "--output", ".autoresearch/latest_metrics.json"],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        print(f"[WARN] collect_metrics failed: {result.stderr}", file=sys.stderr)
        return {}
    metrics_path = REPO_ROOT / ".autoresearch" / "latest_metrics.json"
    if metrics_path.exists():
        return json.loads(metrics_path.read_text())
    return {}

def git_push():
    subprocess.run(["git", "add",
                    ".autoresearch/",
                    "experiments.csv",
                    "notes/"], check=True)
    subprocess.run(["git", "commit", "-m",
                    f"autoresearch: push results {now_iso()}"], check=True)
    subprocess.run(["git", "push", "origin", "main"], check=True)

def get_latest_main_sha() -> str:
    result = subprocess.run(
        ["git", "rev-parse", "origin/main"],
        capture_output=True, text=True
    )
    return result.stdout.strip()

def git_fetch_and_check_new_commits(last_sha: str) -> bool:
    subprocess.run(["git", "fetch", "origin"], check=True)
    current_sha = get_latest_main_sha()
    return current_sha != last_sha

def submit_next_experiment(state: dict):
    """
    array_conf/{next_exp_name}/array.txt を読んでsbatch投入。
    submit-array-with-debug.sh の debug gate を通す。
    """
    next_exp_name = state.get("next_exp_name", "")
    if not next_exp_name:
        print("[ERROR] next_exp_name not set in watcher_state.json")
        return
    config_list = REPO_ROOT / "array_conf" / next_exp_name / "array.txt"
    if not config_list.exists():
        print(f"[ERROR] config_list not found: {config_list}")
        return
    configs = [l for l in config_list.read_text().splitlines()
               if l.strip() and not l.strip().startswith("#")]
    n = len(configs)
    result = subprocess.run(
        ["bash", "scripts/submit-array-with-debug.sh",
         next_exp_name, f"0-{n-1}", str(config_list), "0"],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        print(f"[ERROR] submit failed: {result.stderr}")
        return
    # sbatch出力からarray_job_idを取得 ("Submitted batch job 12345678")
    for line in result.stdout.splitlines():
        if "Submitted batch job" in line:
            new_array_job_id = line.split()[-1]
            state["array_job_id"] = new_array_job_id
            state["exp_name"] = next_exp_name
            state["next_exp_name"] = ""
            state["phase"] = "EXPERIMENT_RUNNING"
            state["submitted_at"] = now_iso()
            save_state(state)
            print(f"[INFO] submitted array {new_array_job_id} for {next_exp_name}")
            return


def main():
    state = load_state()
    phase = state.get("phase", "IDLE")
    print(f"[INFO] watcher tick: phase={phase} time={now_iso()}")

    if phase == "EXPERIMENT_RUNNING":
        array_job_id = state.get("array_job_id", "")
        exp_name = state.get("exp_name", "")
        if not array_job_id:
            print("[ERROR] array_job_id not set")
            resubmit_self()
            return

        done, task_states = all_tasks_terminal(array_job_id)
        if not done:
            running = [k for k, v in task_states.items() if v not in
                       {"COMPLETED","FAILED","CANCELLED","TIMEOUT",
                        "NODE_FAIL","OUT_OF_MEMORY","PREEMPTED"}]
            print(f"[INFO] array {array_job_id} still running: {running}")
            resubmit_self()
            return

        print(f"[INFO] array {array_job_id} all terminal. collecting metrics...")
        metrics = collect_metrics(exp_name, array_job_id)

        # latest_status.json 更新
        failed = [k for k, v in task_states.items() if v != "COMPLETED"]
        status = {
            "exp_name": exp_name,
            "array_job_id": array_job_id,
            "total_tasks": len(task_states),
            "completed": len(task_states) - len(failed),
            "failed": len(failed),
            "finished_at": now_iso(),
            "failed_run_uids": failed,
        }
        (REPO_ROOT / ".autoresearch" / "latest_status.json").write_text(
            json.dumps(status, indent=2, ensure_ascii=False)
        )

        # next_goal.md 生成
        best = metrics.get("best_wer", "N/A")
        (REPO_ROOT / ".autoresearch" / "next_goal.md").write_text(
            f"# Next Goal\n\n"
            f"- Previous wave: {exp_name} (array_job_id={array_job_id})\n"
            f"- Mode: slurm\n"
            f"- Max configs for next wave: 10\n\n"
            f"## Evidence from latest wave\n"
            f"- Best WER: {best}\n"
            f"- See .autoresearch/latest_metrics.json for details.\n\n"
            f"## Instruction\n"
            f"Read notes/autoresearch_checklist.md and propose next wave.\n"
            f"Stay within prompts/search_plan.md.\n"
        )

        # git push して GitHub Actions を起動
        state["last_main_sha"] = get_latest_main_sha()
        save_state(state)
        git_push()

        state["phase"] = "WAITING_FOR_PR_MERGE"
        save_state(state)
        resubmit_self()

    elif phase == "WAITING_FOR_PR_MERGE":
        last_sha = state.get("last_main_sha", "")
        has_new = git_fetch_and_check_new_commits(last_sha)
        if not has_new:
            print(f"[INFO] no new commits on main yet. waiting...")
            resubmit_self()
            return

        print("[INFO] new commits detected on main. pulling and submitting next experiment...")
        subprocess.run(["git", "pull", "origin", "main"], check=True)
        state["last_main_sha"] = get_latest_main_sha()
        submit_next_experiment(state)  # phase → EXPERIMENT_RUNNING に変えてsave_state内でやる
        resubmit_self()

    else:  # IDLE or unknown
        print(f"[INFO] phase={phase}. nothing to do.")
        # IDLEの場合は再投入しない（手動で開始する）


if __name__ == "__main__":
    main()
```

---

## metrics収集スクリプト

### `scripts/collect_metrics.py`

実験ディレクトリを走査して `metrics.json` を収集し、`experiments.csv` を更新する。

```python
#!/usr/bin/env python3
"""
Scan exp/{exp_name}/*/infer/metrics.json and update experiments.csv.
Output summary to .autoresearch/latest_metrics.json.
"""
import argparse
import csv
import json
from pathlib import Path

def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--exp-name", required=True)
    p.add_argument("--array-job-id", required=True)
    p.add_argument("--csv-path", default="experiments.csv")
    p.add_argument("--output", default=".autoresearch/latest_metrics.json")
    return p.parse_args()

def main():
    args = parse_args()
    exp_root = Path("exp") / args.exp_name
    csv_path = Path(args.csv_path)

    # experiments.csv を読む
    rows = []
    fieldnames = []
    if csv_path.exists() and csv_path.stat().st_size > 0:
        with csv_path.open(newline="") as f:
            reader = csv.DictReader(f)
            fieldnames = list(reader.fieldnames or [])
            rows = list(reader)

    # metrics.json を走査
    wave_summary = []
    best_wer = float("inf")
    best_run_uid = ""

    for metrics_path in sorted(exp_root.glob("*/infer/metrics.json")):
        exp_tag = metrics_path.parent.parent.name  # exp_name/exp_tag/infer/metrics.json
        try:
            data = json.loads(metrics_path.read_text())
        except Exception:
            continue

        wer = data.get("WER", data.get("wer", None))
        cer = data.get("CER", data.get("cer", None))

        # experiments.csv の対応行を探してmetricsを書き込む
        for row in rows:
            if row.get("exp_name") == args.exp_name and exp_tag in row.get("run_uid", ""):
                if wer is not None:
                    row["wer"] = str(wer)
                if cer is not None:
                    row["cer"] = str(cer)
                run_uid = row.get("run_uid", "")
                lr = row.get("learning_rate", "")
                method_type = row.get("method_type", "")
                max_epochs = row.get("trainer_max_epochs", "")
                base_config = row.get("base_config", "")
                wave_summary.append({
                    "run_uid": run_uid,
                    "base_config": base_config,
                    "method_type": method_type,
                    "lr": lr,
                    "trainer_max_epochs": max_epochs,
                    "wer": wer,
                    "cer": cer,
                    "status": row.get("status", ""),
                })
                if wer is not None and float(wer) < best_wer:
                    best_wer = float(wer)
                    best_run_uid = run_uid
                break

    # experiments.csv 書き戻し
    # NOTE: wer/cer フィールドが既存のfieldnamesにない場合は追加
    for extra_col in ("wer", "cer"):
        if fieldnames and extra_col not in fieldnames:
            fieldnames.append(extra_col)
    if fieldnames and rows:
        with csv_path.open("w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for row in rows:
                writer.writerow({k: row.get(k, "") for k in fieldnames})

    # latest_metrics.json 出力
    output = {
        "exp_name": args.exp_name,
        "array_job_id": args.array_job_id,
        "wave_summary": wave_summary,
        "best_run_uid": best_run_uid,
        "best_wer": best_wer if best_wer < float("inf") else None,
    }
    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(output, indent=2, ensure_ascii=False))
    print(f"[INFO] wrote {out_path} ({len(wave_summary)} runs)")

if __name__ == "__main__":
    main()
```

**注意**: `experiments.csv` の既存フィールドは `src/experiments_csv.py` の `FIELDS` リストで定義されている。`wer`, `cer` は現在のFIELDSにないため追加が必要、またはcollect_metrics.pyが別ファイルに書くように設計してもよい。

---

## GitHub Actions Workflows

### `.github/workflows/autoresearch.yml`

pushをトリガーに Claude API を呼んで次のwave configを生成し、PRを作る。

```yaml
name: AutoResearch Wave Planner

on:
  push:
    branches: [main]
    paths:
      - ".autoresearch/latest_status.json"
      - ".autoresearch/latest_metrics.json"
      - ".autoresearch/next_goal.md"

jobs:
  plan-next-wave:
    runs-on: ubuntu-latest
    permissions:
      contents: write
      pull-requests: write

    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install dependencies
        run: |
          pip install anthropic pyyaml omegaconf

      - name: Run Claude autoresearch driver
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
          SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL }}
        run: |
          python src/bin/autoresearch_driver.py \
            --repo-root . \
            --prompts-dir prompts \
            --csv-path experiments.csv \
            --autoresearch-dir .autoresearch \
            --model claude-opus-4-7  \
            --max-configs 10

      - name: Create PR
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          # autoresearch_driver.py が出力した branch名を読む
          BRANCH=$(cat .autoresearch/next_branch.txt 2>/dev/null || echo "")
          if [ -z "$BRANCH" ]; then
            echo "No branch to create PR for."
            exit 0
          fi
          gh pr create \
            --title "autoresearch: $(cat .autoresearch/next_exp_name.txt)" \
            --body "$(cat .autoresearch/codex_summary.md)" \
            --base main \
            --head "$BRANCH" \
            --label "autoresearch"
          gh pr merge "$BRANCH" --auto --squash
```

### `.github/workflows/ci.yml`

PRをトリガーにconfig validation testを実行。GPU不要、数秒で完了。

```yaml
name: Config Validation CI

on:
  pull_request:
    branches: [main]
    paths:
      - "conf/**"
      - "array_conf/**"
      - "src/**"
      - "tests/**"

jobs:
  validate-configs:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install test dependencies
        run: |
          pip install pytest pyyaml omegaconf

      - name: Run config tests
        run: |
          pytest tests/ -v --no-header -x
```

---

## Claude API ドライバー

### `src/bin/autoresearch_driver.py`

GitHub Actions から呼ばれる。Claude API でプロンプトを送り、生成されたconfig/codeを新ブランチにcommitする。

```python
#!/usr/bin/env python3
"""
GitHub Actions から呼ばれる Claude API ドライバー。
.autoresearch/ の state を読み、LLM に次の wave config を提案させ、
新ブランチに commit する。
"""
import argparse
import json
import os
import subprocess
from datetime import datetime
from pathlib import Path

import anthropic


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--repo-root", default=".")
    p.add_argument("--prompts-dir", default="prompts")
    p.add_argument("--csv-path", default="experiments.csv")
    p.add_argument("--autoresearch-dir", default=".autoresearch")
    p.add_argument("--model", default="claude-opus-4-7")
    p.add_argument("--max-configs", type=int, default=10)
    p.add_argument("--max-tokens", type=int, default=8192)
    return p.parse_args()


def read_file_safe(path: Path, max_chars: int = 8000) -> str:
    if not path.exists():
        return f"(file not found: {path})"
    text = path.read_text(encoding="utf-8")
    if len(text) > max_chars:
        text = text[-max_chars:]  # 末尾を優先
    return text


def build_system_prompt(repo_root: Path, prompts_dir: Path) -> str:
    search_plan = read_file_safe(prompts_dir / "search_plan.md")
    return f"""You are the experiment planner for iterative autoresearch.

Your job:
1. Read the state files provided.
2. Propose the next experiment wave (configs + array list).
3. Write the config files to conf/{{next_exp_name}}/ .
4. Write the array config list to array_conf/{{next_exp_name}}/array.txt .
5. Write a summary to .autoresearch/codex_summary.md .
6. Write the next_exp_name to .autoresearch/next_exp_name.txt (single line, no newline).
7. Update notes/autoresearch_checklist.md statuses.
8. Append to notes/autoresearch_findings.md.

## Search Space Policy
{search_plan}

## File Edit Policy
Allowed to edit:
- conf/{{next_exp_name}}/   (create new directory and yaml files)
- array_conf/{{next_exp_name}}/array.txt
- .autoresearch/codex_summary.md
- .autoresearch/next_exp_name.txt
- notes/autoresearch_checklist.md
- notes/autoresearch_findings.md

Do NOT edit:
- exp/
- dump/
- data/
- .env
- secrets/
- experiments.csv  (managed by cluster scripts)
- conf/default.yaml, conf/dataset.yaml, conf/inference.yaml  (do not modify templates)

## Test Writing Policy
When adding new configs under conf/{{next_exp_name}}/:
- Each new YAML must be referenced in tests/test_config_load.py as a parametrized case.
- Each new YAML's hyperparameter values must be checked in tests/test_search_plan.py.
- Tests must pass without GPU (config parsing only, no model loading).
- Use pytest. See existing tests/ for format.

## Config Format
New experiment configs must use this structure:
```yaml
defaults:
  - ../../base_template  # or other recipe template

lr: 5e-5
exp_tag: ${{exp_name}}_variant_lr5e-5

method:
  type: method_a
  param_a: 8
  param_b: 0.05
```

## array.txt Format
One config path per line, relative to repo root:
```
conf/{{next_exp_name}}/config_0.yaml
conf/{{next_exp_name}}/config_1.yaml
```
"""


def build_user_prompt(repo_root: Path, autoresearch_dir: Path,
                       csv_path: Path, max_configs: int) -> str:
    ar = autoresearch_dir
    next_goal = read_file_safe(ar / "next_goal.md")
    latest_metrics = read_file_safe(ar / "latest_metrics.json")
    latest_status = read_file_safe(ar / "latest_status.json")
    latest_error = read_file_safe(ar / "latest_error.log", max_chars=3000)
    checklist = read_file_safe(repo_root / "notes" / "autoresearch_checklist.md")
    findings = read_file_safe(repo_root / "notes" / "autoresearch_findings.md", max_chars=4000)

    # experiments.csv の末尾20行だけ渡す（トークン節約）
    csv_text = "(empty)"
    if csv_path.exists() and csv_path.stat().st_size > 0:
        lines = csv_path.read_text().splitlines()
        csv_text = "\n".join(lines[:1] + lines[-20:])  # header + last 20

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    next_exp_name = f"exp_{ts}"

    return f"""## Task

Plan the next experiment wave.

- next_exp_name: {next_exp_name}
- max_configs: {max_configs}

## next_goal.md
{next_goal}

## latest_metrics.json
{latest_metrics}

## latest_status.json
{latest_status}

## latest_error.log (if any)
{latest_error}

## autoresearch_checklist.md
{checklist}

## autoresearch_findings.md (recent entries)
{findings}

## experiments.csv (header + last 20 rows)
{csv_text}

## Action Required
1. Summarize the evidence from latest_metrics.json and experiments.csv.
2. Choose checklist IDs to target this wave.
3. Propose up to {max_configs} configs with clear rationale.
4. Create all files as described in the system prompt.
5. Write .autoresearch/next_exp_name.txt with the value: {next_exp_name}
"""


def apply_file_operations(response_text: str, repo_root: Path):
    """
    Claude の応答からファイル操作を実行する。
    Claude には <file path="...">content</file> 形式で出力させる。
    """
    import re
    pattern = re.compile(
        r'<file path="([^"]+)">(.*?)</file>',
        re.DOTALL
    )
    written = []
    for m in pattern.finditer(response_text):
        rel_path = m.group(1).strip()
        content = m.group(2)
        # leading newline を除去
        if content.startswith("\n"):
            content = content[1:]

        # 安全チェック: 許可されたパスのみ
        allowed_prefixes = ("conf/", "array_conf/", ".autoresearch/", "notes/", "tests/")
        if not any(rel_path.startswith(p) for p in allowed_prefixes):
            print(f"[WARN] skipping disallowed path: {rel_path}")
            continue

        target = repo_root / rel_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        written.append(rel_path)
        print(f"[INFO] wrote: {rel_path}")
    return written


def commit_to_branch(repo_root: Path, next_exp_name: str, written_files: list[str]) -> str:
    branch = f"autoresearch/{next_exp_name}"
    subprocess.run(["git", "checkout", "-b", branch], cwd=repo_root, check=True)
    subprocess.run(["git", "add"] + written_files, cwd=repo_root, check=True)
    subprocess.run(
        ["git", "commit", "-m", f"autoresearch: propose {next_exp_name}"],
        cwd=repo_root, check=True
    )
    subprocess.run(["git", "push", "origin", branch], cwd=repo_root, check=True)
    return branch


def main():
    args = parse_args()
    repo_root = Path(args.repo_root).resolve()
    prompts_dir = (repo_root / args.prompts_dir).resolve()
    autoresearch_dir = (repo_root / args.autoresearch_dir).resolve()
    csv_path = (repo_root / args.csv_path).resolve()

    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    system = build_system_prompt(repo_root, prompts_dir)
    user = build_user_prompt(repo_root, autoresearch_dir, csv_path, args.max_configs)

    print("[INFO] calling Claude API...")
    message = client.messages.create(
        model=args.model,
        max_tokens=args.max_tokens,
        system=system,
        messages=[{"role": "user", "content": user}],
    )
    response_text = message.content[0].text
    print(f"[INFO] Claude response: {len(response_text)} chars")

    # prompts/last_response.txt に保存（デバッグ用）
    (repo_root / "prompts" / "last_response.txt").write_text(response_text, encoding="utf-8")

    # ファイル操作実行
    written = apply_file_operations(response_text, repo_root)

    if not written:
        print("[ERROR] Claude wrote no files. Check prompts/last_response.txt")
        return 1

    # next_exp_name を確認
    next_exp_name_path = autoresearch_dir / "next_exp_name.txt"
    if not next_exp_name_path.exists():
        print("[ERROR] .autoresearch/next_exp_name.txt not written by planner")
        return 1
    next_exp_name = next_exp_name_path.read_text().strip()

    # ブランチ作成・push
    branch = commit_to_branch(repo_root, next_exp_name, written)
    (autoresearch_dir / "next_branch.txt").write_text(branch)

    print(f"[INFO] done. branch={branch} next_exp_name={next_exp_name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

---

## テスト

### `tests/test_config_load.py`

GPU不要。YAMLがomegaconfで読めること、必須キーが存在することを確認。

```python
"""
Config loading tests. GPU-free. Runs in GitHub Actions CI.

To add a new config: append its path to CONFIGS list,
or this test auto-discovers conf/{exp_name}/*.yaml.
"""
import glob
import pytest
from omegaconf import OmegaConf

REQUIRED_KEYS = ["lr", "trainer", "model"]

# 固定テンプレート
TEMPLATE_CONFIGS = [
    "conf/{base_template_1}.yaml",
    "conf/{base_template_2}.yaml",
]

# Claudeが生成したconfを自動検出 (conf/exp_*/配下)
GENERATED_CONFIGS = sorted(glob.glob("conf/exp_*/*.yaml"))

ALL_CONFIGS = TEMPLATE_CONFIGS + GENERATED_CONFIGS


@pytest.mark.parametrize("config_path", ALL_CONFIGS)
def test_config_loads(config_path):
    """YAMLがomegaconfで読めること。"""
    cfg = OmegaConf.load(config_path)
    assert cfg is not None, f"Failed to load {config_path}"


@pytest.mark.parametrize("config_path", GENERATED_CONFIGS)
def test_required_keys_present(config_path):
    """生成configに最低限必要なキーが存在すること。"""
    cfg = OmegaConf.load(config_path)
    cfg_dict = OmegaConf.to_container(cfg, resolve=False)
    for key in ["lr"]:
        assert key in cfg_dict, f"Missing required key '{key}' in {config_path}"
```

### `tests/test_search_plan.py`

生成configの値がsearch_plan.mdの許容範囲内かを確認。

```python
"""
Search space validation tests. GPU-free. Runs in GitHub Actions CI.
Values must stay within the ranges defined in prompts/search_plan.md.
"""
import glob
import pytest
from omegaconf import OmegaConf

# 許容値 (prompts/search_plan.md と同期させること)
ALLOWED_LRS = {1e-5, 3e-5, 5e-5, 1e-4, 2e-4}
ALLOWED_MAX_EPOCHS = {1, 2, 3, 4, 6}
ALLOWED_WARMUP_STEPS = {1000, 3000, 6000, 10000}

GENERATED_CONFIGS = sorted(glob.glob("conf/exp_*/*.yaml"))


def _get(cfg_dict, dotted_key, default=None):
    keys = dotted_key.split(".")
    cur = cfg_dict
    for k in keys:
        if not isinstance(cur, dict) or k not in cur:
            return default
        cur = cur[k]
    return cur


@pytest.mark.parametrize("config_path", GENERATED_CONFIGS)
def test_lr_in_search_plan(config_path):
    cfg = OmegaConf.to_container(OmegaConf.load(config_path), resolve=False)
    lr = _get(cfg, "lr")
    if lr is None:
        pytest.skip("lr not set (may inherit from default)")
    assert float(lr) in ALLOWED_LRS, \
        f"{config_path}: lr={lr} not in {ALLOWED_LRS}"


@pytest.mark.parametrize("config_path", GENERATED_CONFIGS)
def test_max_epochs_in_search_plan(config_path):
    cfg = OmegaConf.to_container(OmegaConf.load(config_path), resolve=False)
    max_epochs = _get(cfg, "trainer.max_epochs")
    if max_epochs is None:
        pytest.skip("trainer.max_epochs not set")
    assert int(max_epochs) in ALLOWED_MAX_EPOCHS, \
        f"{config_path}: trainer.max_epochs={max_epochs} not in {ALLOWED_MAX_EPOCHS}"
```

---

## Claude へのプロンプト出力フォーマット指示

`build_system_prompt()` で Claude に以下を守らせる。**これが一番重要**。

ファイルを書く際は必ず `<file path="...">...</file>` タグを使わせる：

```
When creating or modifying files, output them in this exact format:

<file path="conf/exp_20260429_123456/config_0.yaml">
defaults:
  - ../../base_template

lr: 5e-5
...
</file>

<file path="array_conf/exp_20260429_123456/array.txt">
conf/exp_20260429_123456/config_0.yaml
conf/exp_20260429_123456/config_1.yaml
</file>

<file path=".autoresearch/codex_summary.md">
# Wave Summary
...
</file>

<file path=".autoresearch/next_exp_name.txt">exp_20260429_123456</file>
```

これにより `apply_file_operations()` が正規表現でパースして安全にファイルを書ける。

---

## 実装チェックリスト

### Phase 1: テスト基盤 (GitHub Actions CIの土台)
- [ ] `tests/test_config_load.py` を作成
- [ ] `tests/test_search_plan.py` を作成
- [ ] `.github/workflows/ci.yml` を作成
- [ ] PRを作って CIが動くか確認

### Phase 2: Claude API ドライバー
- [ ] `src/bin/autoresearch_driver.py` を作成
- [ ] `prompts/prompt.txt` に `<file path="...">` 出力フォーマット指示を追記
- [ ] `prompts/followup.txt` に同様に追記
- [ ] `secrets.ANTHROPIC_API_KEY` を GitHub Actions secrets に登録
- [ ] `.github/workflows/autoresearch.yml` を作成
- [ ] 手動でworkflowを起動してClaude がファイルを生成するか確認

### Phase 3: Cluster Watcher
- [ ] `scripts/collect_metrics.py` を作成
  - `experiments.csv` の `wer`/`cer` フィールドを `src/experiments_csv.py` の `FIELDS` に追加
- [ ] `scripts/watcher.py` を作成
- [ ] `scripts/check_and_submit.slurm` を作成
- [ ] `.autoresearch/watcher_state.json` を手動で作成して動作確認
- [ ] 実際のarray jobで end-to-end テスト

### Phase 4: 統合テスト
- [ ] 実験投入 → watcher が完了検知 → git push → GitHub Actions → Claude → PR → auto-merge → watcher が pull → 次の実験投入
- [ ] Slack 通知が各ステップで届くか確認

---

## 注意点・既知の考慮事項

### git push の競合
array job が複数タスク並列で動いても、git push は watcher が array 完了後に **1回だけ** 行う。個々のタスクは push しない。

### `experiments.csv` の `wer`/`cer` フィールド
現在の `src/experiments_csv.py` の `FIELDS` リストに `wer`, `cer` がない。
`collect_metrics.py` が追記するか、`FIELDS` に追加して `run-array.sh` 側でも対応するか決める必要がある。
**推奨**: `FIELDS` に追加し、`run-array.sh` が infer stage 完了後に `experiments_csv.py --mode finish` で書き込む。

### GitHub Actions の secrets
- `ANTHROPIC_API_KEY`: Claude API key
- `SLACK_WEBHOOK_URL`: Slack通知用
- `GITHUB_TOKEN`: PR作成用 (Actions では自動提供)

### watcher_state.json の初期化
ループを最初に起動するには以下を手動で作って `sbatch scripts/check_and_submit.slurm` する：
```json
{
  "phase": "EXPERIMENT_RUNNING",
  "array_job_id": "17915098",
  "exp_name": "exp_smoke3",
  "next_exp_name": "",
  "last_main_sha": "",
  "submitted_at": "2026-04-29T00:00:00-05:00"
}
```

### Claude のモデル選択
- 推奨: `claude-opus-4-7`（最高品質）
- コスト削減したい場合: `claude-sonnet-4-6`
- config生成は複雑な推論を要するのでOpusを推奨
