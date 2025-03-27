#!/bin/bash

# Download model
wget -O model.h5 https://github.com/Hershy23/Color/releases/download/v2.0/model.h5

# Upgrade pip
pip install --upgrade pip

# Install dependencies from requirements.txt
pip install -r requirements.txt
