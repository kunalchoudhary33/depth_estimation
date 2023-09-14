from kiteconnect import KiteConnect
from datetime import datetime
import logging
import json
import time
import pandas_ta as ta

import strategy
import trade_utils
import py_mysql

logging.basicConfig(level=logging.DEBUG)

CRED_CONFIG_PATH = "src/config/cred.json"
CONFIG_PATH = "src/config/config.json"

class Trade():

    def __init__(self):
        with open(CRED_CONFIG_PATH, 'r') as f:
            cred_config = json.load(f)
        self.api_key = cred_config['key'] 
        self.access_token = cred_config['access_tkn']
        self.kite = KiteConnect(api_key=self.api_key)
        self.kite.set_access_token(access_token=self.access_token)
        self.position = self.kite.positions()

        self.py_mysql_obj = py_mysql.Mysql_Server() 

    def fetch_last_rows(self):
        data = self.py_mysql_obj.fetch_ticks()
        last_row = data.iloc[-2]
        date = last_row['date']
        open = last_row['open']
        high = last_row['high']
        low = last_row['low']
        close = last_row['close']
        return date, open, high, low, close
    
    def fetch_all_data(self):
        data = self.py_mysql_obj.fetch_ticks()
        return data
    
    def exist_trade(self):
        is_trade_exist = False
        for i in self.position['net']:
            quantity = i['quantity']
            if(quantity>0):
                is_trade_exist = True
                break
        return is_trade_exist
    
    
    def is_trade_time_range(self, date):
        is_trade_time = False
        hour = int(str(date)[11:13])
        minute = int(str(date)[14:16])
        if(hour==14 and minute>=25):
            is_trade_time = True
        if(hour>=15):
            is_trade_time = True
#         if(hour<=9 and minute<=30):
#             is_trade_time = True
        return is_trade_time
        


def main():
    trade_obj = Trade()
    strategy_obj = strategy.Strategy()
    trade_utils_obj = trade_utils.Trade_utils()
    
    while True:
        obj_now = datetime.now()
        if(obj_now.minute % 5 ==0):
            time.sleep(2)
            
            date, open, high, low, close = trade_obj.fetch_last_rows()
            is_buy = strategy_obj.check_strategy(open, high, low, close)   
            is_trade = trade_obj.exist_trade()
            is_trade_time = trade_obj.is_trade_time_range(date)
            data = trade_obj.fetch_all_data()
            smi_status, k = strategy_obj.smi_value(date, data)
            
            if(is_buy==True and is_trade==False and is_trade_time==False and smi_status==True):
                order_id = trade_utils_obj.place_order()
                logging.info("Buy Tick for : "+str(date))
                logging.info("Order Id for buying is : "+order_id)
                time.sleep(240)
                # break if you want only 1 trade per day
                #break
            elif(is_buy==False):
                logging.info("No Trade for  : "+str(date))
                time.sleep(240)
            else:
                continue
        else:
            continue
        
    
if __name__=="__main__":
    main()
