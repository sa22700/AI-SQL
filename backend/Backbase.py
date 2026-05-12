# SPDX-FileCopyrightText: 2026 Pirkka Toivakka
# SPDX-License-Identifier: Apache-2.0

from pydantic import BaseModel, Field
from typing import Any

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
    columns: list[str]
    rows: list[list[Any]]

class AddUserRequest(LoginRequest):
    new_username: str
    new_password: str
    confirm_password: str
    is_admin: bool = False

class AddUserResponse(BaseModel):
    ok: bool
    username: str | None = None
    is_admin: bool | None = None
    error: str | None = None

class DeleteUserRequest(LoginRequest):
    username_to_delete: str
    confirm: bool = False

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
    rows: list[list[Any]] | None = None
    error: str | None = None

class DeleteTableRequest(LoginRequest):
    table_to_delete: str

class DeleteTableResponse(BaseModel):
    ok: bool
    dropped: str | None = None
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
    confirm: bool = False

class UpdatePartResponse(BaseModel):
    ok: bool
    updated: dict[str, Any] | None = None
    error: str | None = None

class UpdateUserRequest(LoginRequest):
    target_username: str
    new_username: str | None = None
    new_password: str | None = None
    confirm_password: str | None = None
    is_admin: bool | None = None
    confirm: bool = True

class UpdateUserResponse(BaseModel):
    ok: bool
    updated: dict[str, Any] | None = None
    error: str | None = None