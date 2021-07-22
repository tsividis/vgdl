# wrapper around fmri_makeMovie.py for executing inside jobs on the cluster
# necessary because of memory leak
# copy of run_fmri_empaReplay.sh

echo running make movie for subj ${1}, game ${2}

source activate pedro

# run separately for each run, block, and instance, otherwise we OOM (notice most of them will be empty for given game)
for run in {1..6}
do
    for block in {0..2}
    do
        for instance in {0..2}
        do
            echo ==== run_fmri_makeMovie: subj ${1}, run $run, block $block, instance $instance, game ${2}

            # get # of plays with given run, block, instance
            out=`mongo --host holy2a05208.rc.fas.harvard.edu heroku_7lzprs54 --eval "db.plays.count({'subj_id': '${1}', 'run_id': ${run}, 'block_id': ${block}, 'instance_id': ${instance}, 'game_name': '${2}'})"`
            echo mongo play count -- $out

            # https://stackoverflow.com/questions/24628076/bash-convert-n-delimited-strings-into-array/45565601
            SAVEIFS=$IFS   # Save current IFS
            IFS=$'\n'      # Change IFS to new line
            split=($out)  # split into array based on newline
            IFS=$SAVEIFS   # Restore IFS

            #nplays=${split[3]} #ncf
            #nplays=${split[4]} #local
            nplays=${split[2]}
            echo nplays = $nplays

            for (( play=0; play<$nplays; play++ ))
            do
                # run makeMovie 
                echo ---- run_fmri_makeMovie: subj ${1}, run $run, block $block, instance $instance, play $play, game ${2}
                cmd="python -m cProfile -s cumtime fmri_makeMovie.py ${1} ${run} ${block} ${instance} ${play} ${2}"
                echo ${cmd}
                eval ${cmd}
            done
        done
    done
done

echo 'Done'
