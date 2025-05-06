#!/bin/bash
set -e

echo "Setting up virtual environment..."
# shellcheck disable=SC1091
. .venv/bin/activate
echo "Virtual environment ready."

.venv/bin/python set_copilot_instructions.py "$@"
