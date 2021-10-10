# wrapper around fmri_makeMovie.py for executing inside jobs on the cluster
# necessary because of memory leak
# copy of run_fmri_empaReplay.sh

echo running make movie for subj ${1}

source activate pedro

# figure out host based on machine (RC, NCF, local)
if [[ `hostname` == *"Momchil"* ]]; then
    host='localhost'
    nplays_idx=4
else
    host='holy7c22103.rc.fas.harvard.edu'
    nplays_idx=2
fi


# run separately for each run, block, and instance, otherwise we error out 
for run in {1..6}
do
    for block in {0..2}
    do
        for instance in {0..2}
        do
            echo ==== run_fmri_makeMovie: subj ${1}, run $run, block $block, instance $instance

            # get # of plays with given run, block, instance
            out=`mongo --host ${host} heroku_7lzprs54 --eval "db.plays.count({'subj_id': '${1}', 'run_id': ${run}, 'block_id': ${block}, 'instance_id': ${instance}})"`
            echo mongo play count -- $out

            # https://stackoverflow.com/questions/24628076/bash-convert-n-delimited-strings-into-array/45565601
            SAVEIFS=$IFS   # Save current IFS
            IFS=$'\n'      # Change IFS to new line
            split=($out)  # split into array based on newline
            IFS=$SAVEIFS   # Restore IFS

            #nplays=${split[3]} #ncf
            #nplays=${split[4]} #local
            #nplays=${split[2]}
            nplays=${split[$nplays_idx]}
            echo nplays = $nplays

            for (( play=0; play<$nplays; play++ ))
            do
                # run makeMovie 
                echo ---- run_fmri_makeMovie: subj ${1}, run $run, block $block, instance $instance, play $play
                #cmd="python -m cProfile -s cumtime fmri_makeMovie.py --subj-id=${1} --run-id=${run} --block-id=${block} --instance-id=${instance} --play-id=${play}"
                cmd="python fmri_makeMovie.py --subj-id=${1} --run-id=${run} --block-id=${block} --instance-id=${instance} --play-id=${play}"
                echo ${cmd}
                eval ${cmd}
            done
        done
    done
done

echo 'Done'
