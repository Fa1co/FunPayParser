import sqlite3 as sl

from sqlite3 import Error

def sql_connection():
    try:
        connect = sl.connect('FunPay.db')
    except Error:
        print(Error)
    return connect
def sql_table(connect):

    cursor_obj = connect.cursor()
    cursor_obj.execute("CREATE TABLE avg_price(id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, server_id INTEGER, price REAL, year TEXT, month TEXT, day TEXT)")
    connect.commit()


def sqt_table_insert(connect, price_list):
    connect.execute(f'''INSERT INTO avg_price (server_id, price, year, month, day) VALUES (?,?,?,?,?) ''', price_list)
    connect.commit()




