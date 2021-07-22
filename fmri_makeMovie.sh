subjects=( 1 )  #  e.g. subjects=( 1 2 5 6 7 10 )
subj_arg="${subjects[@]}" # stringify it

#games=( 'vgfmri3_chase' 'vgfmri3_helper' 'vgfmri3_bait' 'vgfmri3_lemmings' 'vgfmri3_plaqueAttack' 'vgfmri3_zelda')
#games=( 'vgfmri3_chase' 'vgfmri3_lemmings' 'vgfmri3_plaqueAttack' )
games=('vgfmri3_chase', 'vgfmri3_bait', 'vgfmri3_plaqueAttack')

source activate pedro

for subj in ${subjects[*]}; do
    for game in ${games[*]}; do
        #python fmri_makeMovie.py ${subj} ${game}

        outfileprefix="${MY_SCRATCH}/VGDL/output/fmri_makeMovie_${subj}_${game}"
        echo ---------------------------------------------------------------------------------
        echo Subject ${subj}, game ${game}, file prefix = $outfileprefix

        # send the job to NCF
        sbatch_output=`sbatch -p shared --mem 20001 -t 2-15:20 -o ${outfileprefix}_%j.out -e ${outfileprefix}_%j.err --wrap="./run_fmri_makeMovie.sh ${subj} ${game}"`
        # for local testing
        #sbatch_output=`echo Submitted batch job 88725418`
        echo $sbatch_output

        # Append job id to jobs.txt
        #
        sbatch_output_split=($sbatch_output)
        job_id=${sbatch_output_split[3]}
        echo fmri_makeMovie.sh for subject ${subj}, game ${game}: ${outfileprefix}_${job_id}.out -- $sbatch_output >> jobs.txt

        echo watch job status with: sacct -j ${job_id}
        echo watch output with: tail -f ${outfileprefix}_${job_id}.out
        echo watch error with: tail -f ${outfileprefix}_${job_id}.err

        sleep 1
    done
done
