#!/bin/bash
set -e

# This script runs the switch_copilot_instructions.py script

# Get the script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Run the Python script with the generic runner
"$SCRIPT_DIR/run_python_script.sh" "$SCRIPT_DIR/switch_copilot_instructions.py" "$@"
