import pandas as pd
import math

def decide(open, high, low, close):
    buy_trade = False
    buy_price = 0
    per = (open - close) / open * 100
    mid = (open + close) / 2
    dif1 = high - mid
    dif2 = mid - low
    if(open > close):
        if(per <= 1.5):
            if(abs(dif2 - dif1) <=10):
                buy_trade =  True
                buy_price = (open + close) / 2
            

    return buy_trade, buy_price, per, abs(dif2 - dif1)

#print(decide(173.80,  182.45,  163.45,  171.30))



