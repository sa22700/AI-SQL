import psycopg2
from argon2 import PasswordHasher, exceptions
from DebugLog import log_error

def ask_user():
    connect = psycopg2.connect(
        host='192.168.68.51',
        user='admin',
        password='admin123',
        port='5432',
        database='postgres'
    )
    connect.autocommit = True
    cursor = connect.cursor()
    ph = PasswordHasher()

    while True:
        ask_user_id = input('Username: ')
        add_password = input('Password: ')

        cursor.execute(f'SELECT password FROM users WHERE username = %s', (ask_user_id,))
        result = cursor.fetchone()

        if result:
            stored_hash = result[0]
            try:
                if ph.verify(stored_hash, add_password):
                    print("Login successful!")
                    cursor.close()
                    connect.close()
                    return True
            except exceptions.VerifyMismatchError:
                print("Wrong password.")
                log_error('Wrong password')

            finally:
                cursor.close()
                connect.close()
        else:
            print("Cannot find user in database.")
            cursor.close()
            connect.close()
            return False
