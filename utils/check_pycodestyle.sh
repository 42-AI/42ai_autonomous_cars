#!/usr/bin/env bash

input='.'
if [ $1 ]; then
    input=$1
fi

pycodestyle --max-line-length=120 --exclude="**/*.h5" ${input}