# SPDX-FileCopyrightText: 2026 Pirkka Toivakka
# SPDX-License-Identifier: Apache-2.0

import psycopg
from psycopg import sql
from getpass import getpass
from argon2 import PasswordHasher
from core.SQLAuth import require_admin
from core.DebugLog import log_error
from core.Connection import connect_write

def update_user(
    target_username: str | None = None,
    new_username: str | None = None,
    new_password: str | None = None,
    confirm_password: str | None = None,
    is_admin: bool | None = None,
    admin_username: str | None = None,
    admin_password: str | None = None,
    confirm: bool = True,
) -> dict:
    ph = PasswordHasher()
    interactive = (
        admin_username is None
        and admin_password is None
        and target_username is None
        and new_username is None
        and new_password is None
        and confirm_password is None
        and is_admin is None
    )
    try:
        auth = require_admin(
            admin_username=admin_username,
            admin_password=admin_password,
            interactive=interactive
        )
        if not auth.get("ok"):
            return auth
        auth_username = auth.get("auth", {}).get("username")
        if interactive:
            target_username = input("Username to update: ").strip()
            print("Leave empty if no change")
            new_username = input("New username: ").strip()
            print("Leave empty if no change")
            new_password = getpass("New password: ").strip()
            if new_password:
                confirm_password = getpass("Confirm password: ").strip()
            admin_answer = input(
                "Change admin status? (y/n/empty = no change): "
            ).strip().lower()
            if admin_answer == "y":
                is_admin = True
            elif admin_answer == "n":
                is_admin = False
            else:
                is_admin = None
        else:
            target_username = (target_username or "").strip()
            new_username = (new_username or "").strip()
            new_password = (new_password or "").strip()
            if confirm_password is not None:
                confirm_password = confirm_password.strip()
        if not target_username:
            return {"error": "Missing target username"}
        if target_username == auth_username and is_admin is False:
            return {"error": "Admin cannot remove own admin rights"}
        sets = []
        params = []
        if new_username:
            sets.append(sql.SQL("username = %s"))
            params.append(new_username)
        if new_password:
            if new_password != confirm_password:
                return {"error": "Passwords do not match"}
            password_hash = ph.hash(new_password)
            sets.append(sql.SQL('"password" = %s'))
            params.append(password_hash)
        if is_admin is not None:
            sets.append(sql.SQL("is_admin = %s"))
            params.append(is_admin)
        if not sets:
            return {"error": "Nothing to update"}
        if confirm and interactive:
            answer = input(
                f"Update user '{target_username}' with {len(sets)} change(s)? (y/n): "
            ).strip().lower()
            if answer != "y":
                return {"error": "Cancelled"}
        with connect_write() as conn:
            with conn.cursor() as cursor:
                params.append(target_username)
                update_sql = (
                    sql.SQL("UPDATE users SET ")
                    + sql.SQL(", ").join(sets)
                    + sql.SQL(" WHERE username = %s ")
                    + sql.SQL("RETURNING id, username, is_admin;")
                )
                cursor.execute(update_sql, tuple(params))
                row = cursor.fetchone()
                if not row:
                    return {"error": "User not found"}
                columns = [column[0] for column in cursor.description]
                return {
                    "ok": True,
                    "updated": dict(zip(columns, row))
                }

    except KeyboardInterrupt:
        return {"error": "Cancelled"}

    except psycopg.errors.UniqueViolation:
        return {"error": "Username already exists"}

    except psycopg.Error as e:
        log_error(f"Database error in update_user(): {e}")
        return {"error": str(e)}

    except Exception as e:
        log_error(f"Unexpected error in update_user(): {e}")
        return {"error": str(e)}