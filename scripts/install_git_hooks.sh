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

echo "Explicitly setting pre-commit to use Python 3.12..."
export PRE_COMMIT_PYTHON=python3.12

echo "Shell Script - Installing git hooks ..."
# Install pre-commit
pip install pre-commit
# Install git hooks
pre-commit install

