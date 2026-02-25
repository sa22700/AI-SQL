import os
from fastapi import HTTPException
from core.SQLuser import ask_user

def _verify_user(username: str, password: str) -> dict:
    res = ask_user(username=username, password=password)
    if not res.get("ok"):
        raise HTTPException(status_code=401, detail=res.get("error", "Invalid credentials"))
    return res

def _verify_admin(username: str, password: str) -> dict:
    res = _verify_user(username, password)
    admin_user = os.getenv("DB_USER", "")
    if username != admin_user:
        raise HTTPException(status_code=403, detail="Admin required")
    return res