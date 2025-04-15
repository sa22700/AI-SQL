import psycopg2
from SchemaBuilder import schema_tables, column_builder
from DebugLog import log_error

def database():
    connect = None
    cursor = None
    table_name = None
    add_more = None
    data = None
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

                create_table = input('Create table? (y/n): ').lower()
                if create_table == 'n':
                    break
                elif create_table == 'y':
                    table_name = input('Type new table name: ')
                    try:
                        cursor.execute(f'''
                        CREATE TABLE IF NOT EXISTS {table_name} (
                        id SERIAL PRIMARY KEY,
                        part_name TEXT,
                        part_number TEXT UNIQUE,
                        category TEXT,
                        price DOUBLE PRECISION
                        );
                        ''')
                        print(f'Table "{table_name}" created.')

                    except psycopg2.Error as e:
                        print(f'Error creating table: {e}')
                        log_error(f'Error creating table: {e}')
                        return

                columns = column_builder()
                schema_tables(table_name, columns)

                add_data = input('Add data? (y/n): ').lower()
                if add_data == 'y':
                    data = []
                    while True:
                        try:
                            part = input('Part name: ')
                            number = input('Part number: ')
                            category = input('Category: ')
                            price = float(input('Price: '))
                            data.append((part, number, category, price))
                            add_more = input('Add more data? (y/n): ').lower()

                        except ValueError:
                            print('Price must be number')

                        if add_more == 'n':
                            break
                        elif add_more == 'y':
                            continue

                for part, number, category, price in data:
                    try:
                        cursor.execute(
                            f'INSERT INTO {table_name} (part_name, part_number, category, price) VALUES (%s, %s, %s, %s);',
                            (part, number, category, price)
                        )
                    except psycopg2.Error as e:
                        print(f'Error inserting data: {e}')
                        log_error(f'Error inserting data: {e}')

                print('-' * 32)
                try:
                    query = f'SELECT * FROM {table_name};'
                    cursor.execute(query)
                    print('\nColumns:')
                    for column in cursor.description:
                        print(column[0], end=' ')
                    print('\nRows:')
                    for row in cursor.fetchall():
                        print(row)
                except psycopg2.Error as e:
                    print(f'Error fetching data: {e}')
                    log_error(f'Error fetching data: {e}')

            except psycopg2.Error as e:
                print(f'Database error: {e}')
                log_error(f'Database error: {e}')

            finally:
                cursor.close()
                connect.close()
