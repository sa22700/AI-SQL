from fastapi import FastAPI, HTTPException
from Backbase import LoginRequest, LoginResponse, AskRequest, AskResponse
from SQLuser import ask_user
from SQLcoder import sql_driver

app = FastAPI()

@app.get("/health")
def health():
    return {"ok": True}

@app.post("/login", response_model=LoginResponse)
def login(req: LoginRequest):
    r = ask_user(username=req.username, password=req.password)
    if r.get("ok"):
        return {"ok": True, "username": r.get("username")}
    raise HTTPException(status_code=401, detail=r.get("error", "Invalid credentials"))

@app.post("/aisql", response_model=AskResponse)
def aisql(req: AskRequest):
    r = ask_user(username=req.username, password=req.password)
    if not r.get("ok"):
        raise HTTPException(status_code=401, detail=r.get("error", "Invalid credentials"))
    out = sql_driver(question=req.question)
    if "error" in out:
        raise HTTPException(status_code=400, detail=out["error"])
    return out
