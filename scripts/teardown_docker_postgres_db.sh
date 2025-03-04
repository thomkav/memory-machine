#!/bin/bash
set -e # Exit immediately if a command exits with a non-zero status.

CONTAINER_NAME=$(cat docker/container_name__mock_db.txt)

EXISTING_CONTAINER=$(docker container ls -q --filter name="$CONTAINER_NAME")

if [ -n "$EXISTING_CONTAINER" ];
then
    echo "Halting existing container $EXISTING_CONTAINER"
    docker stop "$EXISTING_CONTAINER"
else
    echo "No existing container $EXISTING_CONTAINER"
fi
