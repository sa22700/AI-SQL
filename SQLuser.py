import psycopg2
from argon2 import PasswordHasher, exceptions
from DebugLog import log_error
from Connection import connect

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
                empty_password = input('Please add new password: ')
                hash_new_password = ph.hash(empty_password)
                cursor.execute('INSERT INTO users (username, "password") VALUES (%s, %s);',
                           (empty_user, hash_new_password))
                print(f'Username {empty_user} added.')

            ask_user_id = input('Username: ')
            add_password = input('Password: ')

            cursor.execute(f'SELECT password FROM users WHERE username = %s', (ask_user_id,))
            result = cursor.fetchone()

            if result:
                stored_hash = result[0]
                try:
                    if ph.verify(stored_hash, add_password):
                        print("Login successful!")
                        break

                except exceptions.VerifyMismatchError:
                    print("Wrong password.")
                    log_error('Wrong password')

            else:
                print("Cannot find user in database.")

    except psycopg2.Error as e:
        print(f"Error: {e}")
        log_error(f"Error in ask_user(): {e}")

    finally:
        cursor.close()
        conn.close()
