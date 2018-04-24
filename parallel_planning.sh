#! /bin/bash
for i in {0..11}
do
  sbatch --mem=10000 -c 4 --wrap="python -m vgdl.parallel_planning --game_number=$i"
done
