# SPDX-FileCopyrightText: 2026 Pirkka Toivakka
# SPDX-License-Identifier: Apache-2.0

import psycopg2
from psycopg2 import sql
from core.SQLuser import ask_user
from core.DebugLog import log_error
from core.Connection import connect_write

def update_part(
    table_name: str | None = None,
    part_number: str | None = None,
    part_name: str | None = None,
    category: str | None = None,
    price: float | None = None,
    admin_username: str | None = None,
    admin_password: str | None = None,
    confirm: bool = True,
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
                part_number = input("Part number to update: ").strip()
            else:
                part_number = part_number.strip()

            if part_name is None:
                raw = input("New part name (leave empty = no change): ").strip()
                part_name = raw if raw else None

            if category is None:
                raw = input("New category (leave empty = no change): ").strip()
                category = raw if raw else None

            if price is None:
                raw = input("New price (leave empty = no change): ").strip()
                if raw:
                    try:
                        price = float(raw)

                    except ValueError:
                        return {"error": "Invalid price"}

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
        sets = []
        params = []
        if part_name is not None:
            part_name = part_name.strip()
            sets.append(sql.SQL("part_name = %s"))
            params.append(part_name)
        if category is not None:
            category = category.strip()
            sets.append(sql.SQL("category = %s"))
            params.append(category)
        if price is not None:
            try:
                price = float(price)

            except (TypeError, ValueError):
                return {"error": "Invalid price"}

            sets.append(sql.SQL("price = %s"))
            params.append(price)
        if not sets:
            return {"error": "Nothing to update"}
        if confirm:
            if interactive:
                ans = (input(
                    f"Update part '{part_number}' in table '{table_name}' with {len(sets)} change(s)? (y/n): "
                ) or "").strip().lower()
                if ans != "y":
                    return {"error": "Cancelled"}
            else:
                return {"error": "Confirmation required"}
        params.append(part_number)
        update_sql = (
            sql.SQL("UPDATE {} SET ").format(sql.Identifier(table_name))
            + sql.SQL(", ").join(sets)
            + sql.SQL(" WHERE part_number = %s RETURNING *;")
        )
        cursor.execute(update_sql, tuple(params))
        row = cursor.fetchone()
        if not row:
            return {"error": "Not found"}
        cols = [c[0] for c in cursor.description]
        return {"ok": True, "updated": dict(zip(cols, row))}

    except psycopg2.Error as e:
        log_error(f"Database error: {e}")
        return {"error": str(e)}

    finally:
        if cursor is not None:
            cursor.close()
        if conn is not None:
            conn.close()