import psycopg2
from psycopg2 import sql
from core.SchemaBuilder import schema_tables, column_builder
from core.DebugLog import log_error
from core.Connection import connect
from argon2 import PasswordHasher, exceptions
from getpass import getpass

def database(
    admin_username: str | None = None,
    admin_password: str | None = None,
    create_table: bool | None = None,
    table_name: str | None = None,
    rows_to: list[tuple[str, str, str, float]] | None = None,
    fetch: bool = True
):
    conn = None
    cursor = None
    ph = PasswordHasher()
    interactive = (
        admin_username is None and admin_password is None and
        create_table is None and table_name is None and
        rows_to is None
    )
    try:
        conn = connect()
        conn.autocommit = True
        cursor = conn.cursor()
        if interactive:
            while True:
                admin_username = input("Username: ").strip()
                admin_password = getpass("Password: ")
                cursor.execute('SELECT "password", is_admin FROM public.users WHERE username = %s', (admin_username,))
                row = cursor.fetchone()
                if not row:
                    retry = input("Faulty username or password. Try again? (y/n): ").strip().lower()
                    if retry != "y":
                        return {"error": "Cancelled"}
                    continue
                try:
                    ph.verify(row[0], admin_password)
                    if not bool(row[1]):
                        retry = input("Admin required. Try again? (y/n): ").strip().lower()
                        if retry != "y":
                            return {"error": "Cancelled"}
                        continue
                    break

                except (exceptions.VerifyMismatchError, exceptions.VerificationError):
                    retry = input("Faulty username or password. Try again? (y/n): ").strip().lower()
                    if retry != "y":
                        return {"error": "Cancelled"}

        else:
            if not admin_username or not str(admin_username).strip():
                return {"error": "Missing username"}
            if not admin_password:
                return {"error": "Missing password"}
            cursor.execute('SELECT "password", is_admin FROM public.users WHERE username = %s', (admin_username,))
            row = cursor.fetchone()
            if not row:
                return {"error": "Invalid admin credentials"}
            try:
                ph.verify(row[0], admin_password)
                if not bool(row[1]):
                    return {"error": "Admin required"}

            except (exceptions.VerifyMismatchError, exceptions.VerificationError):
                return {"error": "Invalid admin credentials"}

        if interactive:
            ans = input("Create table? (y/n): ").strip().lower()
            create_table = (ans == "y")
            if not create_table:
                return {"ok": True, "skipped": "create_table"}
            while True:
                table_name = input("Type new table name: ").strip()
                if not table_name:
                    print("Table name cannot be empty.")
                    continue
                break
            add_data = input("Add data? (y/n): ").strip().lower()
            if add_data == "y":
                rows_to = []
                while True:
                    try:
                        part = input("Part name: ")
                        number = input("Part number: ")
                        category = input("Category: ")
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