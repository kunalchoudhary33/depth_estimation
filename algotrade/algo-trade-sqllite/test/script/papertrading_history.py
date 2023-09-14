import math
import logging
import glob
import pandas as pd
import pandas_ta as ta

from src.script.py_mysql import Mysql_Server
import test_strategy
from utils import decide

logging.basicConfig(level=logging.DEBUG)

class PaperTrading_History():

    def __init__(self):
        self.test_strategy_obj = test_strategy.Strategy()
        data = "C:/Users/Aumni/Desktop/sample/29-Dec/algo-trade-sqllite/src/data/"
        self.dataframe = pd.DataFrame()
#         for csv in glob.glob(data+"*.csv"):
#             dataframe_1 = pd.read_csv(csv)
#             self.dataframe = pd.concat([self.dataframe, dataframe_1])
            
        self.amount = 100000
        self.target = 5
        self.stoploss = 30
        self.is_trade = False   
        self.trade_date = None

    def sell_stock(self,open, high, low, close, buy_price, target, stoploss):
        is_profit = False
        sell_trade = False
        unit = self.amount/buy_price
        traded_amount = 0
        target_price = buy_price + buy_price*(target/100)     
        stop_loss_price = buy_price - buy_price*(stoploss/100)

        if(target_price < high):
            traded_amount = (target_price * unit) - (buy_price * unit)
            sell_trade = True
            is_profit = True
            
        if(stop_loss_price > low):
            traded_amount = (buy_price * unit) - (stop_loss_price * unit)
            sell_trade = True
            is_profit = False
        
        return sell_trade, is_profit, traded_amount


    def stock_analysis(self):
        per = []
        diff = []
        is_buy = []
        for _, rows in self.data.iterrows():
            open = rows['open']
            high = rows['high']
            low = rows['low']
            close = rows['close']
            a,b,c,d = decide(open, high, low, close)
            per.append(c)
            diff.append(d)
            is_buy.append(a)
        new_data = self.data
        new_data['per'] = per
        new_data['diff'] = diff
        new_data['is_buy'] = is_buy

        return new_data
    
    
    def is_trade_time_range(self, date):
        is_trade_time = False
        hour = int(str(date)[11:13])
        minute = int(str(date)[14:16])
        if(hour==13 and minute>=15):
            is_trade_time = True
        if(hour>=15):
            is_trade_time = True
        if(hour<=9 and minute<=30):
            is_trade_time = True
        return is_trade_time

    



def main():
    buy_time = []
    sell_time = []
    b_price = []
    total_amount = []
    k_value = []
    p_l = []
    p_l_a = []
    view_data = pd.DataFrame()
    trade = PaperTrading_History()
    traded_date = []
    
    #data = trade.dataframe.sort_values(by='date')
    data_path = "C:/Users/Aumni/Desktop/sample/29-Dec/algo-trade-sqllite/src/data/"
    #data = pd.DataFrame()
    files = glob.glob(data_path+"*.csv")
    files = sorted(files, key=lambda file:file.lower())
          
    for csv in files:
        data = pd.read_csv(csv)
        for _, last_row in data.iterrows():
            date = last_row['date']
            open = last_row['open']
            high = last_row['high']
            low = last_row['low']
            close = last_row['close']
            if(trade.is_trade==False):
                buy_trade, buy_price = trade.test_strategy_obj.check_strategy(open, high, low, close)
                is_trade_time = trade.is_trade_time_range(date)
                unique_trade_date = last_row['date'].split(" ")[0]
                smi_status, k = trade.test_strategy_obj.smi_value(last_row['date'], data)
                #if(buy_trade==True and buy_price>0 and is_trade_time==False and smi_status==True and unique_trade_date not in traded_date):
                if(buy_trade==True and buy_price>0 and is_trade_time==False and smi_status==True):
                    trade.is_trade = True
                    buy_time.append(last_row['date'])
                    b_price.append(buy_price)
                    trade.trade_date = last_row['date']
                    traded_date.append(last_row['date'].split(" ")[0])
                    k_value.append(k)
            if(trade.is_trade==True):
                sell_trade, is_profit, traded_amount = trade.sell_stock(open, high, low, close, buy_price, trade.target, trade.stoploss) 

                if(sell_trade):
                    trade.is_trade = False
                    if(is_profit):
                        sell_time.append(last_row['date'])
                        p_l.append('Profit')
                        p_l_a.append(math.ceil(traded_amount))
                        trade.amount = trade.amount + traded_amount
                        total_amount.append(math.ceil(trade.amount))
                    else:
                        sell_time.append(last_row['date'])
                        p_l.append('Loss')
                        p_l_a.append(math.ceil(traded_amount))
                        trade.amount = trade.amount - traded_amount
                        total_amount.append(math.ceil(trade.amount))
    
    view_data['buy_time'] = buy_time
    view_data['sell_time'] = sell_time
    view_data['b_price'] = b_price
    view_data['p_l'] = p_l
    view_data['p_l_a'] = p_l_a
    view_data['total_amount'] = total_amount
    view_data['k_value'] = k_value
    with pd.option_context("display.max_rows", 1000):
        print(view_data.head(100))


        
        
if __name__=="__main__":
    main()