from fastapi import HTTPException

def raise_for_error(out: dict) -> None:
    error = out.get("error")
    if not error:
        return
    if error in ("Wrong username or password", "Login failed"):
        raise HTTPException(status_code=401, detail=error)
    if error == "Admin required":
        raise HTTPException(status_code=403, detail=error)
    if error in ("User not found", "Not found", "Table not found"):
        raise HTTPException(status_code=404, detail=error)
    raise HTTPException(status_code=400, detail=error)