# SPDX-FileCopyrightText: 2026 Pirkka Toivakka
# SPDX-License-Identifier: Apache-2.0

import psycopg2
from core.SQLAuth import require_admin
from core.DebugLog import log_error
from core.Connection import connect_write

def delete_user(
    admin_username: str | None = None,
    admin_password: str | None = None,
    username: str | None = None,
    confirm: bool = True
) -> dict:
    cursor = None
    conn = None
    interactive = (
        admin_username is None
        and admin_password is None
        and username is None
    )
    try:
        auth_check = require_admin(
            admin_username=admin_username,
            admin_password=admin_password,
            interactive=interactive
        )
        if not auth_check.get("ok"):
            return auth_check
        auth = auth_check["auth"]
        if interactive:
            while True:
                username = (input("Username to delete: ") or "").strip()
                if username:
                    break
        else:
            username = (username or "").strip()
            if not username:
                return {"error": "Username cannot be empty"}
        if username == auth.get("username"):
            return {"error": "Admin cannot delete itself"}
        if confirm:
            if interactive:
                confirm_answer = (
                    input(f"Delete user '{username}'? (y/n): ") or ""
                ).strip().lower()
                if confirm_answer != "y":
                    return {"error": "Cancelled"}
            else:
                return {"error": "Confirmation required"}
        conn = connect_write()
        conn.autocommit = True
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM public.users WHERE username = %s",
            (username,)
        )
        if cursor.rowcount == 0:
            return {"error": "User not found"}
        return {
            "ok": True,
            "deleted": username
        }

    except psycopg2.Error as e:
        log_error(f"Database error in delete_user(): {e}")
        return {"error": str(e)}

    finally:
        if cursor is not None:
            cursor.close()
        if conn is not None:
            conn.close()