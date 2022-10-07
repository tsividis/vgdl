# run HRR_states for a bunch of subjects
# copied from ccnl_fmri_preproc.sh
#

mkdir output

#subjects=( 1 2 3 4 5 6 7 8 )  #  e.g. subjects=( 1 2 5 6 7 10 )
#subjects=( 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31 32  )  #  e.g. subjects=( 1 2 5 6 7 10 )
#subjects=( 1 2 3 4 5 6 7 8 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31 )  #  e.g. subjects=( 1 2 5 6 7 10 )
#subjects=( 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31 32 )  #  e.g. subjects=( 1 2 5 6 7 10 )
subjects=( 1 )  #  e.g. subjects=( 1 2 5 6 7 10 )
subj_arg="${subjects[@]}" # stringify it

K=10 # 10
N=10 # 10
E=0.05 # 0.05
nsamples=100 # 100
batch_size=10 # 10
normalize=1 # 1
type='kernel' # kernel

# RDM
dist='correlation'
glmodel=24
agg='avg'

echo ---------------- >> jobs.txt
echo --- $(date): Running HRR_states for subjects ${subj_arg} in parallel >> jobs.txt
echo ---------------- >> jobs.txt
git log | head -n 1 >> jobs.txt 

for subj in ${subjects[*]}; do
        outfileprefix="${MY_SCRATCH}/VGDL/output/HRR_states_${subj}"
        echo ---------------------------------------------------------------------------------
        echo Subject ${subj}, file prefix = $outfileprefix

        # send the job to NCF
        #
        sbatch_output=`sbatch -p fasse --mem 60001 -t 2-06:20 -o ${outfileprefix}_%j.out -e ${outfileprefix}_%j.err --wrap="source activate pedro; python HRR_states.py --subj-id=${subj} --K=${K} --N=${N} --E=${E} --nsamples=${nsamples} --batch-size=${batch_size} --normalize=${normalize} --type=${type}  --dist=${dist} --glmodel=${glmodel} --agg=${agg}"`
        # for local testing
        #sbatch_output=`echo Submitted batch job 88725418`
        echo $sbatch_output

        # Append job id to jobs.txt
        #
        sbatch_output_split=($sbatch_output)
        job_id=${sbatch_output_split[3]}
        echo HRR_states.sh for subject ${subj}: ${outfileprefix}_${job_id}.out -- $sbatch_output >> jobs.txt

        echo watch job status with: sacct -j ${job_id}
        echo watch output with: tail -f ${outfileprefix}_${job_id}.out
        echo watch error with: tail -f ${outfileprefix}_${job_id}.err

        sleep 1
done
