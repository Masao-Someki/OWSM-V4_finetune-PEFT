#!/bin/bash
#SBATCH --job-name=autoresearch_watcher
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=2
#SBATCH --mem=4G
#SBATCH --time=0:10:00
#SBATCH --partition=cpu
#SBATCH --account=bbjs-delta-cpu
#SBATCH --output=logs/watcher/%j.log
#SBATCH --error=logs/watcher/%j.log

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

# sbatch 経由でも元のリポジトリから実行する
if [ -n "${SLURM_SUBMIT_DIR:-}" ] && [ -d "${SLURM_SUBMIT_DIR}/scripts" ]; then
  REPO_ROOT="${SLURM_SUBMIT_DIR}"
fi

# SCRIPT_DIR が .autoresearch/ を指している場合、REPO_ROOT を1つ上に修正
if [ "$(basename "${SCRIPT_DIR}")" = ".autoresearch" ]; then
  REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
fi

cd "${REPO_ROOT}"

mkdir -p logs/watcher

# pixi 環境を使う
. scripts/path.sh

# 環境変数ロード (keys/ 以下にある場合)
if [ -f .autoresearch/load-keys.sh ]; then
  . .autoresearch/load-keys.sh
fi

echo "[INFO] watcher started: $(date -Iseconds)"
echo "[INFO] REPO_ROOT=${REPO_ROOT}"
echo "[INFO] SLURM_JOB_ID=${SLURM_JOB_ID:-na}"

python .autoresearch/watcher.py

echo "[INFO] watcher finished: $(date -Iseconds)"
