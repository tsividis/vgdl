# script for calling the Mongo server
echo ---------------- >> jobs.txt
echo --- $(date): Running mongostart.sh >> jobs.txt
echo ---------------- >> jobs.txt

outfileprefix="${MY_SCRATCH}/VGDL/output/mongostart"
echo ---------------------------------------------------------------------------------
echo mongostart.sh

# send the job to NCF
sbatch_output=`sbatch -p fasse --mem 20001 -t 6-15:20 -o ${outfileprefix}_%j.out -e ${outfileprefix}_%j.err --wrap="hostname; echo ${MY_HOME}; ${MY_HOME}/mongostart.sh"`
# for local testing
#sbatch_output=`echo Submitted batch job 88725418`
echo $sbatch_output

# Append job id to jobs.txt
#
sbatch_output_split=($sbatch_output)
job_id=${sbatch_output_split[3]}
echo mongostart.sh: ${outfileprefix}_${job_id}.out -- $sbatch_output >> jobs.txt

echo watch job status with: sacct -j ${job_id}
echo watch output with: tail -f ${outfileprefix}_${job_id}.out
echo watch error with: tail -f ${outfileprefix}_${job_id}.err

sleep 1
