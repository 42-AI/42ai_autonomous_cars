#!/usr/bin/env bash


apt-get remove python3-pip
wget https://bootstrap.pypa.io/get-pip.py
python3 get-pip.py
sudo pip3 install --upgrade setuptools

# cf set_up habituel


#
#matplotlib
#picamera
#tensorflow==1.9.0
#keras==2.1.5
#Pillow
#pandas
#numpy
#h5py
#adafruit-pca9685

## XboxControler:
# sudo apt-get install xboxdrv