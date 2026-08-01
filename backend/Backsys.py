# SPDX-FileCopyrightText: 2026 Pirkka Toivakka
# SPDX-License-Identifier: Apache-2.0

from fastapi import FastAPI, HTTPException
from backend.Backbase import (
    LoginRequest, LoginResponse,
    AskRequest, AskResponse,
    AddUserRequest, AddUserResponse,
    DeleteUserRequest, DeleteUserResponse,
    DatabaseRequest, DatabaseResponse,
    DeletePartRequest, DeletePartResponse,
    UpdatePartRequest, UpdatePartResponse,
    UpdateUserRequest, UpdateUserResponse
)
from core.SQLcoder import sql_driver, load_model
from core.AddUser import add_new_user
from core.SQLcreate import database
from core.DelUser import delete_user
from core.DelParts import delete_part
from core.UpdParts import update_part
from core.UpdUser import update_user
from backend.Depends import verify_user, verify_admin
from backend.Httpfail import raise_for_error
from core.DebugLog import log_error

app = FastAPI()

@app.get("/health")
def health() -> dict:
    return {"ok": True}

@app.post("/login", response_model=LoginResponse)
def login(req: LoginRequest) -> dict:
    try:
        out = verify_user(req.username, req.password)
        return out

    except HTTPException:
        raise

    except Exception as e:
        log_error(str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/aisql", response_model=AskResponse)
def aisql(req: AskRequest) -> dict:
    try:
        verify_user(req.username, req.password)
        if not hasattr(app.state, "llm"):
            app.state.llm = load_model()
        out = sql_driver(app.state.llm, question=req.question)
        raise_for_error(out)
        return out

    except HTTPException:
        raise

    except Exception as e:
        log_error(str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/add_user", response_model=AddUserResponse)
def add_user(req: AddUserRequest) -> dict:
    try:
        verify_admin(req.username, req.password)
        out = add_new_user(
            admin_username=req.username,
            admin_password=req.password,
            new_username=req.new_username,
            new_password=req.new_password,
            confirm_password=req.confirm_password,
            is_admin=req.is_admin
        )
        raise_for_error(out)
        return out

    except HTTPException:
        raise

    except Exception as e:
        log_error(str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/delete_user", response_model=DeleteUserResponse)
def delete_user_endpoint(req: DeleteUserRequest) -> dict:
    try:
        verify_admin(req.username, req.password)
        out = delete_user(
            admin_username=req.username,
            admin_password=req.password,
            username=req.username_to_delete,
            confirm=req.confirm,
        )
        raise_for_error(out)
        return out

    except HTTPException:
        raise

    except Exception as e:
        log_error(str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.post(
    "/database",
    response_model=DatabaseResponse
)
def database_endpoint(req: DatabaseRequest) -> dict:
    try:
        verify_admin(req.username, req.password)
        out = database(
            admin_username=req.username,
            admin_password=req.password,
            product_name=req.product_name,
            product_number=req.product_number,
            manufacturer=req.manufacturer,
            category=req.category,
            price=req.price,
            currency=req.currency,
            attributes=req.attributes
        )
        raise_for_error(out)
        return out

    except HTTPException:
        raise

    except Exception as e:
        log_error(str(e))
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/delete_part", response_model=DeletePartResponse)
def delete_part_endpoint(req: DeletePartRequest) -> dict:
    try:
        verify_admin(req.username, req.password)
        out = delete_part(
            product_id=req.product_id,
            admin_username=req.username,
            admin_password=req.password,
            confirm=req.confirm
        )
        raise_for_error(out)
        return out

    except HTTPException:
        raise

    except Exception as e:
        log_error(str(e))
        raise HTTPException(status_code=500, detail="Internal server error")

@app.put("/update_part", response_model=UpdatePartResponse)
def update_part_endpoint(req: UpdatePartRequest) -> dict:
    try:
        verify_admin(req.username,req.password)
        out = update_part(
            product_id=req.product_id,
            product_name=req.product_name,
            product_number=req.product_number,
            manufacturer=req.manufacturer,
            category=req.category,
            price=req.price,
            admin_username=req.username,
            admin_password=req.password,
            confirm=req.confirm
        )
        raise_for_error(out)
        return out

    except HTTPException:
        raise

    except Exception as e:
        log_error(str(e))
        raise HTTPException(status_code=500, detail="Internal server error")

@app.put("/update_user", response_model=UpdateUserResponse)
def update_user_endpoint(req: UpdateUserRequest) -> dict:
    try:
        verify_admin(req.username, req.password)
        out = update_user(
            target_username=req.target_username,
            new_username=req.new_username,
            new_password=req.new_password,
            confirm_password=req.confirm_password,
            is_admin=req.is_admin,
            admin_username=req.username,
            admin_password=req.password,
            confirm=req.confirm,
        )
        raise_for_error(out)
        return out

    except HTTPException:
        raise

    except Exception as e:
        log_error(str(e))
        raise HTTPException(status_code=500, detail=str(e))
