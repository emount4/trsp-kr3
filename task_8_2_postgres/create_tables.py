from .database import get_db_connection


def create_todos_table():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS todos (
            id SERIAL PRIMARY KEY,
            title TEXT NOT NULL,
            description TEXT,
            completed BOOLEAN NOT NULL DEFAULT FALSE
        )
        """
    )
    conn.commit()
    cur.close()
    conn.close()


if __name__ == "__main__":
    create_todos_table()
    print("todos table created (or already exists)")
