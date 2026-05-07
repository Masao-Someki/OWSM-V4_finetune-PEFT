#!/bin/bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
cd "${REPO_ROOT}"

exp_name="${1:-}"
config_list="${2:-}"
array_base_index="${3:-0}"

if [ -z "${exp_name}" ] || [ -z "${config_list}" ]; then
  echo "Usage: $0 <exp_name> <config_list> [array_base_index]"
  echo "Example: $0 local_exp1 array_conf/exp1/array_example.txt 0"
  exit 1
fi

if [ ! -f "${config_list}" ]; then
  echo "[ERROR] config_list not found: ${config_list}"
  exit 1
fi

stages="train infer measure"
infer_config="conf/inference.yaml"
measure_config="conf/metrics.yaml"
experiment_comment=""
experiments_csv=".autoresearch/experiments.csv"
local_task_id=""
max_configs=10

fast_dev_run=10
fast_dev_max_steps=100
fast_dev_max_epochs=2

quick_train=true

. "${REPO_ROOT}/scripts/parse_options.sh"

mkdir -p "logs/${exp_name}" ".autoresearch/array_conf/${exp_name}" "conf/${exp_name}/generated" "exp/${exp_name}"

mapfile -t all_configs < <(grep -v '^[[:space:]]*$' "${config_list}" | grep -v '^[[:space:]]*#')
if [ "${#all_configs[@]}" -eq 0 ]; then
  echo "[ERROR] no usable config entries in: ${config_list}"
  exit 1
fi

limited_config_list="${config_list}"
if [ "${max_configs}" -gt 0 ] && [ "${#all_configs[@]}" -gt "${max_configs}" ]; then
  limited_config_list=".autoresearch/array_conf/${exp_name}/array_limited_${exp_name}_$$.txt"
  printf "%s\n" "${all_configs[@]:0:${max_configs}}" > "${limited_config_list}"
  echo "[INFO] max_configs=${max_configs} -> truncated config_list to ${limited_config_list}"
fi

mapfile -t effective_configs < <(grep -v '^[[:space:]]*$' "${limited_config_list}" | grep -v '^[[:space:]]*#')
if [ "${#effective_configs[@]}" -eq 0 ]; then
  echo "[ERROR] no usable config entries after limiting: ${limited_config_list}"
  exit 1
fi

if [ -z "${local_task_id}" ]; then
  local_task_id="${array_base_index}"
fi

index=$((local_task_id - array_base_index))
if [ "${index}" -lt 0 ] || [ "${index}" -ge "${#effective_configs[@]}" ]; then
  echo "[ERROR] local_task_id=${local_task_id} (base=${array_base_index}) is out of range."
  echo "        usable task_id range: ${array_base_index}-$((array_base_index + ${#effective_configs[@]} - 1))"
  exit 1
fi
selected_config="${effective_configs[${index}]}"

echo "[INFO] =================================================="
echo "[INFO] Step 1/2: local fast-dev-run debug"
echo "[INFO] exp_name=${exp_name}"
echo "[INFO] local_task_id=${local_task_id}"
echo "[INFO] selected_config=${selected_config}"
echo "[INFO] fast_dev_run=${fast_dev_run}, max_steps=${fast_dev_max_steps}, max_epochs=${fast_dev_max_epochs}"
echo "[INFO] =================================================="

debug_cmd=(
  "${REPO_ROOT}/scripts/run-array.sh"
  --exp_name "${exp_name}"
  --config_list "${limited_config_list}"
  --array_base_index "${array_base_index}"
  --task_id "${local_task_id}"
  --stages "train"
  --experiment_comment "${experiment_comment} [local-debug]"
  --experiments_csv "${experiments_csv}"
  --quick_train true
  --quick_fast_dev_run "${fast_dev_run}"
  --quick_max_steps "${fast_dev_max_steps}"
  --quick_max_epochs "${fast_dev_max_epochs}"
)
"${debug_cmd[@]}"

echo "[INFO] Debug passed."
echo "[INFO] =================================================="
echo "[INFO] Step 2/2: local run-array sample"
echo "[INFO] stages=${stages}"
echo "[INFO] config_list=${limited_config_list}"
echo "[INFO] =================================================="

run_cmd=(
  "${REPO_ROOT}/scripts/run-array.sh"
  --exp_name "${exp_name}"
  --config_list "${limited_config_list}"
  --array_base_index "${array_base_index}"
  --task_id "${local_task_id}"
  --stages "${stages}"
  --experiment_comment "${experiment_comment}"
  --experiments_csv "${experiments_csv}"
  --quick_train "${quick_train}"
  --quick_fast_dev_run "${fast_dev_run}"
  --quick_max_steps "${fast_dev_max_steps}"
  --quick_max_epochs "${fast_dev_max_epochs}"
)
if [ -n "${infer_config}" ]; then
  run_cmd+=(--infer_config "${infer_config}")
fi
if [ -n "${measure_config}" ]; then
  run_cmd+=(--measure_config "${measure_config}")
fi

"${run_cmd[@]}"
