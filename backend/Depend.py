from fastapi import HTTPException
from core.SQLuser import ask_user
from core.DebugLog import log_error
from Httpfail import raise_for_error

def verify_user(username: str, password: str) -> dict:
    try:
        res = ask_user(username=username, password=password)
        raise_for_error(res)
        return res

    except Exception as e:
        log_error(str(e))
        raise HTTPException(status_code=500, detail=str(e))

def verify_admin(username: str, password: str) -> dict:
    try:
        res = verify_user(username, password)
        raise_for_error(res)
        return res

    except Exception as e:
        log_error(str(e))
        raise HTTPException(status_code=500, detail=str(e))