#!/bin/bash

export HF_HOME=$(pwd)/hub
export LD_LIBRARY_PATH="/u/someki1/.pixi/envs/ffmpeg/lib:${LD_LIBRARY_PATH}"
export LD_LIBRARY_PATH="/u/someki1/.pixi/envs/icu/lib:${LD_LIBRARY_PATH}"
export LD_LIBRARY_PATH="/u/someki1/.pixi/envs/readline/lib:${LD_LIBRARY_PATH}"
export PYTHONPATH="$(pwd):${PYTHONPATH:-}"

# activate python
eval "$(pixi shell-hook)"

. parse_options.sh

export WANDB_API_KEY=$(cat wandb.key)
export WANDB_ENTITY=$(cat wandb_entry.key)
