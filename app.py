import threading
import time
from flask import Flask, jsonify, request
from main import BinanceStopLoss
import numpy as np
import pandas as pd
import time
import os.path
import configparser
from apscheduler.schedulers.background import BackgroundScheduler
import atexit
from binance.client import Client
config = configparser.ConfigParser()
config.read('./env.ini')

binance_keys = {
    'api_key': config.get('BINANCE','api_key'),
    'secret_key': config.get('BINANCE','secret_key')
}
import logging
from utils import Utils
utils = Utils()

app = Flask(__name__)

client = Client(binance_keys['api_key'], binance_keys['secret_key'])
bsl = BinanceStopLoss(client,'1h','stops/stops.json')

# export FLASK_APP=app.py
# flask run


@app.route('/')
def hello_world():
    sl = bsl.getStoplosses()
    return str(sl)

@app.route('/createStopLoss', methods=['POST'])
def createStopLoss():
    asset = request.args['asset']
    quote = request.args['quote']
    price = request.args['price']
    return bsl.createStopLoss(asset, quote, price)

@app.route('/removeStopLoss', methods=['DELETE'])
def removeStopLoss():
    asset = request.args['asset']
    return bsl.removeStopLoss(asset)

@app.route('/getStopLoss', methods=['GET'])
def getStopLoss():
    asset = request.args['asset']
    return bsl.getStopLoss(asset)

@app.route('/getAllStopLoss', methods=['GET'])
def getAllStopLoss():
    asset = request.args['asset']
    return bsl.getStopLosses()

def runStopLoss():
    stopLosses = bsl.getStopLosses()
    if len(stopLosses.keys()) > 0:
        for key in stopLosses.keys():
            if stopLosses[key]['active']:
                symbol = stopLosses[key]['asset']+stopLosses[key]['quote']
                candle = bsl.getLatestCandlestick(symbol)
                logging.info('Processing: {}'.format(str(stopLosses[key])))
                prices = bsl.getLatestPrices(symbol)
                askPrice = utils.round_decimals_down(float(prices['ask']))
                if float(candle['close']) < float(stopLosses[key]['price']) and \
                askPrice < float(stopLosses[key]['price']) :
                    quoteQuantity = bsl.getAssetBalance(stopLosses[key]['asset'], stopLosses[key]['quote'])['free'+stopLosses[key]['quote']]
                    quoteQuantity = utils.round_decimals_down(float(quoteQuantity))
                    minNotional = float(bsl.getMinNotional(symbol))
                    if quoteQuantity > minNotional:
                        logging.info("Executing sell order: Quantity - {}  Price - {}  Symbol - {}".format(quoteQuantity, askPrice, symbol ))
                        # res = bsl.executeMarketOrder(symbol, quoteQuantity)
                        logging.info("Order executed for {}".format(symbol))
                        # logging.info(str(res))
                        bsl.turnOffStopLoss(key)
                    else:
                        logging.warn("Quote quantity is less that minimum notional. Please turn off stop loss")
                        logging.info("Min Notional {} Quote Quantity {}".format(minNotional,quoteQuantity))
                else:
                    logging.info("Stop loss not yet reached for {}".format(symbol))
            else:
                logging.info("Stop loss not active for {}".format(key))

    return {'Run':True} 
        

try:
    sched = BackgroundScheduler(daemon=True)
    sched.add_job(
        runStopLoss, 
        trigger='cron',
        minute='40'
    )
    sched.start()
    atexit.register(lambda: sched.shutdown(wait=False))
except Exception as ex:
    logging.ERROR("StopLoss has stopped working")
    logging.ERROR(ex)
