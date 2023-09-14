import json
import pandas_ta as ta
import logging

logging.basicConfig(level=logging.DEBUG)
CONFIG_PATH = "src/config/config.json"

class Strategy():

    def __init__(self):
        with open(CONFIG_PATH, 'r') as f:
            config = json.load(f)        
        self.percent = config['percent']
        self.diff_mid_high_low = config['diff_mid_high_low']
        self.min_k_value = config['min_k_value']
        self.per_diff_close_low = config['per_diff_close_low']


    def bull_candle(self, open, high, low, close):
        is_buy = False
        if(open > close):
            percent_change = (open - close) / open * 100
            if(percent_change <= self.percent):
                mid = (open + close) / 2
                diff_high_mid = high - mid
                diff_mid_low = mid - low
                if(abs(diff_high_mid - diff_mid_low) < self.diff_mid_high_low):
                    is_buy = True
        return is_buy
    
    
    def smi_value(self, date, data):
        status = True    
        try:
            data.ta.stoch(high='high', low='low', k=10, d=1, append=True)
            k = 0
            for _, row in data.iterrows():
                if(row['date']==date):
                    k = row['STOCHk_10_1_3']
            if(k > 0 ):
                if(k >= self.min_k_value):
                    status = False
            logging.info("SMI values activated !!")
            
        except:
            status = False
            k = 0
            logging.info("SMI values not activated !!")
            
        return status, k
    
    
    def low_bull_candle(self, open, high, low, close):
        is_buy = False
        if(open>close):
            percent_change = (open - close) / open * 100
            if(percent_change <= self.percent):
                per_diff_close_low = (close - low) / close * 100
                if(per_diff_close_low <= self.per_diff_close_low):
                    is_buy = True
        return is_buy
    
    
    def check_strategy(self, open, high, low, close):
        is_buy = self.bull_candle(open, high, low, close)
#         if(is_buy==False):
#             is_buy = self.low_bull_candle(open, high, low, close)
        return is_buy
    
    
    