# wrapper around fmri_empaReplay.py for executing inside jobs on the cluster
# necessary b/c of conda env
# also, specify SLURM deets on command line in order to have variables in the output and error file names
# IMPORTANT: only run for 1 subject at a time!!!!! b/c need to save & reload state

echo running empa replay for subj ${1}, game ${2}

source activate pedro

# TODO string coupling with main_agent.py 
rm savedCurricula/curriculum_${2}_*_subj=${1}*

# run separately for each run, block, and instance, otherwise we OOM (notice most of them will be empty for given game)
for run in {1..6}
do
    for block in {0..2}
    do
        for instance in {0..2}
        do
            python fmri_empaReplay.py ${1} ${run} ${block} ${instance} ${2}
        done
    done
done


