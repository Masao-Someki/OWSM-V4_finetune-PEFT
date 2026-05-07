#!/usr/bin/env bash

# Load API keys from repository-local keys/ directory.
# Expected to be sourced by other scripts.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
KEYS_DIR="${REPO_ROOT}/.autoresearch/keys"

_read_key_file() {
  local path="$1"
  if [ -f "${path}" ]; then
    # Use first line and strip CR to avoid newline contamination.
    head -n 1 "${path}" | tr -d '\r'
    return 0
  fi
  return 1
}

_export_if_missing() {
  local var_name="$1"
  local file_path="$2"
  if [ -z "${!var_name:-}" ]; then
    local v=""
    if v="$(_read_key_file "${file_path}")"; then
      if [ -n "${v}" ]; then
        export "${var_name}=${v}"
      fi
    fi
  fi
}

# Preferred keys/ paths
_export_if_missing "WANDB_API_KEY" "${KEYS_DIR}/wandb.key"
_export_if_missing "WANDB_ENTITY" "${KEYS_DIR}/wandb_entity.key"
_export_if_missing "WANDB_PROJECT" "${KEYS_DIR}/wandb_project.key"
_export_if_missing "SLACK_WEBHOOK_URL" "${KEYS_DIR}/slack_webhook.key"
_export_if_missing "OPENAI_API_KEY" "${KEYS_DIR}/openai_api.key"
_export_if_missing "OPENAI_API_KEY" "${KEYS_DIR}/openai.key"
_export_if_missing "OPENAI_API_KEY" "${KEYS_DIR}/OPENAI_API_KEY.key"
_export_if_missing "ANTHROPIC_API_KEY" "${KEYS_DIR}/anthropic_api.key"
_export_if_missing "ANTHROPIC_API_KEY" "${KEYS_DIR}/anthropic.key"
_export_if_missing "HF_TOKEN" "${KEYS_DIR}/hf_token.key"

# Backward compatibility with older root-level files.
_export_if_missing "WANDB_API_KEY" "${REPO_ROOT}/wandb.key"
_export_if_missing "WANDB_ENTITY" "${REPO_ROOT}/wandb_entity.key"
_export_if_missing "WANDB_ENTITY" "${REPO_ROOT}/wandb_entry.key"
