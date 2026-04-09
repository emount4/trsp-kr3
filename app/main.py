#Задание 6.3
import os
import secrets
from dotenv import load_dotenv

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.openapi.docs import get_swagger_ui_html

from .schemas import User, UserInDB
from .security import auth_user, get_password_hash, fake_users_db
from .jwt_auth import router as jwt_router

load_dotenv()

MODE = os.getenv("MODE", "DEV").upper()

app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)


def _docs_unauthorized():
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Unauthorized",
        headers={"WWW-Authenticate": "Basic"},
    )


def docs_auth(credentials: HTTPBasicCredentials = Depends(HTTPBasic())) -> str:
    docs_user = os.getenv("DOCS_USER")
    docs_password = os.getenv("DOCS_PASSWORD")
    if docs_user is None or docs_password is None:
        raise HTTPException(status_code=500, detail="Docs auth not configured")
    if not credentials or not credentials.username or not credentials.password:
        raise _docs_unauthorized()

    if not secrets.compare_digest(credentials.username, docs_user) or not secrets.compare_digest(credentials.password, docs_password):
        raise _docs_unauthorized()
    return credentials.username


if MODE == "DEV":
    @app.get("/openapi.json", include_in_schema=False, dependencies=[Depends(docs_auth)])
    def openapi():
        return app.openapi()

    @app.get("/docs", include_in_schema=False, dependencies=[Depends(docs_auth)])
    def swagger_ui():
        return get_swagger_ui_html(openapi_url="/openapi.json", title="API Docs")

elif MODE == "PROD":
    pass

else:
    raise RuntimeError(f"Unsupported MODE: {MODE}. Use DEV or PROD")


@app.post("/register")
def register(user: User):
    if user.username in fake_users_db:
        raise HTTPException(status_code=400, detail="User already exists")
    hashed = get_password_hash(user.password)
    user_in_db = UserInDB(username=user.username, hashed_password=hashed)
    fake_users_db[user.username] = user_in_db
    return {"message": "User added successfully"}


@app.get("/login")
def login(user: UserInDB = Depends(auth_user)):
    return {"message": f"Welcome, {user.username}!"}


# include JWT auth routes (POST /login, /protected_resource)
app.include_router(jwt_router)
