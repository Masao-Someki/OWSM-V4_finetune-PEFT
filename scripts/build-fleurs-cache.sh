#!/bin/bash
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=32G
#SBATCH --time=6:00:00
# SBATCH -p gpuA40x4,gpuA100x4,gpuA40x4-preempt,gpuA100x4-preempt,gpuA40x4-interactive,gpuA100x4-interactive
#SBATCH -p cpu
#SBATCH --account bbjs-delta-cpu
# SBATCH --gres=gpu:1
#SBATCH --output=logs/%x/%A_%a.log
#SBATCH --error=logs/%x/%A_%a.log
set -euo pipefail

REPO_ROOT="$(pwd)"
SCRIPT_DIR="${REPO_ROOT}/scripts"

splits="train valid test"
hf_repo="google/fleurs"
hf_subsets_train="all"
hf_subsets_valid="all"
hf_subsets_test="all"
cache_dir="${REPO_ROOT}/cache/fleurs"
max_samples_per_subset_train="null"
max_samples_per_subset_valid="50"
max_samples_per_subset_test="null"
ratio="1.0"
seed="2024"
trust_remote_code="true"

if [ ! -f "${SCRIPT_DIR}/parse_options.sh" ]; then
  echo "[ERROR] parse_options.sh not found under: ${SCRIPT_DIR}"
  echo "        Run this script from repository root."
  exit 1
fi
if [ ! -f "${SCRIPT_DIR}/path.sh" ]; then
  echo "[ERROR] path.sh not found under: ${SCRIPT_DIR}"
  echo "        Run this script from repository root."
  exit 1
fi

. "${SCRIPT_DIR}/parse_options.sh"
. "${SCRIPT_DIR}/path.sh"

export splits
export hf_repo
export hf_subsets_train
export hf_subsets_valid
export hf_subsets_test
export cache_dir
export max_samples_per_subset_train
export max_samples_per_subset_valid
export max_samples_per_subset_test
export ratio
export seed
export trust_remote_code

echo "[INFO] Build FLEURS cache"
echo "[INFO] repo=${hf_repo} cache_dir=${cache_dir}"
echo "[INFO] subsets_train=${hf_subsets_train} subsets_valid=${hf_subsets_valid} subsets_test=${hf_subsets_test}"
echo "[INFO] splits=${splits}"

python - <<'PY'
import os
from src.data.dataset import FleursDataset

def _as_none_or_int(v: str):
    if v in ("null", "None", ""):
        return None
    return int(v)

def _resolve_subsets(raw: str):
    s = raw.strip()
    if s == "all":
        return "all"
    if "," in s:
        return [x.strip() for x in s.split(",") if x.strip()]
    return s

split_map = {"train": "train", "valid": "validation", "validation": "validation", "test": "test"}
raw_splits = os.environ["splits"].split()

for raw in raw_splits:
    key = raw.strip().lower()
    if key not in split_map:
        raise ValueError(f"Unsupported split: {raw}")
    split = split_map[key]
    if split == "train":
        max_samples = _as_none_or_int(os.environ["max_samples_per_subset_train"])
        subsets = _resolve_subsets(os.environ["hf_subsets_train"])
    elif split == "validation":
        max_samples = _as_none_or_int(os.environ["max_samples_per_subset_valid"])
        subsets = _resolve_subsets(os.environ["hf_subsets_valid"])
    else:
        max_samples = _as_none_or_int(os.environ["max_samples_per_subset_test"])
        subsets = _resolve_subsets(os.environ["hf_subsets_test"])

    print(f"[INFO] Warming cache for split={split} subsets={subsets} max_samples_per_subset={max_samples}")
    ds = FleursDataset(
        split=split,
        hf_repo=os.environ["hf_repo"],
        hf_subsets=subsets,
        ratio=float(os.environ["ratio"]),
        max_samples_per_subset=max_samples,
        lang_sym_mode="from_subset",
        cache_dir=os.environ["cache_dir"],
        shuffle=True,
        seed=int(os.environ["seed"]),
        trust_remote_code=(os.environ["trust_remote_code"].lower() == "true"),
        use_cache=True,
    )
    print(f"[INFO] split={split} num_examples={len(ds)}")
PY

echo "[INFO] Done."
