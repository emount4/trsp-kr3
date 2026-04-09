#Задание 6.2
from pydantic import BaseModel


class UserBase(BaseModel):
    username: str


class User(UserBase):
    password: str
    role: str = "guest"


class UserInDB(UserBase):
    hashed_password: str
    role: str
