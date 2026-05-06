import psycopg
from core.Connection import connect_write
from core.DebugLog import log_error

def check_users_table() -> dict:
    try:
        with connect_write() as conn:
            with conn.cursor() as cursor:
                cursor.execute("CREATE TABLE IF NOT EXISTS users ("
                               "id SERIAL PRIMARY KEY,"
                               "username TEXT NOT NULL UNIQUE,"
                               "password TEXT NOT NULL,"
                               "is_admin BOOLEAN NOT NULL DEFAULT FALSE"
                               ");")
                return {"ok": True}

    except psycopg.Error as e:
        log_error(f"Error creating users table: {e}")
        return {"error": str(e)}
