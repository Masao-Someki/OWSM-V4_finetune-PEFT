# OWSM PEFT Autoresearch

## 概要

OWSM (OpenWhisper-style Speech Model) の PEFT 手法とハイパーパラメータを自動探索するプロジェクト。
Delta GPU クラスター上で Slurm を使い、ESPnet3 フレームワークで実験を回す。

## 目標

FLEURS データセットでの ASR 性能 (WER/CER) を最大化する最良の PEFT 手法・ハイパーパラメータを自動で見つける。

---

## アーキテクチャ

```
Cluster
  run_experiment.slurm (array job)
    ↓ 完了
  .autoresearch/check_and_submit.slurm (watcher, self-resubmit 型)
    ↓ sacct で全タスク完了確認
    ↓ .autoresearch/collect_metrics.py → .autoresearch/experiments.csv + .autoresearch/ 更新
    ↓ git push → origin/main

GitHub Actions (.github/workflows/autoresearch.yml)
  push trigger (.autoresearch/latest_status.json 等の変化)
    ↓ .autoresearch/autoresearch_driver.py
    ↓ Claude API (claude-opus-4-7) が次の wave config を提案
    ↓ conf/{next_exp_name}/ + .autoresearch/array_conf/{next_exp_name}/array.txt を生成
    ↓ PR 作成 → CI (.github/workflows/ci.yml)
    ↓ CI pass → auto-merge (squash)

Cluster watcher (WAITING_FOR_PR_MERGE フェーズ)
  git fetch → 新コミット検知
    ↓ git pull
    ↓ .autoresearch/next_exp_name.txt を読む
    ↓ sbatch scripts/submit-array-with-debug.sh (debug gate 付き)
    ↓ watcher_state.json を EXPERIMENT_RUNNING に更新して resubmit
```

**役割分担**:
- GitHub = planner / memory / CI
- Cluster = executor
- `.autoresearch/check_and_submit.slurm` (self-resubmit) = watcher / update detector
- `.autoresearch/` = state interface

---

## ファイル構成

### 新アーキテクチャの主要ファイル

| ファイル | 役割 |
|---|---|
| `.autoresearch/check_and_submit.slurm` | watcher Slurm job (self-resubmit, CPU partition) |
| `.autoresearch/watcher.py` | watcher メインロジック (state machine) |
| `.autoresearch/collect_metrics.py` | metrics.json 収集 → experiments.csv 更新 |
| `.autoresearch/autoresearch_driver.py` | GitHub Actions 上で Claude API を呼ぶ |
| `.autoresearch/prompts/` | Claude へのプロンプト群 |
| `.autoresearch/array_conf/` | array job の config リスト |
| `.autoresearch/experiments.csv` | 全実験のメタデータ (fcntl locked) |
| `.autoresearch/results/` | git 管理する実験結果 (metrics/logs のみ、ckpt 除く) |
| `.autoresearch/notes/` | 知見ログ・チェックリスト |
| `.autoresearch/keys/` | API キーファイル (gitignore 対象) |
| `.autoresearch/load-keys.sh` | API キーを環境変数にロード |
| `.autoresearch/submit-array-with-debug.sh` | debug gate 付き Slurm array 投入 |
| `.autoresearch/submit-array.sh` | Slurm array 直接投入 (手動用) |
| `.autoresearch/submit-local-with-debug.sh` | ローカル実行 (debug gate 付き) |
| `.github/workflows/autoresearch.yml` | push trigger → Claude → PR 作成 |
| `.github/workflows/ci.yml` | PR trigger → config/search_plan テスト |
| `tests/test_config_load.py` | config YAML load テスト (GPU 不要) |
| `tests/test_search_plan.py` | search space 制約テスト (GPU 不要) |

### 既存の重要ファイル (変更なし)

| ファイル | 役割 |
|---|---|
| `scripts/run-array.sh` | 個別タスクの実行スクリプト |
| `scripts/submit-array-with-debug.sh` | debug gate + Slurm array 投入 |
| `scripts/submit-local-with-debug.sh` | local 実行 |
| `src/experiments_csv.py` | 実験メタデータ CSV 記録 (fcntl locking) |
| `src/slack_notify.py` | Slack 通知 |
| `run.py` | ESPnet3 エントリーポイント |

### State Interface (`.autoresearch/`)

| ファイル | 書き手 | 読み手 |
|---|---|---|
| `watcher_state.json` | watcher | watcher |
| `latest_status.json` | watcher (collect_metrics後) | GitHub Actions |
| `latest_metrics.json` | collect_metrics.py | GitHub Actions |
| `latest_error.log` | collect_metrics.py | GitHub Actions |
| `next_goal.md` | watcher | GitHub Actions (Claude prompt) |
| `codex_summary.md` | Claude (GitHub Actions) | 人間 |
| `next_exp_name.txt` | Claude (GitHub Actions) | watcher (git pull後) |
| `next_branch.txt` | autoresearch_driver.py | autoresearch.yml (PR作成) |
| `stop.json` | Claude | watcher / 人間 |

---

## Watcher の状態機械

`watcher_state.json` の `phase` フィールドで管理:

- **`EXPERIMENT_RUNNING`**: array job 完了を5分ごとに sacct でポーリング
  → 全タスク terminal → metrics 収集 → git push → `WAITING_FOR_PR_MERGE`
- **`WAITING_FOR_PR_MERGE`**: GitHub main の更新を5分ごとに git fetch でポーリング
  → 新コミット → git pull → sbatch 次の実験 → `EXPERIMENT_RUNNING`
- **`IDLE`**: 何もしない (手動起動が必要)

### ループ開始手順

```bash
# 1. 最初の実験を手動で投入
bash .autoresearch/submit-array-with-debug.sh exp_smoke3 0-2 .autoresearch/array_conf/exp_smoke3/array.txt 0

# 2. watcher_state.json を更新
cat > .autoresearch/watcher_state.json <<EOF
{
  "phase": "EXPERIMENT_RUNNING",
  "array_job_id": "<sbatch で返ってきた job id>",
  "exp_name": "exp_smoke3",
  "last_main_sha": ""
}
EOF

# 3. watcher を起動
sbatch .autoresearch/check_and_submit.slurm
```

---

## GitHub Actions 設定

### 必要な Secrets

| Secret | 説明 |
|---|---|
| `ANTHROPIC_API_KEY` | Claude API キー |
| `SLACK_WEBHOOK_URL` | Slack 通知用 (任意) |
| `GITHUB_TOKEN` | PR 作成用 (Actions が自動提供) |

### Branch Protection (auto-merge に必要)

- main ブランチに `Require status checks to pass before merging` を設定
- `Config Validation CI` ジョブを required status check に追加
- `Allow auto-merge` を有効化

---

## テスト

```bash
# GPU 不要、ローカルでも実行可能
pytest tests/ -v --no-header
```

- `tests/test_config_load.py`: YAML が omegaconf で読めること、必須キー存在確認
- `tests/test_search_plan.py`: lr/peft_type/max_epochs/warmup_steps が search_plan.md の範囲内

---

## 探索空間

詳細は `.autoresearch/prompts/search_plan.md` を参照。

1. **PEFT ファミリー**: lora / espnet_lora / adalora / randlora / vblora / delora
2. **LR**: 1e-5, 3e-5, 5e-5, 1e-4, 2e-4
3. **Epoch**: 1, 2, 4, 6
4. **Warmup steps**: 1000, 3000, 6000, 10000
5. **データ拡張**: dataset.ratio, time_apply_prob, text_prev_apply_prob

---

## 環境・インフラ

- クラスター: Delta GPU (account: `bbjs-delta-gpu`, CPU: `bbjs-delta-cpu`)
- ジョブ管理: Slurm
- パッケージ管理: pixi
- Python: 3.11, torch 2.8.0
- フレームワーク: ESPnet3 (fork: `Masao-Someki/espnet`, branch `espnet3/fix_collect_stats`)
- モデル: `espnet/owsm_ctc_v4_1B` (メモリ要求: 32G 以上)
- 実験追跡: WandB (`owsm-peft-autoresearch` project)
- 通知: Slack webhook

---

## Claude / GitHub Actions への指示方針

- `.autoresearch/` を最初に読む
- 最小変更のみ (`conf/exp_*/`, `.autoresearch/array_conf/`, `.autoresearch/notes/`, `.autoresearch/`, `tests/` のみ)
- `exp/`, `dump/`, `data/`, `secrets/`, `.env`, `.autoresearch/keys/` は編集不可
- `conf/default.yaml` 等のテンプレートは編集不可
- 変更は `<file path="...">...</file>` 形式で出力
- 直接 main へ push せず、PR 経由

---

## 現状の課題

- C0 (smoke test): Slurm controller 接続エラーで未完 → 再試行待ち
- C6 (安定性): OOM kill (exit 137) → メモリ要求を 32G に修正済み
- C1〜C5: 実験データなし
