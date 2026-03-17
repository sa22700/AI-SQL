# SPDX-FileCopyrightText: 2026 Pirkka Toivakka
# SPDX-License-Identifier: Apache-2.0

import psycopg2
from argon2 import PasswordHasher
from core.DebugLog import log_error
from core.Connection import connect_write
from core.SQLuser import ask_user
from getpass import getpass

def add_new_user(
        admin_username: str | None = None,
        admin_password: str | None = None,
        new_username: str | None = None,
        new_password: str | None = None,
        confirm_password: str | None = None
    ) -> dict:
    cursor = None
    conn = None
    ph = PasswordHasher()
    interactive = (
            admin_username is None
            or admin_password is None
            or new_username is None
            or new_password is None
            or confirm_password is None
        )
    try:
        if interactive:
            auth = ask_user()
        else:
            if not admin_username or not str(admin_username).strip():
                return {"error": "Missing username"}
            if not admin_password:
                return {"error": "Missing password"}
            auth = ask_user(username=admin_username, password=admin_password)
        if not auth.get("ok"):
            return {"error": auth.get("error", "Login failed")}
        if not auth.get("user", {}).get("is_admin"):
            return {"error": "Admin required"}
        conn = connect_write()
        conn.autocommit = True
        cursor = conn.cursor()
        if interactive:
            while True:
                new_username = input("Add new username: ").strip()
                new_username = (new_username or "").strip()
                if not new_username:
                    print("Username cannot be empty")
                    continue
                new_password = getpass("Add new password: ")
                confirm_password = getpass("Confirm new password: ")
                if new_password != confirm_password:
                    print("Passwords do not match.")
                    continue
                if not new_password:
                    print("Password cannot be empty")
                    continue
                cursor.execute('SELECT 1 FROM users WHERE username = %s', (new_username,))
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
                    return {"ok": True, "username": new_username}
        else:
            new_username = (new_username or "").strip()
            if not new_username:
                return {"error": "Username cannot be empty"}
            if new_password != confirm_password:
                return {"error": "Passwords do not match"}
            if not new_password:
                return {"error": "Password cannot be empty"}
            cursor.execute('SELECT 1 FROM users WHERE username = %s', (new_username,))
            row = cursor.fetchone()
            if row:
                return {"error": "Username already exists"}
            hashed = ph.hash(new_password)
            cursor.execute(
                'INSERT INTO users (username, "password") VALUES (%s, %s)',
                (new_username, hashed)
            )
            return {"ok": True, "username": new_username}

    except psycopg2.Error as e:
            log_error(f'Error: {e}')
            return {'error': str(e)}

    finally:
        if cursor is not None:
            cursor.close()
        if conn is not None:
            conn.close()