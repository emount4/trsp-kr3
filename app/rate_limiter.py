#Задание 6.5
from fastapi import HTTPException, status, Request, Depends
from time import time

_storage: dict[str, list[float]] = {}


def _is_allowed(key: str, limit: int, period: int) -> bool:
    now = time()
    window_start = now - period
    timestamps = _storage.get(key, [])
    timestamps = [ts for ts in timestamps if ts >= window_start]
    if len(timestamps) >= limit:
        _storage[key] = timestamps
        return False
    timestamps.append(now)
    _storage[key] = timestamps
    return True


def rate_limit_register(request: Request):
    client = request.client.host if request.client else "unknown"
    key = f"register:{client}"
    allowed = _is_allowed(key, limit=1, period=60)
    if not allowed:
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="Too many requests")


def rate_limit_login(request: Request):
    client = request.client.host if request.client else "unknown"
    key = f"login:{client}"
    allowed = _is_allowed(key, limit=5, period=60)
    if not allowed:
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="Too many requests")
