# wrapper around fmri_agentPlay.py for executing inside jobs on the cluster
# necessary b/c of conda env
# also, specify SLURM deets on command line in order to have variables in the output and error file names
# IMPORTANT: only run for 1 subject at a time!!!!! b/c need to save & reload state

echo running agent play for agent ${1}, subj ${2}, game ${3}, steps_for_level ${4}, tag ${5}, ${6} ${7}

hostname

source activate pedro

collection='sim_results'

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
# TODO string coupling with bookkeeping.py, dqn_agent.py, EMPA.py, fmri_agentPlay.py
curriculum_file=${curriculum_dir}/curriculum_${1}_${3}_*_subj=${2}*
echo Curriculum file: ${curriculum_file}
ls -latch ${curriculum_file}
echo 'NOT REMOVING CURRICULUM FILE!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!1'
#rm ${curriculum_file}

tot_plays=0
level=0

# run separately for each run, block, and instance, otherwise we OOM (notice most of them will be empty for given game)
for run in {1..6}
do
    for block in {0..2}
    do
        for instance in {0..2}
        do
            echo ==== run_fmri_agentPlay: subj ${2}, run $run, block $block, instance $instance, game ${3}

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

            if [[ $nplays -gt 0 ]] 
            then
                # make sure to skip levels that we have already played
                # note this assumes that we are not removing the saved curricula
                out=`mongo --host ${host} heroku_7lzprs54  --authenticationDatabase "admin" -u "root" -p "parolatabe" --eval "db.${collection}.count({'agent_name': '${1}', 'subj_id': '${2}', 'game_name': '${3}', 'tag': '${5}'})"`
                echo mongo nlevel -- $out
                # https://stackoverflow.com/questions/24628076/bash-convert-n-delimited-strings-into-array/45565601
                SAVEIFS=$IFS   # Save current IFS
                IFS=$'\n'      # Change IFS to new line
                split=($out)  # split into array based on newline
                IFS=$SAVEIFS   # Restore IFS
                nlevels=${split[2]}
                echo nlevels vs level -- $nlevels vs $level
                if [ "$nlevels" -ne "$level" ]
                then
                    echo NOT EQUAL : skipping 
                    level=$(( level + 1 ))
                    continue
                fi
                level=$(( level + 1 ))

                # make sure current level is actually not computed
                out=`mongo --host ${host} heroku_7lzprs54  --authenticationDatabase "admin" -u "root" -p "parolatabe" --eval "db.${collection}.count({'agent_name': '${1}', 'subj_id': '${2}', 'game_name': '${3}', 'results.level': ${level}, 'tag': '${5}'})"`
                echo mongo level $level count -- $out
                # https://stackoverflow.com/questions/24628076/bash-convert-n-delimited-strings-into-array/45565601
                SAVEIFS=$IFS   # Save current IFS
                IFS=$'\n'      # Change IFS to new line
                split=($out)  # split into array based on newline
                IFS=$SAVEIFS   # Restore IFS
                nentries=${split[2]}
                echo nentries $nentries
                if [ "$nentries" -ne 0 ]
                then
                    echo FOUND ENTRY FOR LEVEL $level: aborting script
                    exit 1
                fi

                # run agentPlay
                echo ---- run_fmri_agentPlay: agent ${1}, subj ${2}, run $run, block $block, instance $instance, game ${3}
                #cmd="python -m cProfile -s cumtime fmri_agentPlay.py --agent-name=${1} --subj-id=${2} --run-id=${run} --block-id=${block} --instance-id=${instance}  --game-name=${3}"
                cmd="python -W ignore::UserWarning fmri_agentPlay.py --agent-name=${1} --subj-id=${2} --run-id=${run} --block-id=${block} --instance-id=${instance} --game-name=${3} --steps-per-level=${4} --tag=${5} ${6} ${7}"
                echo ${cmd}
                eval ${cmd}

            fi

        done
    done
done

echo 'Done'
