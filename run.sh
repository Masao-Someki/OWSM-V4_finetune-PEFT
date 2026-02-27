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


config_path=conf/train.yaml

. parse_options.sh
. path.sh

python run.py \
    --stages train \
    --train_config ${config_path} \
    --infer_config conf/inference.yaml
