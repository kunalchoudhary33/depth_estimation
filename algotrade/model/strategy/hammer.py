import numpy as np
import pymannkendall as mk
from scipy.signal import argrelextrema


class Hammer():
    def __init__(self):
        pass
    
    def is_hammer_candle(self,open, high, low, close):
        return (((high - low) > 3 * (open - close)) and
                ((close - low) / (.001 + high - low) > 0.6) and
                ((open - low) / (.001 + high - low) > 0.6))


    def is_hammer_valid(self,data, prev_data):
        is_trend = False
        is_trade_allowed = False
        is_last_candle_vol_trade_allowed = False
        is_trend_momentum = False
    
        # Find slope of trend
        df_close = data['Close']
        output = mk.original_test(df_close)
        slope = output[7]
        p_value = output[2]
    
        # Low of hammer candle should be minimum of the trend
        df_low = min(data['Low'].to_list())
        hammer_low = data.iloc[-1]['Low']
    
        # Min candle should red out of prev 10
        data_new = data.iloc[:-1]
        count_red = 0
        max_vol_candle = 0
        for _,rows in data_new.iterrows():
            if(rows['Open']>=rows['Close']):
                count_red = count_red + 1
                if((int(rows['High']) - int(rows['Low'])) > max_vol_candle):
                    max_vol_candle = (int(rows['High']) - int(rows['Low']))

        if((int(data_new[-1:]['High']) - int(data_new[-1:]['Low'])) != max_vol_candle):
            is_last_candle_vol_trade_allowed = True
        

        # Avoid buy setup near resistance
        #levels = get_levels(prev_data)
        #candle_high = data.iloc[-1]['High']
        #res_level = levels[1] + ((levels[2] - levels[1]) / 2)
        #if(candle_high <= res_level):
        #    is_trade_allowed = True

        df_trend_low = min(data_new['Low'].to_list())
        df_trend_high = max(data_new['High'].to_list())
        if(int(df_trend_high) - int(df_trend_low)>=90):
            is_trend_momentum = True
    

        if(slope <= -7 and 
            p_value<=0.05 and 
            (df_low == hammer_low) and 
            count_red >= 7 and 
            is_last_candle_vol_trade_allowed == True and
            is_trend_momentum == True):

            max_idx = argrelextrema(data_new['High'].values, np.greater, order=10)[0]
            min_idx = argrelextrema(data_new['Low'].values, np.less, order=10)[0]
        
            #if(len(max_idx)==0 and len(min_idx)==0):
            is_trend = True
            #    print("##########################################################################")
            #    print(data_new.iloc[-1]['Date'])
            #    print("max_idx : "+str(max_idx))
            #    print("min_idx : "+str(min_idx))
            #    print("##########################################################################")

        return is_trend
