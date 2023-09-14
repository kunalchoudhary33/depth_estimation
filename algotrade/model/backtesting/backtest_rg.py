import time
import glob
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from sklearn.cluster import KMeans
import shutil

import sys
sys.path.insert(1, 'D:/algotrade/')

from model.strategy.hammer import Hammer 
from model.strategy.invertedhammer import InvertedHammer
from model.strategy.redgreen import RedGreen



ham = Hammer()
iham = InvertedHammer()
rg_obj = RedGreen()


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
    print(day)
    data = pd.read_csv(day)
    data = data.reset_index()
    d = {'Open':'first', 'High':'max','Low':'min','Close':'last'}
    data['Date'] = pd.to_datetime(data['Date'])
    
    curr_day = str(day.split("\\")[-1].split(".")[0])
    ivix_value = india_vix_value.get(curr_day)

    data = data.resample('1T', on='Date').agg(d)
    data = data.reset_index()

    data = data.dropna()
    data_new = pd.DataFrame()
    count_days = count_days + 1
    daily_res_date.append(day.split("/")[-1].split(".")[0])
    count = 0
    trade_active = False
    reserve_trade_active = False
    trade = False
    target_price = 0
    stop_price = 0
    entry_price = 0
    stop_loss = 0
    trade_time_index = {}
    count_sl = 0
    risk_riward_ratio = 1.5
    print(count_days)
    entry = 0
    stoploss = 0
    target = 0
    
    fig = go.Figure(data=go.Candlestick(x=data['Date'], open=data['Open'], high=data['High'], low=data['Low'], close=data['Close']))

    for _,rows in data.iterrows():
        hammer_valid = False
        ihammer_valid = False
        count = count + 1
        
        
        if(trade_active == False):
            prev_data = data[:count]
            #rg_long_valid, mhigh, mlow, resistance_ls, support_ls =  rg_obj.is_rg_long_valid(prev_data)
            #if(rg_long_valid == True):
            #    reserve_trade_active = True
            #    entry = mhigh
            #    stoploss = mlow
            #    target = resistance_ls[0]
            #    continue

            rg_short_valid, mhigh, mlow, resistance_ls, support_ls =  rg_obj.is_rg_short_valid(prev_data)
            if(rg_short_valid == True):
                reserve_trade_active = True
                entry = mlow
                stoploss = mhigh
                target = support_ls[0]
                continue
            

        if(reserve_trade_active == True):
            if(rows['Low'] <= entry):
                print(entry, target, stoploss)
                fig.add_hline(y=entry, line_width=1, line_color="black")
                fig.add_hline(y=stoploss, line_width=1, line_color="red")
                fig.add_hline(y=target, line_width=1, line_color="green")
                print("Buy here !!")
                break

            
            
            

            print("######################################")
            print("Found : ")
            print(rows['Date'])
            print("######################################")
        if(count>=30):
            break     
            
    layout = go.Layout(autosize=False,width=3000,height=2000)
    fig.update_layout(layout)
    fig.write_image("D:/algotrade/data/rg_data/short/"+str(day).split("\\")[-1].split(".")[0]+".png")
    
    #if(count_days==10):
    #    break

    