# pytrading: some trading experiments
# https://github.com/arrabyte/pytrading
#
# Copyright 2020 Alessandro Arrabito
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

import bs4 as bs
import pickle
import requests
from datetime import datetime, timedelta
import json
import yfinance
from enum import Enum
import stocks_selector
import pandas
import math
import scrapers
import sys, getopt

class PositionType(Enum):
  Long = 1,
  Short = 2,

position_opened = {}
total_gain = 0

def open_position(asset, price = 0.0 , qty = 0, postype: PositionType = PositionType.Long, target_price=0):
  global position_opened
  position_opened[asset] = {'price':price, 'qty': qty, 'positionType' : postype}
  print("Open", asset, round(price, 2), "Qty", qty, "position", postype, "Amount", round(price*qty, 2), "target", round(target_price, 2))

def close_position(asset, close_price = 0.0, qty = 0):
  global total_gain
  global position_opened
  ref = position_opened[asset]
  pos_type = ref['positionType']
  gain = (close_price - ref['price'] if pos_type == PositionType.Long else  ref['price'] - close_price) * ref['qty']
  success = True if gain > 0 else False
  ref['qty'] -= ref['qty'] if qty == 0 else qty
  if ref['qty'] == 0:
    del position_opened[asset]
  total_gain += gain
  print("Close", asset, round(close_price, 2), "Success" if success else "Fail", "Gain", round(gain,2),
    str(round((close_price - ref['price'])*100 / ref['price'] , 2)) + '%')

def backtest(stock, day, investment = 2000.00):
  current_day = day.strftime("%Y-%m-%d")
  end_day = (day + timedelta(days = 1)).strftime("%Y-%m-%d")

  data = yfinance.download(stock[0], start=current_day, end=end_day, interval = "5m")

  if data.empty:
    print(stock[0], 'date', current_day, 'intraday data not available')
    return

  start_price = data['Open'][0] if not math.isnan(data['Open'][0]) else data['Open'][1] #sometimes open[0] is nan
  qty = int(investment / start_price)
  asset = stock[0]
  target_price = stock[1]['pre_close']
  position = stock[1]['position']
  open_position(stock[0], start_price, qty, PositionType.Long if target_price > start_price else PositionType.Short, target_price)
  closed = False
  for tick in data['Close']:
    if position == "Short" and tick <= target_price:
      close_position(asset, tick, qty)
      closed = True
      break

    if position == "Long" and tick >= target_price:
      close_position(asset, tick, qty)
      closed = True
      break

  if not closed:
      close_position(asset, data['Close'][-1], qty)

def backtest_runner(stocks : [], start_date: datetime, end_date: datetime):
  start = start_date.replace(hour=0, minute=0, second=0)
  end = end_date.replace(hour=23, minute=59, second=59)
  global total_gain
  global position_opened

  for day in pandas.bdate_range(start=start, end=end):
    best_gaps = stocks_selector.GapStocksSelector(stocks, day).search()

    if not best_gaps:
      print("Market is closed on day", day.date())
    else:
      investment = 2000.00
      for gap in best_gaps:
        print("gap" , gap)

      position_opened = {}
      total_gain = 0
      for title in best_gaps:
        backtest(title, day, investment)
        if position_opened:
          raise Exception("Some positions are still open", position_opened)
      print("total gain", round(total_gain, 2))

def test_mib_star():
  stocks = scrapers.get_market_stocks(scrapers.MarketIndexScraperInfo.MIB)
  stocks.extend(scrapers.get_market_stocks(scrapers.MarketIndexScraperInfo.STAR))
  backtest_runner(stocks, datetime(2020, 6, 30) , datetime(2020, 7, 10))
'''
def main(argv):
  try:
    opts, args = getopt.getopt(argv,"f:t:",["from=", "to="])
  except getopt.GetoptError:
    print('scrapers.py --market=MIB|STAR')
    sys.exit(2)

  marketIndex = MarketIndexScraperInfo.STAR
  if args:
    if 'STAR' in args:
      marketIndex = MarketIndexScraperInfo.STAR
    elif 'MIB' in args:
      marketIndex = MarketIndexScraperInfo.MIB

  print(get_market_stocks(marketIndex))

if __name__ == "__main__":
  main(sys.argv[1:])
'''