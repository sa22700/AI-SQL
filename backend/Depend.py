from fastapi import HTTPException
from core.SQLuser import ask_user

def verify_user(username: str, password: str) -> dict:
    res = ask_user(username=username, password=password)
    if not res.get("ok"):
        raise HTTPException(status_code=401, detail=res.get("error", "Invalid credentials"))
    return res

def verify_admin(username: str, password: str) -> dict:
    res = verify_user(username, password)
    if not res.get("user", {}).get("is_admin"):
        raise HTTPException(status_code=403, detail="Admin required")
    return res