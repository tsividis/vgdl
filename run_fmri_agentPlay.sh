# wrapper around fmri_agentPlay.py for executing inside jobs on the cluster
# necessary b/c of conda env
# also, specify SLURM deets on command line in order to have variables in the output and error file names
# IMPORTANT: only run for 1 subject at a time!!!!! b/c need to save & reload state

echo running agent play for agent ${1}, subj ${2}, game ${3}, steps_for_level ${4}, tag ${5}

hostname

source activate pedro

# figure out host based on machine (RC, NCF, local)
if [[ `hostname` == *"Momchil"* ]]; then
    host='localhost'
    nplays_idx=4
    curriculum_dir=savedCurricula
else
    host='holy7c22212.rc.fas.harvard.edu'
    nplays_idx=2
    curriculum_dir=${MY_SCRATCH}/VGDL/savedCurricula
fi

# remove current agent state
# TODO string coupling with bookkeeping.py, dqn_agent.py, EMPA.py, fmri_agentPlay.py
curriculum_file=${curriculum_dir}/curriculum_${1}_${3}_*_subj=${2}*
echo Curriculum file:
ls -latch ${curriculum_file}
rm ${curriculum_file}

tot_plays=0

# run separately for each run, block, and instance, otherwise we OOM (notice most of them will be empty for given game)
for run in {1..6}
do
    for block in {0..2}
    do
        for instance in {0..2}
        do
            echo ==== run_fmri_agentPlay: subj ${2}, run $run, block $block, instance $instance, game ${3}

            # run agentPlay
            echo ---- run_fmri_agentPlay: agent ${1}, subj ${2}, run $run, block $block, instance $instance, game ${3}
            #cmd="python -m cProfile -s cumtime fmri_agentPlay.py --agent-name=${1} --subj-id=${2} --run-id=${run} --block-id=${block} --instance-id=${instance}  --game-name=${3}"
            cmd="python -W ignore::DeprecationWarning fmri_agentPlay.py --agent-name=${1} --subj-id=${2} --run-id=${run} --block-id=${block} --instance-id=${instance} --game-name=${3} --steps-per-level=${4} --tag=${5} --insert"
            echo ${cmd}
            eval ${cmd}

        done
    done
done

echo 'Done'
