#!/usr/bin/env bash

# Create envs with pyenv. Run it from the set_up folder with `source pyenv.sh`

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

    # install package for the xbox driver
    sudo apt-get install xboxdrv

    # install pyenv
    sudo apt-get install bzip2 libbz2-dev libreadline6 libreadline6-dev libffi-dev libssl1.0-dev sqlite3 libsqlite3-dev -y
    git clone git://github.com/yyuu/pyenv.git ~/.pyenv
    git clone https://github.com/pyenv/pyenv-virtualenv.git $(pyenv root)/plugins/pyenv-virtualenv
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

pyenv install 2.7.13
pyenv install 3.5.3
pyenv install 3.7.5
pyenv install 3.8.0


source ~/.zshrc

pyenv versions

echo "creating virtualenvs"
pyenv virtualenv 3.5.3 venv_3.5.3
pyenv virtualenv 3.7.5 venv_3.7.5

source ~/.zshrc

echo "source .zshrc"

pyenv activate venv_3.5.3
pip install --upgrade pip setuptools wheel
pip install -r requirements_py353.txt
pyenv deactivate

pyenv activate venv_3.7.5
pip install --upgrade pip setuptools wheel
pip install -r requirements_py375.txt
pyenv deactivate

cd ..
rm .python-version
pyenv global 3.7.5
pyenv local venv_3.7.5

pyenv versions
pyenv global
pyenv local