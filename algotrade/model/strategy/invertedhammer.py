import numpy as np
import pymannkendall as mk
from scipy.signal import argrelextrema


class InvertedHammer():
    def __init__(self):
        pass

    def is_inverted_hammer_candle(self,open, high, low, close):
        return (((high - low) > 3 * (open - close)) and
                ((high - close) / (.001 + high - low) > 0.6)
                and ((high - open) / (.001 + high - low) > 0.6))

    def is_inverted_hammer_valid(self,data, prev_data):
        is_trend = False
        is_trade_allowed = False
        is_last_candle_vol_trade_allowed = False
        is_trend_momentum = False

        # Find slope of trend
        df_close = data['Close']
        output = mk.original_test(df_close)
        slope = output[7]
        p_value = output[2]
    
        # ihammer candle high should be last in the trend
        df_high = max(data['High'].to_list())
        hammer_high = data.iloc[-1]['High']
    
        # Min candle should green out of prev 10
        data_new = data.iloc[:-1]
        count_green = 0 
        max_vol_candle = 0
        for _,rows in data_new.iterrows():
            if(rows['Close']>=rows['Open']):
                count_green = count_green + 1
                if((int(rows['High']) - int(rows['Low'])) > max_vol_candle):
                    max_vol_candle = (int(rows['High']) - int(rows['Low']))

        # Last candle in the trend should not be the maximum volume. 
        # If not this may continue the trend and no revershal is expected.
        if((int(data_new[-1:]['High']) - int(data_new[-1:]['Low'])) != max_vol_candle):
            is_last_candle_vol_trade_allowed = True


            
        # Avoid sell setup near resistance
        #levels = get_levels(prev_data)
        #candle_low = data.iloc[-1]['Low']
        #sup_level = levels[1] - ((levels[1] - levels[0]) / 2)
        #if(candle_low >= sup_level):
        #    is_trade_allowed = True

        df_trend_low = min(data_new['Low'].to_list())
        df_trend_high = max(data_new['High'].to_list())
        if(int(df_trend_high) - int(df_trend_low)>=90):
            is_trend_momentum = True


        if(slope >= 4 and 
            p_value<=0.05 and 
            (df_high == hammer_high) and 
            count_green >= 7 and 
            is_last_candle_vol_trade_allowed==True and 
            is_trend_momentum==True):
        
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
