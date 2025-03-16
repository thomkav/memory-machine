#!/bin/bash
set -e

echo "Activating virtual environment..."
# shellcheck disable=SC1091
source .venv/bin/activate

rio run