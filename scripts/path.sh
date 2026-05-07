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

if [ -f "${SCRIPT_DIR}/load-keys.sh" ]; then
  . "${SCRIPT_DIR}/load-keys.sh"
else
  echo "[WARN] ${SCRIPT_DIR}/load-keys.sh not found; continuing without it."
fi

init_git_ssh() {
  if ! command -v ssh-agent >/dev/null 2>&1 || ! command -v ssh-add >/dev/null 2>&1; then
    echo "[WARN] ssh-agent/ssh-add not found; skipping git SSH initialization."
    return 0
  fi

  if [ -z "${SSH_AUTH_SOCK:-}" ]; then
    eval "$(ssh-agent -s)" >/dev/null
  fi

  # Add configured key first, then common defaults if no key is loaded.
  if [ -n "${GIT_SSH_KEY_PATH:-}" ] && [ -f "${GIT_SSH_KEY_PATH}" ]; then
    ssh-add "${GIT_SSH_KEY_PATH}" >/dev/null 2>&1 || true
  fi

  if ! ssh-add -l >/dev/null 2>&1; then
    if [ -f "${HOME}/.ssh/id_ed25519" ]; then
      ssh-add "${HOME}/.ssh/id_ed25519" >/dev/null 2>&1 || true
    elif [ -f "${HOME}/.ssh/id_rsa" ]; then
      ssh-add "${HOME}/.ssh/id_rsa" >/dev/null 2>&1 || true
    fi
  fi

  mkdir -p "${HOME}/.ssh"
  chmod 700 "${HOME}/.ssh"
  if [ ! -f "${HOME}/.ssh/known_hosts" ] || ! grep -q "github.com" "${HOME}/.ssh/known_hosts"; then
    ssh-keyscan -H github.com >> "${HOME}/.ssh/known_hosts" 2>/dev/null || true
    chmod 600 "${HOME}/.ssh/known_hosts" 2>/dev/null || true
  fi
}

init_git_ssh

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
