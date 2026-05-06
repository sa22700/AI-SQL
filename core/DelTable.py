# SPDX-FileCopyrightText: 2026 Pirkka Toivakka
# SPDX-License-Identifier: Apache-2.0

import psycopg
from psycopg import sql
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
        with connect_write() as conn:
            with conn.cursor() as cursor:
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

    except psycopg.Error as e:
        log_error(f"Database error in drop_table(): {e}")
        return {"error": str(e)}