#! /usr/bin/bash

git clone https://github.com/deep5050/radio-active.git && cd radio-active
pip install -r requirements
echo "alias radio-active='python3 $PWD/radio-active'" >> ~/.bashrc

# run `source ~/.bashrc` then