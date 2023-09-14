from kiteconnect import KiteTicker
import logging
#from py_mysql import *
import json

logging.basicConfig(level=logging.DEBUG)

CRED_CONFIG_PATH = "D:/algo-trade-sqllite/src/config/cred.json"
CONFIG_PATH = "D:/algo-trade-sqllite/src/config/config.json"

class Store_Date():

    def __init__(self):
        with open(CRED_CONFIG_PATH, 'r') as f:
            cred_config = json.load(f)
        self.api_key = cred_config['key'] 
        self.access_token = cred_config['access_tkn']

        with open(CONFIG_PATH, 'r') as f:
            config = json.load(f)
        self.tokens = [config['tokens']]

        #self.mysql_server = Mysql_Server()
        self.kws=KiteTicker(self.api_key,self.access_token)



    def on_ticks(self,ws,ticks):
        #insert_tick=self.mysql_server.insert_ticks(ticks)
        logging.info(ticks)



    def on_connect(self,ws,response):
        ws.subscribe(self.tokens)
        ws.set_mode(ws.MODE_FULL,self.tokens)


def main():
    store_data = Store_Date() 
    store_data.kws.on_ticks=store_data.on_ticks
    store_data.kws.on_connect=store_data.on_connect
    store_data.kws.connect()

if __name__=="__main__":
    main()
