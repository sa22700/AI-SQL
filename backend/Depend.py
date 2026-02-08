from fastapi import Body, HTTPException
from core.SQLuser import ask_user
from backend.Backbase import LoginRequest, AskRequest, AddUserRequest, DeleteUserRequest, DatabaseRequest

def _verify_user(username: str, password: str) -> None:
    res = ask_user(username=username, password=password)
    if not res.get("ok"):
        raise HTTPException(status_code=401, detail=res.get("error", "Invalid credentials"))

def dep_login(req: LoginRequest = Body(...)) -> LoginRequest:
    _verify_user(req.username, req.password)
    return req

def dep_ask(req: AskRequest = Body(...)) -> AskRequest:
    _verify_user(req.username, req.password)
    return req

def dep_admin_add(req: AddUserRequest = Body(...)) -> AddUserRequest:
    _verify_user(req.admin_username, req.admin_password)
    return req

def dep_admin_del(req: DeleteUserRequest = Body(...)) -> DeleteUserRequest:
    _verify_user(req.admin_username, req.admin_password)
    if req.username_to_delete == req.admin_username:
        raise HTTPException(status_code=400, detail="Admin cannot delete itself")
    return req

def dep_admin_db(req: DatabaseRequest = Body(...)) -> DatabaseRequest:
    _verify_user(req.admin_username, req.admin_password)
    return req
