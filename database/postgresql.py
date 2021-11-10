import psycopg2

from config import DB_HOST, DB_NAME, DB_PASS, DB_USER


# connection to db
def sql_start():
    global base, cur
    base = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST)
    cur = base.cursor()
    if base:
        print('DB connected success')
    cur.execute('SELECT EXISTS(SELECT * FROM information_schema.tables WHERE table_name=%s)', ('currency_data',))
    is_table_exist = cur.fetchone()[0]
    if is_table_exist == False:
        cur.execute('CREATE TABLE currency_data(id SERIAL PRIMARY KEY, currency_info JSON)')
        base.commit()

def is_table_empty():
    cur.execute('SELECT EXISTS(SELECT * FROM currency_data)')
    is_empty = cur.fetchone()[0]
    print(is_empty)

async def insert_value(json_data):
    cur.execute('INSERT INTO currency_data (currency_info) VALUES (%s)', (json_data,))
    base.commit()

async def max_id():
    cur.execute('SELECT MAX(id) FROM currency_data')
    max_id_from_table = cur.fetchone()
    return max_id_from_table[0]

async def get_data(id):
    cur.execute('SELECT * FROM currency_data WHERE id=%s', (id,))
    return cur.fetchone()