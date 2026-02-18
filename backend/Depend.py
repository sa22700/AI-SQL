from fastapi import HTTPException
from core.SQLuser import ask_user

def _verify_user(username: str, password: str) -> dict:
    res = ask_user(username=username, password=password)
    if not res.get("ok"):
        raise HTTPException(status_code=401, detail=res.get("error", "Invalid credentials"))
    return res

def _verify_admin(username: str, password: str) -> None:
    res = _verify_user(username, password)
    if res.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin required")
