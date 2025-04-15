import psycopg2
from psycopg2 import sql
from SchemaBuilder import schema_tables, column_builder
from DebugLog import log_error
from Connection import connect

def database():
    conn = None
    cursor = None
    table_name = None
    add_more = None
    data = None
    while True:
        login = input('Username: ')
        main_password = input('Password: ')

        if login == 'admin' and main_password == 'admin123':
            try:
                conn = connect()
                conn.autocommit = True
                cursor = conn.cursor()

                create_table = input('Create table? (y/n): ').lower()
                if create_table == 'n':
                    break
                elif create_table == 'y':
                    table_name = input('Type new table name: ')
                    try:
                        safe_sql = sql.SQL('''
                            CREATE TABLE IF NOT EXISTS {} (
                                id SERIAL PRIMARY KEY,
                                part_name TEXT,
                                part_number TEXT UNIQUE,
                                category TEXT,
                                price DOUBLE PRECISION
                            );
                        ''').format(sql.Identifier(table_name))
                        cursor.execute(safe_sql)
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
                        insert_sql = sql.SQL('''
                            INSERT INTO {} (part_name, part_number, category, price)
                            VALUES (%s, %s, %s, %s);
                        ''').format(sql.Identifier(table_name))

                        cursor.execute(insert_sql, (part, number, category, price))

                    except psycopg2.Error as e:
                        print(f'Error inserting data: {e}')
                        log_error(f'Error inserting data: {e}')

                print('-' * 32)
                try:
                    select_sql = sql.SQL('SELECT * FROM {}').format(sql.Identifier(table_name))
                    cursor.execute(select_sql)
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
                conn.close()
