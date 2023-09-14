from kiteconnect import KiteConnect
from kiteconnect import KiteTicker
import undetected_chromedriver as uc
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import pyotp
import logging
import json

logging.basicConfig(level=logging.DEBUG)
CRED_CONFIG_PATH = "/home/ubuntu/algotrade/execution/config/cred.json"


class Auth_Token():
    def __init__(self):
        self.api_key = 'czwkcv66rtnvliol'
        self.api_secret = 'ubye2iro93g82hea99zvjxadcm41aa84'
        self.acc_tkn = 'qa4NMuK4liUwYeH2L5YWUZnSJQg7zjfm'
        self.user_id = 'ZN3081'
        self.user_pwd = 'ANKUjatin33_'
        self.totp_key = 'LVW34NNKM66USUPBPHBCOYEPGYYRAHKF'
        

    def login_in_zerodha(self):
        api_key = self.api_key
        api_secret = self.api_secret
        user_id = self.user_id
        user_pwd = self.user_pwd
        totp_key = self.totp_key
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        #driver = webdriver.Chrome(executable_path='/home/ubuntu/algotrade/algo-trade-sqllite/utils/chromedriver', chrome_options=chrome_options)
        #options = webdriver.ChromeOptions()
        path = '/home/ubuntu/algotrade/algo-trade-sqllite/utils/chromedriver'
        chrome_options.add_argument('--load-extension='+path)
        driver = webdriver.Chrome(executable_path=ChromeDriverManager().install(), options=chrome_options)
        driver.get(f'https://kite.trade/connect/login?api_key={api_key}&v=3')
        login_id = WebDriverWait(driver, 10).until(lambda x: x.find_element_by_xpath('//*[@id="userid"]'))
        login_id.send_keys(user_id)

        pwd = WebDriverWait(driver, 10).until(lambda x: x.find_element_by_xpath('//*[@id="password"]'))
        pwd.send_keys(user_pwd)

        submit = WebDriverWait(driver, 10).until(lambda x: x.find_element_by_xpath('//*[@id="container"]/div/div/div[2]/form/div[4]/button'))
        submit.click()

        time.sleep(1)

        totp = WebDriverWait(driver, 10).until(lambda x: x.find_element_by_xpath('//*[@id="totp"]'))
        authkey = pyotp.TOTP(totp_key)
        totp.send_keys(authkey.now())

        continue_btn = WebDriverWait(driver, 10).until(lambda x: x.find_element_by_xpath('//*[@id="container"]/div/div/div[2]/form/div[3]/button'))
        continue_btn.click()

        time.sleep(5)

        url = driver.current_url
        initial_token = url.split('request_token=')[1]
        request_token = initial_token.split('&')[0]
        self.acc_tkn = request_token

        driver.close()
        
        kite = KiteConnect(api_key = api_key)
        data = kite.generate_session(request_token, api_secret=api_secret)
        kite.set_access_token(data['access_token'])
        self.acc_tkn = data['access_token']
        self.write_json()

        return kite
    
    
    def write_json(self):
        dict_cred = {
            'key' : self.api_key,
            'secret' : self.api_secret,
            'access_tkn' : self.acc_tkn
        }
        cred_object = json.dumps(dict_cred, indent = 3)
        with open(CRED_CONFIG_PATH, "w") as outfile:
            outfile.write(cred_object)

if __name__ == '__main__':
    auth_obj = Auth_Token()
    kiteobj = auth_obj.login_in_zerodha()
