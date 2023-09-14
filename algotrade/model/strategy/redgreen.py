import numpy as np
import pandas_ta  as ta
from scipy.signal import argrelextrema
import logging
import datetime

logging.basicConfig(level=logging.DEBUG)

class RedGreen():

    def __init__(self):
        self.risk_reward_ratio = 3.00


    def candle_color(self, open, close):
        color = ""
        if(open>=close):
            color = "red"
        else:
            color = "green"
        return color

    def get_ema(self, data, trade_option):
        curr_time = datetime.datetime.now()
        curr_time_min = curr_time + datetime.timedelta(minutes=30)
        curr_time_timezone = curr_time_min + datetime.timedelta(hours=5)
        minute = curr_time_timezone.minute
        hour = curr_time_timezone.hour

        if(hour == 9 and minute<20):
            if(trade_option=="CE"):
                ema = data.iloc[-2]['high']+5
            elif(trade_option=="PE"):
                ema = data.iloc[-2]['low']-5
        else:
            ema = ta.ema(data['close'], 5).to_list()[-2]
        return round(ema,2)


    def get_sup_res(self, data, resistance_ls, support_ls):
        data_new = data
        resistance_ls = []
        support_ls = []
        max_idx = argrelextrema(data_new['high'].values, np.greater, order=5)[0]
        min_idx = argrelextrema(data_new['low'].values, np.less, order=5)[0]

        if(len(max_idx)==0):
            resistance_ls.append(data.iloc[0]['high'])
        if(len(min_idx)==0):
            support_ls.append(data.iloc[0]['low'])
        if(len(max_idx)>=1):
            #for ls in max_idx:
                #resistance_ls.append(data.iloc[ls]['high'])
            resistance_ls.clear()
            resistance_ls.append(data.iloc[max_idx[-1]]['high'])
        if(len(min_idx)>=1):
            #for ls in min_idx:
                #support_ls.append(data.iloc[ls]['low'])
            support_ls.clear()
            support_ls.append(data.iloc[min_idx[-1]]['low'])


        #resistance_ls = list(set(resistance_ls))
        #support_ls = list(set(support_ls))

        #resistance_ls = sorted(resistance_ls, key=int, reverse=True)
        #support_ls = sorted(support_ls, key=int, reverse=False)

        return resistance_ls, support_ls


    def get_high_low(self, data):
        max_high = max(data.iloc[-3]['high'], data.iloc[-2]['high'])
        min_low = min(data.iloc[-3]['low'], data.iloc[-2]['low'])
        return max_high, min_low


    def is_risk_reward_valid_long(self, mhigh, mlow, resistance_ls, support_ls):
        is_rr_valid = False
        target_value = 0
        if(len(resistance_ls)>1):
            count = 0
            for res in resistance_ls:
                if(count == 0 and mhigh > res):
                    target_value = resistance_ls[0]
                    break

                elif(mhigh > res):
                    target_value = resistance_ls[count-1]
                    break

                elif(count == len(resistance_ls)-1 and mhigh < res):
                    target_value = resistance_ls[count]
                    break

                count = count + 1
        else:
            target_value = resistance_ls[0]

        risk = mhigh - mlow
        reward = target_value - mhigh
        rr = reward / risk


        if(rr >= self.risk_reward_ratio):
            is_rr_valid = True
            logging.info("########### This is CE   ####################")
            logging.info("risk reward : "+str(rr))
            logging.info("mhigh : "+str(mhigh))
            logging.info("mlow : "+str(mlow))
            logging.info("target_value : "+str(target_value))
            logging.info("#############################################")

        return is_rr_valid

    def is_risk_reward_valid_short(self, mhigh, mlow, resistance_ls, support_ls):

        is_rr_valid = False

        target_value = 0
        if(len(support_ls)>1):
            count = 0
            for sup in support_ls:
                if(count == 0 and mlow < sup):
                    target_value = support_ls[0]
                    break

                elif(mlow < sup):
                    target_value = support_ls[count-1]
                    break

                elif(count == len(support_ls)-1 and mlow > sup):
                    target_value = support_ls[count]
                    break

                count = count + 1
        else:
            target_value = support_ls[0]

        risk = mhigh - mlow
        reward = mlow - target_value
        rr = reward / risk
        if(rr >= self.risk_reward_ratio):
            is_rr_valid = True
            logging.info("########### This is PE   ####################")
            logging.info("risk reward : "+str(rr))
            logging.info("mhigh : "+str(mhigh))
            logging.info("mlow : "+str(mlow))
            logging.info("target_value : "+str(target_value))
            logging.info("#############################################")
        return is_rr_valid

    def is_rg_long_valid(self, data, resistance_ls, support_ls):
        resistance_ls, support_ls = self.get_sup_res(data, resistance_ls, support_ls)
        logging.info("Looking for Long setup")
        is_rg_valid = False
        mhigh = 0
        mlow = 0
        if(len(data)>2):
            prev_color = self.candle_color(data.iloc[-3]['open'], data.iloc[-3]['close'])
            curr_color = self.candle_color(data.iloc[-2]['open'], data.iloc[-2]['close'])
            ## Calculate 5ema and if last candle high is less than 5ema
            ema = self.get_ema(data, "CE")
            prev_high = data.iloc[-2]['high']
            is_rg_valid_candle_size = self.is_rg_valid_candle_size(data, 'CE')
            if(prev_color != curr_color and prev_high < ema and is_rg_valid_candle_size == True):
                mhigh, mlow = self.get_high_low(data)
                resistance_ls, support_ls = self.get_sup_res(data, resistance_ls, support_ls)
                is_rg_valid = self.is_risk_reward_valid_long(mhigh, mlow, resistance_ls, support_ls)
                print("is_rg_valid for CE : "+str(is_rg_valid))
        return is_rg_valid, mhigh, mlow, resistance_ls, support_ls


    def is_rg_short_valid(self, data, resistance_ls, support_ls):
        resistance_ls, support_ls = self.get_sup_res(data, resistance_ls, support_ls)
        logging.info("Looking for Short setup")
        is_rg_valid = False
        mhigh = 0
        mlow = 0

        if(len(data)>2):
            prev_color = self.candle_color(data.iloc[-3]['open'], data.iloc[-3]['close'])
            curr_color = self.candle_color(data.iloc[-2]['open'], data.iloc[-2]['close'])
            ## Calculate 5ema and if last candle low is greater than 5ema
            ema = self.get_ema(data, "PE")
            prev_low = data.iloc[-2]['low']
            is_rg_valid_candle_size = self.is_rg_valid_candle_size(data, 'PE')
            if(prev_color != curr_color and prev_low > ema and is_rg_valid_candle_size == True):
                mhigh, mlow = self.get_high_low(data)
                resistance_ls, support_ls = self.get_sup_res(data, resistance_ls, support_ls)
                is_rg_valid = self.is_risk_reward_valid_short(mhigh, mlow, resistance_ls, support_ls)
                print("is_rg_valid for PE : "+str(is_rg_valid))
        return is_rg_valid, mhigh, mlow, resistance_ls, support_ls

    ## Second candle high should be minimum 50% of the first candle and vice versa.
    def is_rg_valid_candle_size(self, data, option):
        is_rg_valid = False
        if(option=='CE'):
            sec_high = data.iloc[-2]['high']
            fst_mid = data.iloc[-3]['low'] + (data.iloc[-3]['high'] - data.iloc[-3]['low']/2)
            if(sec_high >= fst_mid):
                is_rg_valid = True
        elif(option=='PE'):
            sec_low = data.iloc[-2]['low']
            fst_mid = data.iloc[-3]['low'] + (data.iloc[-3]['high'] - data.iloc[-3]['low']/2)
            if(sec_low <= fst_mid):
                is_rg_valid = True
        else:
            is_rg_valid = False
        return is_rg_valid

