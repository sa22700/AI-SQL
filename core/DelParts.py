# SPDX-FileCopyrightText: 2026 Pirkka Toivakka
# SPDX-License-Identifier: Apache-2.0

import psycopg2
from psycopg2 import sql
from core.SQLAuth import require_admin
from core.DebugLog import log_error
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
        table_name is None
        and part_number is None
        and admin_username is None
        and admin_password is None
    )
    try:
        auth = require_admin(
            admin_username=admin_username,
            admin_password=admin_password,
            interactive=interactive
        )
        if not auth.get("ok"):
            return auth
        if interactive:
            table_name = input("Table name: ").strip()
            part_number = input("Part number to delete: ").strip()
        else:
            table_name = (table_name or "").strip()
            part_number = (part_number or "").strip()
        if not table_name:
            return {"error": "Missing table_name"}
        if not part_number:
            return {"error": "Missing part_number"}
        if confirm:
            if interactive:
                answer = (
                    input(
                        f"Delete part '{part_number}' from table '{table_name}'? (y/n): "
                    ) or ""
                ).strip().lower()
                if answer != "y":
                    return {"error": "Cancelled"}
            else:
                return {"error": "Confirmation required"}
        conn = connect_write()
        conn.autocommit = True
        cursor = conn.cursor()
        delete_sql = sql.SQL(
            "DELETE FROM {} WHERE part_number = %s;"
        ).format(
            sql.Identifier(table_name)
        )
        cursor.execute(delete_sql, (part_number,))
        if cursor.rowcount == 0:
            return {"error": "Not found"}
        return {
            "ok": True,
            "deleted": part_number,
            "table": table_name
        }

    except psycopg2.Error as e:
        log_error(f"Database error in delete_part(): {e}")
        return {"error": str(e)}

    finally:
        if cursor is not None:
            cursor.close()
        if conn is not None:
            conn.close()