#!/bin/bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
cd "${REPO_ROOT}"

notify_slack_array_submitted() {
  local exp_name="$1"
  local array_job_id="$2"
  local array_range="$3"
  local config_list="$4"
  local config_count="$5"
  if [ -z "${SLACK_WEBHOOK_URL:-}" ]; then
    return 0
  fi
  python - <<PY
from src.slack_notify import format_status_message, post_slack_message
post_slack_message(
    text=format_status_message(
        title="Array Submitted",
        body_lines=[
            "- exp_name: \`${exp_name}\`",
            "- array_job_id: \`${array_job_id}\`",
            "- array_range: \`${array_range}\`",
            "- config_count: \`${config_count}\`",
            "- config_list: \`${config_list}\`",
        ],
    )
)
PY
}

exp_name="${1:-}"
array_range="${2:-}"
config_list="${3:-}"
array_base_index="${4:-0}"

if [ -z "${exp_name}" ] || [ -z "${array_range}" ] || [ -z "${config_list}" ]; then
  echo "Usage: $0 <exp_name> <array_range> <config_list> [array_base_index]"
  echo "Example: $0 exp1 0-5 array_conf/exp1/array_example.txt 0"
  exit 1
fi

if [ ! -f "${config_list}" ]; then
  echo "[ERROR] config_list not found: ${config_list}"
  exit 1
fi

# Optional overrides (use --config style args via parse_options.sh)
stages="train"
infer_config=""
measure_config=""
experiment_comment=""
experiments_csv=".autoresearch/experiments.csv"
debug_task_id=""
max_configs=10

debug_time="01:00:00"
debug_mem="32G"
debug_partition="gpuA40x4,gpuA100x4,gpuA40x4-preempt,gpuA100x4-preempt,gpuA40x4-interactive,gpuA100x4-interactive"
debug_account="bbjs-delta-gpu"
debug_gres="gpu:1"
debug_cpus=4

# Debug-run should be a quick smoke test before array submission.
quick_train=true
quick_fast_dev_run=10
quick_max_steps=100
quick_max_epochs=3

. "${REPO_ROOT}/scripts/parse_options.sh"

if [ -z "${debug_task_id}" ]; then
  debug_task_id="${array_base_index}"
fi

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

range_main="${array_range%%\%*}"
range_suffix=""
if [[ "${array_range}" == *%* ]]; then
  range_suffix="%${array_range#*%}"
fi
if [[ "${range_main}" =~ ^([0-9]+)-([0-9]+)$ ]]; then
  req_start="${BASH_REMATCH[1]}"
  req_end="${BASH_REMATCH[2]}"
elif [[ "${range_main}" =~ ^([0-9]+)$ ]]; then
  req_start="${BASH_REMATCH[1]}"
  req_end="${BASH_REMATCH[1]}"
else
  echo "[ERROR] unsupported array_range format: ${array_range}"
  echo "        expected forms like 0-9, 3, 0-99%8"
  exit 1
fi

available_start="${array_base_index}"
available_end=$((array_base_index + ${#effective_configs[@]} - 1))
effective_start="${req_start}"
effective_end="${req_end}"
if [ "${effective_start}" -lt "${available_start}" ]; then
  effective_start="${available_start}"
fi
if [ "${effective_end}" -gt "${available_end}" ]; then
  effective_end="${available_end}"
fi
if [ "${effective_end}" -lt "${effective_start}" ]; then
  echo "[ERROR] effective array range is empty after applying limits."
  echo "        requested=${array_range}, available=${available_start}-${available_end}"
  exit 1
fi
effective_array_range="${effective_start}-${effective_end}${range_suffix}"

if [ "${debug_task_id}" -lt "${available_start}" ] || [ "${debug_task_id}" -gt "${available_end}" ]; then
  debug_task_id="${available_start}"
fi

debug_comment="${experiment_comment} [debug-gate]"
array_comment="${experiment_comment} [array-run]"

echo "[INFO] =================================================="
echo "[INFO] Step 1/2: submit debug job (must pass before array)"
echo "[INFO] exp_name=${exp_name}"
echo "[INFO] debug_task_id=${debug_task_id}"
echo "[INFO] config_list=${limited_config_list}"
echo "[INFO] resources: time=${debug_time}, mem=${debug_mem}, gres=${debug_gres}, partition=${debug_partition}"
echo "[INFO] effective_array_range=${effective_array_range}"
echo "[INFO] =================================================="

debug_submit=(
  sbatch
  --wait
  --job-name "${exp_name}_debug"
  --nodes 1
  --ntasks-per-node 1
  --cpus-per-task "${debug_cpus}"
  --mem "${debug_mem}"
  --time "${debug_time}"
  --partition "${debug_partition}"
  --account "${debug_account}"
  --gres "${debug_gres}"
  --output "logs/${exp_name}/debug_%j.log"
  --error "logs/${exp_name}/debug_%j.log"
  "${REPO_ROOT}/scripts/run-array.sh"
  --exp_name "${exp_name}"
  --config_list "${limited_config_list}"
  --array_base_index "${array_base_index}"
  --task_id "${debug_task_id}"
  --stages "${stages}"
  --experiment_comment "${debug_comment}"
  --experiments_csv "${experiments_csv}"
  --quick_train "${quick_train}"
  --quick_fast_dev_run "${quick_fast_dev_run}"
  --quick_max_steps "${quick_max_steps}"
  --quick_max_epochs "${quick_max_epochs}"
)
if [ -n "${infer_config}" ]; then
  debug_submit+=(--infer_config "${infer_config}")
fi
if [ -n "${measure_config}" ]; then
  debug_submit+=(--measure_config "${measure_config}")
fi

set +e
"${debug_submit[@]}"
debug_rc=$?
set -e

if [ "${debug_rc}" -ne 0 ]; then
  echo "[ERROR] Debug job failed (exit=${debug_rc}). Array submission is skipped."
  exit "${debug_rc}"
fi

echo "[INFO] Debug job passed."
echo "[INFO] =================================================="
echo "[INFO] Step 2/2: submit array job"
echo "[INFO] array_range=${effective_array_range}"
echo "[INFO] =================================================="

array_submit=(
  sbatch
  --job-name "${exp_name}"
  --array "${effective_array_range}"
  --output "logs/${exp_name}/%A_%a.log"
  --error "logs/${exp_name}/%A_%a.log"
  "${REPO_ROOT}/scripts/run-array.sh"
  --exp_name "${exp_name}"
  --config_list "${limited_config_list}"
  --array_base_index "${array_base_index}"
  --stages "${stages}"
  --experiment_comment "${array_comment}"
  --experiments_csv "${experiments_csv}"
)
if [ -n "${infer_config}" ]; then
  array_submit+=(--infer_config "${infer_config}")
fi
if [ -n "${measure_config}" ]; then
  array_submit+=(--measure_config "${measure_config}")
fi

submit_out="$("${array_submit[@]}")"
echo "${submit_out}"

array_job_id="$(echo "${submit_out}" | awk '{print $4}')"
if [ -n "${array_job_id}" ]; then
  cp -f "${limited_config_list}" ".autoresearch/array_conf/${exp_name}/array_${array_job_id}.txt"
  echo "[INFO] saved array config list: .autoresearch/array_conf/${exp_name}/array_${array_job_id}.txt"
  notify_slack_array_submitted "${exp_name}" "${array_job_id}" "${effective_array_range}" "${limited_config_list}" "${#effective_configs[@]}"
fi
