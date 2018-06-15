#!bin/bash

# Build docker file. You should login with "docker login", but since you only have
# to do this once, I'm not putting it on the script
## build an image with this particular name
sudo docker build -t ptsividis/vgdl-parallel-model .

## Bind host (AWS) file system (in particular, the vgdl folder) to the /source directory in the Docker image
## and then run /source/run_games.py
sudo docker run -v /home/ubuntu/vgdl:/source ptsividis/default_parameters python /source/run_games.py

## doing so will, say, create local .csv files (or whatever) that are directly accessible from the host (AWS) directory.

