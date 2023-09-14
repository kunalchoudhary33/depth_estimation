from kiteconnect import KiteConnect
import datetime
import logging
import json
import time
import pandas_ta as ta
import sys
import warnings
warnings.filterwarnings("ignore")

sys.path.insert(1, '/home/ubuntu/algotrade/')
from execution.script.bot_util import BotUtil
from model.strategy.redgreen import RedGreen
from database.script.database_server import Database_Server
CRED_CONFIG_PATH = "/home/ubuntu/algotrade/execution/config/cred.json"
CONFIG_PATH = "/home/ubuntu/algotrade/execution/config/config.json"
PRICE_CONFIG_PATH = "/home/ubuntu/algotrade/execution/config/price_config.json"

logging.basicConfig(level=logging.DEBUG)

class Trade():

    def __init__(self):
        with open(CRED_CONFIG_PATH, 'r') as f:
            cred_config = json.load(f)
        self.api_key = cred_config['key'] 
        self.access_token = cred_config['access_tkn']
        self.kite = KiteConnect(api_key=self.api_key)
        self.kite.set_access_token(access_token=self.access_token)
        self.position = self.kite.positions()

        self.py_mysql_obj = Database_Server() 
        self.bot = BotUtil()

        #self.trade_count = 0
        self.last_traded_price = 0

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

    def get_ltp(self):
        try:
            with open(PRICE_CONFIG_PATH, 'r') as f:
                config = json.load(f)
            self.last_traded_price = [config['ltp']][0]
        except Exception as ex:
            pass
        return self.last_traded_price




def main():
    logging.info("Algo Trade Started.")
    trade_obj = Trade()
    rg_obj = RedGreen()
    minute_ls = 0
    mhigh = 0
    mlow = 0
    resistance_ls = []
    support_ls = []
    is_strategy_found = False
    trade_option = ""
    trade_expire_time = datetime.datetime.now()
    trade_count = 0

    while True:
        if(trade_count>=3):
            logging.info('Day End')
            break

        if(is_strategy_found==False):
            obj_now = datetime.datetime.now()
            minute = obj_now.minute
            if(minute != minute_ls):
                minute_ls = minute
                time.sleep(1.5)
                logging.info("#############################################################################################")
                curr_time = datetime.datetime.now()
                curr_time_min = curr_time + datetime.timedelta(minutes=30)
                curr_time_timezone = curr_time_min + datetime.timedelta(hours=5)
                logging.info("Current time : "+str(curr_time_timezone))

                prev_data = trade_obj.fetch_all_data()

                rg_short_valid, mhigh, mlow, resistance_ls, support_ls =  rg_obj.is_rg_short_valid(prev_data, resistance_ls, support_ls)
                logging.info("resistance_ls : "+str(resistance_ls))
                logging.info("support_ls : "+str(support_ls))

                if(rg_short_valid==True):
                    is_strategy_found = True
                    trade_option = "PE"
                    logging.info("Setup found for : "+str(trade_option))
                    logging.info("Order will be places if prices breaks low : "+str(mlow))
                    curr_time = datetime.datetime.now()
                    curr_time_min = curr_time + datetime.timedelta(minutes=30)
                    curr_time_timezone = curr_time_min + datetime.timedelta(hours=5)
                    trade_expire_time = curr_time_timezone + datetime.timedelta(minutes=1)
                    continue

                rg_long_valid, mhigh, mlow, resistance_ls, support_ls =  rg_obj.is_rg_long_valid(prev_data, resistance_ls, support_ls)
                if(rg_long_valid==True):
                    is_strategy_found = True
                    trade_option = "CE"
                    logging.info("Setup found for : "+str(trade_option))
                    logging.info("Order will be placed if prices breaks high : "+str(mhigh))
                    curr_time = datetime.datetime.now()
                    curr_time_min = curr_time + datetime.timedelta(minutes=30)
                    curr_time_timezone = curr_time_min + datetime.timedelta(hours=5)
                    trade_expire_time = curr_time_timezone + datetime.timedelta(minutes=1)



        elif(is_strategy_found==True and trade_option=="CE"):
            ltp = trade_obj.get_ltp()
            curr_time = datetime.datetime.now()
            curr_time_min = curr_time + datetime.timedelta(minutes=30)
            curr_time_timezone = curr_time_min + datetime.timedelta(hours=5)
            if(ltp > mhigh):
                order_id = trade_obj.bot.place_order(mhigh, mlow, trade_option)
                logging.info("Order pending")
                #time.sleep(10)
                ltp = trade_obj.get_ltp()
                if(ltp >= mhigh):
                    logging.info("Order Confirmed")
                    order_id = trade_obj.bot.bot(trade_option)
                    logging.info("order_id : "+str(order_id))
                    trade_count = trade_count + 1
                    is_strategy_found=False
                #else:
                    #order_id = trade_obj.bot.slipage_execution()
                    #is_strategy_found=False
                    #logging.info("Slipage execution. Looking for new setup")
                    #logging.info("order_id : "+str(order_id))

            if(ltp < mlow or curr_time_timezone>=trade_expire_time):
                logging.info("Setup Canceled. Looking for new setup")
                is_strategy_found=False

        elif(is_strategy_found==True and trade_option=="PE"):
            ltp = trade_obj.get_ltp()
            curr_time = datetime.datetime.now()
            curr_time_min = curr_time + datetime.timedelta(minutes=30)
            curr_time_timezone = curr_time_min + datetime.timedelta(hours=5)
            if(ltp < mlow):
                order_id = trade_obj.bot.place_order(mhigh, mlow, trade_option)
                logging.info("Order pending")
                #time.sleep(10)
                ltp = trade_obj.get_ltp()
                if(ltp <= mlow):
                    logging.info("Order Confirmed")
                    order_id = trade_obj.bot.bot(trade_option)
                    logging.info("order_id : "+str(order_id))
                    trade_count = trade_count + 1
                    is_strategy_found=False
                #else:
                    #order_id = trade_obj.bot.slipage_execution()
                    #is_strategy_found=False
                    #logging.info("Slipage execution. Looking for new setup.")
                    #logging.info("order_id : "+str(order_id))

            if(ltp > mhigh or curr_time_timezone>=trade_expire_time):
                logging.info("Setup Canceled. Looking for new setup")
                is_strategy_found=False


        #logging.info("#############################################################################################")
        #logging.info("  ")


if __name__=="__main__":
    logging.info(' Algo will start at 9:17 am ')
    while True:
        curr_time = datetime.datetime.now()
        curr_time_min = curr_time + datetime.timedelta(minutes=30)
        curr_time_timezone = curr_time_min + datetime.timedelta(hours=5)
        minute = curr_time_timezone.minute
        hour = curr_time_timezone.hour
        logging.info('Waiting.. ')
        if(hour >= 9 and minute >= 17):
            logging.info("#############################################################################################")
            logging.info("ALGO STARTED!!!")
            time.sleep(1.5)
            main()
            break



## ssh -i C:/Users/Aumni/Downloads/algotrade.pem ubuntu@65.2.167.247
