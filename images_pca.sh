# run images_pca for a bunch of 
# copied from ccnl_fmri_preproc.sh
#

mkdir output


echo ---------------- >> jobs.txt
echo --- $(date): Running images_pca for  >> jobs.txt
echo ---------------- >> jobs.txt
git log | head -n 1 >> jobs.txt 

outfileprefix="${MY_SCRATCH}/VGDL/output/images_pca"
echo ---------------------------------------------------------------------------------
echo file prefix = $outfileprefix

# send the job to NCF
#
sbatch_output=`sbatch -p fasse --mem 20001 -t 1-15:20 -o ${outfileprefix}_%j.out -e ${outfileprefix}_%j.err --wrap="source activate pedro3; python images_pca.py"`
# for local testing
#sbatch_output=`echo Submitted batch job 88725418`
echo $sbatch_output

# Append job id to jobs.txt
#
sbatch_output_split=($sbatch_output)
job_id=${sbatch_output_split[3]}
echo images_pca.sh: ${outfileprefix}_${job_id}.out -- $sbatch_output >> jobs.txt

echo watch job status with: sacct -j ${job_id}
echo watch output with: tail -f ${outfileprefix}_${job_id}.out
echo watch error with: tail -f ${outfileprefix}_${job_id}.err

sleep 1
