import threading
import time
from flask import Flask, jsonify, request
from binance import Binance
import numpy as np
import pandas as pd
import time
import os.path


app = Flask(__name__)
global binance
global stopLossActive
global columns 
columns=['base','quote','time_started','time_stopped','executed','stop','limit']
stopLossActive = False
binance = Binance()

# export FLASK_APP=app.py
# flask run
@app.before_first_request
def activate_job():
    global stopLossActive
    def run_job():
        while True:
            if stopLossActive:
                print("Run recurring task")
                time.sleep(3)

    thread = threading.Thread(target=run_job)
    thread.start()

global stoploss
@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/addStopLoss', methods=['POST'])
def addStopLoss():
    base = request.args['base']
    quote = request.args['quote']
    stopLossLevel = request.args['stopLossLevel']

    columns=['base','quote','time_started','time_stopped','executed','stop','limit']

    newStopLoss = {}
    newStopLoss['base'] = base
    newStopLoss['quote'] = quote
    newStopLoss['time_started'] = int(time.time())
    newStopLoss['time_stopped'] = np.NaN
    newStopLoss['executed'] = False
    newStopLoss['stop'] = stopLossLevel
    newStopLoss['limit'] = np.NaN
    filename = 'stops/%s_%s.csv'%(base,quote)
    if os.path.isfile(filename):
        df = pd.read_csv(filename)
        print(df.iloc[-1,:]['executed'])
        stopLoc = df.columns.get_loc('stop')
        executedLoc = df.columns.get_loc('executed')
        if df.iloc[-1,executedLoc]:
            df = df.append(newStopLoss,ignore_index=True)
        else:
            df.iloc[-1,stopLoc] = newStopLoss['stop']
        df.to_csv(filename,index=False)
    else:
        df = pd.DataFrame(newStopLoss,index=[0])
        df.to_csv(filename,index=False)

    return 'Hello, World!'



@app.route('/hasHitStoploss', methods=['POST'])
def hasHitStoploss():
    base = request.args['base']
    quote = request.args['quote']
    filename = 'stops/%s_%s.csv'%(base,quote)
    if os.path.isfile(filename):
        df = pd.read_csv(filename)
        print(df.iloc[-1,:]['executed'])
        stopLoc = df.columns.get_loc('stop')
        executedLoc = df.columns.get_loc('executed')
        return jsonify({'stopLossLevel': df.iloc[-1,stopLoc],'isStopLossBreached': df.iloc[-1,executedLoc]})
    else:
        return jsonify({'stopLossLevel': 0,'isStopLossBreached': False})
        


def run_stop_loss(symbol='BTCUSDT',interval='1h',stoploss=35000):
    global binance
    return binance.last_close_above_stoploss(symbol, interval, stoploss)
  
