#!/usr/bin/env bash

# Setup  conda env on Raspberry Pi
# Run this script from the utils folder like this: source desktop_set_up.sh
# Note picamera and xbox driver are installed separately with apt-get

if [[ ! -e ~/miniconda ]]
then
    wget https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ~/miniconda.sh
    bash ~/miniconda.sh -b -p ~/miniconda
    rm ~/miniconda.sh
    export PATH=~/miniconda/bin:$PATH
    echo "Mini conda installed"
fi

# Check for xbox driver and python-picamera
sudo apt-get update
sudo apt-get install xboxdrv
sudo apt-get install python3-picamera

conda update conda
conda env remove -n patate-env
conda env create -n patate-env python=3.7 -f ./patate-env.yml
conda activate patate-env
sudo pip install picamera

echo "patate-env activated"

## XboxControler:
# sudo apt-get install xboxdrv

# sudo pip install picamera
#If you are using the Raspbian distro, it is best to install picamera using the system’s package manager: apt. This will ensure that picamera is easy to keep up to date, and easy to remove should you wish to do so. It will also make picamera available for all users on the system. To install picamera using apt simply:
#
#$ sudo apt-get update
#$ sudo apt-get install python-picamera python3-picamera