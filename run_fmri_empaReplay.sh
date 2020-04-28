# wrapper around fmri_empaReplay.py for executing inside jobs on the cluster
# necessary b/c of conda env
# also, specify SLURM deets on command line in order to have variables in the output and error file names
# IMPORTANT: only run for 1 subject at a time!!!!! b/c need to save & reload state

echo running empa replay for subj ${1}, game ${2}

source activate pedro

# TODO string coupling with main_agent.py 
#rm savedCurricula/curriculum_${2}_*_subj=${1}*

# run separately for each run, block, and instance, otherwise we OOM (notice most of them will be empty for given game)
for run in {1..6}
do
    for block in {0..2}
    do
        for instance in {0..2}
        do
            echo ==== run_fmri_empaReplay: subj ${1}, run $run, block $block, instance $instance, game ${2}

            # get # of plays with given run, block, instance
            out=`mongo --host holy7c22306.rc.fas.harvard.edu heroku_7lzprs54 --eval "db.plays.count({'subj_id': '${1}', 'run_id': ${run}, 'block_id': ${block}, 'instance_id': ${instance}, 'game_name': '${2}'})"`

            echo mongo out -- $out

            # https://stackoverflow.com/questions/24628076/bash-convert-n-delimited-strings-into-array/45565601
            SAVEIFS=$IFS   # Save current IFS
            IFS=$'\n'      # Change IFS to new line
            split=($out) # split into array based on newline
            IFS=$SAVEIFS   # Restore IFS

            nplays=${split[3]}
            echo nplays = $nplays

            for (( play=0; play<$nplays; play++ ))
            do
                echo ---- run_fmri_empaReplay: subj ${1}, run $run, block $block, instance $instance, play $play, game ${2}
                cmd="python -m cProfile -s cumtime fmri_empaReplay.py ${1} ${run} ${block} ${instance} ${play} ${2}"
                echo ${cmd}
                eval ${cmd}
            done
        done
    done
done


