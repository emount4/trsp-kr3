#Задание 6.5
from .main import app  # expose FastAPI instance as `app` for uvicorn (use `uvicorn app:app`)

__all__ = ["app"]
