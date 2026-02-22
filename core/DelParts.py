import psycopg2
from psycopg2 import sql
from argon2 import PasswordHasher, exceptions
from getpass import getpass
from core.Connection import connect
from core.DebugLog import log_error

def delete_part(
    table_name: str,
    part_number: str,
    admin_username: str | None = None,
    admin_password: str | None = None,
    confirm: bool = True
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
        if confirm:
            if interactive:
                ans = (input(
                    f"Delete part '{part_number}' from table '{table_name}'? (y/n): "
                ) or "").strip().lower()
                if ans != "y":
                    return {"error": "Cancelled"}
            else:
                return {"error": "Confirmation required"}

        del_sql = sql.SQL(
            "DELETE FROM {} WHERE part_number = %s;"
        ).format(sql.Identifier(table_name)
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