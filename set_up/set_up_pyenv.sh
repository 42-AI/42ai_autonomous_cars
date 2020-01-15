#!/usr/bin/env bash

# Create envs with pyenv. Run it from the set_up folder with `source set_up_pyenv.sh`

os=$(uname)

if [ -z $PYENV_ROOT ]
then
  if [ "$os" = "Darwin" ]
  then
    echo "os is Darwin"
    brew install pyenv
    brew install pyenv-virtualenv
  elif [ "$os" = "Linux" ]
  then
    echo "os is Linux"
    sudo apt-get update

    # install pyenv
    sudo apt-get install bzip2 libbz2-dev libreadline6 libreadline6-dev libffi-dev libssl1.0-dev sqlite3 libsqlite3-dev -y
    sudo apt-get install liblzma-dev -y
    git clone git://github.com/yyuu/pyenv.git ~/.pyenv
    git clone https://github.com/pyenv/pyenv-virtualenv.git ~/.pyenv/plugins/pyenv-virtualenv
  else
    echo "OS not recognized"
    exit
  fi
fi

if [ -z $PYENV_ROOT ]
then
  echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.zshrc
  echo 'export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.zshrc
  echo -e 'if command -v pyenv 1>/dev/null 2>&1; then\n  eval "$(pyenv init -)"\n  eval "$(pyenv virtualenv-init -)"\nfi' >> ~/.zshrc
  source $HOME/.zshrc
fi

pyenv install 3.7.3
# pyenv install 3.8.0


source $HOME/.zshrc

pyenv versions

echo "creating virtualenvs"
pyenv virtualenv 3.7.3 venv_3.7.3

source ~/.zshrc

echo "source .zshrc"

# Setting environment
pyenv activate venv_3.7.3
pip install --upgrade pip setuptools wheel
if [ "$os" = "Darwin" ]
  then
    echo "os is Darwin"
    pip install -r requirements_desktop_py373.txt
  elif [ "$os" = "Linux" ]
  then
    echo "os is Linux"
    # install package for the xbox driver
    sudo apt-get install xboxdrv

    sudo apt-get install -y libhdf5-dev libc-ares-dev libeigen3-dev
    pip install keras_applications==1.0.8 --no-deps
    pip install keras_preprocessing==1.1.0 --no-deps
    pip install h5py==2.9.0
    sudo apt-get install -y openmpi-bin libopenmpi-dev
    sudo apt-get install -y libatlas-base-dev
    pip install six mock
    wget https://github.com/PINTO0309/Tensorflow-bin/raw/master/tensorflow-2.0.0-cp37-cp37m-linux_armv7l.whl
    pip install tensorflow-2.0.0-cp37-cp37m-linux_armv7l.whl
    pip install -r requirements_raspberry_pi_py373.txt
    rm tensorflow-2.0.0-cp37-cp37m-linux_armv7l.whl
  fi
pyenv deactivate


# Setting pyenv global and local
cd ..
pyenv global 3.7.3
pyenv local venv_3.7.3

pyenv versions
pyenv global
pyenv local
