#!/bin/bash
#
#SBATCH -p fasse # partition (queue)
#SBATCH -c 1 # number of cores
#SBATCH --mem 20000 # memory pool for all cores
#SBATCH -t 0-15:00 # time (D-HH:MM)
#SBATCH -o slurm.%N.%j.out # STDOUT
#SBATCH -e slurm.%N.%j.err # STDERR

echo test
echo $MY_CANNON_LAB

ls -latch $MY_CANNON_LAB/mongo

cd $MY_CANNON_LAB/mongo
mongorestore --host holy7c22103.rc.fas.harvard.edu
