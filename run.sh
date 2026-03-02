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
config_path=conf/whisper_peft_lora_basic_falar.yaml #conf/owsm_peft_lora_basic_falar.yaml # add dahee

. parse_options.sh
. path.sh

# for falar
export HF_HOME=/work/nvme/bbjs/clin10/eurospeech_finetune/espnet/egs3/eurospeech_portugal/s2t1/hub       

python run.py \
    --stages train \
    --train_config ${config_path} 
    # --infer_config conf/inference.yaml

# replace config for data + modify dataset.yaml
