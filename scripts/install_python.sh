#!/bin/bash

echo "Makefile - Installing Python3, depending on OS ..."

# confirm that python version is passed as argument
if [ -z "$1" ]; then
    echo "Makefile - Python version not passed as argument."
    exit 1
fi

echo "Makefile - Python version is $1, skipping if already installed ..."

# If MacOS, install pyenv
if [ "$(uname -s)" = "Darwin" ]; then
    # If pyenv is not installed, install it
    if ! command -v pyenv 1>/dev/null 2>&1; then
        echo "Makefile - pyenv is not installed, installing it ..."
        brew install pyenv
        echo "Makefile - Done installing pyenv."
    fi
elif [ "$(uname -s)" = "Linux" ]; then
    # If pyenv is not installed, install it
    if ! command -v pyenv 1>/dev/null 2>&1; then
        echo "Makefile - pyenv is not installed, installing it ..."
        curl https://pyenv.run | bash
        echo "Makefile - Done installing pyenv."
    fi
else
    echo "Makefile - OS not supported."
    exit 1
fi

# If pyenv is installed, use it to install the specified version of Python
if command -v pyenv 1>/dev/null 2>&1; then

    # If on CircleCI, upgrade pyenv
    if [ "$CIRCLECI" = "true" ]; then
        echo "Makefile - Upgrading pyenv ..."
        cd /opt/circleci/.pyenv/plugins/python-build/../.. || exit
        git fetch origin master
        git reset --hard origin/master
        cd - || exit
        echo "Makefile - Done upgrading pyenv."
    fi

    echo "Makefile - pyenv is installed, using it to install Python $1, skipping if already installed ..."
    pyenv install "$1" -s # install the specified version of Python, skipping if already installed
    pyenv global "$1" # set the installed version as the global version
    echo "Makefile - Done installing Python $1."
    exit 0
else
    echo "Makefile - pyenv is not installed, exiting."
    exit 1
fi

echo "Makefile - Done installing Python3."
