# wrapper around fmri_empaReplay.py for executing inside jobs on the cluster
# necessary b/c of conda env
# also, specify SLURM deets on command line in order to have variables in the output and error file names
# IMPORTANT: only run for 1 subject at a time!!!!! b/c need to save & reload state

echo running empa replay for subj ${1}, game ${2}

source activate pedro

# TODO string coupling with main_agent.py 
rm savedCurricula/curriculum_${2}_*_subj=${1}*

# run separately for each run, otherwise we OOM
python fmri_empaReplay.py ${1} 1 ${2}
python fmri_empaReplay.py ${1} 2 ${2}
python fmri_empaReplay.py ${1} 3 ${2}
python fmri_empaReplay.py ${1} 4 ${2}
python fmri_empaReplay.py ${1} 5 ${2}
python fmri_empaReplay.py ${1} 6 ${2}

