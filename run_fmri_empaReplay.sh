# wrapper around fmri_empaReplay.py for executing inside jobs on the cluster
# necessary b/c of conda env
# also, specify SLURM deets on command line in order to have variables in the output and error file names

echo running empa replay for ${1} ${2}

source activate pedro
python fmri_empaReplay.py ${1} ${2}

