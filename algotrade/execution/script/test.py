import sqlite3
import pandas as pd
import datetime
from kiteconnect import KiteTicker
from kiteconnect import KiteConnect
import logging
import json
import sys
import time

logging.basicConfig(level=logging.DEBUG)

CONFIG_PATH = "D:/algotrade/execution/config/config.json"
PRICE_CONFIG_PATH = "D:/algotrade/execution/config/price_config.json"
CRED_CONFIG_PATH = "/home/ubuntu/algotrade/execution/config/cred.json"

last_traded_price = 0

with open(CRED_CONFIG_PATH, 'r') as f:
    cred_config = json.load(f)
api_key = cred_config['key'] 
access_token = cred_config['access_tkn']
kite = KiteConnect(api_key=api_key)
kite.set_access_token(access_token=access_token)

print("##################### Start ##################################")
def get_position():
    bprice = 0
    position = kite.positions()
    for open_position in position['net']:
        quantity = open_position['quantity']
        if(quantity>0):
            print("This is open ")
            print(open_position)
            bprice = open_position['buy_price']
            print("This is in price")
            print(bprice)
            break
    return bprice

bp = get_position()
print(bp)
print('This is bprice : '+str(int(bp)))
kite.place_order(
    variety='regular',
    exchange='NFO',
    tradingsymbol='BANKNIFTY23APR42800CE',
    transaction_type='SELL',
    quantity=25,
    product='NRML',
    order_type='MARKET'
)

print("Stop ##################################")
