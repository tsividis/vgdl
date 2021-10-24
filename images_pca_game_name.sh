# run images_pca for a bunch of 
# copied from ccnl_fmri_preproc.sh
#

mkdir output

game_names=( 'vgfmri3_chase' )
#game_names=( 'vgfmri3_chase' 'vgfmri3_helper' 'vgfmri3_bait' 'vgfmri3_lemmings' 'vgfmri3_plaqueAttack' 'vgfmri3_zelda')
#game_names=( 'vgfmri4_chase' 'vgfmri4_helper' 'vgfmri4_bait' 'vgfmri4_lemmings' 'vgfmri4_avoidgeorge' 'vgfmri4_zelda')

echo ---------------- >> jobs.txt
echo --- $(date): Running images_pca for  >> jobs.txt
echo ---------------- >> jobs.txt
git log | head -n 1 >> jobs.txt 

for game_name in ${game_names[*]}; do
        outfileprefix="${MY_SCRATCH}/VGDL/output/images_pca_${game_name}"
        echo ---------------------------------------------------------------------------------
        echo game name ${game_name}, file prefix = $outfileprefix

        # send the job to NCF
        #
        sbatch_output=`sbatch -p fasse --mem 20001 -t 1-15:20 -o ${outfileprefix}_%j.out -e ${outfileprefix}_%j.err --wrap="source activate pedro3; python images_pca.py ${game_name}"`
        # for local testing
        #sbatch_output=`echo Submitted batch job 88725418`
        echo $sbatch_output

        # Append job id to jobs.txt
        #
        sbatch_output_split=($sbatch_output)
        job_id=${sbatch_output_split[3]}
        echo images_pca.sh for game_name ${game_name}: ${outfileprefix}_${job_id}.out -- $sbatch_output >> jobs.txt

        echo watch job status with: sacct -j ${job_id}
        echo watch output with: tail -f ${outfileprefix}_${job_id}.out
        echo watch error with: tail -f ${outfileprefix}_${job_id}.err

        sleep 1
done
