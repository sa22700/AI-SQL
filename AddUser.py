import psycopg2
from argon2 import PasswordHasher, exceptions
from DebugLog import log_error
from Connection import connect
from getpass import getpass

def add_new_user():
    cursor = None
    conn = None
    print('Login into main account!')
    while True:
        login = input('Username: ')
        main_password = getpass('Password: ')
        try:
            conn = connect()
            conn.autocommit = True
            cursor = conn.cursor()
            ph = PasswordHasher()
            cursor.execute('SELECT "password" FROM users WHERE username = %s', (login,))
            row = cursor.fetchone()
            if not row:
                print('Faulty username or password')
                retry = input('Try again? (y/n): ')
                if retry.lower() != 'y':
                    break
                cursor.close()
                cursor = None
                conn.close()
                conn = None
                continue
            try:
                ph.verify(row[0], main_password)

            except (exceptions.VerifyMismatchError, exceptions.VerificationError):
                print('Faulty username or password')
                retry = input('Try again? (y/n): ')
                if retry.lower() != 'y':
                    break
                cursor.close()
                cursor = None
                conn.close()
                conn = None
                continue

            add_user = input('Add new user username: ')
            add_password = getpass('Add new password: ')
            again_password = getpass('Confirm password: ')
            if add_password != again_password:
                print('Passwords do not match.')
                continue
            if not add_password:
                print('Password cannot be empty.')
                continue
            cursor.execute('SELECT * FROM users WHERE username = %s', (add_user,))
            if cursor.fetchone():
                print('Username already exists.')
                continue
            hashed_password = ph.hash(add_password)
            cursor.execute(f'INSERT INTO users (username, "password") VALUES (%s, %s)',
                    (add_user, hashed_password ))
            print(f'Username {add_user} added.')
            add_more = input('Do you want to add more? (y/n)')
            if add_more == 'y':
                continue
            elif add_more == 'n':
                break
            else:
                print('Faulty username or password')
                retry = input('Try again? (y/n): ')
                if retry.lower() != 'y':
                    break

        except psycopg2.Error as e:
            print(f'Error: {e}')
            log_error(f'Error: {e}')

        finally:
            cursor.close()
            conn.close()