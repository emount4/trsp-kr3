from pydantic import BaseModel


class TodoCreate(BaseModel):
    title: str
    description: str | None = ""


class Todo(BaseModel):
    id: int
    title: str
    description: str | None = ""
    completed: bool = False
