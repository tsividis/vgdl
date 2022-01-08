# Use a python-ubuntu image as parent
FROM ubuntu:16.04

# Update
RUN apt-get update

# Install python dependencies
RUN apt-get update \
  && apt-get install -y wget gcc make openssl libffi-dev libgdbm-dev libsqlite3-dev libssl-dev zlib1g-dev \
  && apt-get clean

# Pygame dependencies
RUN DEBIAN_FRONTEND="noninteractive" apt-get install tzdata -y
RUN apt-get install libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev libfreetype6-dev \
                    libsmpeg-dev libportmidi-dev libjpeg-dev python-setuptools \
                    libswscale-dev libavformat-dev libavcodec-dev -y

# Build Python from source
RUN apt install python-minimal

# Get pip
RUN wget "https://bootstrap.pypa.io/pip/2.7/get-pip.py" && python get-pip.py && rm get-pip.py
RUN python -m pip install --upgrade pip
RUN python --version \
  && pip --version

# Copy the current directory contents into the container at /app
WORKDIR /root/rc_rl/
COPY requirements.txt /root/rc_rl/

# Install any needed packages specified in requirements.txt
RUN python -m pip install -r requirements.txt

copy . /root/rc_rl/
# Workdir
WORKDIR /root/rc_rl
