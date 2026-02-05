from pydantic import BaseModel

class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    ok: bool
    username: str | None = None
    error: str | None = None

class AskRequest(LoginRequest):
    question: str

class AskResponse(BaseModel):
    sql: str
    rows: list[list]
