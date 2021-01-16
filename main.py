from binance import Binance
from datetime import datetime
import pandas as pd 
import numpy as np 
import schedule
import time
from app import addStopLoss
import os.path


class BinanceStopLoss:
    def __init__(self, binanceClient, interval):
        self.client = binanceClient
        self.interval = interval

    def getLatestCandlestick(self, client, base, quote, interval):
        pass

    def getCurrencyBalances(self, client):
        pass

    def latestPrice(self, client):
        pass

    def executeMarketOrder(self, client):
        pass

    def getActiveStoplosses(self):
        pass





def run_test():
    schedule.every(1).minutes.do(test)
    print('started')
    while True:
        schedule.run_pending()
        time.sleep(1)
        


if __name__=="__main__":
    from binance.client import Client
    client = Client(api_key, api_secret)
    binance = Binance()
    print(binance.getTickData('BTCUSDT'))
    
    
    # addStopLoss('BTC','USDT','35000')
    
    # run_test()
    #TODO: Add if current candlestick is X percentage away from stop loss, close 
    # binance = Binance()
    # x = binance.GetAllOrderInfo('BTCUSDT')
    # df = pd.DataFrame(x)
    # df = binance.cleanData(df, 'time',[])
    # for row in range(0, len(df)):
    #     print(df.iloc[row])
    # df2 = pd.DataFrame(binance.GetAccountInfo()['balances'])
    # df2['free'] = pd.to_numeric(df2['free'])
    # #TODO: We can use this to determine what positions we're in. Then we can enact stoploss if holding is above threshold
    # df2 = df2[df2['free']>0]
    # print(df2)
    