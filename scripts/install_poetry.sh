#!/bin/bash

# Check if .venv directory exists
if [ ! -d ".venv" ]; then
    echo "The .venv directory doesn't exist. Please create it before running this script."
    exit 1
fi

# Log poetry installation
echo "Shell Script - Installing poetry ..."

# Upgrade pip using pip from the .venv directory
#shellcheck disable=SC1091
. .venv/bin/activate

# Read poetry version and install
POETRY_VERSION=$(cat ./poetry.version)
pip install poetry=="$POETRY_VERSION" --quiet

# Log completion
echo "Shell Script - Done installing poetry."
