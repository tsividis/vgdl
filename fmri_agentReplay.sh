# rue fmri_agentReplay for a bunch of subjects
# copied from ccnl_fmri_preproc.sh
#

mkdir output

#agent='DQN'
agent='EMPA'

#subjects=( 1 2 3 4 5 6 7 8 )  #  e.g. subjects=( 1 2 5 6 7 10 )
subjects=( 1  )
#subjects=( 1 9          10  11 )  #  e.g. subjects=( 1 2 5 6 7 10 )
#subjects=(  13 14 15 16 17 18 19 20 21 22 23 24 25 26  27 28 29 30 31 32)  #  e.g. subjects=( 1 2 5 6 7 10 )
#subjects=(  16 17 18 19 20 21 22 23 24 25 26  27 28 29 30 31 32)  #  e.g. subjects=( 1 2 5 6 7 10 )
subj_arg="${subjects[@]}" # stringify it

#games=( 'vgfmri3_chase' 'vgfmri3_helper' 'vgfmri3_bait' 'vgfmri3_lemmings' 'vgfmri3_plaqueAttack' 'vgfmri3_zelda')
#games=( 'vgfmri4_chase' 'vgfmri4_helper' 'vgfmri4_bait' 'vgfmri4_lemmings' 'vgfmri4_avoidgeorge' 'vgfmri4_zelda')
#games=(  'vgfmri4_helper' 'vgfmri4_bait' 'vgfmri4_lemmings' 'vgfmri4_avoidgeorge' 'vgfmri4_zelda')
#games=( 'vgfmri3_lemmings' 'vgfmri3_plaqueAttack')
#games=( 'vgfmri3_lemmings' 'vgfmri3_plaqueAttack' )
#games=( 'vgfmri4_lemmings' 'vgfmri4_avoidgeorge' )
#games=( 'vgfmri3_helper' 'vgfmri3_bait'  'vgfmri3_zelda' )
#games=( 'vgfmri3_chase' 'vgfmri3_bait'  'vgfmri3_zelda' )
#games=( 'vgfmri4_helper' 'vgfmri4_bait'  'vgfmri4_zelda'  )
#games=( 'vgfmri4_chase' 'vgfmri4_helper' 'vgfmri4_bait'  'vgfmri4_zelda' )
#games=( 'vgfmri4_chase' 'vgfmri4_bait' 'vgfmri4_zelda')
games=( 'vgfmri3_chase')
#games=( 'vgfmri4_chase')
#games=( 'none' )

echo ---------------- >> jobs.txt
echo --- $(date): Running fmri_agentReplay for subjects ${subj_arg} in parallel >> jobs.txt
echo ---------------- >> jobs.txt
git log | head -n 1 >> jobs.txt

for subj in ${subjects[*]}; do
    for game in ${games[*]}; do
        outfileprefix="${MY_SCRATCH}/VGDL/output/fmri_agentReplay_${subj}_${game}"
        echo ---------------------------------------------------------------------------------
        echo Subject ${subj}, game ${game}, file prefix = $outfileprefix

        # send the job to NCF
        # mem 20000 for all but lemmings & plaqueattach (2 days); for them, 90000 (5 days)
        # OOM helper; up to 50000
        # sprites % 20: time 0-15 for all but lem & PA; for them, 1-15
        #
        sbatch_output=`sbatch -p fasse_gpu --gres=gpu --mem 20001 -t 1-15:20 -o ${outfileprefix}_%j.out -e ${outfileprefix}_%j.err --wrap="./run_fmri_agentReplay.sh ${agent} ${subj} ${game}"`
        # for local testing
        #sbatch_output=`echo Submitted batch job 88725418`
        echo $sbatch_output

        # Append job id to jobs.txt
        #
        sbatch_output_split=($sbatch_output)
        job_id=${sbatch_output_split[3]}
        echo fmri_agentReplay.sh for subject ${subj}, game ${game}: ${outfileprefix}_${job_id}.out -- $sbatch_output >> jobs.txt

        echo watch job status with: sacct -j ${job_id}
        echo watch output with: tail -f ${outfileprefix}_${job_id}.out
        echo watch error with: tail -f ${outfileprefix}_${job_id}.err

        sleep 1
    done
done
