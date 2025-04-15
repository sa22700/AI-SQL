import psycopg2

def connect():
    return psycopg2.connect(
        host='192.168.68.51',
        user='admin',
        password='admin123',
        port='5432',
        database='postgres'
    )