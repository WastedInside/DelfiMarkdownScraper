#!/bin/bash

# Ensure pip is installed
if ! command -v pip &> /dev/null
then
    echo "pip could not be found, please install pip first."
    exit
fi

# Install the required packages
pip install -r requirements.txt
