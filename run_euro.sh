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


# config_path=conf/train.yaml
config_path=conf/owsm_peft_lora_basic_euro.yaml # euro 버전 따로 만듦

. parse_options.sh
. path.sh


python run.py \
    --stages train \
    --train_config ${config_path} \
    # --infer_config conf/inference.yaml

# dataset.yaml에서 원하는 데이터로더로 넣어주고 >> dataset_euro.yaml을 만듦
