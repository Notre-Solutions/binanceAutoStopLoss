from datetime import datetime
import pandas as pd 
import json
import numpy as np 
import schedule
import os.path
import logging
from utils import Utils
import time
from binance.enums import *
# from app import addStopLoss
import os.path
import os

binance_keys = {
    'api_key': os.environ['API_KEY'],
    'secret_key': os.environ['SECRET_KEY']
}

class BinanceStopLoss:
    def __init__(self, binanceClient, interval, stopsFilePath):
        self.client = binanceClient
        self.interval = interval
        self.stopsFilePath = stopsFilePath
        self.utils = Utils()

    def createStopLoss(self, asset, quote, price):
        data = self.getStopLosses()
        data[asset] = {
                'active': True,
                'asset': asset,
                'quote': quote,
                'price': price
        }
        self.writeToStopLossJson(data)
        return data[asset]

    def writeToStopLossJson(self,data):
        
        with open(self.stopsFilePath, 'w') as outfile:
            json.dump(data, outfile)

    def getStopLosses(self):
        if os.path.isfile(self.stopsFilePath):
            with open(self.stopsFilePath) as json_file:
                return json.load(json_file)
        else:
            print ("File not exist")
            return {}
        

    def getStopLoss(self, asset):
        data = self.getStopLosses()
        if asset in data.keys():
            return {'isInStopsFile': True, 'data':data[asset]}
        return {'isInStopsFile': False}  

    def turnOffStopLoss(self, asset):
        data = self.getStopLosses()
        if asset in data.keys():
            data[asset]['active'] = False
            self.writeToStopLossJson(data)
            return {'isInStopsFile': True, 'data':data[asset]}
        return {'isInStopsFile': False}
        pass

    def removeStopLoss(self, asset):
        stopsFile = 'stops/stops.json'
        data = self.getStopLosses()
        del data[asset]
        with open(stopsFile, 'w') as outfile:
            json.dump(data, outfile)
        return data

    def getAssetBalance(self,asset,quote):
        balance = self.client.get_asset_balance(asset=asset)
        balance['free'+quote] = float(balance['free']) * float(self.getLatestPrices(asset+quote)['ask'])
        return balance
        

    def getLatestPrices(self, symbol):
        depth = self.client.get_order_book(symbol=symbol,limit=5)
        prices = {'ask':depth['asks'][0][0],
                    'bid':depth['bids'][0][0]}
        return prices
        pass

    def getLatestCandlestick(self, symbol):
        klines = self.client.get_klines(symbol=symbol, interval=self.interval,limit=2)
        candle = {
          'opentime': datetime.utcfromtimestamp(klines[0][0]/1000).strftime('%Y-%m-%d %H:%M:%S'),
          'open': klines[0][1],
          'high': klines[0][2],
          'low': klines[0][3],
          'close': klines[0][4],
          'volume': klines[0][5],
        }
        return candle

    def getMinNotional(self,symbol):
        info = self.client.get_symbol_info(symbol=symbol)
        # return float(info['filters'][0]['minPrice']) * float(self.getLatestPrices(symbol)['ask'])
        for i in info['filters']:
            if i['filterType'] == 'MIN_NOTIONAL':
                return i['minNotional']

    def executeMarketOrder(self, symbol, quoteQuantity):
        response = self.client.create_order(symbol=symbol, type=ORDER_TYPE_MARKET,side=SIDE_SELL, quoteOrderQty=quoteQuantity)
        import csv
        del response['fills']
        
        with open(r'orders.csv', 'a', newline='') as csvfile:
            fieldnames = ['symbol', 'orderId', 'orderListId', 'clientOrderId', 'transactTime',
            'price', 'origQty', 'executedQty', 'cummulativeQuoteQty', 'status',
            'timeInForce', 'type', 'side']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writerow(response)

        if response['status'] == 'FILLED':
            return response
        else: 
            logging.info('EXECUTION FAILED')
            print(response)
            return response

    def getActiveStoplosses(self):
        pass





if __name__=="__main__":
    pass
    