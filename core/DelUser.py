import psycopg2
from argon2 import PasswordHasher, exceptions
from core.DebugLog import log_error
from core.Connection import connect
from getpass import getpass

def delete_user(
    admin_username: str | None = None,
    admin_password: str | None = None,
    username: str | None = None,
):
    cursor = None
    conn = None
    ph = PasswordHasher()
    interactive = (
        admin_username is None
        or admin_password is None
        or username is None
    )
    try:
        conn = connect()
        conn.autocommit = True
        cursor = conn.cursor()
        if interactive:
            print("Login into admin account!")
            while True:
                admin_username = (input("Admin username: ") or "").strip()
                admin_password = getpass("Admin password: ")
                cursor.execute('SELECT "password" FROM users WHERE username = %s', (admin_username,))
                row = cursor.fetchone()
                if not row:
                    retry = (input("Invalid admin credentials. Try again? (y/n): ") or "").strip().lower()
                    if retry != "y":
                        return {"error": "Cancelled"}
                    continue
                try:
                    ph.verify(row[0], admin_password)
                    break

                except (exceptions.VerifyMismatchError, exceptions.VerificationError):
                    retry = (input("Invalid admin credentials. Try again? (y/n): ") or "").strip().lower()
                    if retry != "y":
                        return {"error": "Cancelled"}
                    continue

        else:
            admin_username = (admin_username or "").strip()
            if not admin_username:
                return {"error": "Invalid admin credentials"}
            cursor.execute('SELECT "password" FROM users WHERE username = %s', (admin_username,))
            row = cursor.fetchone()
            if not row:
                return {"error": "Invalid admin credentials"}
            try:
                ph.verify(row[0], admin_password or "")

            except (exceptions.VerifyMismatchError, exceptions.VerificationError):
                return {"error": "Invalid admin credentials"}

        if interactive:
            while True:
                username = (input("Username to delete: ") or "").strip()
                if username:
                    break
        else:
            username = (username or "").strip()
            if not username:
                return {"error": "Username cannot be empty"}
        if username == admin_username:
            return {"error": "Admin cannot delete itself"}
        if interactive:
            confirm_answer = (input(f"Delete user '{username}'? (y/n): ") or "").strip().lower()
            if confirm_answer != "y":
                return {"error": "Cancelled"}
        cursor.execute("DELETE FROM users WHERE username = %s", (username,))
        if cursor.rowcount == 0:
            return {"error": "User not found"}
        return {"ok": True, "deleted": username}

    except psycopg2.Error as e:
        log_error(f"Error: {e}")
        return {"error": str(e)}

    finally:
        if cursor is not None:
            cursor.close()
        if conn is not None:
            conn.close()
