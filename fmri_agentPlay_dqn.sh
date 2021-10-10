# run fmri_agentPlay for a bunch of subjects
# copied from ccnl_fmri_preproc.sh
#

mkdir output

#subjects=( 1 2 3 4 5 6 7 8 )  #  e.g. subjects=( 1 2 5 6 7 10 )
#subjects=( 1 2 3 4 5 6 7 8 9 10 11 )  #  e.g. subjects=( 1 2 5 6 7 10 )
#subjects=(12  14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30  31 32)
subjects=(14)
subj_arg="${subjects[@]}" # stringify it

insert='--insert' # whether to insert any results in the db
#insert=''

#record_video_info='--record-video-info'  # whether to save the encountered states
record_video_info=''

#agent='EMPA'
#tag='attempt_2_states_steps_1200'
#steps_per_level=1200 # fMRI level # frames in a minute

agent='DQN'
tag='eval1_gpu'
steps_per_level=1200

#agent='Random'
#tag='attempt_1'
#steps_per_level=1200 # fMRI level # frames in a minute

#games=( 'vgfmri3_chase' )
#games=( 'vgfmri3_chase' 'vgfmri3_helper' 'vgfmri3_bait' 'vgfmri3_lemmings' 'vgfmri3_plaqueAttack' 'vgfmri3_zelda')
#games=(  'vgfmri3_helper' 'vgfmri3_bait'  'vgfmri3_zelda')

#games=(  'vgfmri4_lemmings' 'vgfmri4_zelda') # 90000, 2 days
#games=( 'vgfmri4_avoidgeorge' ) # 50000, 2 days

#games=(   'vgfmri4_lemmings'  'vgfmri4_avoidgeorge') # 140000 , 4 days
games=( 'vgfmri4_bait' ) # 140000, 4 days
#games=( 'vgfmri4_chase' ) # 50000, 4 days

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
        sbatch_output=`sbatch -p fasse_gpu --gres=gpu --mem 40001 -t 2-0:20 -o ${outfileprefix}_%j.out -e ${outfileprefix}_%j.err --wrap="./run_fmri_agentPlay.sh ${agent} ${subj} ${game} ${steps_per_level} ${tag} ${insert} ${record_video_info}"`
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
