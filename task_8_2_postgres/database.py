import os
import psycopg2
from psycopg2.extras import RealDictCursor


def get_db_connection():
    dsn = os.getenv("PG_DSN")
    if not dsn:
        host = os.getenv("PG_HOST", "localhost")
        port = os.getenv("PG_PORT", "5432")
        db = os.getenv("PG_DB", "testdb")
        user = os.getenv("PG_USER", "postgres")
        password = os.getenv("PG_PASSWORD", "postgres")
        dsn = f"host={host} port={port} dbname={db} user={user} password={password}"
    conn = psycopg2.connect(dsn)
    return conn
