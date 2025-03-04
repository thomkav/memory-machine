#!/bin/bash

# install coreutils depending on os
echo "Installing coreutils..."
if [[ "$OSTYPE" == "darwin"* ]]; then
    brew install coreutils
fi
