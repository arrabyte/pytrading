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
from datetime import datetime
import json
from enum import Enum
import sys, getopt

class TrendingType(Enum):
  BEST = "Migliori"
  WORST = "Peggiori"

class MarketIndexScraperInfo(Enum):
  STAR = {'url': 'https://it.wikipedia.org/wiki/FTSE_Italia_STAR', 'suffix': '.MI', 'key': {'class': "wikitable sortable"}, 'position': 0}
  MIB = {'url': 'https://en.wikipedia.org/wiki/FTSE_MIB', 'suffix': '.MI', 'key': {'class': "wikitable sortable", 'id': 'constituents'}, 'position': 1}

def get_market_stocks(market_index):
    stocks_name = []
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1312.27 Safari/537.17'}
    resp = requests.get(market_index.value['url'])
    soup = bs.BeautifulSoup(resp.text, 'lxml')
    table = soup.find('table', market_index.value['key'])
    for row in table.findAll('tr')[1:]:
        fields = row.findAll('td')

        #price = fields[1].text
        #obj = {'isin': isin, 'stock': stock, 'price': price, 'date': datetime.now().timestamp()}
        stocks_name.append(fields[market_index.value['position']].text + market_index.value['suffix'])
    return stocks_name


def get_stocks(TrendingType):
    stocks = []
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1312.27 Safari/537.17'}
    resp = requests.get('https://www.borse.it/idee-di-trading/storico-trading-ideas/')
    soup = bs.BeautifulSoup(resp.text, 'lxml')
    table = soup.find('h3', {'class': "table-header"}, True, TrendingType.value).find_next_sibling()
    for row in table.findAll('tr')[1:]:
        isin = row['id']
        fields = row.findAll('td')
        stock = fields[0].text
        price = fields[1].text
        obj = {'isin': isin, 'stock': stock, 'price': price, 'date': datetime.now().timestamp()}
        stocks.append(obj)
    return stocks

def get_best_stocks():
  return get_stocks(TrendingType.BEST)

def get_worst_stocks():
  return get_stocks(TrendingType.WORST)

def main(argv):
  try:
    opts, args = getopt.getopt(argv,"m:",["market="])
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
