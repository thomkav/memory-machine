#!/bin/sh
set -e # Exit immediately if a command exits with a non-zero status.

# This script runs the unit tests with pytest and coverage.
export PYTHONPATH=.:$PYTHONPATH

echo "Running unit tests..."

echo "Setting environment variables..."
# shellcheck disable=SC1091
. scripts/set_env_testing.sh
echo "Environment variables set."

echo "Setting up virtual environment..."
# shellcheck disable=SC1091
. .venv/bin/activate
echo "Virtual environment ready."

echo "Starting unit tests..."

# Determine if we are running all unit tests or a subset.
TEST_FILE_PATTERN="${TEST_FILE_PATTERN:-}"  # The file pattern for the unit tests to run.
TEST_CLASS="${TEST_CLASS:-}"  # The class pattern for the unit tests to run.

# Set the theme for pytest. This is just to address this issue:
#   ERROR: PYTEST_THEME environment variable had an invalid value: 
#   'MOCKED_PYTEST_THEME_VALUE'. Only valid pygment styles are allowed.
# If this is not an issue for you, you can remove these lines.
unset PYTEST_THEME
export PYTEST_THEME=default

if [ -z "$TEST_FILE_PATTERN" ] && [ -z "$TEST_CLASS" ]; then
    echo "Running all unit tests with coverage..."
    pytest --cov=. --cov-report=term-missing --cov-report=html
else
    # Determine if we are running unit tests for a specific file or class.
    # Note: Adjusting for pytest specifics might require handling the patterns differently.

    if [ -n "$TEST_FILE_PATTERN" ]; then
        echo "Running unit tests for file pattern: $TEST_FILE_PATTERN"
        pytest -vv -rA -k "$TEST_FILE_PATTERN"
    fi

    if [ -n "$TEST_CLASS" ]; then
        echo "Running unit tests for class pattern: $TEST_CLASS"
        # This might need adjustment based on how you want to filter by class with pytest.
        pytest -vv -rA -k "$TEST_CLASS"
    fi
fi

echo "Unit tests complete."

LOGICAL_ENVIRONMENT="${LOGICAL_ENVIRONMENT:-}"
GITHUB_ACTIONS="${GITHUB_ACTIONS:-}"

if [ -z "$LOGICAL_ENVIRONMENT" ] && [ "$GITHUB_ACTIONS" != "true" ] && [ -z "$TEST_FILE_PATTERN" ] && [ -z "$TEST_CLASS" ]; then
    echo "Opening coverage report in browser..."
    open htmlcov/index.html
    echo "Done."
fi
