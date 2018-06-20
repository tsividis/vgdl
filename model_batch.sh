#!/bin/bash


#SBATCH --job-name=run_vgdl_model
#SBATCH --array=0-2
#SBATCH --output=slurm_logs/array_%A_%a.out
#SBATCH --time=120
#SBATCH --qos=tenenbaum
#SBTACH --cpus-per-task=2
#SBATCH --mem=4G

# This is the root path of the repo
ROOT="/om2/user/tsividis/vgdl"
# This is used for path binding if working on OM
BASE="$(echo "$ROOT" | cut -d "/" -f2)"

# Paths
CONT="${ROOT}/singularity/pyenv.simg"
SRC=""
DST=""

# Figure out which game and hyperparameter
N_GAMES=10
N_PARAMS=3
GAME_NUMBER=$(($SLURM_ARRAY_TASK_ID % $N_GAMES))
HYPER_IDX=$(($SLURM_ARRAY_TASK_ID % $N_PARAMS))

# CMD="echo \"-m vgdl.load_games --game_name ${GAME_NAME} --hyperparameter_index ${HYPER_IDX}\""

# if we are running on OpenMind, add the singularity module
. /etc/os-release
OS=$NAME
if [ "$OS" = "CentOS Linux" ]; then
    module add openmind/singularity
fi

# make log path if not already present
if [ ! -d "slurm_logs" ]; then
    mkdir "slurm_logs"
fi

# finally, run the model
singularity exec  -B "/$BASE:/$BASE" $CONT python -m vgdl.load_games --game_number $GAME_NUMBER --hyperparameter_index $HYPER_IDX