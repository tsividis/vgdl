#! /bin/bash
for i in {0..5} 
do 
    python -m vgdl.parallel_planning --game_number=$i & 
done
