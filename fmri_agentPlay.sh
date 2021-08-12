# run fmri_agentPlay for a bunch of subjects
# copied from ccnl_fmri_preproc.sh
#

mkdir output

#subjects=( 1 2 3 4 5 6 7 8 )  #  e.g. subjects=( 1 2 5 6 7 10 )
subjects=( 1 2 )  #  e.g. subjects=( 1 2 5 6 7 10 )
subj_arg="${subjects[@]}" # stringify it

agent='DQN'

echo ---------------- >> jobs.txt
echo --- $(date): Running fmri_agentPlay for subjects ${subj_arg} in parallel >> jobs.txt
echo ---------------- >> jobs.txt
git log | head -n 1 >> jobs.txt

for subj in ${subjects[*]}; do
        outfileprefix="${MY_SCRATCH}/VGDL/output/fmri_agentPlay_${agent}_${subj}"
        echo ---------------------------------------------------------------------------------
        echo Subject ${subj}, file prefix = $outfileprefix

        # send the job to NCF
        #
        sbatch_output=`sbatch -p shared --mem 20001 -t 1-15:20 -o ${outfileprefix}_%j.out -e ${outfileprefix}_%j.err --wrap="source activate pedro; python fmri_agentPlay.py --agent-name=${agent} --subj-id=${subj}"`
        # for local testing
        #sbatch_output=`echo Submitted batch job 88725418`
        echo $sbatch_output

        # Append job id to jobs.txt
        #
        sbatch_output_split=($sbatch_output)
        job_id=${sbatch_output_split[3]}
        echo fmri_agentPlay.sh for subject ${subj}: ${outfileprefix}_${job_id}.out -- $sbatch_output >> jobs.txt

        echo watch job status with: sacct -j ${job_id}
        echo watch output with: tail -f ${outfileprefix}_${job_id}.out
        echo watch error with: tail -f ${outfileprefix}_${job_id}.err

        sleep 1
done
