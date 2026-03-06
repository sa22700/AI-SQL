import psycopg2
from argon2 import PasswordHasher, exceptions
from core.DebugLog import log_error
from core.Connection import connect
from getpass import getpass

def add_new_user(
        admin_username: str | None = None,
        admin_password: str | None = None,
        new_username: str | None = None,
        new_password: str | None = None,
        confirm_password: str | None = None
    ) -> dict:
    cursor = None
    conn = None
    ph = PasswordHasher()
    interactive = (
            admin_username is None or admin_password is None or
            new_username is None or new_password is None or
            confirm_password is None
        )
    try:
        conn = connect()
        conn.autocommit = True
        cursor = conn.cursor()
        if interactive:
            print('Login into main account!')
            while True:
                admin_username = input('Username: ').strip()
                admin_password = getpass('Password: ')
                cursor.execute('SELECT "password", is_admin FROM users WHERE username = %s', (admin_username,))
                row = cursor.fetchone()
                if not row:
                    retry = input('Faulty username or password. Try again? (y/n): ').strip().lower()
                    if retry != 'y':
                        return {'error': 'Cancelled'}
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
                    continue
        else:
            cursor.execute('SELECT "password", is_admin FROM users WHERE username = %s', (admin_username,))
            row = cursor.fetchone()
            if not row:
                return {"error": "Invalid admin credentials"}
            try:
                ph.verify(row[0], admin_password)
                if not bool(row[1]):
                    log_error("Admin required")
                    return {"error": "Admin required"}

            except (exceptions.VerifyMismatchError, exceptions.VerificationError):
                log_error("Invalid admin credentials")
                return {"error": "Invalid admin credentials"}

        if interactive:
            while True:
                new_username = input("Add new username: ").strip()
                new_username = (new_username or "").strip()
                if not new_username:
                    print("Username cannot be empty")
                    continue
                new_password = getpass("Add new password: ")
                confirm_password = getpass("Confirm new password: ")
                if new_password != confirm_password:
                    print("Passwords do not match.")
                    continue
                if not new_password:
                    print("Password cannot be empty")
                    continue
                cursor.execute('SELECT 1 FROM users WHERE username = %s', (new_username,))
                row = cursor.fetchone()
                if row:
                    print("Username already exists.")
                    continue
                hashed = ph.hash(new_password)
                cursor.execute(
                    'INSERT INTO users (username, "password") VALUES (%s, %s)',
                    (new_username, hashed)
                )
                print(f"Username {new_username} added.")
                add_more = input("Do you want to add more? (y/n): ").strip().lower()
                if add_more != "y":
                    return {"ok": True, "username": new_username}
        else:
            new_username = (new_username or "").strip()
            if not new_username:
                return {"error": "Username cannot be empty"}
            if new_password != confirm_password:
                return {"error": "Passwords do not match"}
            if not new_password:
                return {"error": "Password cannot be empty"}
            cursor.execute('SELECT 1 FROM users WHERE username = %s', (new_username,))
            row = cursor.fetchone()
            if row:
                return {"error": "Username already exists"}
            hashed = ph.hash(new_password)
            cursor.execute(
                'INSERT INTO users (username, "password") VALUES (%s, %s)',
                (new_username, hashed)
            )
            return {"ok": True, "username": new_username}

    except psycopg2.Error as e:
            log_error(f'Error: {e}')
            return {'error': str(e)}

    finally:
        if cursor is not None:
            cursor.close()
        if conn is not None:
            conn.close()