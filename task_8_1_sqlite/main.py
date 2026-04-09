from fastapi import FastAPI, HTTPException, status
import secrets

from .schemas import User
from .database import get_db_connection

app = FastAPI()


@app.post("/register", status_code=status.HTTP_201_CREATED)
def register(user: User):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT username FROM users")
    rows = cur.fetchall()
    for row in rows:
        if secrets.compare_digest(row[0], user.username):
            conn.close()
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User already exists")

    cur.execute("INSERT INTO users (username, password) VALUES (?, ?)", (user.username, user.password))
    conn.commit()
    conn.close()

    return {"message": "User registered successfully!"}
