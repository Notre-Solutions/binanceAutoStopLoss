from main import BinanceStopLoss
from binance.client import Client
from datetime import datetime
from datetime import datetime, timedelta
import pandas as pd 
import logging
from utils import Utils
import unittest
import configparser
config = configparser.ConfigParser()
config.read('./env.ini')
binance_keys = {
    'api_key': config.get('BINANCE','api_key'),
    'secret_key': config.get('BINANCE','secret_key')
}
class BinanceStopLossTest(unittest.TestCase):
  
  def setUp(self):
    utils = Utils()
    client = Client(binance_keys['api_key'], binance_keys['secret_key'])
    self.stopLoss = BinanceStopLoss(client,'1h','stops/stopsTest.json')
    self.interval = '1h'
    self.asset = 'BTC'
    self.quote = 'USDT'
    self.price = 35000

  def test_Balance(self):
    balance = self.stopLoss.getAssetBalance(self.asset, self.quote)
    try:
      float(balance['free'])
      float(balance['free'+self.quote])
      float(balance['locked'])
    except ValueError:
      self.fail("Values cannot be cast to float")

  def test_LatestPrice(self):
    prices = self.stopLoss.getLatestPrices(self.asset+self.quote)
    try:
      float(prices['ask'])
      float(prices['bid'])
    except ValueError:
      self.fail("Values cannot be cast to float")
    print(prices)

  def test_GetLatestCandlestick(self):
    latestCandle = self.stopLoss.getLatestCandlestick(self.asset+self.quote)
    lastHourStr = str(datetime.now().replace(microsecond=0, second=0, minute=0) - timedelta(hours=1))
    self.assertEqual(lastHourStr,latestCandle['opentime'])
    

  def test_CreateStopLoss(self):
    sl = self.stopLoss.createStopLoss(self.asset,self.quote,self.price)
    slCompare = {'active': True, 'asset': self.asset, 'quote': self.quote, 'price': self.price}
    self.assertEqual(slCompare, sl)
    print(sl)
    self.stopLoss.removeStopLoss(self.asset)
    
  def test_GetStopLosses(self):
    slCompare = {}
    slCompare[self.asset] = self.stopLoss.createStopLoss(self.asset,self.quote,self.price)
    sl = self.stopLoss.getStopLosses()
    self.assertEqual(slCompare,sl)
    self.stopLoss.removeStopLoss(self.asset)
  
  def test_TurnOffStopLoss(self):
    slCompare = self.stopLoss.createStopLoss(self.asset,self.quote,self.price)
    sl = self.stopLoss.turnOffStopLoss(self.asset)
    self.assertEqual(True,sl['isInStopsFile'])
    self.assertEqual(False,sl['data']['active'])
    self.stopLoss.removeStopLoss(self.asset)
    print(sl)

  def test_RemoveStopLoss(self):
    self.stopLoss.createStopLoss(self.asset,self.quote,self.price)
    slCompare = self.stopLoss.removeStopLoss(self.asset)
    self.assertEqual({},slCompare)

if __name__=="__main__":
  unittest.main()