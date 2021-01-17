import requests
import json
import pandas as pd
import decimal
import time
import hmac 
import time
import hashlib
import configparser
from datetime import datetime

# At the current time Binance rate limits are: 1200 requests per minute. 10 orders per second. 100,000 orders per 24hrs.
config = configparser.ConfigParser()
config.read('./env.ini')

binance_keys = {
    'api_key': config.get('BINANCE','api_key'),
    'secret_key': config.get('BINANCE','secret_key')
}

class Binance:
    def __init__(self):
        self.base = 'https://api.binance.com'
        self.endpoints = {
            'order': '/api/v1/order',
            'account': '/api/v3/account',
            'testOrder': '/api/v1/order/test',
            'allOrders': '/api/v3/allOrders',
            'klines': '/api/v1/klines',
            'exchangeInfo': '/api/v1/exchangeInfo',
            'ticker': '/api/v1/ticker/price'
        }
    
    def cleanData(self, df, indexColName='Date', droppedCols=['Unnamed: 0']):
        df = df.dropna()
        df[indexColName] = [datetime.utcfromtimestamp(i/1000).strftime('%Y-%m-%d %H:%M:%S') for i in df[indexColName] ]
        df.set_index(indexColName, inplace=True)
        df.index = pd.to_datetime(df.index)
        if 'Unnamed: 0' in df.columns:
            df = df.drop(columns=droppedCols)
        df.columns = map(str.capitalize, df.columns)
        return df

    def GetTradingSymbols(self):
        """ Get all the symbols which are tradeable (currently) """

        url = self.base + self.endpoints['exchangeInfo']

        try:
            response = requests.get(url)
            data = json.loads(response.text)
        except Exception as e:
            print('Exception occurred when trying to access '+url)
            print(e)
            return []

        pairs_list = []
        base_list = []
        quotes_list = []
        res = []
        for pair in data['symbols']:
            if pair['status'] == 'TRADING':
                pairs_list.append(pair['symbol'])
                base_list.append(pair['baseAsset'])
                quotes_list.append(pair['quoteAsset'])
        
        lis = {'pair': pairs_list, 'base': base_list, 'quote': quotes_list}
        df = pd.DataFrame(lis)
        return df

    def GetSymbolData(self, symbol:str, interval:str, startTime=None, endTime=None):
        '''Get trading data for one symbol'''
        print('Retrieving Symbol Data for %s'%symbol)
        
        params = '?&symbol=' + symbol + '&interval='+ interval 
        
        if startTime and endTime:
            params = params + '&startTime=' + str(startTime)+ '&endTime=' + str(endTime)

        url = self.base + self.endpoints['klines'] + params

        # Download data
        data = requests.get(url)
        print(data)
        dictionary = json.loads(data.text)
        # Put in dataframe and clean up
        df = pd.DataFrame.from_dict(dictionary)
        df = df.drop(range(6,12), axis=1)

        # Rename columns
        col_names = ['time','open','high','low','close','volume']
        df.columns = col_names

        # Transform values from strings to floats
        for col in col_names:
            df[col] = df[col].astype(float)

        return df 
    
    def getTickData(self, symbol):
        
        params = '?&symbol=' + symbol
        url = self.base + self.endpoints['klines'] + params

        data = requests.get(url)
        print(data)
        dictionary = json.loads(data.text)

        print(dictionary)
    
    def last_close_above_stoploss(self, symbol:str, interval:str, stopLoss):
        binance = Binance()
        latestCandleSticks = binance.GetSymbolData(symbol,interval)
        latestCandleSticks = self.cleanData(latestCandleSticks, 'time', droppedCols=[])
        return True if stopLoss > latestCandleSticks.Close[-2] else False


    def PlaceOrder(self, symbol:str, side:str, type:str, quantity: float, price:float, test:bool=True):
        '''
        Symbol: ETHBTC

        ETH = base Asset (what we buy)
        BTC - quote Asset (what we sell for)
        quantity - how much ETH we want
        price - how much BTC we're willing to sell it for
        
        '''
        
        params = {
            'symbol': symbol,
            'side': side,
            'type': type,
            'timeInForce': 'GTC',
            'quantity': quantity,
            'price': self.floatToString(price),
            'recvWindow': 5000,
            'timestamp': int(round(time.time()*1000))
        }

        self.signRequest(params)

        url = ''
        if test:
            url = self.base + self.endpoints['testOrder']
        else:
            url = self.base + self.endpoints['order']
        
        try:
            response = requests.post(url, params = params , headers={'X-MBX-APIKEY':binance_keys['api_key']})
        except Exception as e:
            print('Exception occurred when trying to place an order on '+url) 
            print(e)
            response = {'code':'-1','msg':e}
            return None
        return json.loads(response.text )

    def CancelOrder(self, symbol:str, orderId:str):
        '''
            Cancels the order on a symbol based on orderId
        '''
        
        params = {
            'symbol': symbol,
            'orderId': orderId,
            'recvWindow': 5000,
            'timestamp': int(round(time.time()*1000))
        }

        self.signRequest(params)

        url = self.base + self.endpoints['order']
        
        try:
            response = requests.delete(url, params = params , headers={'X-MBX-APIKEY':binance_keys['api_key']})
        except Exception as e:
            print('Exception occurred when trying to cancel an order on '+url) 
            print(e)
            response = {'code':'-1','msg':e}
            return None

    def GetOrderInfo(self, symbol:str, orderId:str):
        '''
            Get info about an order on a symbol based on orderId
        '''
        
        params = {
            'symbol': symbol,
            'orderId': orderId,
            'recvWindow': 5000,
            'timestamp': int(round(time.time()*1000))
        }

        self.signRequest(params)

        url = self.base + self.endpoints['order']
        
        try:
            response = requests.get(url, params = params , headers={'X-MBX-APIKEY':binance_keys['api_key']})
        except Exception as e:
            print('Exception occurred when trying to get info on an order '+url) 
            print(e)
            response = {'code':'-1','msg':e}
            return None

        return json.loads(response.text )

    def GetAllOrderInfo(self, symbol:str):
        '''
            Get info about all orders on a symbol
        '''
        
        params = {
            'symbol': symbol,
            'timestamp': int(round(time.time()*1000))
        }

        self.signRequest(params)

        url = self.base + self.endpoints['allOrders']
        
        try:
            response = requests.get(url, params = params , headers={'X-MBX-APIKEY':binance_keys['api_key']})
        except Exception as e:
            print('Exception occurred when trying to get all orders on a symbol '+url) 
            print(e)
            response = {'code':'-1','msg':e}
            return None
        print(response)
        return json.loads(response.text)

    def GetAccountInfo(self):
        '''
            Get info about all orders on a symbol
        '''
        
        params = {
            'timestamp': int(round(time.time()*1000))
        }

        self.signRequest(params)

        url = self.base + self.endpoints['account']
        
        try:
            response = requests.get(url, params = params , headers={'X-MBX-APIKEY':binance_keys['api_key']})
        except Exception as e:
            print('Exception occurred when trying to get all orders on a symbol '+url) 
            print(e)
            response = {'code':'-1','msg':e}
            return None
        print(response)
        return json.loads(response.text)

    def floatToString(self,f: float):
        ''' Converts the given float to a string, without reverting to the scientific notation '''
        ctx = decimal.Context()
        ctx.prec = 12
        d1 = ctx.create_decimal(repr(f))
        return format(d1, 'f')

    def signRequest(self, params:dict):
        ''' Signs the request to Binance API'''
        query_string = '&'.join(['{}={}'.format(d,params[d]) for d in params])
        signature = hmac.new(binance_keys['secret_key'].encode('utf-8'),query_string.encode('utf-8'), hashlib.sha256)
        params['signature'] = signature.hexdigest()
