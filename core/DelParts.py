# SPDX-FileCopyrightText: 2026 Pirkka Toivakka
# SPDX-License-Identifier: Apache-2.0

import psycopg2
from psycopg2 import sql
from core.DebugLog import log_error
from core.SQLuser import ask_user
from core.Connection import connect_write

def delete_part(
    table_name: str | None = None,
    part_number: str | None = None,
    admin_username: str | None = None,
    admin_password: str | None = None,
    confirm: bool = True
) -> dict:
    conn = None
    cursor = None
    interactive = (
        admin_username is None
        or admin_password is None
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
        if interactive:
            if table_name is None:
                table_name = input("Table name: ").strip()
            else:
                table_name = table_name.strip()
            if part_number is None:
                part_number = input("Part number to delete: ").strip()
            else:
                part_number = part_number.strip()
        else:
            table_name = (table_name or "").strip()
            part_number = (part_number or "").strip()
        if not table_name:
            return {"error": "Missing table_name"}
        if not part_number:
            return {"error": "Missing part_number"}
        conn = connect_write()
        conn.autocommit = True
        cursor = conn.cursor()
        if confirm:
            if interactive:
                ans = (input(
                    f"Delete part '{part_number}' from table '{table_name}'? (y/n): "
                ) or "").strip().lower()
                if ans != "y":
                    return {"error": "Cancelled"}
            else:
                return {"error": "Confirmation required"}
        del_sql = sql.SQL("DELETE FROM {} WHERE part_number = %s;").format(
            sql.Identifier(table_name)
        )
        cursor.execute(del_sql, (part_number,))
        if cursor.rowcount == 0:
            return {"error": "Not found"}
        return {"ok": True, "deleted": part_number, "table": table_name}

    except psycopg2.Error as e:
        log_error(f"Database error: {e}")
        return {"error": str(e)}

    finally:
        if cursor is not None:
            cursor.close()
        if conn is not None:
            conn.close()