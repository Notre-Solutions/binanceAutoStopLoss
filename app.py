import threading
import time
from flask import Flask, jsonify, request
from binance import Binance
import numpy as np
import pandas as pd
import time



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

@app.route('/', methods=['POST'])
def addStopLoss(base, quote, stopLossLevel):
    columns=['base','quote','time_started','time_stopped','executed','stop','limit']
    newStopLoss = {}
    newStopLoss['base'] = base
    newStopLoss['quote'] = quote
    newStopLoss['time_started'] = int(time.time())
    newStopLoss['time_stopped'] = np.NaN
    newStopLoss['executed'] = False
    newStopLoss['stop'] = stopLossLevel
    newStopLoss['limit'] = np.NaN
    df = pd.read_csv('stop_loss.csv')
    # Get the last index of base 
    # TODO: Check if it's been executed or stopped. If so continue if not, stop it and add a new one. (Delete the filtering)
    df2 = df[(df['executed']==False)&(df['time_stopped']==np.NaN)&(df['base']==base)]
    if len(df) == 1:
        newStopLoss['time_started'] = df2.iloc[0]['time_started']
        df.iloc[0] = newStopLoss
    else:
        df.append(newStopLoss,ignore_index=True)
    df.to_csv('stop_loss.csv',index=False)
    return 'Hello, World!'



@app.route('/stoploss', methods=['POST'])
def hasHitStoploss():
    symbol = request.args['symbol']
    interval = request.args['interval']
    stoploss = int(request.args['stoploss'])
    status = run_stop_loss(symbol, interval, stoploss)
    return jsonify({'isStopLossBreached':status})

def run_stop_loss(symbol='BTCUSDT',interval='1h',stoploss=35000):
    global binance
    return binance.last_close_above_stoploss(symbol, interval, stoploss)
  
