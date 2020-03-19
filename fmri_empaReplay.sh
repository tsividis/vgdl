# run fmri_empaReplay for a bunch of subjects
# copied from ccnl_fmri_preproc.sh
#

mkdir output

subjects=( 1 )  #  e.g. subjects=( 1 2 5 6 7 10 )
subj_arg="${subjects[@]}" # stringify it

#games=('vgfmri3_sokoban' 'vgfmri3_chase' 'vgfmri3_helper' 'vgfmri3_bait' 'vgfmri3_lemmings' 'vgfmri3_plaqueAttack' 'vgfmri3_zelda')
games=('vgfmri3_chase')

echo ---------------- >> jobs.txt
echo --- $(date): Running fmri_empaReplay for subjects ${subj_arg} in parallel >> jobs.txt
echo ---------------- >> jobs.txt

for subj in ${subjects[*]}; do
    for game in ${games[*]}; do
        outfileprefix="output/fmri_empaReplay_${subj}_${game}"
        echo ---------------------------------------------------------------------------------
        echo Subject ${subj}, game ${game}, file prefix = $outfileprefix

        # send the job to NCF
        #
        sbatch_output=`sbatch -p ncf --mem 100000 -t 2-15:20 -o ${outfileprefix}_%j.out -e ${outfileprefix}_%j.err --wrap="./run_fmri_empaReplay.sh ${subj} ${game}"`
        # for local testing
        #sbatch_output=`echo Submitted batch job 88725418`
        echo $sbatch_output

        # Append job id to jobs.txt
        #
        sbatch_output_split=($sbatch_output)
        job_id=${sbatch_output_split[3]}
        echo fmri_empaReplay.sh for subject ${subj}, game ${game}: ${outfileprefix}_${job_id}.out -- $sbatch_output >> jobs.txt

        echo watch job status with: sacct -j ${job_id}
        echo watch output with: tail -f ${outfileprefix}_${job_id}.out
        echo watch error with: tail -f ${outfileprefix}_${job_id}.err

        sleep 1
    done
done
