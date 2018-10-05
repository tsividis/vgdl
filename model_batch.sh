#!/bin/bash


#SBATCH --job-name=run_vgdl_model
#SBATCH --array=0-40%30
#SBATCH --output=slurm_logs/main/array_%A_%a.out
#SBATCH --time=1480
#SBATCH --qos=tenenbaum
#SBTACH --cpus-per-task=2
#SBATCH --mem=16G

# --array=0-2%30 tells it to run array instances 0-2 and to never run more than 30 jobs at a time.
# if i'm using qos=tenenbaum i shouldn't exceed 30.
# if i use qos normal i can run more. but then jobs might get taken down and will resume later.
# given that I don't have safe states it's hard to do that well.

# This is the root path of the repo
ROOT="/om2/user/tsividis/vgdl"
# This is used for path binding if working on OM
BASE="$(echo "$ROOT" | cut -d "/" -f2)"

# Paths
CONT="${ROOT}/singularity/pyenv.simg"
SRC=""
DST=""

# Figure out which game and hyperparameter
# N_GAMES=14
# N_PARAMS=3
# GAME_NUMBER=$(($SLURM_ARRAY_TASK_ID % $N_GAMES))
# HYPER_IDX=$(($SLURM_ARRAY_TASK_ID % $N_PARAMS))
GAME_NUMBER=$SLURM_ARRAY_TASK_ID

# if we are running on OpenMind, add the singularity module
. /etc/os-release
OS=$NAME
if [ "$OS" = "CentOS Linux" ]; then
    module add openmind/singularity
fi

# make log path if not already present
if [ ! -d "${ROOT}/slurm_logs/main" ]; then
    mkdir "${ROOT}/slurm_logs/main"
fi

# finally, run the model
# singularity exec  -B "/$BASE:/$BASE" $CONT python -m vgdl.load_games --game_number $GAME_NUMBER --hyperparameter_index $HYPER_IDX
singularity exec  -B "/$BASE:/$BASE" $CONT python -m vgdl.load_games --game_number $GAME_NUMBER --hyperparameter_index 3 --IW 2 --extra_atom_allowed True --make_movie False
#echo "-m vgdl.load_games --game_name ${GAME_NAME} --hyperparameter_index ${HYPER_IDX}"
