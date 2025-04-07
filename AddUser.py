import psycopg2
from argon2 import PasswordHasher
from DebugLog import log_error

def add_new_user():
    cursor = None
    connect = None
    print('Login into main account!')
    while True:
        login = input('Username: ')
        main_password = input('Password: ')

        if login == 'admin' and main_password == 'admin123':
            try:
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
                add_user = input('Add new user username: ')
                add_password = input('Add new password: ')

                cursor.execute('SELECT * FROM users WHERE username = %s;', (add_user,))
                if cursor.fetchone():
                    print('Username already exists.')
                    continue

                hashed_password = ph.hash(add_password)
                cursor.execute(f'INSERT INTO users (username, "password") VALUES (%s, %s);',
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
                connect.close()
        else:
            print('Faulty username or password')