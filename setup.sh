#!/bin/bash
pyenv install 3.10.12  # Install Python 3.10
pyenv global 3.10.12   # Set it as the global version
pip install --upgrade pip
pip install -r requirements.txt
