from fastapi import FastAPI, HTTPException
from backend.Backbase import (
    LoginRequest, LoginResponse,
    AskRequest, AskResponse,
    AddUserRequest, AddUserResponse,
    DeleteUserRequest, DeleteUserResponse,
    DatabaseRequest, DatabaseResponse,
    DeleteTableRequest, DeleteTableResponse,
    DeletePartRequest, DeletePartResponse,
    UpdatePartRequest, UpdatePartResponse,
)
from core.SQLcoder import sql_driver
from core.AddUser import add_new_user
from core.SQLcreate import database
from core.DelUser import delete_user
from core.DelTable import drop_table
from core.DelParts import delete_part
from core.UpdParts import update_part
from backend.Depend import verify_user, verify_admin
from Httpfail import raise_for_error

app = FastAPI()

@app.get("/health")
def health() -> dict:
    return {"ok": True}

@app.post("/login", response_model=LoginResponse)
def login(req: LoginRequest) -> dict:
    verify_user(req.username, req.password)
    return {"ok": True, "username": req.username, "error": None}

@app.post("/aisql", response_model=AskResponse)
def aisql(req: AskRequest) -> dict:
    try:
        verify_user(req.username, req.password)
        out = sql_driver(question=req.question)
        return out

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/add_user", response_model=AddUserResponse)
def add_user(req: AddUserRequest) -> dict:
    verify_admin(req.username, req.password)
    out = add_new_user(
        admin_username=req.username,
        admin_password=req.password,
        new_username=req.new_username,
        new_password=req.new_password,
        confirm_password=req.confirm_password,
    )
    raise_for_error(out)
    return {"ok": True, "username": out.get("username"), "error": None}

@app.post("/delete_user", response_model=DeleteUserResponse)
def delete_user_endpoint(req: DeleteUserRequest) -> dict:
    verify_admin(req.username, req.password)
    out = delete_user(
        admin_username=req.username,
        admin_password=req.password,
        username=req.username_to_delete,
    )
    raise_for_error(out)
    return {"ok": True, "deleted": out.get("deleted"), "error": None}

@app.post("/database", response_model=DatabaseResponse)
def database_endpoint(req: DatabaseRequest) -> dict:
    verify_admin(req.username, req.password)
    out = database(
        admin_username=req.username,
        admin_password=req.password,
        create_table=req.create_table,
        table_name=req.table_name,
        rows_to=[(r.part_name, r.part_number, r.category, r.price) for r in req.rows] if req.rows else None,
        fetch=req.fetch,
    )
    raise_for_error(out)
    return out

@app.post("/delete_table", response_model=DeleteTableResponse)
def delete_table_endpoint(req: DeleteTableRequest) -> dict:
    verify_admin(req.username, req.password)
    out = drop_table(
        admin_username=req.username,
        admin_password=req.password,
        table_name=req.table_to_delete,
        cascade=False,
        confirm=False,
    )
    raise_for_error(out)
    return {"ok": True, "deleted": out.get("deleted"), "error": None}

@app.post("/delete_part", response_model=DeletePartResponse)
def delete_part_endpoint(req: DeletePartRequest) -> dict:
    verify_admin(req.username, req.password)
    out = delete_part(
        table_name=req.table_name,
        part_number=req.part_to_delete,
        admin_username=req.username,
        admin_password=req.password,
        confirm=False,
    )
    raise_for_error(out)
    return {"ok": True, "deleted": out.get("deleted"), "error": None}

@app.put("/update_part", response_model=UpdatePartResponse)
def update_part_endpoint(req: UpdatePartRequest) -> dict:
    verify_admin(req.username, req.password)
    out = update_part(
        table_name=req.table_name,
        part_number=req.target_part_number,
        part_name=req.new_part_name,
        category=req.new_category,
        price=req.new_price,
        admin_username=req.username,
        admin_password=req.password,
        confirm=False,
    )
    raise_for_error(out)
    return {"ok": True, "updated": req.target_part_number, "error": None}