#!/usr/bin/env bash

# To run this file: `source connect_ssh.sh`


# Check for xbox driver and python-picamera
sudo apt-get update
sudo apt-get install xboxdrv
sudo apt-get install python3-picamera
sudo apt autoremove

# Update pip and setuptools
# sudo apt-get remove python3-pip
if [[ ! -e get-pip.py ]]
then
  wget https://bootstrap.pypa.io/get-pip.py
  sudo python3 get-pip.py
  # sudo pip3 install --upgrade setuptools
fi


# Create venv
python3 -m venv patate_py353
source patate_py353/bin/activate
pip3 install --upgrade pip setuptools
pip3 install -r requirements_py353.txt

echo "patate_py353 env created."
