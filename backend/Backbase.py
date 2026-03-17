# SPDX-FileCopyrightText: 2026 Pirkka Toivakka
# SPDX-License-Identifier: Apache-2.0

from pydantic import BaseModel, Field

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

class AddUserRequest(LoginRequest):
    new_username: str
    new_password: str
    confirm_password: str

class AddUserResponse(BaseModel):
    ok: bool
    username: str | None = None
    error: str | None = None

class DeleteUserRequest(LoginRequest):
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

class DatabaseRequest(LoginRequest):
    create_table: bool
    table_name: str
    rows: list[DbRow] = Field(default_factory=list)
    fetch: bool = True

class DatabaseResponse(BaseModel):
    ok: bool
    table: str | None = None
    created: bool | None = None
    inserted: int | None = None
    columns: list[str] | None = None
    rows: list[list] | None = None
    error: str | None = None

class DeleteTableRequest(LoginRequest):
    table_to_delete: str

class DeleteTableResponse(BaseModel):
    ok: bool
    deleted: str | None = None
    error: str | None = None

class DeletePartRequest(LoginRequest):
    table_name: str
    part_to_delete: str

class DeletePartResponse(BaseModel):
    ok: bool
    deleted: str | None = None
    error: str | None = None

class UpdatePartRequest(LoginRequest):
    table_name: str
    target_part_number: str
    new_part_name: str | None = None
    new_category: str | None = None
    new_price: float | None = None

class UpdatePartResponse(BaseModel):
    ok: bool
    updated: str | None = None
    error: str | None = None