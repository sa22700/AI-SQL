from fastapi import FastAPI, HTTPException
from Backbase import LoginRequest, LoginResponse, AskRequest, AskResponse, AddUserRequest, AddUserResponse, DeleteUserRequest, DeleteUserResponse, DatabaseRequest, DatabaseResponse
from core.SQLcoder import sql_driver
from core.AddUser import add_new_user
from core.Connection import connect
from core.SQLcreate import database
from Depend import _verify_user, _verify_admin

app = FastAPI()

@app.get("/health")
def health():
    return {"ok": True}

@app.post("/login", response_model=LoginResponse)
def login(req: LoginRequest):
    _verify_user(req.username, req.password)
    return {"ok": True, "username": req.username}

@app.post("/aisql", response_model=AskResponse)
def aisql(req: AskRequest):
    _verify_user(req.username, req.password)
    out = sql_driver(question=req.question)
    if "error" in out:
        raise HTTPException(status_code=400, detail=out["error"])
    return out

@app.post("/add_user", response_model=AddUserResponse)
def add_user(req: AddUserRequest):
    _verify_admin(req.username, req.password)
    out = add_new_user(
        admin_username=req.username,
        admin_password=req.password,
        new_username=req.new_username,
        new_password=req.new_password,
        confirm_password=req.confirm_password,
    )
    if out.get("ok"):
        return {"ok": True, "username": out.get("username"), "error": None}
    raise HTTPException(status_code=400, detail=out.get("error", "User creation failed"))

@app.post("/delete_user", response_model=DeleteUserResponse)
def delete_user(req: DeleteUserRequest):
    _verify_admin(req.username, req.password)
    if req.username_to_delete == req.username:
        raise HTTPException(status_code=400, detail="Admin cannot delete itself")
    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM users WHERE username=%s", (req.username_to_delete,))
            if cur.rowcount == 0:
                raise HTTPException(status_code=404, detail="User not found")
        conn.commit()
    return {"ok": True, "deleted": req.username_to_delete, "error": None}

@app.post("/database", response_model=DatabaseResponse)
def database_endpoint(req: DatabaseRequest):
    _verify_admin(req.username, req.password)
    out = database(
        admin_username=req.username,
        admin_password=req.password,
        create_table=req.create_table,
        table_name=req.table_name,
        rows_to=[(r.part_name, r.part_number, r.category, r.price) for r in req.rows] if req.rows else None,
        fetch=req.fetch,
    )
    if out.get("error"):
        raise HTTPException(status_code=400, detail=out["error"])
    return out
