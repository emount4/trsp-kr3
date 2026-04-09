#Задание 7.1
from fastapi import Depends, HTTPException, status
from .jwt_auth import verify_token


def role_required(*allowed_roles: str):
    def _checker(payload: dict = Depends(verify_token)):
        role = payload.get("role")
        if role is None or role not in allowed_roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
        return payload

    return _checker
