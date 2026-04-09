#Задание 6.2
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from typing import Dict
import secrets

from .schemas import UserInDB

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBasic()

fake_users_db: Dict[str, UserInDB] = {}

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def _unauthorized_exc():
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Unauthorized",
        headers={"WWW-Authenticate": "Basic"},
    )


def auth_user(credentials: HTTPBasicCredentials = Depends(security)) -> UserInDB:
    if not credentials or not credentials.username or not credentials.password:
        raise _unauthorized_exc()

    username = credentials.username
    password = credentials.password

    user = fake_users_db.get(username)
    if not user:
        raise _unauthorized_exc()

    if not secrets.compare_digest(username, user.username):
        raise _unauthorized_exc()

    if not verify_password(password, user.hashed_password):
        raise _unauthorized_exc()

    return user


def authenticate_user(username: str, password: str) -> bool:
    """Проверяет username/password против in-memory DB. Возвращает True/False."""
    user = fake_users_db.get(username)
    if not user:
        return False
    return verify_password(password, user.hashed_password)
