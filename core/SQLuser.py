# SPDX-FileCopyrightText: 2026 Pirkka Toivakka
# SPDX-License-Identifier: Apache-2.0

import psycopg
from argon2 import PasswordHasher, exceptions
from getpass import getpass
from core.DebugLog import log_error
from core.Connection import connect_read, connect_write
from core.CheckDB import check_users_table

def ask_user(
    username: str | None = None,
    password: str | None = None,
    booth_username: str | None = None,
    booth_password: str | None = None,
    booth_confirm: str | None = None
) -> dict:
    ph = PasswordHasher()
    interactive = (
        username is None and password is None and
        booth_username is None and booth_password is None and
        booth_confirm is None
    )
    try:
        check = check_users_table()
        if "error" in check:
            return check
        with connect_read() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) FROM users")
                user_count = cursor.fetchone()[0]
        if user_count == 0:
            with connect_write() as conn:
                with conn.cursor() as cursor:
                    if interactive:
                        print("User list is empty")
                        while True:
                            booth_username = input("Please add new username: ").strip()
                            booth_password = getpass("Please add new password: ")
                            booth_confirm = getpass("Confirm password: ")
                            if booth_password != booth_confirm:
                                print("Passwords do not match")
                                continue
                            if not booth_username:
                                print("Username cannot be empty")
                                continue
                            if not booth_password:
                                print("Password cannot be empty")
                                continue
                            hashed = ph.hash(booth_password)
                            cursor.execute(
                                'INSERT INTO users (username, "password", "is_admin") VALUES (%s, %s, %s);',
                                (booth_username, hashed, True)
                            )
                            print(f"Username {booth_username} added.")
                            break
                    else:
                        if booth_password != booth_confirm:
                            return {"error": "Passwords do not match"}
                        if not booth_username:
                            return {"error": "Username cannot be empty"}
                        if not booth_password:
                            return {"error": "Password cannot be empty"}
                        hashed = ph.hash(booth_password)
                        cursor.execute(
                            'INSERT INTO users (username, "password", "is_admin") VALUES (%s, %s, %s);',
                            (booth_username, hashed, True)
                        )
                        if username is None and password is None:
                            username = booth_username
                            password = booth_password
        if interactive:
            with connect_read() as conn:
                with conn.cursor() as cursor:
                    while True:
                        username = input("Username: ").strip()
                        password = getpass("Password: ")
                        if not username:
                            print("Username cannot be empty")
                            continue
                        if not password:
                            print("Password cannot be empty")
                            continue
                        cursor.execute(
                            'SELECT "password", is_admin FROM users WHERE username = %s',
                            (username,)
                        )
                        row = cursor.fetchone()
                        if not row:
                            print("Cannot find user in database.")
                            continue
                        stored_hash = row[0]
                        try:
                            ph.verify(stored_hash, password)
                            return {
                                "ok": True,
                                "username": username,
                                "user": {
                                    "is_admin": bool(row[1])
                                }
                            }

                        except (
                            exceptions.VerifyMismatchError,
                            exceptions.VerificationError
                        ):
                            print("Wrong username or password.")
                            log_error("Wrong username or password")
                            continue

        else:
            if not username or not str(username).strip():
                return {"error": "Missing username"}
            if not password:
                return {"error": "Missing password"}
            username = username.strip()
            with connect_read() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        'SELECT "password", is_admin FROM users WHERE username = %s',
                        (username,)
                    )
                    row = cursor.fetchone()
            if not row:
                return {"error": "Wrong username or password"}
            stored_hash = row[0]
            try:
                ph.verify(stored_hash, password)
                return {
                    "ok": True,
                    "username": username,
                    "user": {
                        "is_admin": bool(row[1])
                    }
                }

            except (
                exceptions.VerifyMismatchError,
                exceptions.VerificationError
            ):
                log_error("Wrong username or password")
                return {"error": "Wrong username or password"}

    except psycopg.Error as e:
        log_error(f"Error in ask_user(): {e}")
        return {"error": str(e)}