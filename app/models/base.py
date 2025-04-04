"""This module covers core objects related to connecting to the DB.

Details specific to schemas and tables belong in a separate file.
"""

import psycopg2
from db.config import PGDATABASE, PGHOST, PGPASSWORD, PGPORT, PGUSER
from psycopg2.extensions import connection as Psycopg2Connection
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase

PG_URI = f"postgresql://{PGUSER}:{PGPASSWORD}@{PGHOST}:{PGPORT}/{PGDATABASE}"
try:
    DB_ENGINE__SQLALCHEMY = create_engine(PG_URI)
except Exception:
    DB_ENGINE__SQLALCHEMY = None


class Psycopg2Engine:
    """
    Psycopg2 Engine

    Usage:
    ```
    psycopg2_db_engine = Psycopg2Engine(PG_URI)
    with psycopg2_db_engine.connect() as conn:
        # Perform operations with the connection, like
        # conn.execute("SELECT * FROM my_table")
    ```
    """

    def __init__(self, uri: str):
        self.uri = uri

    def connect(self) -> Psycopg2Connection:
        return psycopg2.connect(self.uri)


DB_ENGINE__PSYCOPG2 = Psycopg2Engine(PG_URI)


class SchemaSpecificBaseModel(DeclarativeBase):
    """Base class for schema-specific models."""

    __abstract__ = True
    __table_args__ = {"schema": "public"}
    __table_initialized__ = False
