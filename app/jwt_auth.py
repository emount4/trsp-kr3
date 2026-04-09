#Задание 6.4
import os
from datetime import datetime, timedelta

import jwt
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Request
from fastapi import status as _status
import secrets

from .schemas import User
from .security import authenticate_user, fake_users_db
from .rate_limiter import rate_limit_login

router = APIRouter()

SECRET_KEY = os.getenv("JWT_SECRET_KEY", "change-me-in-prod")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

def create_access_token(subject: str, role: str, expires_delta: timedelta | None = None) -> str:
    to_encode = {"sub": subject, "role": role}
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


bearer_scheme = HTTPBearer()


def verify_token(auth: HTTPAuthorizationCredentials = Depends(bearer_scheme)) -> dict:
    token = auth.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        role: str | None = payload.get("role")
        if username is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        return {"username": username, "role": role}
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")
    except jwt.PyJWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")


@router.post("/login", dependencies=[Depends(rate_limit_login)])
def login_for_access_token(form_data: User):
    found_user = None
    for existing, userobj in fake_users_db.items():
        if secrets.compare_digest(existing, form_data.username):
            found_user = userobj
            break
    if not found_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if not authenticate_user(form_data.username, form_data.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authorization failed")

    access_token = create_access_token(subject=form_data.username, role=found_user.role)
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/protected_resource")
def protected_resource(payload: dict = Depends(verify_token)):
    return {"message": f"Access granted for {payload.get('username')}"}
