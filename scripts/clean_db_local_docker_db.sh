#!/#!/bin/bash
set -e # Exit immediately if a command exits with a non-zero status.

echo "Setting environment variables for local..."
# shellcheck disable=SC1091
. scripts/set_env_testing.sh
echo "Environment variables set for local."

handle_error() {
    echo "An error occurred. Exiting."
    exit 1
}

trap handle_error ERR

FLYWAY_VERSION="$(cat .flyway-version)"

# Clean the database, using a flyway docker container
echo "Running flyway clean"
( 
    timeout 180s docker run --rm \
      --network=host \
      -e "FLYWAY_URL=jdbc:postgresql://$PGHOST:$PGPORT/$PGDATABASE" \
      -e "FLYWAY_USER=$PGUSER" \
      -e "FLYWAY_PASSWORD=$PGPASSWORD" \
      -e "FLYWAY_TABLE=$FLYWAY_TABLE" \
      -e "FLYWAY_SCHEMAS=unspecified" \
      -e "FLYWAY_CLEAN_DISABLED=false" \
      "flyway/flyway:$FLYWAY_VERSION" \
      clean
)

EXIT_STATUS=$?

if [ $EXIT_STATUS -eq 124 ]; then
    echo "The operation timed out."
    exit 124
elif [ $EXIT_STATUS -ne 0 ]; then
    echo "Docker command failed with exit status $EXIT_STATUS"
    exit $EXIT_STATUS
fi

echo "Database cleaned."