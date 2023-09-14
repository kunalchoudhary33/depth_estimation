import math
import logging

from src.script.py_mysql import Mysql_Server
from utils import decide
import test_strategy

logging.basicConfig(level=logging.DEBUG)

class Test_Trade():

    def __init__(self):
        self.py_mysql_obj = Mysql_Server() 
        self.data = self.py_mysql_obj.fetch_ticks()
        self.test_strategy_obj = test_strategy.Strategy()
        
        self.amount = 100000
        self.target = 10
        self.stoploss = 30
        self.is_trade = False
        

    def sell_stock(self,open, high, low, close, buy_price, target, stoploss):
        is_profit = False
        sell_trade = False
        unit = self.amount/buy_price
        traded_amount = 0
        target_price = buy_price + buy_price*(target/100)     
        stop_loss_price = buy_price - buy_price*(stoploss/100)

        if(target_price < high):
            sell_trade = True
            is_profit = True
            traded_amount = (target_price * unit) - (buy_price * unit)
            self.amount = self.amount + traded_amount
            print("Total Amount : "+str(self.amount))
            
        if(stop_loss_price > low):
            sell_trade = True
            is_profit = False
            traded_amount = (buy_price * unit) - (stop_loss_price * unit)
            self.amount = self.amount - traded_amount
            print("Total Amount : "+str(self.amount))
            
        
        return sell_trade, is_profit, traded_amount


    def stock_analysis(self):
        per = []
        diff = []
        is_buy = []
        diff_per = []
        for _, rows in self.data.iterrows():
            open = rows['open']
            high = rows['high']
            low = rows['low']
            close = rows['close']

            a,b,c,d = decide(open, high, low, close)
            per.append(c)
            diff.append(d)
            is_buy.append(a)
            diff_per.append((close - low) / close * 100)

        new_data = self.data
        new_data['per'] = per
        new_data['diff'] = diff
        new_data['diff_per'] = diff_per
        new_data['is_buy'] = is_buy

        return new_data




def main():
    trade = Test_Trade()
    #print(trade.data.head(5))
    new_data = trade.stock_analysis()
    data_new = new_data.loc[new_data['per']>0]
    print(data_new.tail(100))

    for _, last_row in trade.data.iterrows():
        open = last_row['open']
        high = last_row['high']
        low = last_row['low']
        close = last_row['close']
        if(trade.is_trade==False):

            buy_trade, buy_price = trade.test_strategy_obj.check_strategy(open, high, low, close)
    
            if(buy_trade==True and buy_price>0 and int(str(last_row['date'])[11:13])<15):
                trade.is_trade = True
                logging.info("Time is : "+str(last_row['date'])+" Buy around "+str(buy_price))
        if(trade.is_trade==True):
            sell_trade, is_profit, traded_amount = trade.sell_stock(open, high, low, close, buy_price, trade.target, trade.stoploss)
            if(sell_trade):
                trade.is_trade = False
                if(is_profit):
                    logging.info("Time is : "+str(last_row['date'])+" profit is amount Rs : "+str(math.ceil(traded_amount)))
                else:
                    logging.info("Time is : "+str(last_row['date'])+" loss is amount Rs : -"+str(math.ceil(traded_amount)))


if __name__=="__main__":
    main()