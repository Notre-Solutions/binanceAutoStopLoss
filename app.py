import threading
import time
from flask import Flask, jsonify, request
from binance import Binance


app = Flask(__name__)
global binance
binance = Binance()

# export FLASK_APP=app.py
# flask run
# @app.before_first_request
# def activate_job():
#     def run_job():
#         while True:
#             print("Run recurring task")
#             time.sleep(3)

#     thread = threading.Thread(target=run_job)
#     thread.start()

global stoploss
@app.route('/')
def hello_world():
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
  
