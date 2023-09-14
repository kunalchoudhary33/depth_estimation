import datetime

class Strategy():

    def __init__(self):
        self.percent = 1.5
        self.diff_mid_high_low = 10
        self.min_k_value = 50
        self.per_diff_close_low = 1.5
        


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
        data.ta.stoch(high='high', low='low', k=10, d=10, append=True)
        k = 0
        for _, row in data.iterrows():
            if(row['date']==date):
                k = row['STOCHk_10_10_3']
        if(k > 0 ):
            if(k >= self.min_k_value):
                status = False
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
    
    
    
    def tralling_decay_target(self, buy_date, curr_date):
        decay_target = False
        print(type(buy_date))
        print(type(curr_date))
        date_min = datetime.datetime.strptime(buy_date) + datetime.timedelta(minutes=35)
        if(curr_date>=date_min):
            decay_target = True
        return decay_target
    
    
    def check_strategy(self, open, high, low, close):
        buy_price = 0
        is_buy = self.bull_candle(open, high, low, close)
        buy_price = (open + close) / 2

        return is_buy, buy_price
    
    
    