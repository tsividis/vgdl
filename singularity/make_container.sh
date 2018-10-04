#!/bin/bash


CONTNAME="pyenv.simg"
DEFFILE="Singularity"

# copy over the python requirements for automation
if [ ! -f "requirements.txt" ]; then
    cp ../requirements.txt requirements.txt
fi

# if we are running on OpenMind, we need to use `vagrant`
. /etc/os-release
OS=$NAME
if [ "$OS" = "CentOS Linux" ]; then

    # Setup variables to prevent dumps into /home/user
    export VAGRANT_HOME="$PWD/.vagrant.d"
    export VAGRANT_DOTFILE_PATH="$PWD/.vagrant"
    export VAGRANT_SERVER_URL="https://app.vagrantup.com"

    # Get vagrant file if needed
    if [ ! -f "Vagrantfile" ]; then
        vagrant init singularityware/singularity-2.4
    fi

    # initialize vagrant
    vagrant up
    VBoxManage setproperty machinefolder "$PWD"
    vagrant ssh -c "cd /vagrant_data && export SINGULARITY_DISABLE_CACHE=True && \
    	sudo singularity build $CONTNAME $DEFFILE"

    vagrant halt
else
    export SINGULARITY_DISABLE_CACHE=True
	  sudo singularity build $CONTNAME $DEFFILE
fi

# clean up requirements.txt
if [ -f "requirements.txt" ]; then
    rm requirements.txt
fi
