"""Create users table for task_8_1_sqlite.

Run once:
    python -m task_8_1_sqlite.create_tables
"""
from .database import get_db_connection


def create_users_table():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            password TEXT NOT NULL
        )
        """
    )
    conn.commit()
    conn.close()


if __name__ == "__main__":
    create_users_table()
    print("users table created (or already exists)")
