from kiteconnect import KiteTicker
#from datetime import datetime
import datetime
import logging
import json
import sys

sys.path.insert(1, '/home/ubuntu/algotrade/')

from execution.script.bot_util import BotUtil
from database.script.database_server import Database_Server
CRED_CONFIG_PATH = "/home/ubuntu/algotrade/execution/config/cred.json"
CONFIG_PATH = "/home/ubuntu/algotrade/execution/config/config.json"

logging.basicConfig(level=logging.DEBUG)

class Stream():

    def __init__(self):
        logging.info('Stream started')
        with open(CRED_CONFIG_PATH, 'r') as f:
            cred_config = json.load(f)
        self.api_key = cred_config['key'] 
        self.access_token = cred_config['access_tkn']

        with open(CONFIG_PATH, 'r') as f:
            config = json.load(f)
        self.tokens = [config['tokens']]

        self.bot = BotUtil()
        self.mysql_server = Database_Server()
        self.kws=KiteTicker(self.api_key,self.access_token)


    def on_ticks(self,ws,ticks):
        self.bot.set_ltp(ticks)
        for tick in ticks:
            logging.info("market price : "+str(tick['last_price']))
        #logging.info(ticks)
        insert_tick=self.mysql_server.insert_ticks(ticks)



    def on_connect(self,ws,response):
        ws.subscribe(self.tokens)
        ws.set_mode(ws.MODE_FULL,self.tokens)


def main():
    stream_data = Stream() 
    stream_data.kws.on_ticks=stream_data.on_ticks
    stream_data.kws.on_connect=stream_data.on_connect
    stream_data.kws.connect()

if __name__=="__main__":
    logging.info("##############   Streaming of data started  ##############################")
    mysql_server = Database_Server()
    mysql_server.truncate_table()
    logging.info('Table truncated!!')
    while True:
        curr_time = datetime.datetime.now()
        curr_time_min = curr_time + datetime.timedelta(minutes=30)
        curr_time_timezone = curr_time_min + datetime.timedelta(hours=5)
        minute = curr_time_timezone.minute
        hour = curr_time_timezone.hour
        if(hour == 9 and minute == 15):
            main()
