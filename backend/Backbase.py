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

class AddUserRequest(BaseModel):
    admin_username: str
    admin_password: str
    new_username: str
    new_password: str
    confirm_password: str

class AddUserResponse(BaseModel):
    ok: bool
    username: str | None = None
    error: str | None = None


class DeleteUserRequest(BaseModel):
    admin_username: str
    admin_password: str
    username_to_delete: str

class DeleteUserResponse(BaseModel):
    ok: bool
    deleted: str | None = None
    error: str | None = None

class DbRow(BaseModel):
    part_name: str
    part_number: str
    category: str
    price: float

class DatabaseRequest(BaseModel):
    admin_username: str
    admin_password: str
    create_table: bool
    table_name: str
    rows: list[DbRow] = []
    fetch: bool = True

class DatabaseResponse(BaseModel):
    ok: bool
    table: str | None = None
    created: bool | None = None
    inserted: int | None = None
    columns: list[str] | None = None
    rows: list[list] | None = None
    error: str | None = None