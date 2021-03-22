#!/bin/bash
#================================================#
#  INSTALLING TENSORFLOW ON UBUNTU               #
#================================================#
sudo apt update
sudo apt install python3-dev python3-pip python3-venv

python3 -m venv --system-site-packages ./venv
source ./venv/bin/activate  # sh, bash, or zsh
pip install --upgrade pip
pip list  # show packages installed within the virtual environment

deactivate  # don't exit until you're done using TensorFlow

pip3 install --user --upgrade tensorflow  # install in $HOME

#=================================================#
#Reference:https://www.tensorflow.org/install/pip #
#=================================================#
