# run fmri_agentPlay for a bunch of subjects
# copied from ccnl_fmri_preproc.sh
#

mkdir output

#subjects=( 1 2 3 4 5 6 7 8 )  #  e.g. subjects=( 1 2 5 6 7 10 )
subjects=( 1 )  #  e.g. subjects=( 1 2 5 6 7 10 )
subj_arg="${subjects[@]}" # stringify it
insert='--insert' # whether to insert any results in the db
#insert=''
record_video_info='--record-video-info'  # whether to save the encountered states
#record_video_info=''


#agent='DQN'
#tag='train'
#steps_per_level=100000

agent='Random'
tag='insert_no_states_fuck'
steps_per_level=1200 # fMRI level # frames in a minute

games=( 'vgfmri3_chase' )
#games=( 'vgfmri3_chase' 'vgfmri3_helper' 'vgfmri3_bait' 'vgfmri3_lemmings' 'vgfmri3_plaqueAttack' 'vgfmri3_zelda')

echo ---------------- >> jobs.txt
echo --- $(date): Running fmri_agentPlay for subjects ${subj_arg} in parallel >> jobs.txt
echo ---------------- >> jobs.txt
git log | head -n 1 >> jobs.txt

for subj in ${subjects[*]}; do
    for game in ${games[*]}; do
        outfileprefix="${MY_SCRATCH}/VGDL/output/fmri_agentPlay_${agent}_${subj}_${game}"
        echo ---------------------------------------------------------------------------------
        echo agent ${agent}, subject ${subj}, game ${game}, tag ${tag}, file prefix = $outfileprefix

        # send the job to NCF
        #
        #sbatch_output=`sbatch -p fasse --mem 20001 -t 1-15:20 -o ${outfileprefix}_%j.out -e ${outfileprefix}_%j.err --wrap="source activate pedro; python fmri_agentPlay.py --agent-name=${agent} --subj-id=${subj} --steps-per-level=${steps_per_level} --game-name=${game}"`
        sbatch_output=`sbatch -p fasse --mem 20001 -t 0-2:20 -o ${outfileprefix}_%j.out -e ${outfileprefix}_%j.err --wrap="./run_fmri_agentPlay.sh ${agent} ${subj} ${game} ${steps_per_level} ${tag} ${insert} ${record_video_info}"`
        # for local testing
        #sbatch_output=`echo Submitted batch job 88725418`
        echo $sbatch_output

        # Append job id to jobs.txt
        #
        sbatch_output_split=($sbatch_output)
        job_id=${sbatch_output_split[3]}
        echo fmri_agentPlay.sh for subject ${subj}, game ${game}: ${outfileprefix}_${job_id}.out -- $sbatch_output >> jobs.txt

        echo watch job status with: sacct -j ${job_id}
        echo watch output with: tail -f ${outfileprefix}_${job_id}.out
        echo watch error with: tail -f ${outfileprefix}_${job_id}.err

        sleep 1
    done
done
