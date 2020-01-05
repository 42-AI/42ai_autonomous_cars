#!/usr/bin/env bash

# This script aims to fix import errors
# Run this script from the set_up folder like this: source set_pythonpath.sh

PROJECT_DIRECTORY=$(dirname $PWD)

if [[ -z $PYTHONPATH ]]
then
    export PYTHONPATH="$PROJECT_DIRECTORY"
    source ~/.zshrc
elif [[ $PYTHONPATH != *$PROJECT_DIRECTORY* ]]
then
    export PYTHONPATH="$(dirname $PWD):$PYTHONPATH"
    source ~/.zshrc
fi

python -V
echo "PYTHONPATH is now: $PYTHONPATH. It is independant of any conda environment"
