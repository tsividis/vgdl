#!bin/bash

# Build docker file. You should login with "docker login", but since you only have
# to do this once, I'm not putting it on the script
sudo docker build -t ptsividis/vgdl-default-parameters .

# Modify this to contain whichever set you want to run
# Each container's log file will be written inside that container, under the name game_$i_output.txt
# (this is just because I don't know how of a clean way of writing them to the local
# directory)
for i in {0..14}
do
  sudo docker run ptsividis/vgdl-default-parameters python -m vgdl.parallel_planning --game_number=$i >> game_$i_output.txt
done

# There is a small tradeoff here between giving the logs unique names vs. not:
# the first option allows you to put them all in your local directory without
# fear of overwriting stuff, but you do have to know the game number in order
# to access them remotely
