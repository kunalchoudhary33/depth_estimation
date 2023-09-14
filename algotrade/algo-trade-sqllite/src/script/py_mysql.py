import sqlite3
import pandas as pd
import datetime


class Mysql_Server():

    def __init__(self):
        self.connection_obj = sqlite3.connect('database/mydatabase.db')

    def insert_ticks(self,ticks):
        cursorObj = self.connection_obj.cursor()
        insert_into_table="""insert into ticks(last_price,date) values(?,?);"""
        for tick in ticks:
            last_price = tick['last_price']
            date_org = tick['timestamp']
            date_min = date_org + datetime.timedelta(minutes=30)
            date_final = date_min + datetime.timedelta(hours=5)
            data_tuple = (last_price,date_final)
            cursorObj.execute(insert_into_table,data_tuple)
        try:
            self.connection_obj.commit()
        except Exception:
            self.connection_obj.rollback()

    def fetch_ticks(self):
        data=pd.read_sql('select * from ticks',con=self.connection_obj,parse_dates=['date'])
        data=pd.DataFrame(data)
        if(len(data)>0):
            data=data.set_index(['date'])
            ticks=data.loc[:,['last_price']]
            data=ticks['last_price'].resample('5min').ohlc().dropna().reset_index()
        return data

    def truncate_table(self):
        cursor=self.connection_obj.cursor()
        cursor.execute("Delete from ticks;")
        try:
            self.connection_obj.commit()
        except Exception:
            self.connection_obj.rollback()        
