# Use an official Python runtime as a parent image
FROM python:2

# Set the working directory to /app
WORKDIR /home/loula/Programming/python/vgdl

# Copy the current directory contents into the container at /app
ADD . .

# OpenAI gym stuff
RUN apt-get update \
    && apt-get install -y libav-tools \
    python-setuptools \
    libpq-dev \
    libjpeg-dev \
    curl \
    cmake \
    swig \
    freeglut3 \
    python-opengl \
    libboost-all-dev \
    libglu1-mesa \
    libglu1-mesa-dev \
    libsdl2-2.0-0\
    libgles2-mesa-dev \
    libsdl2-dev \
    wget \
    unzip \
    git \
    xserver-xorg-input-void \
    xserver-xorg-video-dummy \
    python-gtkglext1 \
    xpra \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && easy_install pip


# opencv stuff
# Various Python and C/build deps
RUN apt-get update && apt-get install -y \ 
    wget \
    build-essential \ 
    cmake \ 
    git \
    unzip \ 
    pkg-config \
    python-dev \ 
    python-opencv \ 
    libopencv-dev \ 
    libav-tools  \ 
    libjpeg-dev \ 
    libpng-dev \ 
    libtiff-dev \ 
    libjasper-dev \ 
    libgtk2.0-dev \ 
    python-numpy \ 
    python-pycurl \ 
    libatlas-base-dev \
    gfortran \
    webp \ 
    python-opencv \ 
    qt5-default \
    libvtk6-dev \ 
    zlib1g-dev

# Install Open CV - Warning, this takes absolutely forever
RUN mkdir -p ~/opencv cd ~/opencv && \


# Install any needed packages specified in requirements.txt
RUN pip install --trusted-host pypi.python.org -r requirements.txt

# Make port 80 available to the world outside this container
EXPOSE 80

# Define environment variable
ENV NAME World

