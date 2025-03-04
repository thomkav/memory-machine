#!/bin/bash

# Check if .venv directory exists
if [ ! -d ".venv" ]; then
    echo "The .venv directory doesn't exist. Please create it before running this script."
    exit 1
fi

echo "Shell Script - Activating virtual environment ..."
#shellcheck disable=SC1091
. .venv/bin/activate
echo "Shell Script - Done activating virtual environment."

echo "Shell Script - Installing dependencies using pip ..."
.venv/bin/pip install --upgrade pip
.venv/bin/pip install -r requirements.txt
.venv/bin/pip install -r requirements-dev.txt
echo "Shell Script - Done installing dependencies."