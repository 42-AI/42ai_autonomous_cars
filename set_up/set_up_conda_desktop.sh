#!/usr/bin/env bash

# Setup conda env on Mac desktop.
# Run this script from the set_up folder like this: source set_up_conda_desktop.sh
# https://towardsdatascience.com/a-guide-to-conda-environments-bc6180fc533


# Install miniconda if needed
if [[ ! -e /usr/local/bin/conda ]]
then
    brew cask install miniconda
    conda config --add channels conda-forge
    conda init zsh
    source ~/.zshrc
    echo "Miniconda installed"
fi


# install environment
conda update conda
conda env remove -n patate_py373
conda env create --file ./patate_py373.yml
