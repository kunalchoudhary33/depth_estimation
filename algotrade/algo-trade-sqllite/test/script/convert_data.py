import pandas as pd
import datetime

data = pd.read_csv('/home/choudhak/Desktop/data/practise/algo-trade/test/data/2021-02-11.txt', sep=" ", header=None)

data = data.iloc[:,:10]
a_datetime = datetime.datetime(2021, 2, 11)
date = []
last_price = []
for _, rows in data.iterrows():
    tm = rows[0].split('{')[-1].split(".")[0]
    added_seconds = datetime.timedelta(0, int(tm))
    new_datetime = a_datetime + added_seconds
    date.append(new_datetime)
    lp = (rows[9].split(',')[0])
    last_price.append(lp)
    
new_df = pd.DataFrame()
new_df['date'] = date
new_df['last_price'] = last_price
new_df.to_csv("/home/choudhak/Desktop/data/practise/algo-trade/test/data/2021-02-11.csv", header=True, index=False)