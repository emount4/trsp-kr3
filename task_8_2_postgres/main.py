from fastapi import FastAPI, HTTPException, status
from typing import Optional

from .schemas import TodoCreate, Todo
from .database import get_db_connection

app = FastAPI()


@app.post("/todos", response_model=Todo, status_code=status.HTTP_201_CREATED)
def create_todo(payload: TodoCreate):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO todos (title, description, completed) VALUES (%s, %s, %s) RETURNING id, title, description, completed",
        (payload.title, payload.description, False),
    )
    row = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()
    if row is None:
        raise HTTPException(status_code=500, detail="Failed to create todo")
    return {"id": row[0], "title": row[1], "description": row[2], "completed": row[3]}


@app.get("/todos/{tid}", response_model=Todo)
def read_todo(tid: int):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, title, description, completed FROM todos WHERE id = %s", (tid,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Not found")
    return {"id": row[0], "title": row[1], "description": row[2], "completed": row[3]}


@app.put("/todos/{tid}", response_model=Todo)
def update_todo(tid: int, payload: TodoCreate, completed: Optional[bool] = False):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id FROM todos WHERE id = %s", (tid,))
    if not cur.fetchone():
        cur.close()
        conn.close()
        raise HTTPException(status_code=404, detail="Not found")
    cur.execute(
        "UPDATE todos SET title = %s, description = %s, completed = %s WHERE id = %s RETURNING id, title, description, completed",
        (payload.title, payload.description, completed, tid),
    )
    row = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()
    return {"id": row[0], "title": row[1], "description": row[2], "completed": row[3]}


@app.delete("/todos/{tid}")
def delete_todo(tid: int):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id FROM todos WHERE id = %s", (tid,))
    if not cur.fetchone():
        cur.close()
        conn.close()
        raise HTTPException(status_code=404, detail="Not found")
    cur.execute("DELETE FROM todos WHERE id = %s", (tid,))
    conn.commit()
    cur.close()
    conn.close()
    return {"message": "Deleted"}
