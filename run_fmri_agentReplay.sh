# wrapper around fmri_agentReplay.py for executing inside jobs on the cluster
# necessary b/c of conda env
# also, specify SLURM deets on command line in order to have variables in the output and error file names
# IMPORTANT: only run for 1 subject at a time!!!!! b/c need to save & reload state

echo running agent replay for agent ${1}, subj ${2}, game ${3}

source activate pedro

# figure out collection based on agent
if [ ${1} == "EMPA" ]; then
    collection='regressors'
elif [ ${1} == "DQN" ]; then
    collection='dqn_regressors'
else
    echo 'Invalid agent'
    exit 1
fi

# figure out host based on machine (RC, NCF, local)
if [[ `hostname` == *"Momchil"* ]]; then
    host='localhost'
    nplays_idx=4
    curriculum_dir=savedCurricula
else
    host='holy7c22211.rc.fas.harvard.edu'
    nplays_idx=2
    curriculum_dir=${MY_SCRATCH}/VGDL/savedCurricula
fi

# remove current agent state
# TODO string coupling with bookkeeping.py, dqn_agent.py, EMPA.py, fmri_agentReplay.py
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
            echo ==== run_fmri_agentReplay: subj ${2}, run $run, block $block, instance $instance, game ${3}

            # get # of plays with given run, block, instance
            out=`mongo --host ${host} heroku_7lzprs54  --authenticationDatabase "admin" -u "root" -p "parolatabe" --eval "db.plays.count({'subj_id': '${2}', 'run_id': ${run}, 'block_id': ${block}, 'instance_id': ${instance}, 'game_name': '${3}'})"`

            echo mongo play count -- $out

            # https://stackoverflow.com/questions/24628076/bash-convert-n-delimited-strings-into-array/45565601
            SAVEIFS=$IFS   # Save current IFS
            IFS=$'\n'      # Change IFS to new line
            split=($out)  # split into array based on newline
            IFS=$SAVEIFS   # Restore IFS

            #nplays=${split[3]} #ncf
            #nplays=${split[2]}
            nplays=${split[$nplays_idx]}
            echo nplays = $nplays

            for (( play=0; play<$nplays; play++ ))
            do
                # make sure that the thing worked and the regressors got inserted
                # if not, abort (so we can fix it & resume; o/w savedCurricula gets fucked and we have to start all over
                #out=`mongo --host ${host} heroku_7lzprs54 --eval "db.${collection}.count({'subj_id': '${2}', 'game_name': '${3}'})"`
                #out=`mongo --host ${host} heroku_7lzprs54 --eval "db.regressors_cannon_spriteEvery20.count({'subj_id': '${2}', 'game_name': '${3}'})"`
                out=`mongo --host ${host} heroku_7lzprs54  --authenticationDatabase "admin" -u "root" -p "parolatabe" --eval "db.${collection}.count({'subj_id': '${2}', 'game_name': '${3}'})"`
                echo mongo total ${collection} count -- $out

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


                # run agentReplay
                echo ---- run_fmri_agentReplay: agent ${1}, subj ${2}, run $run, block $block, instance $instance, play $play, game ${3}
                #cmd="python -m cProfile -s cumtime fmri_agentReplay.py --agent-name=${1} --subj-id=${2} --run-id=${run} --block-id=${block} --instance-id=${instance} --play-id=${play} --game-name=${3}"
                cmd="python fmri_agentReplay.py --agent-name=${1} --subj-id=${2} --run-id=${run} --block-id=${block} --instance-id=${instance} --play-id=${play} --game-name=${3}"
                echo ${cmd}
                eval ${cmd}

                ((tot_plays=tot_plays+1))
            done
        done
    done
done

echo 'Done'
