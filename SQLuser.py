import psycopg2
from argon2 import PasswordHasher, exceptions
from DebugLog import log_error
from Connection import connect
from getpass import getpass

def ask_user():
    conn = None
    cursor = None
    try:
        conn = connect()
        conn.autocommit = True
        cursor = conn.cursor()
        ph = PasswordHasher()
        while True:
            cursor.execute('SELECT COUNT(*) FROM users')
            is_empty = cursor.fetchone()[0]
            if is_empty == 0:
                print('User list is empty.')
                empty_user = input('Please add new user: ')
                empty_password = getpass('Please add new password: ')
                again_password = getpass('Confirm password: ')
                if empty_password != again_password:
                    print('Passwords do not match.')
                    continue
                if not empty_password:
                    print('Password cannot be empty.')
                    continue
                hash_new_password = ph.hash(empty_password)
                cursor.execute('INSERT INTO users (username, "password") VALUES (%s, %s);',
                           (empty_user, hash_new_password))
                print(f'Username {empty_user} added.')
            ask_user_id = input('Username: ')
            add_password = getpass('Password: ')
            if not add_password:
                print('Password cannot be empty.')
                continue
            cursor.execute(f'SELECT password FROM users WHERE username = %s', (ask_user_id,))
            result = cursor.fetchone()
            if result:
                stored_hash = result[0]
                try:
                    if ph.verify(stored_hash, add_password):
                        print("Login successful!")
                        return True

                except exceptions.VerifyMismatchError:
                    print("Wrong password.")
                    log_error('Wrong password')

            else:
                print("Cannot find user in database.")

    except psycopg2.Error as e:
        print(f"Error: {e}")
        log_error(f"Error in ask_user(): {e}")


    finally:

        if cursor is not None:
            cursor.close()

        if conn is not None:
            conn.close()

    return False
