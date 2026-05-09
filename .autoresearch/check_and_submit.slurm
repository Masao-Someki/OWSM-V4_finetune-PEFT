#!/bin/bash
#SBATCH --job-name=autoresearch_watcher
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=1G
#SBATCH --time=0:5:00
#SBATCH --partition=cpu
#SBATCH --account=bbjs-delta-cpu
#SBATCH --output=logs/watcher/%j.log
#SBATCH --error=logs/watcher/%j.log

# set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

# Even when launched via sbatch, run from the original repository root.
if [ -n "${SLURM_SUBMIT_DIR:-}" ] && [ -d "${SLURM_SUBMIT_DIR}/scripts" ]; then
  REPO_ROOT="${SLURM_SUBMIT_DIR}"
fi

# If SCRIPT_DIR points to .autoresearch/, adjust REPO_ROOT to its parent.
if [ "$(basename "${SCRIPT_DIR}")" = ".autoresearch" ]; then
  REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
fi

cd "${REPO_ROOT}"

mkdir -p logs/watcher

# Use the pixi environment.
. scripts/path.sh

# Load environment variables if key files are available.
if [ -f .autoresearch/load-keys.sh ]; then
  . .autoresearch/load-keys.sh
fi

echo "[INFO] watcher started: $(date -Iseconds)"
echo "[INFO] REPO_ROOT=${REPO_ROOT}"
echo "[INFO] SLURM_JOB_ID=${SLURM_JOB_ID:-na}"

python .autoresearch/watcher.py

echo "[INFO] watcher finished: $(date -Iseconds)"
