from binance import Binance
from datetime import datetime
import pandas as pd 
import numpy as np 
import schedule
import time

def cleanData(df, indexColName='Date', droppedCols=['Unnamed: 0']):
  df = df.dropna()
  df.set_index(indexColName, inplace=True)
  df.index = pd.to_datetime(df.index)
  if 'Unnamed: 0' in df.columns:
    df = df.drop(columns=droppedCols)
  df.columns = map(str.capitalize, df.columns)
  return df

def test():
    print('Starting..')
    binance = Binance()
    latestCandleSticks = binance.GetSymbolData('BTCUSDT','1h')
    latestCandleSticks.time = [datetime.utcfromtimestamp(i/1000).strftime('%Y-%m-%d %H:%M:%S') for i in latestCandleSticks.time ]
    latestCandleSticks = cleanData(latestCandleSticks, 'time', droppedCols=[])
    print(latestCandleSticks)

def run_test():
    schedule.every(1).minutes.do(test)
    print('started')
    while True:
        schedule.run_pending()
        time.sleep(1)
        


if __name__=="__main__":
    # run_test()
    #Does it give opening time of candlestick or close?
    test()