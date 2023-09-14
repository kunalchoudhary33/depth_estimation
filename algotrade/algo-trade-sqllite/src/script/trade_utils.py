import logging
from kiteconnect import KiteConnect
import json
import math

logging.basicConfig(level=logging.DEBUG)
CRED_CONFIG_PATH = "src/config/cred.json"
CONFIG_PATH = "src/config/config.json"


class Trade_utils():

    def __init__(self):
        with open(CRED_CONFIG_PATH, 'r') as f:
            cred_config = json.load(f)
        self.api_key = cred_config['key'] 
        self.access_token = cred_config['access_tkn']
        with open(CONFIG_PATH, 'r') as f:
            config = json.load(f)
        self.tokens = config['tokens']
        self.trading_symbol = config['trading_symbol'] 
        self.quantity = config['quantity']
        self.target = config['target_percentage'] 
        self.stop_loss = config['stop_loss_percentage'] 
        self.kite = KiteConnect(api_key=self.api_key)
        self.kite.set_access_token(self.access_token)
        self.instrument_dump = self.kite.instruments(exchange='NFO')
        
        
    def get_max_quantity(self, last_price):
        amount = self.kite.margins()['equity']['net']
        total_shares = amount / last_price
        unit_share = total_shares / 25
        quantity = math.floor(unit_share) * 25
        return quantity


    def fetch_ltp(self, instrument):
        ticks = self.kite.quote(instrument)
        last_trad_price = ticks[str(instrument)]['last_price']
        return last_trad_price
    
    def fetch_ltp_banknifty(self):
        ticks = self.kite.quote('NSE:NIFTY BANK')
        ltp_banknifty = ticks['NSE:NIFTY BANK']['last_price']
        return ltp_banknifty


    def fetch_inrange_instrument(self):
        ltp_banknifty = self.fetch_ltp_banknifty()
        pre_token = str(self.trading_symbol)[:14]
        post_token = str(self.trading_symbol)[17:]
        index = int(str(ltp_banknifty)[:3])
        instrument_symbol = pre_token+str(index)+post_token
        for inst in self.instrument_dump:
            if(inst['tradingsymbol']==instrument_symbol):
                instrument = inst['instrument_token']
        return instrument, instrument_symbol


    def place_order(self):
        try:
            
            instrument, instrument_symbol = self.fetch_inrange_instrument()
            last_price = self.fetch_ltp(instrument)
            self.quantity = self.get_max_quantity(last_price)
            target_price = math.ceil(last_price + (last_price*self.target)/100)
            slotloss_price = math.floor(last_price - (last_price*self.stop_loss)/100)
            order_id = self.kite.place_order('regular', 'NFO', instrument_symbol, 'BUY', self.quantity, 'NRML', 'MARKET')
            order_dict = [{"transaction_type": self.kite.TRANSACTION_TYPE_SELL, "quantity": self.quantity, 'order_type': self.kite.ORDER_TYPE_LIMIT, "product": self.kite.PRODUCT_NRML , "price": slotloss_price}, 
                        {"transaction_type": self.kite.TRANSACTION_TYPE_SELL, "quantity": self.quantity, 'order_type': self.kite.ORDER_TYPE_LIMIT, "product": self.kite.PRODUCT_NRML , "price": target_price}]
            self.kite.place_gtt(self.kite.GTT_TYPE_OCO, instrument_symbol, self.kite.EXCHANGE_NFO, [slotloss_price, target_price], last_price, order_dict)

            logging.info("############################# Order Placed ##########################################")
            logging.info("Order placed. ID is: {}".format(order_id))
            logging.info("Order places at : {} with Traget : {} and StopLoss : {}".format(last_price, target_price, slotloss_price))
            
        except Exception as e:
            logging.info("Order placement failed: {}".format(e.message))
        self.kite.orders()
        self.kite.instruments()
        return order_id
    

# def main():
#     obj = Trade_utils()
#     ord = obj.place_order()
#     print(ord)

# if __name__=="__main__":
#     main()
    
