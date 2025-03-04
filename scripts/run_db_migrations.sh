#!/bin/bash
set -e # Exit immediately if a command exits with a non-zero status.

FLYWAY_VERSION="$(cat .flyway-version)"

FLYWAY_CONTAINER_NAME="project-name__flyway-$FLYWAY_VERSION"

echo "> Removing existing flyway docker container if it exists."
CONTAINER_EXISTS=$(docker container ls -q --filter name="$FLYWAY_CONTAINER_NAME")
if [ -n "$CONTAINER_EXISTS" ]; then
  docker container rm -f "$FLYWAY_CONTAINER_NAME" || true
  echo "> flyway docker container removed."
fi

MIGRATION_DIR="$(pwd)/db/unspecified/sql"
MIGRATION_DIR_ABSOLUTE=$(realpath "$MIGRATION_DIR")
# Ensure migration directory exists and is not empty.
if [ ! -d "$MIGRATION_DIR_ABSOLUTE" ] || [ -z "$(ls -A "$MIGRATION_DIR_ABSOLUTE")" ]; then
  echo "> No migrations found. Exiting."
  exit 0
else
  echo "> Migrations found, printing contents:"
  ls -la "$MIGRATION_DIR_ABSOLUTE"
fi

echo "> Running DB migrations."
docker run --rm \
  --name "$FLYWAY_CONTAINER_NAME" \
  --network=host \
  -e "FLYWAY_URL=jdbc:postgresql://$PGHOST:$PGPORT/$PGDATABASE" \
  -e "FLYWAY_USER=$PGUSER" \
  -e "FLYWAY_PASSWORD=$PGPASSWORD" \
  -e "FLYWAY_SCHEMAS=unspecified" \
  -e "FLYWAY_LOCATIONS=filesystem:/migrations" \
  -v "$MIGRATION_DIR_ABSOLUTE:/migrations" \
  "flyway/flyway:$FLYWAY_VERSION" \
  migrate
echo "> Migrations complete."