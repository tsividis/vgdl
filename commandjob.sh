# convenience script for calling single or set of commands
# EXAMPLE: ./commandjob.sh "echo 12tf; hostname"
command=${1}

echo ---------------- >> jobs.txt
echo --- $(date): Running ${command} >> jobs.txt
echo ---------------- >> jobs.txt

outfileprefix="${MY_SCRATCH}/VGDL/output/command"
echo ---------------------------------------------------------------------------------
echo $command

# send the job to NCF
sbatch_output=`sbatch -p fasse --mem 20001 -t 0-15:20 -o ${outfileprefix}_%j.out -e ${outfileprefix}_%j.err --wrap="${command}"`
# for local testing
#sbatch_output=`echo Submitted batch job 88725418`
echo $sbatch_output

# Append job id to jobs.txt
#
sbatch_output_split=($sbatch_output)
job_id=${sbatch_output_split[3]}
echo ${command}: ${outfileprefix}_${job_id}.out -- $sbatch_output >> jobs.txt

echo watch job status with: sacct -j ${job_id}
echo watch output with: tail -f ${outfileprefix}_${job_id}.out
echo watch error with: tail -f ${outfileprefix}_${job_id}.err

sleep 1
