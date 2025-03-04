#!/bin/bash
set -e # Exit immediately if a command exits with a non-zero status.
# Dump the schema of a PostgreSQL database.

# Set environment variables.
echo "Setting environment variables..."
# shellcheck disable=SC1091
source scripts/set_env_testing.sh
echo "Environment variables set."


CONTAINER_NAME__MOCK_DB=$(cat docker/container_name__mock_db.txt)
# Confirm that the container name is set.
if [ -z "$CONTAINER_NAME__MOCK_DB" ]; then
    echo "CONTAINER_NAME__MOCK_DB is not set. Exiting."
    exit 1
fi

# Dump the schema of the database.
SCHEMA_DUMP_FILE_AFTER_RUN="db/db_schema_name/schema_dump_after_run.sql"
echo "Dumping schema of $PGDATABASE database..."
docker exec -i "$CONTAINER_NAME__MOCK_DB" pg_dump -U "$PGUSER" -s -n schema_name "$PGDATABASE" > $SCHEMA_DUMP_FILE_AFTER_RUN
echo "Schema of $PGDATABASE database dumped to $SCHEMA_DUMP_FILE_AFTER_RUN."

SCHEMA_DUMP_FILE="db/db_schema_name/schema_dump.sql"
echo "Comparing schema dump files..."
# Compare the schema dump files.
SCHEMA_PASSES=1
if cmp -s "$SCHEMA_DUMP_FILE" "$SCHEMA_DUMP_FILE_AFTER_RUN"; then
    echo "Schema dump files are the same."
else
    echo "Schema dump files are different. We expected the schema dump file to be the same after running the migrations."
    echo "Diff with the original schema dump file:"
    diff "$SCHEMA_DUMP_FILE" "$SCHEMA_DUMP_FILE_AFTER_RUN" || true
    echo "Run \`make db-tests\` to write the computed schema dump file. Inspect the changed schema dump, and commit if output is expected."
    SCHEMA_PASSES=0
fi

# Copy the computed schema dump file to the original schema dump file.
echo "Copying the computed schema dump file to the original schema dump file..."
cp "$SCHEMA_DUMP_FILE_AFTER_RUN" "$SCHEMA_DUMP_FILE"

# Exit with an error if the schema dump files are different.
if [ $SCHEMA_PASSES -eq 0 ]; then
    echo "Schema dump files are different. Exiting. If working as expected, commit the changes to the schema dump file."
    exit 1
fi