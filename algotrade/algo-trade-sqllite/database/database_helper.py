import sqlite3
from sqlite3 import Error


def sql_connection():
    try:
        con = sqlite3.connect(':memory:')
        print("Connection is established: Database is created in memory")
    except Error:
        print(Error)
    finally:
        con.close()


def sql_connection():
    try:
        con = sqlite3.connect('D:/algotrade/database/mydatabase.db')
        return con
    except Error:
        print(Error)

def sql_table(con):
    cursorObj = con.cursor()
    cursorObj.execute("create table ticks(last_price float(32),date timestamp)")
    con.commit()

con = sql_connection()
sql_connection()
sql_connection()
#sql_table(con)