#!/bin/bash
set -e # Exit immediately if a command exits with a non-zero status.
set -o pipefail # The exit status of the last command that threw a non-zero exit code in a pipeline.


echo "Setting up PostgreSQL database..."

echo "Setting environment variables"
# shellcheck disable=SC1091
source scripts/set_env_testing.sh
echo "Environment variables set."

# This script initializes and fully migrates a PostgreSQL database for local testing.
CONTAINER_NAME=$(cat docker/container_name__mock_db.txt)
export CONTAINER_NAME

EXISTING_CONTAINER=$(docker container ls -q --filter name="$CONTAINER_NAME")

if [ -n "$EXISTING_CONTAINER" ];
then
    echo "Removing existing container $EXISTING_CONTAINER"
    docker stop "$EXISTING_CONTAINER"
fi


echo "Starting PostgreSQL database in Docker container"
docker run --rm -d \
  --name "${CONTAINER_NAME}" \
  --publish "${PGPORT}:5432" \
  --env "POSTGRES_USER=${PGUSER}" \
  --env "POSTGRES_PASSWORD=${PGPASSWORD}" \
  --env "POSTGRES_DB=${PGDATABASE}" \
  --env "PGUSER=${PGUSER}" \
  --env "PGDATABASE=${PGDATABASE}" \
  --env "PGPASSWORD=${PGPASSWORD}" \
  --env "PGSCHEMA=${PGSCHEMA}" \
  postgres:12.7

echo "Waiting for PostgreSQL to start"
timeout 90s bash -c "until docker exec ${CONTAINER_NAME} pg_isready -h 127.0.0.1 ; do sleep 1 ; done"
echo "PostgreSQL started"

echo "Running all local migrations"
bash scripts/run_all_local_migrations.sh
echo "All local migrations complete."

echo "Listing all schemas in local PostgreSQL database..."
docker exec -i "$CONTAINER_NAME" psql -U "$PGUSER" -d "$PGDATABASE" -c "\dn"
echo "Done."

echo "Database ready with dummy schemas."
