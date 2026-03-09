import psycopg2
from core.DebugLog import log_error
from core.SQLuser import ask_user
from core.Connection import connect_write

def delete_user(
    admin_username: str | None = None,
    admin_password: str | None = None,
    username: str | None = None,
) -> dict:
    cursor = None
    conn = None
    interactive = (
        admin_username is None
        or admin_password is None
        or username is None
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
        conn = connect_write()
        conn.autocommit = True
        cursor = conn.cursor()
        if interactive:
            while True:
                username = (input("Username to delete: ") or "").strip()
                if username:
                    break
        else:
            username = (username or "").strip()
            if not username:
                return {"error": "Username cannot be empty"}
        if username == auth.get("username"):
            return {"error": "Admin cannot delete itself"}
        if interactive:
            confirm_answer = (input(f"Delete user '{username}'? (y/n): ") or "").strip().lower()
            if confirm_answer != "y":
                return {"error": "Cancelled"}
        cursor.execute("DELETE FROM public.users WHERE username = %s", (username,))
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