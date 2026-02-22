import psycopg2
from psycopg2 import sql
from argon2 import PasswordHasher, exceptions
from getpass import getpass
from core.Connection import connect
from core.DebugLog import log_error

def update_part(
    table_name: str,
    part_number: str,
    part_name: str | None = None,
    category: str | None = None,
    price: float | None = None,
    admin_username: str | None = None,
    admin_password: str | None = None,
    confirm: bool = True,
):
    conn = None
    cursor = None
    ph = PasswordHasher()
    interactive = (
        admin_username is None
        or admin_password is None
    )
    try:
        conn = connect()
        conn.autocommit = True
        cursor = conn.cursor()
        if admin_username is None:
            admin_username = (input("Admin username: ") or "").strip()
        if admin_password is None:
            admin_password = getpass("Admin password: ")
        cursor.execute('SELECT "password" FROM users WHERE username = %s',
            (admin_username,))
        row = cursor.fetchone()
        if not row:
            return {"error": "Invalid admin credentials"}
        try:
            ph.verify(row[0], admin_password)
        except (exceptions.VerifyMismatchError, exceptions.VerificationError):
            return {"error": "Invalid admin credentials"}
        table_name = (table_name or "").strip()
        part_number = (part_number or "").strip()
        if not table_name:
            return {"error": "Missing table_name"}
        if not part_number:
            return {"error": "Missing part_number"}
        sets = []
        params = []
        if part_name is not None:
            part_name = (part_name or "").strip()
            sets.append(sql.SQL("part_name = %s"))
            params.append(part_name)
        if category is not None:
            category = (category or "").strip()
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
            sql.SQL(
                "UPDATE {} SET "
            ).format(sql.Identifier(table_name))
            + sql.SQL(
            ", "
        ).join(sets)
            + sql.SQL(
            " WHERE part_number = %s RETURNING *;"
        ))
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
