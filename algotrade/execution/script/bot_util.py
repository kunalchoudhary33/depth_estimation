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

CONFIG_PATH = "/home/ubuntu/algotrade/execution/config/config.json"
PRICE_CONFIG_PATH = "/home/ubuntu/algotrade/execution/config/price_config.json"
CRED_CONFIG_PATH = "/home/ubuntu/algotrade/execution/config/cred.json"



class BotUtil():

    def __init__(self):
        self.ltp = 0
        with open(CRED_CONFIG_PATH, 'r') as f:
            cred_config = json.load(f)
        self.api_key = cred_config['key'] 
        self.access_token = cred_config['access_tkn']

        with open(CONFIG_PATH, 'r') as f:
            config = json.load(f)
        self.tokens = [config['tokens']]
        self.trading_symbol = [config['trading_symbol']]

        self.option = [config['option']]
        self.index = [config['index']]
        self.lot_size = [config['lot_size']]
        self.spare_lot_size = [config['spare_lot_size']]
        self.expiry = [config['expiry']]
        self.buy_price = 0
        self.target = []
        self.stop_loss = []
        self.last_traded_price = 0
        self.risk_reward_ratio = 2.00

        self.kite = KiteConnect(api_key=self.api_key)
        self.kite.set_access_token(access_token=self.access_token)

    def get_ltp(self):
        try:
            with open(PRICE_CONFIG_PATH, 'r') as f:
                config = json.load(f)
            self.last_traded_price = [config['ltp']][0]
        except Exception as ex:
            pass
        return self.last_traded_price


    def set_ltp(self, ticks):
        for tick in ticks:
            self.ltp = tick['last_price']

        dict_cred = {
            'ltp' : self.ltp
        }
        price_object = json.dumps(dict_cred, indent = 1)
        with open(PRICE_CONFIG_PATH, "w") as outfile:
            outfile.write(price_object)



    def get_position(self):
        self.position = self.kite.positions()
        for open_position in self.position['net']:
            quantity = open_position['quantity']
            if(quantity>0):
                self.tradingsymbol = open_position['tradingsymbol']
                self.quantity = open_position['quantity']
        return self.position


    def get_position_size(self):
        capital = 50000
        risk_per_trade_per = 5
        stop_loss = 90
        position_size = ((capital * (risk_per_trade_per / 100)) / stop_loss)/25



    def excutation(self, qnty):
        instrument_symbol = self.tradingsymbol
        order_id = self.kite.place_order('regular', 'NFO', instrument_symbol, 'SELL', qnty, 'NRML', 'MARKET')
        return order_id

    def slipage_execution(self):
        self.get_position()
        order_id = self.excutation(self.quantity)
        return order_id


    def ce_bot(self):
        is_spare_quantity_booked = False
        is_half_stop_loss_moved = False
        is_quarter_stop_loss_moved = False
        order_id = 0
        count = 0


        target_price = self.target[0]
        stop_loss_price = self.stop_loss[0]
        spare_target = self.buy_price + (1.5 * (self.buy_price - self.stop_loss[0]))
        half_stop_loss_price = self.buy_price - (self.buy_price - self.stop_loss[0]) / 2
        half_target_price = self.buy_price + (self.target[0] - self.buy_price) / 2
        quarter_target = self.buy_price + (0.75 * (self.target[0] - self.buy_price))

        logging.info("entry price : "+str(self.buy_price))
        logging.info("target : "+str(target_price))
        logging.info("stop loss : "+str(stop_loss_price))
        #logging.info("spare target : "+str(spare_target))
        #logging.info("quarter target : "+str(quarter_target))

        if(self.index[0]=="NIFTY BANK"):
            spare_quantity = self.spare_lot_size[0] * 25
        if(self.index[0]=="NIFTY 50"):
            spare_quantity = self.spare_lot_size[0] * 50

        for i in range(sys.maxsize**10):
            count = count + 1
            last_traded_price = self.get_ltp()
            if(is_spare_quantity_booked == False and last_traded_price>=spare_target):
                self.get_position()
                #order_id = self.excutation(spare_quantity)
                #logging.info("Spare Quantity booked. Total lot booked :  "+str(self.spare_lot_size))
                is_spare_quantity_booked = True


            if(is_half_stop_loss_moved == False and last_traded_price>=half_target_price):
                #stop_loss_price = half_stop_loss_price
                is_half_stop_loss_moved = True
                #logging.info("Stop loss reduced to half. New Stoploss : "+str(stop_loss_price))

            if(is_quarter_stop_loss_moved == False and last_traded_price>=quarter_target):
                #stop_loss_price = self.buy_price
                is_quarter_stop_loss_moved = True
                #logging.info("Stop loss at entry price. New Stoploss : "+str(stop_loss_price))

            if(last_traded_price>=target_price):
                self.get_position()
                order_id = self.excutation(self.quantity)
                logging.info("Price hit the target")
                time.sleep(60)
                break

            if(last_traded_price < stop_loss_price):
                self.get_position()
                order_id = self.excutation(self.quantity)
                logging.info("Price hit the stop loss")
                time.sleep(60)
                break

        return order_id


    def pe_bot(self):
        is_spare_quantity_booked = False
        is_half_stop_loss_moved = False
        is_quarter_stop_loss_moved = False
        order_id = 0
        count = 0

        target_price = self.target[0]
        stop_loss_price = self.stop_loss[0]
        spare_target = self.buy_price - (1.50 * (self.stop_loss[0] - self.buy_price))
        half_stop_loss_price = self.buy_price + (self.stop_loss[0] - self.buy_price) / 2
        half_target_price = self.buy_price - (self.buy_price - self.target[0]) / 2
        quarter_target = self.buy_price - (0.75 * (self.buy_price - self.target[0]))

        logging.info("entry price : "+str(self.buy_price))
        logging.info("target : "+str(target_price))
        logging.info("stop loss : "+str(stop_loss_price))
        #logging.info("spare target : "+str(spare_target))
        #logging.info("half_target_price : "+str(half_target_price))
        #logging.info("quarter target : "+str(quarter_target))

        if(self.index[0]=="NIFTY BANK"):
            spare_quantity = self.spare_lot_size[0] * 25
        if(self.index[0]=="NIFTY 50"):
            spare_quantity = self.spare_lot_size[0] * 50

        for i in range(sys.maxsize**10):
            count = count + 1
            last_traded_price = self.get_ltp()
            if(is_spare_quantity_booked == False and last_traded_price<=spare_target):
                self.get_position()
                #order_id = self.excutation(spare_quantity)
                #logging.info("Spare Quantity booked. Total lot booked :  "+str(self.spare_lot_size))
                is_spare_quantity_booked = True

            if(is_half_stop_loss_moved == False and last_traded_price<=half_target_price):
                #stop_loss_price = half_stop_loss_price
                is_half_stop_loss_moved = True
                #logging.info("Stop loss reduced to half. New Stoploss : "+str(stop_loss_price))

            if(is_quarter_stop_loss_moved == False and last_traded_price<=quarter_target):
                #stop_loss_price = self.buy_price
                is_quarter_stop_loss_moved = True
                #logging.info("Stop loss at entry price. New Stoploss : "+str(stop_loss_price))


            if(last_traded_price<=target_price):
                self.get_position()
                order_id = self.excutation(self.quantity)
                logging.info("Price hit the target")
                time.sleep(60)
                break

            if(last_traded_price > stop_loss_price):
                self.get_position()
                order_id = self.excutation(self.quantity)
                logging.info("Price hit the stop loss")
                time.sleep(60)
                break

        return order_id


    def fetch_instrument(self, trade_option):
        if(self.index[0]=="NIFTY BANK"):
            ticks = self.kite.quote('NSE:NIFTY BANK')
            ltp = ticks['NSE:NIFTY BANK']['last_price']
            if(trade_option=="CE"):
                instrument_symbol = "BANKNIFTY23"+str(self.expiry[0])+str(int(str(ltp)[:3]) - 0)+"00"+trade_option
            if(trade_option=="PE"):
                instrument_symbol = "BANKNIFTY23"+str(self.expiry[0])+str(int(str(ltp)[:3]) + 1)+"00"+trade_option
            quantity = self.lot_size[0] * 25
        if(self.index=="NIFTY 50"):
            ticks = self.kite.quote('NSE:NIFTY 50')
            ltp = ticks['NSE:NIFTY 50']['last_price']
            instrument_symbol = "NIFTY233"+str(self.expiry[0])+str(str(ltp)[:3])+"00"+self.option[0]
            quantity = self.lot_size[0] * 50
        return quantity, instrument_symbol




    def set_target_stoploss(self, mhigh, mlow, trade_option):
        target_value = 0
        stop_loss = 0
        self.target.clear()
        self.stop_loss.clear()
        if(trade_option=="CE"):
            target_value = mhigh + (self.risk_reward_ratio * (mhigh - mlow))
            stop_loss = mlow
        if(trade_option=="PE"):
            target_value = mlow - (self.risk_reward_ratio * (mhigh - mlow))
            stop_loss = mhigh

        self.target.append(target_value)
        self.stop_loss.append(stop_loss)



    def place_order(self, mhigh, mlow, trade_option):
        try:
            quantity, instrument_symbol = self.fetch_instrument(trade_option)
            order_id = self.kite.place_order('regular', 'NFO', instrument_symbol, 'BUY', quantity, 'NRML', 'MARKET')

            if(trade_option=="CE"):
                self.buy_price = mhigh
                self.set_target_stoploss(mhigh, mlow, trade_option)
            elif(trade_option=="PE"):
                self.buy_price = mlow
                self.set_target_stoploss(mhigh, mlow, trade_option)

            logging.info("############################# Order Placed ##########################################")
            logging.info("trade_option : "+str(trade_option))
            logging.info("buy_price : "+str(self.buy_price))
            logging.info("Traget Value : "+str(self.target))
            logging.info("Stop Loss : "+str(self.stop_loss))
            logging.info("mhigh : "+str(mhigh))
            logging.info("mlow : "+str(mlow))
            logging.info("Order placed. ID is: {}".format(order_id))

        except Exception as e:
            logging.info("Order placement failed: {}".format(e))
        return order_id



    def bot(self, trade_option):
        logging.info("###########  AUTO PILOT MODE ON  ####################")
        logging.info("Option trading in : "+str(trade_option))
        if(trade_option=="CE"):
            order_id = self.ce_bot()
            logging.info("Order booked : "+str(trade_option))
        elif(trade_option=="PE"):
            order_id = self.pe_bot()
            logging.info("Order booked : "+str(trade_option))
        return order_id
