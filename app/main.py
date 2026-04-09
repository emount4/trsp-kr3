#Задание 6.3
import os
import secrets
from dotenv import load_dotenv

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.openapi.docs import get_swagger_ui_html

from .schemas import User, UserInDB
from .security import auth_user, get_password_hash, fake_users_db
from database import get_db_connection
from .rate_limiter import rate_limit_register
from .jwt_auth import router as jwt_router
from .roles import role_required

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


@app.post("/register", status_code=status.HTTP_201_CREATED, dependencies=[Depends(rate_limit_register)])
def register(user: User):
    # check existence in DB using secrets.compare_digest
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT username FROM users")
    rows = cur.fetchall()
    for row in rows:
        existing = row[0]
        if secrets.compare_digest(existing, user.username):
            conn.close()
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User already exists")

    # insert into DB
    cur.execute("INSERT INTO users (username, password) VALUES (?, ?)", (user.username, user.password))
    conn.commit()
    conn.close()

    # also add to in-memory DB used by other parts of app (store hashed password there)
    hashed = get_password_hash(user.password)
    user_in_db = UserInDB(username=user.username, hashed_password=hashed, role=user.role)
    fake_users_db[user.username] = user_in_db

    return {"message": "User registered successfully!"}


@app.get("/login")
def login(user: UserInDB = Depends(auth_user)):
    return {"message": f"Welcome, {user.username}!"}


app.include_router(jwt_router)


_resources: dict[int, dict] = {}
_next_id = 1


@app.post("/resources", dependencies=[Depends(role_required("admin"))])
def create_resource(body: dict | None = None, payload: dict = Depends(role_required("admin"))):
    global _next_id
    rid = _next_id
    _next_id += 1
    _resources[rid] = {"id": rid, "data": body or {}, "owner": payload.get("username")}
    return _resources[rid]


@app.get("/resources")
def list_resources(payload: dict = Depends(role_required("admin", "user", "guest"))):
    return list(_resources.values())


@app.put("/resources/{rid}")
def update_resource(rid: int, body: dict | None = None, payload: dict = Depends(role_required("admin", "user"))):
    if rid not in _resources:
        raise HTTPException(status_code=404, detail="Not found")
    _resources[rid]["data"] = body or {}
    return _resources[rid]


@app.delete("/resources/{rid}")
def delete_resource(rid: int, payload: dict = Depends(role_required("admin"))):
    if rid not in _resources:
        raise HTTPException(status_code=404, detail="Not found")
    return _resources.pop(rid)
