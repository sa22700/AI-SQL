import psycopg2
from core.Connection import connect_write
from core.DebugLog import log_error

def check_users_table() -> dict:
    conn = None
    cursor = None
    try:
        conn = connect_write()
        conn.autocommit = True
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS users ("
                       "id SERIAL PRIMARY KEY,"
                       "username TEXT NOT NULL UNIQUE,"
                       "password TEXT NOT NULL,"
                       "is_admin BOOLEAN NOT NULL DEFAULT FALSE"
                       ");")
        return {"ok": True}

    except psycopg2.Error as e:
        log_error(f"Error creating users table: {e}")
        return {"error": str(e)}

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()