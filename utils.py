
import math
import logging
import datetime
class Utils:

  def __init__(self):
    lastHourDateTime = datetime.datetime.now() - datetime.timedelta(hours = 1)
    print(lastHourDateTime.strftime('%Y-%m-%d')+'.log')
    logging.basicConfig(filename=lastHourDateTime.strftime('%Y-%m-%d')+'.log', 
    level=logging.INFO, format='%(asctime)s %(message)s',
    datefmt='%m-%d-%Y %I:%M:%S:')


  def round_decimals_down(self, number:float, decimals:int=2):
      """
      Returns a value rounded down to a specific number of decimal places.
      """
      if not isinstance(decimals, int):
          raise TypeError("decimal places must be an integer")
      elif decimals < 0:
          raise ValueError("decimal places has to be 0 or more")
      elif decimals == 0:
          return math.floor(number)

      factor = 10 ** decimals
      return math.floor(number * factor) / factor