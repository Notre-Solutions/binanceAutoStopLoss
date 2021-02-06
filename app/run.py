import threading
import time
from flask import Flask, jsonify, request
from main import BinanceStopLoss
import numpy as np
import pandas as pd
import time
import os
import os.path
from flask_pymongo import PyMongo
from apscheduler.schedulers.background import BackgroundScheduler
import atexit
from binance.client import Client
import configparser

import logging
from utils import Utils
utils = Utils()
binance_keys = {}
application = Flask(__name__)


if 'API_KEY' in os.environ:
    binance_keys = {
    'api_key': os.environ['API_KEY'],
    'secret_key': os.environ['SECRET_KEY']
    }
    application.config["MONGO_URI"] = 'mongodb://' + os.environ['MONGODB_USERNAME'] + ':' + os.environ['MONGODB_PASSWORD'] + '@' + os.environ['MONGODB_HOSTNAME'] + ':27017/' + os.environ['MONGODB_DATABASE']

else:
    config = configparser.ConfigParser()
    config.read('./uat.ini')

    binance_keys = {
        'api_key': config.get('BINANCE','API_KEY'),
        'secret_key': config.get('BINANCE','SECRET_KEY')
    }



client = Client(binance_keys['api_key'], binance_keys['secret_key'])
bsl = BinanceStopLoss(client,'4h','./stops/stops.json')
triggerExecution = False
# export FLASK_APP=app.py
# flask run


@application.route('/')
def hello_world():
    sl = bsl.getStoplosses()
    return str(sl)

@application.route('/createStopLoss', methods=['POST'])
def createStopLoss():
    asset = request.args['asset']
    quote = request.args['quote']
    price = request.args['price']
    return bsl.createStopLoss(asset, quote, price)

@application.route('/removeStopLoss', methods=['DELETE'])
def removeStopLoss():
    asset = request.args['asset']
    return bsl.removeStopLoss(asset)

@application.route('/getStopLoss', methods=['GET'])
def getStopLoss():
    asset = request.args['asset']
    return bsl.getStopLoss(asset)

@application.route('/getAllStopLosses', methods=['GET'])
def getAllStopLosses():
    return bsl.getStopLosses()

@application.route('/triggerExecution', methods=['POST'])
def triggerExecution():
    trig = request.args['triggerExecution']
    if trig.lower() == 'true':
        triggerExecution = True
    else:
        triggerExecution = False
    return {'triggerExecution': triggerExecution}

@application.route('/runStopLoss', methods=['POST'])
def runStopLossEndpoint():
    run = request.args['runStopLoss']
    if run.lower() == 'true':
        return runStopLoss()
    return {'Run':False}


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
                        if triggerExecution:
                            res = bsl.executeMarketOrder(symbol, quoteQuantity)
                            logging.info(str(res))
                        logging.info("Order executed for {}".format(symbol))
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
        minute='01'
    )
    sched.start()
    atexit.register(lambda: sched.shutdown(wait=False))
except Exception as ex:
    logging.ERROR("StopLoss has stopped working")
    logging.ERROR(ex)

if __name__ == "__main__":
    
    ENVIRONMENT_DEBUG = os.environ.get("APP_DEBUG", True)
    ENVIRONMENT_PORT = os.environ.get("APP_PORT", 5000)
    application.run(host='0.0.0.0', port=ENVIRONMENT_PORT, debug=ENVIRONMENT_DEBUG)