import psycopg2
from psycopg2 import sql
from argon2 import PasswordHasher, exceptions
from getpass import getpass
from core.Connection import connect
from core.DebugLog import log_error

def drop_table(
    admin_username: str | None = None,
    admin_password: str | None = None,
    table_name: str | None = None,
    cascade: bool = False,
    confirm: bool = True,
) -> dict:
    conn = None
    cursor = None
    ph = PasswordHasher()
    interactive = (
        admin_username is None
        or admin_password is None
        or table_name is None
    )
    try:
        conn = connect()
        conn.autocommit = True
        cursor = conn.cursor()
        if interactive:
            admin_username = (input("Admin username: ") or "").strip()
            admin_password = getpass("Admin password: ")
        else:
            admin_username = (admin_username or "").strip()
            admin_password = admin_password or ""
        if not admin_username or not admin_password:
            return {"error": "Invalid admin credentials"}
        cursor.execute(
            'SELECT "password", is_admin FROM public.users WHERE username = %s',
            (admin_username,)
        )
        row = cursor.fetchone()
        if not row:
            return {"error": "Invalid admin credentials"}
        try:
            ph.verify(row[0], admin_password)

        except (exceptions.VerifyMismatchError, exceptions.VerificationError):
            return {"error": "Invalid admin credentials"}

        if not bool(row[1]):
            return {"error": "Admin required"}
        if interactive:
            table_name = (input("Table to delete: ") or "").strip()
        else:
            table_name = (table_name or "").strip()
        if not table_name:
            return {"error": "Missing table_name"}
        if confirm:
            if interactive:
                ans = (input(f"Delete table '{table_name}'? (y/n): ") or "").strip().lower()
                if ans != "y":
                    return {"error": "Cancelled"}
            else:
                return {"error": "Confirmation required"}
        drop_sql = sql.SQL("DROP TABLE IF EXISTS {}{};").format(
            sql.Identifier(table_name),
            sql.SQL(" CASCADE") if cascade else sql.SQL(""),
        )
        cursor.execute(drop_sql)
        return {"ok": True, "dropped": table_name, "cascade": cascade}

    except psycopg2.Error as e:
        log_error(f"Database error: {e}")
        return {"error": str(e)}

    finally:
        if cursor is not None:
            cursor.close()
        if conn is not None:
            conn.close()