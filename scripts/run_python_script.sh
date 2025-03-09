#!/bin/bash
set -e

# This script runs a Python script with the correct Python path and environment
# Usage: run_python_script.sh <python_script_path> [args...]

# Get the project root directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Ensure we're in the project root
cd "$PROJECT_ROOT"

# Activate the virtual environment if it exists
if [ -d ".venv" ]; then
    echo "Activating virtual environment..."
    # shellcheck disable=SC1091
    source .venv/bin/activate
fi

# Set Python path to include the project root
export PYTHONPATH="$PROJECT_ROOT:$PYTHONPATH"

# Check if the script exists
SCRIPT_PATH="$1"
if [ ! -f "$SCRIPT_PATH" ]; then
    echo "Error: Python script not found: $SCRIPT_PATH"
    exit 1
fi

# Remove the first argument (script path)
shift

# Run the Python script with the remaining arguments
echo "Running Python script: $SCRIPT_PATH"
python "$SCRIPT_PATH" "$@"
