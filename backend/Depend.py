from fastapi import HTTPException
from core.SQLuser import ask_user
from core.DebugLog import log_error
from Httpfail import raise_for_error

def verify_user(username: str, password: str) -> dict:
    try:
        res = ask_user(username=username, password=password)
        raise_for_error(res)
        return res
    except HTTPException:
        raise
    except Exception as e:
        log_error(f"verify_user failed: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

def verify_admin(username: str, password: str) -> dict:
    res = verify_user(username, password)
    if not res.get("user", {}).get("is_admin"):
        raise HTTPException(status_code=403, detail="Admin required")
    return res