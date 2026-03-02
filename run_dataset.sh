#!/bin/bash
#SBATCH --job-name=dataset
#SBATCH --account=bbjs-delta-cpu
#SBATCH --partition=cpu
#SBATCH --time=24:00:00
#SBATCH --cpus-per-task=16
#SBATCH --mem=64G
#SBATCH --output=logs/%x_%j.out

# export HF_HOME=/scratch/bbjs/dyang10/hf_cache
# export HF_HUB_CACHE=/scratch/bbjs/dyang10/hf_cache/hub
# export HF_DATASETS_CACHE=/scratch/bbjs/dyang10/hf_cache/datasets
# export TRANSFORMERS_CACHE=/scratch/bbjs/dyang10/hf_cache/transformers
# mkdir -p $HF_HUB_CACHE $HF_DATASETS_CACHE $TRANSFORMERS_CACHE
export HF_HOME=/work/nvme/bbjs/dyang10/hf_cache
export HF_HUB_CACHE=/work/nvme/bbjs/dyang10/hf_cache/hub
export HF_DATASETS_CACHE=/work/nvme/bbjs/dyang10/hf_cache/datasets
export TRANSFORMERS_CACHE=/work/nvme/bbjs/dyang10/hf_cache/transformers
mkdir -p "$HF_HUB_CACHE" "$HF_DATASETS_CACHE" "$TRANSFORMERS_CACHE"
export TMPDIR=/work/nvme/bbjs/dyang10/tmp 

mkdir -p logs

export HF_HUB_DOWNLOAD_THREADS=16

python src/data/create_dataset.py \
  --output_dir /work/nvme/bbjs/dyang10/datasets/falar_portugal \
  --cache_dir /work/nvme/bbjs/dyang10/hf_cache

# python src/data/create_dataset.py \
#   --output_dir /work/nvme/bbjs/dyang10/datasets/eurospeech_portugal \
#   --cache_dir /work/nvme/bbjs/dyang10/hf_cache_euro
# create_dataset.py 주석 바꿔야함 & 위에 hf_cache_euro로 바꾸고