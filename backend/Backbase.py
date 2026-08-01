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

class DatabaseRequest(LoginRequest):
    product_name: str
    product_number: str | None = None
    manufacturer: str | None = None
    category: str | None = None
    price: float | None = None
    currency: str = "EUR"
    attributes: dict[str, Any] = Field(default_factory=dict)

class DatabaseResponse(BaseModel):
    ok: bool
    inserted: int | None = None
    products: list[dict[str, Any]] | None = None
    error: str | None = None

class DeletePartRequest(LoginRequest):
    product_id: int
    confirm: bool = False

class DeletePartResponse(BaseModel):
    ok: bool
    deleted: dict[str, Any] | None = None
    error: str | None = None

class UpdatePartRequest(LoginRequest):
    product_id: int
    product_name: str | None = None
    product_number: str | None = None
    manufacturer: str | None = None
    category: str | None = None
    price: float | None = None
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