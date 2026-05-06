# SPDX-FileCopyrightText: 2026 Pirkka Toivakka
# SPDX-License-Identifier: Apache-2.0

import psycopg
from psycopg import sql
from core.SQLAuth import require_admin
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
    interactive = (
        admin_username is None
        and admin_password is None
        and table_name is None
        and part_number is None
        and part_name is None
        and category is None
        and price is None
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
            part_number = input("Part number to update: ").strip()
            raw = input("New part name (leave empty = no change): ").strip()
            part_name = raw if raw else None
            raw = input("New category (leave empty = no change): ").strip()
            category = raw if raw else None
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
        sets = []
        params = []
        if part_name is not None:
            part_name = part_name.strip()
            if part_name:
                sets.append(sql.SQL("part_name = %s"))
                params.append(part_name)
        if category is not None:
            category = category.strip()
            if category:
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
                answer = (
                    input(
                        f"Update part '{part_number}' in table '{table_name}' "
                        f"with {len(sets)} change(s)? (y/n): "
                    ) or ""
                ).strip().lower()
                if answer != "y":
                    return {"error": "Cancelled"}
            else:
                return {"error": "Confirmation required"}
        with connect_write() as conn:
            with conn.cursor() as cursor:
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
                columns = [column[0] for column in cursor.description]
                return {
                    "ok": True,
                    "updated": dict(zip(columns, row))
                }

    except psycopg.Error as e:
        log_error(f"Database error in update_part(): {e}")
        return {"error": str(e)}