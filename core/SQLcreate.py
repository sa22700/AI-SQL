# SPDX-FileCopyrightText: 2026 Pirkka Toivakka
# SPDX-License-Identifier: Apache-2.0

import psycopg2
from psycopg2 import sql
from core.SchemaBuilder import schema_tables, column_builder
from core.DebugLog import log_error
from core.Connection import connect_write
from core.SQLuser import ask_user

def database(
    admin_username: str | None = None,
    admin_password: str | None = None,
    create_table: bool | None = None,
    table_name: str | None = None,
    rows_to: list[tuple[str, str, str, float]] | None = None,
    fetch: bool = True
) -> dict:
    conn = None
    cursor = None
    interactive = (
        admin_username is None and admin_password is None and
        create_table is None and table_name is None and
        rows_to is None
    )
    try:
        if interactive:
            auth = ask_user()
        else:
            if not admin_username or not str(admin_username).strip():
                return {"error": "Missing username"}
            if not admin_password:
                return {"error": "Missing password"}
            auth = ask_user(username=admin_username, password=admin_password)
        if not auth.get("ok"):
            return {"error": auth.get("error", "Login failed")}
        if not auth.get("user", {}).get("is_admin"):
            return {"error": "Admin required"}
        conn = connect_write()
        conn.autocommit = True
        cursor = conn.cursor()
        if interactive:
            ans = input("Create table? (y/n): ").strip().lower()
            create_table = (ans == "y")
            while True:
                if create_table:
                    table_name = input("Type new table name: ").strip()
                else:
                    table_name = input("Type existing table name: ").strip()
                if not table_name:
                    print("Table name cannot be empty.")
                    continue
                break
            if not create_table:
                cursor.execute(
                    """
                    SELECT EXISTS (
                        SELECT 1
                        FROM information_schema.tables
                        WHERE table_schema = 'public'
                        AND table_name = %s
                    )
                    """,
                    (table_name,)
                )
                exists = cursor.fetchone()[0]
                if not exists:
                    return {"error": f"Table '{table_name}' does not exist"}
            add_data = input("Add data? (y/n): ").strip().lower()
            if add_data == "y":
                rows_to = []
                while True:
                    try:
                        part = input("Part name: ").strip()
                        number = input("Part number: ").strip()
                        category = input("Category: ").strip()
                        price = float(input("Price: "))
                        rows_to.append((part, number, category, price))

                    except ValueError:
                        print("Price must be number")
                        continue

                    add_more = input("Add more data? (y/n): ").strip().lower()
                    if add_more != "y":
                        break
        else:
            if create_table is None:
                create_table = False
            if (create_table or rows_to or fetch) and (not table_name or not str(table_name).strip()):
                return {"error": "Missing table_name"}
            if not create_table and table_name:
                cursor.execute(
                    """
                    SELECT EXISTS (
                        SELECT 1
                        FROM information_schema.tables
                        WHERE table_schema = 'public'
                        AND table_name = %s
                    )
                    """,
                    (table_name,)
                )
                exists = cursor.fetchone()[0]
                if not exists:
                    return {"error": f"Table '{table_name}' does not exist"}
        created = False
        if create_table:
            create_sql = sql.SQL(
                "CREATE TABLE IF NOT EXISTS {} ("
                "id SERIAL PRIMARY KEY, "
                "part_name TEXT, "
                "part_number TEXT UNIQUE, "
                "category TEXT, "
                "price DOUBLE PRECISION"
                ");"
            ).format(sql.Identifier(table_name))
            cursor.execute(create_sql)
            created = True
            columns = column_builder()
            schema_tables(table_name, columns)
        inserted = 0
        if rows_to:
            insert_sql = sql.SQL(
                "INSERT INTO {} (part_name, part_number, category, price) "
                "VALUES (%s, %s, %s, %s);"
            ).format(sql.Identifier(table_name))
            for part, number, category, price in rows_to:
                cursor.execute(insert_sql, (part, number, category, price))
                inserted += 1
        result = {"ok": True, "table": table_name, "created": created, "inserted": inserted}
        if fetch and table_name:
            select_sql = sql.SQL("SELECT * FROM {}").format(sql.Identifier(table_name))
            cursor.execute(select_sql)
            cols = [c[0] for c in cursor.description]
            row = cursor.fetchall()
            result["columns"] = cols
            result["rows"] = [list(r) for r in row]
        return result

    except psycopg2.Error as e:
        log_error(f"Database error: {e}")
        return {"error": str(e)}

    finally:
        if cursor is not None:
            cursor.close()
        if conn is not None:
            conn.close()