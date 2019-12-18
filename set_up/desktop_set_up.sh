#!/usr/bin/env bash

# Setup conda env on Mac desktop
# Run this script from the utils folder like this: source desktop_set_up.sh


if [[ ! -e /usr/local/bin/conda ]]
then
    brew cask install miniconda
    conda config --add channels conda-forge
    conda init zsh
    source ~/.zshrc
    echo "Mini conda installed"
fi

conda update conda

conda env remove -n patate-env
conda env create -n patate-env python=3.7 -f ./patate-env.yml

conda activate patate-env
echo "patate-env activated"
