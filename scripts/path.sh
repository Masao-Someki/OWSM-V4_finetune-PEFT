#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

# export HF_HOME=$(pwd)/hub
export HF_HOME=/work/nvme/bbjs/dyang10/hf_cache
export LD_LIBRARY_PATH="/u/someki1/.pixi/envs/ffmpeg/lib:${LD_LIBRARY_PATH}"
export LD_LIBRARY_PATH="/u/someki1/.pixi/envs/icu/lib:${LD_LIBRARY_PATH}"
export LD_LIBRARY_PATH="/u/someki1/.pixi/envs/readline/lib:${LD_LIBRARY_PATH}"
export PYTHONPATH="${REPO_ROOT}:${PYTHONPATH:-}"

export ESPNET_ROOT=/work/nvme/bbjs/dyang10/espnet
export PYTHONPATH="${ESPNET_ROOT}:${REPO_ROOT}:${PYTHONPATH:-}"

export OWSM_ROOT=/work/nvme/bbjs/dyang10/OWSM/OWSM-V4_finetune-PEFT
export ESPNET_MODEL_ZOO_CACHE="${REPO_ROOT}/.cache/espnet_model_zoo"
mkdir -p "${ESPNET_MODEL_ZOO_CACHE}"

# activate python
if [ -z "${PIXI_ENVIRONMENT_NAME:-}" ]; then
  eval "$(pixi shell-hook)"
fi

. "${SCRIPT_DIR}/load-keys.sh"

if [ -z "${WANDB_ENTITY:-}" ]; then
  export WANDB_ENTITY="masao-someki"
fi
if [ -z "${WANDB_PROJECT:-}" ]; then
  export WANDB_PROJECT="owsm-peft-autoresearch"
fi

show_key_status() {
  local keys=(
    WANDB_API_KEY
    WANDB_ENTITY
    WANDB_PROJECT
    SLACK_WEBHOOK_URL
    HF_TOKEN
    OPENAI_API_KEY
  )
  local k=""
  for k in "${keys[@]}"; do
    if [ -n "${!k:-}" ]; then
      echo "${k}=SET"
    else
      echo "${k}=EMPTY"
    fi
  done
}

# Optional status print:
#   . scripts/path.sh --check-keys
if [ "${1:-}" = "--check-keys" ]; then
  show_key_status
fi
