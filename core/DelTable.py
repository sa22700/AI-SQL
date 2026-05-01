# SPDX-FileCopyrightText: 2026 Pirkka Toivakka
# SPDX-License-Identifier: Apache-2.0

import psycopg2
from psycopg2 import sql
from core.SQLAuth import require_admin
from core.DebugLog import log_error
from core.Connection import connect_write
from core.SchemaBuilder import remove_schema_table

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
        and admin_password is None
        and table_name is None
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
            table_name = (input("Table to delete: ") or "").strip()
        else:
            table_name = (table_name or "").strip()
        if not table_name:
            return {"error": "Missing table_name"}
        if confirm:
            if interactive:
                answer = (
                    input(f"Delete table '{table_name}'? (y/n): ") or ""
                ).strip().lower()
                if answer != "y":
                    return {"error": "Cancelled"}
            else:
                return {"error": "Confirmation required"}
        conn = connect_write()
        conn.autocommit = True
        cursor = conn.cursor()
        drop_sql = sql.SQL(
            "DROP TABLE IF EXISTS {}{};"
        ).format(
            sql.Identifier(table_name),
            sql.SQL(" CASCADE") if cascade else sql.SQL("")
        )
        cursor.execute(drop_sql)
        schema_result = remove_schema_table(
            table_name=table_name,
            interactive=interactive
        )
        if "error" in schema_result:
            return schema_result
        return {
            "ok": True,
            "dropped": table_name,
            "cascade": cascade,
            "schema": schema_result.get("action")
        }

    except psycopg2.Error as e:
        log_error(f"Database error in drop_table(): {e}")
        return {"error": str(e)}

    finally:
        if cursor is not None:
            cursor.close()
        if conn is not None:
            conn.close()