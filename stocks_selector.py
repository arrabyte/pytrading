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

from datetime import datetime, timedelta
import yfinance

def previous_market_day(day, offset = 1):
      previous = day - timedelta(days=offset)
      day_of_week = previous.weekday()
      if day_of_week > 4: #0 is monday and 4 is friday
        previous = previous - timedelta(days = day_of_week - 4)
      return previous

def is_market_day(day):
      return True if day.weekday() <= 4 else False

class StocksSelector:
  stocks = []
  current_day = datetime.today()
  def __init__(self, stocks: [], start_day: datetime):
    self.stocks = stocks
    self.current_day = start_day

  def search(self, bestN = 5):
    pass

class GapStocksSelector(StocksSelector):
  def search(self, bestN = 5):
    day = self.current_day
    if not is_market_day(day):
      return iter([])

    current_day = day.strftime("%Y-%m-%d")
    previous_day = previous_market_day(day).strftime("%Y-%m-%d")
    print("search best gap on close date", previous_day, " and open date", current_day)
    gaps = {}
    for stock_name in self.stocks:
      try:
        stock_data = yfinance.Ticker(stock_name)

        hist = None
        if day.date() < datetime.now().date():
          end_day = ( day + timedelta(days=1) ).strftime("%Y-%m-%d")
          hist = stock_data.history(start = previous_day,
            end = end_day, prepost=False, actions=False, auto_adjust= False)
        else:
          hist = stock_data.history(period='2d',  prepost=False, actions=False, auto_adjust= False)

        #if 'Empty DataFrame' not in hist:
        if not hist.empty:
          if current_day not in hist['Open']:
            print('market is still closed')
            return

          if previous_day not in hist['Close']:
            print('market is still closed')
            return

          gap = hist['Open'][current_day] - hist['Close'][previous_day]
          position = ""
          if hist['Open'][current_day] > hist['High'][previous_day]:
              position = 'Short'
          elif hist['Open'][current_day] < hist['Low'][previous_day]:
              position = 'Long'
          else:
            continue

          gaps[stock_name] = {
            'gap': abs(gap),
            'position': 'Short' if gap > 0 else 'Long',
            'prc': (hist['Open'][current_day] - hist['Close'][previous_day]) * 100 / hist['Close'][previous_day],
            'pre_close': hist['Close'][previous_day],
            'open' : hist['Open'][current_day]
          }

      except ValueError:
        print("Exception fetching data ", ValueError)


    sorted_gaps = sorted(gaps.items(), key = lambda x:abs(x[1]['prc']), reverse=True)
    sorted_gaps_selections = sorted_gaps[0:bestN]
    return sorted_gaps_selections
