#!/bin/bash
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=32G
#SBATCH --time=24:00:00
#SBATCH -p gpuA40x4,gpuA100x4
#SBATCH --account bbjs-delta-gpu
#SBATCH --gres=gpu:1
#SBATCH --output=logs/%x_%j.out

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
cd "${REPO_ROOT}"

# config_path=conf/train.yaml
config_path=conf/owsm_peft_lora_basic.yaml

. "${SCRIPT_DIR}/parse_options.sh"
. "${SCRIPT_DIR}/path.sh"

python run.py \
    --stages train \
    --training_config ${config_path}
