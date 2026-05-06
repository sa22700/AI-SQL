# SPDX-FileCopyrightText: 2026 Pirkka Toivakka
# SPDX-License-Identifier: Apache-2.0

import psycopg
from argon2 import PasswordHasher
from getpass import getpass
from core.SQLAuth import require_admin
from core.DebugLog import log_error
from core.Connection import connect_write

def add_new_user(
    admin_username: str | None = None,
    admin_password: str | None = None,
    new_username: str | None = None,
    new_password: str | None = None,
    confirm_password: str | None = None
) -> dict:
    ph = PasswordHasher()
    interactive = (
        admin_username is None
        and admin_password is None
        and new_username is None
        and new_password is None
        and confirm_password is None
    )
    try:
        auth = require_admin(
            admin_username=admin_username,
            admin_password=admin_password,
            interactive=interactive
        )
        if not auth.get("ok"):
            return auth
        with connect_write() as conn:
            with conn.cursor() as cursor:
                if interactive:
                    while True:
                        new_username = input("Add new username: ").strip()
                        new_password = getpass("Add new password: ")
                        confirm_password = getpass("Confirm new password: ")
                        new_username = (new_username or "").strip()
                        if not new_username:
                            print("Username cannot be empty")
                            continue
                        if new_password != confirm_password:
                            print("Passwords do not match.")
                            continue
                        if not new_password:
                            print("Password cannot be empty")
                            continue
                        cursor.execute(
                            'SELECT 1 FROM users WHERE username = %s',
                            (new_username,)
                        )
                        row = cursor.fetchone()
                        if row:
                            print("Username already exists.")
                            continue
                        hashed = ph.hash(new_password)
                        cursor.execute(
                            'INSERT INTO users (username, "password") VALUES (%s, %s)',
                            (new_username, hashed)
                        )
                        print(f"Username {new_username} added.")
                        add_more = input("Do you want to add more? (y/n): ").strip().lower()
                        if add_more != "y":
                            return {
                                "ok": True,
                                "username": new_username
                            }
                else:
                    new_username = (new_username or "").strip()
                    new_password = new_password or ""
                    confirm_password = confirm_password or ""
                    if not new_username:
                        return {"error": "Username cannot be empty"}
                    if new_password != confirm_password:
                        return {"error": "Passwords do not match"}
                    if not new_password:
                        return {"error": "Password cannot be empty"}
                    cursor.execute(
                        'SELECT 1 FROM users WHERE username = %s',
                        (new_username,)
                    )
                    row = cursor.fetchone()
                    if row:
                        return {"error": "Username already exists"}
                    hashed = ph.hash(new_password)
                    cursor.execute(
                        'INSERT INTO users (username, "password") VALUES (%s, %s)',
                        (new_username, hashed)
                    )
                    return {
                        "ok": True,
                        "username": new_username
                    }

    except psycopg.Error as e:
        log_error(f"Error in add_new_user(): {e}")
        return {"error": str(e)}