#!/bin/bash
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=16G
#SBATCH --time=6:00:00
#SBATCH -p gpuA40x4,gpuA100x4
# SBATCH -p cpu
#SBATCH --account bbjs-delta-gpu
# SBATCH --gres=gpu:1
#SBATCH --output=logs/%x/%A_%a.log
#SBATCH --error=logs/%x/%A_%a.log

# set -euo pipefail

SCRIPT_DIR="$(pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

# Under sbatch, this script may run from a spooled copy.
# Prefer the original submit directory when it looks like our repo root.
if [ -n "${SLURM_SUBMIT_DIR:-}" ] && [ -d "${SLURM_SUBMIT_DIR}/scripts" ]; then
  REPO_ROOT="${SLURM_SUBMIT_DIR}"
  SCRIPT_DIR="${REPO_ROOT}/scripts"
fi

# Fallback: if script-local helpers are missing, resolve from cwd/scripts.
if [ ! -f "${SCRIPT_DIR}/parse_options.sh" ] || [ ! -f "${SCRIPT_DIR}/path.sh" ]; then
  if [ -f "$(pwd)/scripts/parse_options.sh" ] && [ -f "$(pwd)/scripts/path.sh" ]; then
    REPO_ROOT="$(pwd)"
    SCRIPT_DIR="${REPO_ROOT}/scripts"
  fi
fi

cd "${REPO_ROOT}"

stages="train"
exp_name=""
config_list=""
array_base_index=0
task_id=""
array_range=""
submit_with_debug=false
max_configs=10
debug_task_id=""
debug_time="01:00:00"
debug_mem="32G"
debug_partition="gpuA40x4,gpuA100x4"
debug_account="bbjs-delta-gpu"
debug_gres="gpu:1"
debug_cpus=4
array_partition="gpuA40x4,gpuA100x4"
array_account="bbjs-delta-gpu"
array_gres="gpu:1"
array_cpus=4
array_mem="32G"
array_time="06:00:00"
keep_runtime_config=true
experiment_comment=""
experiments_csv="experiments.csv"
experiments_csv_lock=".autoresearch/store/experiments.csv.lock"
infer_config=""
measure_config=""
quick_train=false
quick_fast_dev_run=10
quick_max_steps=100
quick_max_epochs=3
quick_num_device=1
quick_num_nodes=1
quick_max_samples_per_subset=10
quick_batch_size=""
quick_batch_bins=""
slack_webhook_url="${SLACK_WEBHOOK_URL:-}"

. "${SCRIPT_DIR}/parse_options.sh"
. "${SCRIPT_DIR}/path.sh"

# Submit mode: run debug gate first, then submit the full array only if debug passes.
if [ "${submit_with_debug}" = "true" ]; then
  if [ -z "${exp_name}" ] || [ -z "${array_range}" ] || [ -z "${config_list}" ]; then
    echo "[ERROR] submit_with_debug=true requires --exp_name, --array_range, and --config_list."
    echo "Example:"
    echo "  bash scripts/run-array.sh --submit_with_debug true --exp_name exp_x --array_range 0-2 --config_list .autoresearch/array_conf/exp_x/array.txt"
    exit 1
  fi
  if [ ! -f "${config_list}" ]; then
    echo "[ERROR] config_list not found: ${config_list}"
    exit 1
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
    exit 1
  fi
  effective_array_range="${effective_start}-${effective_end}${range_suffix}"

  if [ -z "${debug_task_id}" ]; then
    debug_task_id="${array_base_index}"
  fi
  if [ "${debug_task_id}" -lt "${available_start}" ] || [ "${debug_task_id}" -gt "${available_end}" ]; then
    debug_task_id="${available_start}"
  fi

  debug_comment="${experiment_comment} [debug-gate]"
  array_comment="${experiment_comment} [array-run]"

  echo "[INFO] Step 1/2: submit debug job"
  debug_submit=(
    sbatch
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
    --stages "train"
    --experiment_comment "${debug_comment}"
    --experiments_csv "${experiments_csv}"
    --quick_train true
    --quick_fast_dev_run "${quick_fast_dev_run}"
    --quick_max_steps "${quick_max_steps}"
    --quick_max_epochs "${quick_max_epochs}"
  )
  debug_out="$("${debug_submit[@]}")" || exit $?
  echo "${debug_out}"
  debug_job_id="$(echo "${debug_out}" | awk '{print $4}')"
  if [ -z "${debug_job_id}" ]; then
    echo "[ERROR] could not parse debug job id from sbatch output"
    exit 1
  fi

  echo "[INFO] Step 2/2: submit array job (${effective_array_range}) with dependency=afterok:${debug_job_id}"
  submit_out="$(sbatch \
    --job-name "${exp_name}" \
    --array "${effective_array_range}" \
    --dependency "afterok:${debug_job_id}" \
    --cpus-per-task "${array_cpus}" \
    --mem "${array_mem}" \
    --time "${array_time}" \
    --partition "${array_partition}" \
    --account "${array_account}" \
    --gres "${array_gres}" \
    --output "logs/${exp_name}/%A_%a.log" \
    --error "logs/${exp_name}/%A_%a.log" \
    "${REPO_ROOT}/scripts/run-array.sh" \
    --exp_name "${exp_name}" \
    --config_list "${limited_config_list}" \
    --array_base_index "${array_base_index}" \
    --stages "${stages}" \
    --experiment_comment "${array_comment}" \
    --experiments_csv "${experiments_csv}")"
  echo "${submit_out}"
  array_job_id="$(echo "${submit_out}" | awk '{print $4}')"
  if [ -z "${array_job_id}" ]; then
    echo "[ERROR] could not parse array job id from sbatch output"
    exit 1
  fi

  echo "[INFO] Waiting for debug job completion: ${debug_job_id}"
  while squeue -h -j "${debug_job_id}" >/dev/null 2>&1 && [ -n "$(squeue -h -j "${debug_job_id}")" ]; do
    sleep 5
  done

  debug_state="$(sacct -n -P -j "${debug_job_id}" --format=State | head -n1 | awk -F'|' '{print $1}' | awk '{print $1}' | tr '[:lower:]' '[:upper:]')"
  if [ -z "${debug_state}" ]; then
    echo "[WARN] could not read debug state from sacct; leaving dependent array as-is (${array_job_id})"
  elif [ "${debug_state}" != "COMPLETED" ]; then
    echo "[ERROR] debug job failed with state=${debug_state}. Canceling dependent array ${array_job_id}."
    scancel "${array_job_id}" || true
    mkdir -p .autoresearch/store .autoresearch/failure_logs
    rm -rf .autoresearch/failure_logs/*
    debug_log_path="logs/${exp_name}/debug_${debug_job_id}.log"
    if [ -f "${debug_log_path}" ]; then
      cp -f "${debug_log_path}" ".autoresearch/failure_logs/debug_${debug_job_id}.log"
    fi
    cat > .autoresearch/store/latest_status.json <<EOF
{
  "exp_name": "${exp_name}",
  "debug_job_id": "${debug_job_id}",
  "array_job_id": "${array_job_id}",
  "status": "DEBUG_FAILED",
  "debug_state": "${debug_state}"
}
EOF
    current_branch="$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "")"
    if [ -n "${current_branch}" ]; then
      git add .autoresearch/store/latest_status.json .autoresearch/failure_logs/ "${experiments_csv}" || true
      if [ -n "$(git diff --cached --name-only)" ]; then
        git -c user.name=autoresearch-bot -c user.email=autoresearch-bot@users.noreply.github.com commit -m "autoresearch: debug failed ${exp_name} (${debug_job_id})" || true
        git push origin "${current_branch}" || true
      fi
    fi
    exit 1
  else
    echo "[INFO] Debug gate passed (state=${debug_state}). Array ${array_job_id} will proceed."
  fi

  if [ -n "${array_job_id}" ]; then
    cp -f "${limited_config_list}" ".autoresearch/array_conf/${exp_name}/array_${array_job_id}.txt"
    echo "[INFO] saved array config list: .autoresearch/array_conf/${exp_name}/array_${array_job_id}.txt"
  fi
  exit 0
fi

# Keep all runtime caches under the repo so sbatch jobs don't touch read-only $HOME paths.
export XDG_CACHE_HOME="${REPO_ROOT}/.cache"
export MPLCONFIGDIR="${REPO_ROOT}/.cache/matplotlib"
export NUMBA_CACHE_DIR="${REPO_ROOT}/.cache/numba"
export NUMBA_DISABLE_JIT="${NUMBA_DISABLE_JIT:-1}"
export HF_HOME="${REPO_ROOT}/.cache/huggingface"
export HUGGINGFACE_HUB_CACHE="${HF_HOME}/hub"
export HF_DATASETS_CACHE="${HF_HOME}/datasets"
export HF_MODULES_CACHE="${HF_HOME}/modules"
export HF_HUB_OFFLINE="${HF_HUB_OFFLINE:-1}"
export HF_DATASETS_OFFLINE="${HF_DATASETS_OFFLINE:-1}"
mkdir -p "${XDG_CACHE_HOME}" "${MPLCONFIGDIR}" "${NUMBA_CACHE_DIR}"
mkdir -p "${HF_HOME}" "${HUGGINGFACE_HUB_CACHE}" "${HF_DATASETS_CACHE}"

# If a prewarmed shared HF datasets module cache exists, copy FLEURS module locally
# so offline jobs can resolve dataset configs without touching read-only locks.
shared_fleurs_module="/work/nvme/bbjs/dyang10/hf_cache/modules/datasets_modules/datasets/google--fleurs"
local_fleurs_module="${HF_HOME}/modules/datasets_modules/datasets/google--fleurs"
if [ -d "${shared_fleurs_module}" ] && [ ! -d "${local_fleurs_module}" ]; then
  mkdir -p "$(dirname "${local_fleurs_module}")"
  cp -a "${shared_fleurs_module}" "${local_fleurs_module}" || true
fi

if [ -n "${slack_webhook_url}" ]; then
  export SLACK_WEBHOOK_URL="${slack_webhook_url}"
fi

if [ -z "${task_id}" ]; then
  task_id="${SLURM_ARRAY_TASK_ID:-}"
fi
if [ -z "${task_id}" ]; then
  echo "[ERROR] task_id is empty. Set --task_id or run with sbatch --array=..."
  exit 1
fi

if [ -z "${exp_name}" ]; then
  exp_name="${SLURM_JOB_NAME:-}"
fi
if [ -z "${exp_name}" ]; then
  echo "[ERROR] exp_name is empty. Pass --exp_name <name> (or use sbatch --job-name)."
  exit 1
fi

mkdir -p "logs/${exp_name}" ".autoresearch/array_conf/${exp_name}" "conf/${exp_name}/generated" "exp/${exp_name}"

if [ -z "${config_list}" ]; then
  parent_id="${SLURM_ARRAY_JOB_ID:-${SLURM_JOB_ID:-}}"
  if [ -z "${parent_id}" ]; then
    echo "[ERROR] config_list is empty and no slurm job id is available."
    exit 1
  fi
  config_list=".autoresearch/array_conf/${exp_name}/array_${parent_id}.txt"
fi

if [ ! -f "${config_list}" ]; then
  echo "[ERROR] config_list not found: ${config_list}"
  exit 1
fi

mapfile -t configs < <(grep -v '^[[:space:]]*$' "${config_list}" | grep -v '^[[:space:]]*#')
if [ "${#configs[@]}" -eq 0 ]; then
  echo "[ERROR] no usable config entries in: ${config_list}"
  exit 1
fi

index=$((task_id - array_base_index))
if [ "${index}" -lt 0 ] || [ "${index}" -ge "${#configs[@]}" ]; then
  echo "[ERROR] task_id=${task_id} (base=${array_base_index}) is out of range."
  echo "        usable index range: [0, $((${#configs[@]} - 1))]"
  echo "        config_list entries: ${#configs[@]}"
  exit 1
fi

selected="${configs[${index}]}"
config_path="${selected}"
if [ ! -f "${config_path}" ]; then
  if [ -f "conf/${exp_name}/${selected}" ]; then
    config_path="conf/${exp_name}/${selected}"
  else
    echo "[ERROR] selected config does not exist: ${selected}"
    echo "        also tried: conf/${exp_name}/${selected}"
    exit 1
  fi
fi

base_cfg_name="$(basename "${config_path}")"
base_cfg_stem="${base_cfg_name%.yaml}"
runtime_cfg="conf/${exp_name}/generated/runtime_${SLURM_ARRAY_JOB_ID:-na}_${task_id}.yaml"
runtime_exp_tag="${exp_name}_${base_cfg_stem}_a${task_id}"
run_uid="${SLURM_ARRAY_JOB_ID:-${SLURM_JOB_ID:-na}}_${task_id}_${runtime_exp_tag}"

cat > "${runtime_cfg}" <<EOF
defaults:
  - ../../$(realpath --relative-to=conf "${config_path}")

recipedir: .
exp_tag: ${runtime_exp_tag}
exp_dir: \${recipedir}/exp/${exp_name}/\${exp_tag}
wandb:
  group: ${exp_name}
EOF

if [ "${quick_train}" = "true" ]; then
  cat >> "${runtime_cfg}" <<EOF
num_device: ${quick_num_device}
num_nodes: ${quick_num_nodes}
max_samples_per_subset_train: ${quick_max_samples_per_subset}
max_samples_per_subset_valid: ${quick_max_samples_per_subset}
max_samples_per_subset_test: ${quick_max_samples_per_subset}
trainer:
  fast_dev_run: ${quick_fast_dev_run}
  max_steps: ${quick_max_steps}
  max_epochs: ${quick_max_epochs}
EOF
  if [ -n "${quick_batch_size}" ] || [ -n "${quick_batch_bins}" ]; then
    cat >> "${runtime_cfg}" <<EOF
dataloader:
  train:
    iter_factory:
      batches:
EOF
    if [ -n "${quick_batch_size}" ]; then
      cat >> "${runtime_cfg}" <<EOF
        batch_size: ${quick_batch_size}
EOF
    fi
    if [ -n "${quick_batch_bins}" ]; then
      cat >> "${runtime_cfg}" <<EOF
        batch_bins: ${quick_batch_bins}
EOF
    fi
    cat >> "${runtime_cfg}" <<EOF
  valid:
    iter_factory:
      batches:
EOF
    if [ -n "${quick_batch_size}" ]; then
      cat >> "${runtime_cfg}" <<EOF
        batch_size: ${quick_batch_size}
EOF
    fi
    if [ -n "${quick_batch_bins}" ]; then
      cat >> "${runtime_cfg}" <<EOF
        batch_bins: ${quick_batch_bins}
EOF
    fi
  fi
fi

resolved_infer_config=""
resolved_measure_config=""
if [ -n "${infer_config}" ]; then
  resolved_infer_config="conf/${exp_name}/generated/infer_${SLURM_ARRAY_JOB_ID:-na}_${task_id}.yaml"
  cat > "${resolved_infer_config}" <<EOF
defaults:
  - ../../$(realpath --relative-to=conf "${infer_config}")

train_config_path: ${runtime_cfg}
exp_tag: ${runtime_exp_tag}
exp_dir: ./exp/${exp_name}/${runtime_exp_tag}
inference_dir: \${exp_dir}/infer
EOF
  if [ "${quick_train}" = "true" ]; then
    cat >> "${resolved_infer_config}" <<EOF
max_samples_per_subset_test: ${quick_max_samples_per_subset}
EOF
  fi
fi
if [ -n "${measure_config}" ]; then
  resolved_measure_config="conf/${exp_name}/generated/measure_${SLURM_ARRAY_JOB_ID:-na}_${task_id}.yaml"
  cat > "${resolved_measure_config}" <<EOF
defaults:
  - ../../$(realpath --relative-to=conf "${measure_config}")

train_config_path: ${runtime_cfg}
exp_tag: ${runtime_exp_tag}
exp_dir: ./exp/${exp_name}/${runtime_exp_tag}
inference_dir: \${exp_dir}/infer
EOF
fi

echo "[INFO] exp_name=${exp_name}"
echo "[INFO] job_id=${SLURM_JOB_ID:-na} array_job_id=${SLURM_ARRAY_JOB_ID:-na} task_id=${task_id}"
echo "[INFO] config_list=${config_list}"
echo "[INFO] selected_index=${index} selected_config=${config_path}"
echo "[INFO] runtime_config=${runtime_cfg}"

read -r -a stage_args <<< "${stages}"
if [ "${#stage_args[@]}" -eq 0 ]; then
  stage_args=("train")
fi

run_args=(python run.py --stages "${stage_args[@]}" --training_config "${runtime_cfg}")
if [ -n "${resolved_infer_config}" ]; then
  run_args+=(--inference_config "${resolved_infer_config}")
fi
if [ -n "${resolved_measure_config}" ]; then
  run_args+=(--metrics_config "${resolved_measure_config}")
fi
run_cmd_text="$(printf '%q ' "${run_args[@]}")"

track_common=(
  --csv-path "${experiments_csv}"
  --lock-path "${experiments_csv_lock}"
  --run-uid "${run_uid}"
  --exp-name "${exp_name}"
  --experiment-comment "${experiment_comment}"
  --stages "${stages}"
  --config-list "${config_list}"
  --train-config-path "${runtime_cfg}"
  --infer-config-path "${resolved_infer_config}"
  --measure-config-path "${resolved_measure_config}"
  --base-config "${config_path}"
  --runtime-config "${runtime_cfg}"
  --slurm-job-name "${SLURM_JOB_NAME:-}"
  --slurm-job-id "${SLURM_JOB_ID:-}"
  --slurm-array-job-id "${SLURM_ARRAY_JOB_ID:-}"
  --slurm-array-task-id "${task_id}"
  --hostname "${HOSTNAME:-$(hostname)}"
  --cuda-visible-devices "${CUDA_VISIBLE_DEVICES:-}"
  --command "${run_cmd_text}"
)

python src/experiments_csv.py --mode start "${track_common[@]}"

run_exit=0
"${run_args[@]}" || run_exit=$?

python src/experiments_csv.py --mode finish --exit-code "${run_exit}" "${track_common[@]}"

if [ "${keep_runtime_config}" != "true" ]; then
  rm -f "${runtime_cfg}"
  rm -f "${resolved_infer_config}"
  rm -f "${resolved_measure_config}"
fi

exit "${run_exit}"
