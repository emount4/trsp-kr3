# Task 8.1 - sqlite
from pydantic import BaseModel


class User(BaseModel):
    username: str
    password: str
