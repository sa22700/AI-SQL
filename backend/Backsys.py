from fastapi import FastAPI, HTTPException, Depends
from backend.Backbase import LoginRequest, LoginResponse, AskRequest, AskResponse, AddUserRequest, AddUserResponse, DeleteUserRequest, DeleteUserResponse, DatabaseRequest, DatabaseResponse
from core.SQLcoder import sql_driver
from core.AddUser import add_new_user
from core.Connection import connect
from core.SQLcreate import database
from Depend import dep_login, dep_ask, dep_admin_add, dep_admin_del, dep_admin_db

app = FastAPI()

@app.get("/health")
def health():
    return {"ok": True}

@app.post("/login", response_model=LoginResponse)
def login(req: LoginRequest = Depends(dep_login)):
    return {"ok": True, "username": req.username}

@app.post("/aisql", response_model=AskResponse)
def aisql(req: AskRequest = Depends(dep_ask)):
    out = sql_driver(question=req.question)
    if "error" in out:
        raise HTTPException(status_code=400, detail=out["error"])
    return out

@app.post("/add_user", response_model=AddUserResponse)
def add_user(req: AddUserRequest = Depends(dep_admin_add)):
    out = add_new_user(
        admin_username=req.admin_username,
        admin_password=req.admin_password,
        new_username=req.new_username,
        new_password=req.new_password,
        confirm_password=req.confirm_password,
    )
    if out.get("ok"):
        return {"ok": True, "username": out.get("username"), "error": None}
    raise HTTPException(status_code=400, detail=out.get("error", "User creation failed"))

@app.post("/delete_user", response_model=DeleteUserResponse)
def delete_user(req: DeleteUserRequest = Depends(dep_admin_del)):
    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM users WHERE username=%s", (req.username_to_delete,))
            if cur.rowcount == 0:
                raise HTTPException(status_code=404, detail="User not found")
        conn.commit()
    return {"ok": True, "deleted": req.username_to_delete, "error": None}

@app.post("/database", response_model=DatabaseResponse)
def database_endpoint(req: DatabaseRequest = Depends(dep_admin_db)):
    out = database(
        admin_username=req.admin_username,
        admin_password=req.admin_password,
        create_table=req.create_table,
        table_name=req.table_name,
        rows_to=[(r.part_name, r.part_number, r.category, r.price) for r in req.rows] if req.rows else None,
        fetch=req.fetch,
    )
    if out.get("error"):
        raise HTTPException(status_code=400, detail=out["error"])
    return out
