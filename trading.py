import pandas_datareader.data as web
import pandas as pd
from FindTrendingStocks import findTrendingStocks
from algo import decide
from datetime import datetime
import alpaca_trade_api as tradeapi
import requests
import json
from config import *
from algo import *
import os
import time
import csv
from pandas_datareader._utils import RemoteDataError

# alpaca api information, used for requests
BASE_URL = 'https://paper-api.alpaca.markets'
ACCOUNT_URL = '{}/v2/account'.format(BASE_URL)
ORDERS_URL = '{}/v2/orders'.format(BASE_URL)
HEADERS = {'APCA-API-KEY-ID' : API_KEY, 'APCA-API-SECRET-KEY' : SECRET_KEY}

# returns json of information on the account, like equity, buying power, etc.
def getAccountInfo():
	r = requests.get(ACCOUNT_URL, headers = HEADERS)
	return json.loads(r.content)

# creates an order for either buy or sell
def create_order(symbol, qty, side, type, time_in_force):
	data = {
		'symbol' : symbol,
		'qty' : qty,
		'side' : side,
		'type' : type,
		'time_in_force' : time_in_force
	}
	try:
		r = requests.post(ORDERS_URL, json = data, headers = HEADERS)
		response = json.loads(r.content)
		return json.loads(r.content)
	except NameError as e:
		print(e)

# get stocks on the watchlist and portfolio and save them in a set to determine
# which stocks to watch		
def getWatchList():
	trending = []
	fObj = open('watchlist.csv')
	for line in fObj:
		if line != '':
			trending.append(line.strip())
	watchlist = list(portfolio.keys()) + trending
	watchlist = set(watchlist)
	return watchlist

# updates the portfolio.csv file after transactions
def updatePortfolio():
	fObj = open('portfolio.csv', 'w')
	for key in portfolio:
		fObj.write(str(key) + ',' + str(portfolio[key]) + '\n')
	fObj.close()

# cycle function that will repeat (loop), gets stock data and decides what to do
def cycle():
	watchlist = getWatchList()
	for symbol in watchlist:
		try:
			move = decide(symbol)
			if move == 'sell':
				create_order(symbol, portfolio[symbol], 'sell', 'market', 'gtc')
				print('Sold ' + symbol + ' at ' + str(getPrice(symbol)))
				del portfolio[symbol]
				updatePortfolio()
			elif move == 'buy':
				if float(getAccountInfo()['buying_power']) < 3000:
					continue;
				create_order(symbol, 3000 // getPrice(symbol), 'buy', 'market', 'gtc')
				print('Bought ' + symbol + ' at ' + str(getPrice(symbol)))
				portfolio[symbol] = 3000 // getPrice(symbol)
				updatePortfolio()
			else:
				continue;
		except RemoteDataError as e:
			print(e)
		except KeyError as a:
			print(a)
