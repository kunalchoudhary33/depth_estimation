import time
import glob
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from sklearn.cluster import KMeans
import shutil

import sys
sys.path.insert(1, 'D:/algotrade/')

from model.strategy.hammer import Hammer # import is_hammer_candle #, is_hammer_valid
from model.strategy.invertedhammer import InvertedHammer #import is_inverted_hammer_candle, is_inverted_hammer_valid



ham = Hammer()
iham = InvertedHammer()


data_path = "D:/tradeBot/data/download/2022/06/"
#data_path = "D:/tradeBot/data/raw_images/"

stoploss_path = "D:/tradeBot/data/backtest/stoploss_total/"

trade_time = []
strategy = []
result = []
count_days = 0
amount = 0
capital = []
daily_res_date = []
daily_res_target = []
daily_res_stop_loss = []
daily_res_pnl = []
daily_india_vix = []

india_vix_data = pd.read_csv("D:/tradeBot/data/download/indiavix.csv")
india_vix_value = {}
for _,rows in india_vix_data.iterrows():
    india_vix_value[str(rows['date']).split(" ")[0]] = rows['close']


for day in glob.glob(data_path+"*.csv"):
    data = pd.read_csv(day)
    data = data.reset_index()
    d = {'Open':'first', 'High':'max','Low':'min','Close':'last'}
    data['Date'] = pd.to_datetime(data['Date'])
    
    curr_day = str(day.split("\\")[-1].split(".")[0])
    ivix_value = india_vix_value.get(curr_day)
    if(ivix_value<15):
        print("Ignoring this file due to low vix")
        print("File : "+str(curr_day))
        print("India Vix : "+str(ivix_value))
    data = data.resample('1T', on='Date').agg(d)
    data = data.reset_index()

    data = data.dropna()
    data_new = pd.DataFrame()
    count_days = count_days + 1
    daily_res_date.append(day.split("/")[-1].split(".")[0])
    count = 0
    trade_active = False
    trade = False
    target_price = 0
    stop_price = 0
    entry_price = 0
    stop_loss = 0
    trade_time_index = {}
    count_sl = 0
    risk_riward_ratio = 1.5 # x = rrr = 1 : x
    print(count_days)


    for _,rows in data.iterrows():
        hammer_valid = False
        ihammer_valid = False
        count = count + 1
        
        if(trade_active == False):
            hammer_pattern = ham.is_hammer_candle(rows['Open'], rows['High'], rows['Low'], rows['Close'])
            if(hammer_pattern == True and count>=20):
                prev_data = data[:count]
                hammer_valid = ham.is_hammer_valid(data[count-11:count], prev_data)

            inverted_hammer_pattern = iham.is_inverted_hammer_candle(rows['Open'], rows['High'], rows['Low'], rows['Close'])
            if(inverted_hammer_pattern == True and count>=20):
                prev_data = data[:count]
                ihammer_valid = iham.is_inverted_hammer_valid(data[count-11:count], prev_data)
            
            if(hammer_valid == True ):
                trade_active = True
                trade = "Buy"
                entry_price = rows['Close']
                stop_loss = abs(rows['Close'] - rows['Low'])
                stop_price = rows['Low'] - 0.10 * stop_loss
                target_price = rows['Close'] + risk_riward_ratio * stop_loss
                trade_time.append(rows['Date'])
                strategy.append("Hammer")
                daily_india_vix.append(ivix_value)
                
            elif(ihammer_valid == True ):
                trade_active = True
                trade = "Sell"
                entry_price = rows['Close']
                stop_loss = abs(rows['High'] - rows['Close'])
                stop_price = rows['High'] + 0.10 * stop_loss
                target_price = rows['Close'] - risk_riward_ratio * stop_loss
                trade_time.append(rows['Date'])
                strategy.append("Inverted Hammer")
                daily_india_vix.append(ivix_value)
                
                
        elif(trade_active==True):
            if(trade == "Buy"):
                if(rows['High'] >= target_price):
                    trade_active = False
                    result.append("Target")
                    print("Target with vix : "+str(ivix_value))
                    trade_time_index[(rows['Date'])] = "green"
                    amount = amount + risk_riward_ratio * stop_loss
                    capital.append(amount)
                elif(rows['Low']<= stop_price):
                    trade_active = False
                    result.append("Stop Loss")
                    print("Stop Loss with vix : "+str(ivix_value))
                    trade_time_index[(rows['Date'])] = "red"
                    amount = amount - stop_loss
                    capital.append(amount)
                    count_sl = count_sl + 1
                    #shutil.copy(str(day).split(".")[0]+".png", stoploss_path)
                
            if(trade == "Sell"):
                if(rows['Low'] <= target_price):
                    trade_active = False
                    result.append("Target")
                    print("Target with vix : "+str(ivix_value))
                    trade_time_index[(rows['Date'])] = "green"
                    amount = amount + risk_riward_ratio * stop_loss
                    capital.append(amount)
                elif(rows['High']>= stop_price):
                    trade_active = False
                    result.append("Stop Loss")
                    print("Stop Loss with vix : "+str(ivix_value))
                    trade_time_index[(rows['Date'])] = "red"
                    amount = amount - stop_loss
                    capital.append(amount)
                    count_sl = count_sl + 1
                    #shutil.copy(str(day).split(".")[0]+".png", stoploss_path)
        if(count_sl >=4):
            break

        if(count>=345):
            break

    if(trade_active == True):
        result.append("No trade")
        capital.append(amount)

    fig = go.Figure(data=go.Candlestick(x=data['Date'], open=data['Open'], high=data['High'], low=data['Low'], close=data['Close']))
    tar_count = 0
    stop_count = 0
    for key, value in trade_time_index.items():
        fig.add_vline(x=key, line_width=0.5, line_color=value)
        if(value=="red"):
            stop_count = stop_count + 1
        else:
            tar_count = tar_count + 1

    daily_res_target.append(tar_count)
    daily_res_stop_loss.append(stop_count)
    daily_res_pnl.append((60 * tar_count) - (30 * stop_count))
    

    layout = go.Layout(autosize=False,width=3000,height=2000)
    fig.update_layout(layout)
    fig.write_image("D:/tradeBot/data/download/backtest_res/2022_07_08/"+str(day).split("\\")[-1].split(".")[0]+".png")

    
daily_res = pd.DataFrame()
daily_res['Date'] = daily_res_date
daily_res['Target'] = daily_res_target
daily_res['Stop Loss'] = daily_res_stop_loss
daily_res['Pnl'] = daily_res_pnl
daily_res.to_csv("D:/tradeBot/data/download/backtest_res/2022_07_08/daily_pnl.csv", index=False, header=True)

   
data_res = pd.DataFrame()
data_res['trade_time'] = trade_time
data_res['strategy'] = strategy
data_res['result'] = result
data_res['capital'] = capital
data_res['india_vix'] = daily_india_vix
data_res.to_csv("D:/tradeBot/data/download/backtest_res/2022_07_08/backtest_result.csv", index=False, header=True)

output = data_res['result'].value_counts()
#try:
stoploss = data_res['result'].value_counts()['Stop Loss']
#except : 
#    stoploss = 0

#try:
target = data_res['result'].value_counts()['Target']
#except:
#    target = 0

print("Total trades : "+str(target+stoploss))
print("Total Target : "+str(target))
print("Total stoploss : "+str(stoploss))
winrate = (target / (target + stoploss))
print("winrate : "+str(winrate))
print("Points collected : "+str(amount))
