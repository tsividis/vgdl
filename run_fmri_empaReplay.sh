# wrapper around fmri_empaReplay.py for executing inside jobs on the cluster
# necessary b/c of conda env
# also, specify SLURM deets on command line in order to have variables in the output and error file names
# IMPORTANT: only run for 1 subject at a time!!!!! b/c need to save & reload state

echo running empa replay for subj ${1}, game ${2}

source activate pedro

# TODO string coupling with main_agent.py 
rm ${MY_SCRATCH}/VGDL/savedCurricula/curriculum_${2}_*_subj=${1}*

tot_plays=0

# run separately for each run, block, and instance, otherwise we OOM (notice most of them will be empty for given game)
for run in {1..6}
do
    for block in {0..2}
    do
        for instance in {0..2}
        do
            echo ==== run_fmri_empaReplay: subj ${1}, run $run, block $block, instance $instance, game ${2}

            # get # of plays with given run, block, instance
            out=`mongo --host holy7c18111.rc.fas.harvard.edu heroku_7lzprs54 --eval "db.plays.count({'subj_id': '${1}', 'run_id': ${run}, 'block_id': ${block}, 'instance_id': ${instance}, 'game_name': '${2}'})"`

            echo mongo play count -- $out

            # https://stackoverflow.com/questions/24628076/bash-convert-n-delimited-strings-into-array/45565601
            SAVEIFS=$IFS   # Save current IFS
            IFS=$'\n'      # Change IFS to new line
            split=($out)  # split into array based on newline
            IFS=$SAVEIFS   # Restore IFS

            #nplays=${split[3]} #ncf
            nplays=${split[2]}
            echo nplays = $nplays

            for (( play=0; play<$nplays; play++ ))
            do
                # make sure that the thing worked and the regressors got inserted
                # if not, abort (so we can fix it & resume; o/w savedCurricula gets fucked and we have to start all over
                #out=`mongo --host holy7c18111.rc.fas.harvard.edu heroku_7lzprs54 --eval "db.regressors.count({'subj_id': '${1}', 'game_name': '${2}'})"`
                #out=`mongo --host holy7c18111.rc.fas.harvard.edu heroku_7lzprs54 --eval "db.regressors_cannon_spriteEvery20.count({'subj_id': '${1}', 'game_name': '${2}'})"`
                out=`mongo --host holy7c18111.rc.fas.harvard.edu heroku_7lzprs54 --eval "db.regressors.count({'subj_id': '${1}', 'game_name': '${2}'})"`
                echo mongo total regressor count -- $out

                # https://stackoverflow.com/questions/24628076/bash-convert-n-delimited-strings-into-array/45565601
                SAVEIFS=$IFS   # Save current IFS
                IFS=$'\n'      # Change IFS to new line
                split=($out)  # split into array based on newline
                IFS=$SAVEIFS   # Restore IFS

                #nregs=${split[3]} # ncf
                nregs=${split[2]}
                echo tot_plays vs nregs -- $tot_plays vs. $nregs
                if [ "$tot_plays" -ne "$nregs" ]
                then
                    #echo NOT EQUAL: aborting script
                    #exit 1
                    echo NOT EQUAL: skipping 
                    ((tot_plays=tot_plays+1))
                    continue
                fi


                # run empaReplay
                echo ---- run_fmri_empaReplay: subj ${1}, run $run, block $block, instance $instance, play $play, game ${2}
                cmd="python -m cProfile -s cumtime fmri_empaReplay.py ${1} ${run} ${block} ${instance} ${play} ${2}"
                echo ${cmd}
                eval ${cmd}

                ((tot_plays=tot_plays+1))
            done
        done
    done
done

echo 'Done'
