#!/bin/bash
# Run EMPA (load_games.py) for a single game via SLURM.
# Usage: ./run_load_games.sh <game_name> [task_id]
#
# Example:
#   ./run_load_games.sh vgfmri4_bait
#   ./run_load_games.sh vgfmri4_bait 42
#
# Track progress:
#   sacct -j <job_id>                        -- job status
#   tail -f <outfile>                        -- live stdout
#   tail -f <errfile>                        -- live stderr (printed to same .out file too)
#   grep "n_level\|Win\|episode\|DECIDING" <outfile>  -- scan for key events

game=${1}
task_id=${2:-0}

if [ -z "$game" ]; then
    echo "Usage: $0 <game_name> [task_id]"
    exit 1
fi

outfileprefix="${MY_SCRATCH}/VGDL/output/load_games_${game}"

mkdir -p "${MY_SCRATCH}/VGDL/output"

echo "----------------" >> jobs.txt
echo "--- $(date): Submitting load_games for game=${game}, task_id=${task_id}" >> jobs.txt
echo "----------------" >> jobs.txt
git log | head -n 1 >> jobs.txt

sbatch_output=`sbatch \
    -p fasse \
    --mem 50000 \
    -t 5-0:00 \
    -o ${outfileprefix}_%j.out \
    -e ${outfileprefix}_%j.err \
    --wrap="hostname; module load Anaconda2/2019.10-fasrc01; source activate pedro; cd /n/home_fasse/mtomov13/py_vgdl && python -m vgdl.load_games --game_name ${game} --task_ID ${task_id} --produce_printout True"`

echo $sbatch_output

sbatch_output_split=($sbatch_output)
job_id=${sbatch_output_split[3]}

echo "load_games for game=${game}, task_id=${task_id}: ${outfileprefix}_${job_id}.out -- $sbatch_output" >> jobs.txt

echo ""
echo "Job submitted: ${job_id}"
echo "Watch job status : sacct -j ${job_id}"
echo "Watch output     : tail -f ${outfileprefix}_${job_id}.out"
echo "Watch errors     : tail -f ${outfileprefix}_${job_id}.err"
echo "Scan for progress: grep -E 'n_level|Win=|episode|DECIDING|level [0-9]' ${outfileprefix}_${job_id}.out"
