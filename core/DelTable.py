# SPDX-FileCopyrightText: 2026 Pirkka Toivakka
# SPDX-License-Identifier: Apache-2.0

import psycopg2
from psycopg2 import sql
from core.SQLuser import ask_user
from core.DebugLog import log_error
from core.Connection import connect_write

def drop_table(
    admin_username: str | None = None,
    admin_password: str | None = None,
    table_name: str | None = None,
    cascade: bool = False,
    confirm: bool = True,
) -> dict:
    conn = None
    cursor = None
    interactive = (
        admin_username is None
        or admin_password is None
        or table_name is None
    )
    try:
        if interactive:
            auth = ask_user()
        else:
            admin_username = (admin_username or "").strip()
            admin_password = admin_password or ""
            if not admin_username or not admin_password:
                return {"error": "Invalid admin credentials"}
            auth = ask_user(username=admin_username, password=admin_password)
        if not auth.get("ok"):
            return {"error": auth.get("error", "Login failed")}
        if not auth.get("user", {}).get("is_admin"):
            return {"error": "Admin required"}
        conn = connect_write()
        conn.autocommit = True
        cursor = conn.cursor()
        if interactive:
            table_name = (input("Table to delete: ") or "").strip()
        else:
            table_name = (table_name or "").strip()
        if not table_name:
            return {"error": "Missing table_name"}
        if confirm:
            if interactive:
                ans = (input(f"Delete table '{table_name}'? (y/n): ") or "").strip().lower()
                if ans != "y":
                    return {"error": "Cancelled"}
            else:
                return {"error": "Confirmation required"}
        drop_sql = sql.SQL("DROP TABLE IF EXISTS {}{};").format(
            sql.Identifier(table_name),
            sql.SQL(" CASCADE") if cascade else sql.SQL(""),
        )
        cursor.execute(drop_sql)
        return {"ok": True, "dropped": table_name, "cascade": cascade}

    except psycopg2.Error as e:
        log_error(f"Database error: {e}")
        return {"error": str(e)}

    finally:
        if cursor is not None:
            cursor.close()
        if conn is not None:
            conn.close()