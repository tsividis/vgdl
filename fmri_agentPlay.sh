# run fmri_agentPlay for a bunch of subjects
# copied from ccnl_fmri_preproc.sh
#

mkdir output

#subjects=( 1 2 3 4 5 6 7 8 )  #  e.g. subjects=( 1 2 5 6 7 10 )
#subjects=( 1 2 3 4 5 6 7 8 9 10 11 )  #  e.g. subjects=( 1 2 5 6 7 10 )
#subjects=(13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31 32)
subjects=(14)
subj_arg="${subjects[@]}" # stringify it

insert='--insert' # whether to insert any results in the db
#insert=''

#record_video_info='--record-video-info'  # whether to save the encountered states
record_video_info=''

metacontroller_index=0 #0, 4, 5
hyperparameter_index='short-term' #'short-term','short-term-no-novelty'
epsilon_greedy=0  #0, 1
max_nodes_scale='1'  # 1, 0.1, 0.01

agent='EMPA'
#tag='attempt_1_states'
#tag='attempt_3_colors'
#tag='attempt_4_colors'
tag='2026_03_24'
#tag='attempt_2_states_steps_1200'
#tag='ablation_AGH3_attempt_1'
#tag='ablation_IW_attempt_1'
#tag='ablation_epsgreedy_attempt_1'
#tag='ablation_nodes_attempt_1'
#tag='ablation_lessnodes_attempt_1'
steps_per_level=1200 # fMRI level # frames in a minute

#agent='DQN'
#tag='eval_1_nongpu_steps_1200'
#steps_per_level=100000
#steps_per_level=1200 # fMRI level # frames in a minute

#agent='Random'
#tag='attempt_1'
#steps_per_level=1200 # fMRI level # frames in a minute

#games=( 'vgfmri3_chase' )
#games=( 'vgfmri3_chase' 'vgfmri3_helper' 'vgfmri3_bait' 'vgfmri3_lemmings' 'vgfmri3_plaqueAttack' 'vgfmri3_zelda')
#games=(  'vgfmri3_helper' 'vgfmri3_bait'  'vgfmri3_zelda')

# see commit 1d234e28da082c05a7fccdfdd16855d13f52128b

#games=(  'vgfmri3_plaqueAttack' ) # 140000, 5 days

#games=(  'vgfmri4_lemmings' ) # 90000, 2 days
#games=( 'vgfmri4_avoidgeorge' ) # 50000, 2 days
#games=( 'vgfmri4_zelda' )  # 90000? 
#games=(...)

#games=( 'vgfmri4_helper' ) # n 140000 , 4 days
#games=( 'vgfmri4_bait' 'vgfmri4_chase' 'vgfmri4_zelda' ) # 140000, 4 days
#games=( 'vgfmri4_bait' 'vgfmri4_chase' 'vgfmri4_zelda' 'vgfmri4_helper' 'vgfmri4_avoidgeorge' 'vgfmri4_lemmings' ) # 140000, 4 days
#games=( 'vgfmri4_chase' ) # 50000, 4 days
#games=( 'vgfmri4_bait' ) # 50000, 4 days
games=('vgfmri4_zelda')
#games=( 'vgfmri3_c.hase' ) # 50000, 4 days

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
        #sbatch_output=`sbatch -p fasse_bigmem --mem 450001 -t 7-00:00 -o ${outfileprefix}_%j.out -e ${outfileprefix}_%j.err --wrap="source activate pedro; python fmri_agentPlay.py --agent-name=${agent} --subj-id=${subj} --steps-per-level=${steps_per_level} --game-name=${game}"`
        #sbatch_output=`sbatch -p fasse_gpu --gres=gpu --mem 20001 -t 0-0:20 -o ${outfileprefix}_%j.out -e ${outfileprefix}_%j.err --wrap="./run_fmri_agentPlay.sh ${agent} ${subj} ${game} ${steps_per_level} ${tag} ${insert} ${record_video_info}"`
        #sbatch_output=`sbatch -p fasse_bigmem --mem 450000 -t 7-0:00 -o ${outfileprefix}_%j.out -e ${outfileprefix}_%j.err --wrap="./run_fmri_agentPlay.sh ${agent} ${subj} ${game} ${steps_per_level} ${tag} ${insert} ${record_video_info}"`
        sbatch_output=`sbatch -p fasse --mem 140000 -t 6-0:00 -o ${outfileprefix}_%j.out -e ${outfileprefix}_%j.err --wrap="./run_fmri_agentPlay.sh ${agent} ${subj} ${game} ${steps_per_level} ${tag} ${hyperparameter_index} ${metacontroller_index} ${epsilon_greedy} ${max_nodes_scale} ${insert} ${record_video_info}"`
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
