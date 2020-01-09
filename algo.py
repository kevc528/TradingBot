import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import math
from pandas_datareader import data as web
from datetime import datetime, timedelta
from FindTrendingStocks import findTrendingStocks
import datetime as dt
from sklearn.linear_model import LinearRegression

# portfolio stored as a dict for stock to number of stocks
portfolio = {}

# obtain the portfolio of stocks currently holding
def initPortfolio():
	try:
		fObj = open('portfolio.csv')
		for line in fObj:
			if line != '':
				lineSplit = line.strip().split(',')
				portfolio[lineSplit[0]] = lineSplit[1]
		fObj.close()
	except OSError:
		fObj = open('portfolio.csv', 'w')
		fObj.close()

# max num of stocks in portfolio
MAX_SIZE = 30

# returns up, low, width of 20 day bollinger bands
def find20BBBounds(symbol):
	df = web.DataReader(symbol, data_source = 'yahoo', 
		start = datetime.now() - timedelta(days = 40), end = datetime.now())
	df['20 Day MA'] = df['Adj Close'].rolling(window = 20).mean()
	df['20 Day STD'] = df['Adj Close'].rolling(window = 20).std().apply(
		lambda x: x * (math.sqrt(19) / math.sqrt(20)))
	df['Upper Band'] = df['20 Day MA'] + 2 * df['20 Day STD']
	df['Lower Band'] = df['20 Day MA'] - 2 * df['20 Day STD']
	return (df.iloc[-1]['Upper Band'], df.iloc[-1]['Lower Band'], 
	(df.iloc[-1]['Upper Band'] - df.iloc[-1]['Lower Band']) / df.iloc[-1]['20 Day MA'])	

# returns up, low, width of 10 day bollinger bands
def find10BBBounds(symbol):
	df = web.DataReader(symbol, data_source = 'yahoo', 
		start = datetime.now() - timedelta(days = 40), end = datetime.now())
	df['10 Day MA'] = df['Adj Close'].rolling(window = 10).mean()
	df['10 Day STD'] = df['Adj Close'].rolling(window = 10).std().apply(
		lambda x: x * (math.sqrt(9) / math.sqrt(10)))
	df['Upper Band'] = df['10 Day MA'] + 1.5 * df['10 Day STD']
	df['Lower Band'] = df['10 Day MA'] - 1.5 * df['10 Day STD']
	return (df.iloc[-1]['Upper Band'], df.iloc[-1]['Lower Band'], 
	(df.iloc[-1]['Upper Band'] - df.iloc[-1]['Lower Band']) / df.iloc[-1]['10 Day MA'])		

# uses linear regression to find the best fit lines for bands and price
def findEquations(symbol):
	df = web.DataReader(symbol, data_source = 'yahoo', 
		start = datetime.now() - timedelta(days = 90), end = datetime.now())
	df['20 Day MA'] = df['Adj Close'].rolling(window = 20).mean()
	df['20 Day STD'] = df['Adj Close'].rolling(window = 20).std().apply(
		lambda x: x * (math.sqrt(19) / math.sqrt(20)))
	df['Upper Band'] = df['20 Day MA'] + 2 * df['20 Day STD']
	df['Lower Band'] = df['20 Day MA'] - 2 * df['20 Day STD']
	df = df.reset_index()
	df['Date'] = pd.to_datetime(df['Date'])
	df['Date']= df['Date'].map(dt.datetime.toordinal)
	df['Date'] = df['Date'] - df.iloc[-5]['Date']
	prevChart = df.iloc[-5:]

	BBModel = LinearRegression()
	normalizedX = prevChart['Date'].values.reshape(-1, 1)
	normalizedY1 = prevChart['Upper Band'].values.reshape(-1, 1)
	BBModel.fit(normalizedX, normalizedY1)

	RTModel = LinearRegression()
	normalizedY2 = prevChart['Adj Close'].values.reshape(-1, 1)
	RTModel.fit(normalizedX, normalizedY2)

	BBModel2 = LinearRegression()
	normalizedY3 = prevChart['Lower Band'].values.reshape(-1, 1)
	BBModel2.fit(normalizedX, normalizedY3)

	return (BBModel.coef_[0][0], RTModel.coef_[0][0], BBModel2.coef_[0][0],
		BBModel.intercept_[0], RTModel.intercept_[0], BBModel2.intercept_[0])

# plotting bounds using 10 day bollinger bands method, for testing
def plotBBBounds10(symbol):
	df = web.DataReader(symbol, data_source = 'yahoo', 
		start = datetime.now() - timedelta(days = 100), end = datetime.now())
	df['10 Day MA'] = df['Adj Close'].rolling(window = 10).mean()
	df['10 Day STD'] = df['Adj Close'].rolling(window = 10).std().apply(
		lambda x: x * (math.sqrt(9) / math.sqrt(10)))
	df['Upper Band'] = df['10 Day MA'] + 1.5 * df['10 Day STD']
	df['Lower Band'] = df['10 Day MA'] - 1.5 * df['10 Day STD']
	df[['Adj Close', '10 Day MA', 'Upper Band', 'Lower Band']].plot(figsize=(12,6))

	plt.style.use('fivethirtyeight')
	fig = plt.figure(figsize=(12,6))
	ax = fig.add_subplot(111)
	x_axis = df.index.get_level_values(0)

	ax.fill_between(x_axis, df['Upper Band'], df['Lower Band'], color='grey')

	ax.plot(x_axis, df['Adj Close'], color='blue', lw=2)
	ax.plot(x_axis, df['10 Day MA'], color='black', lw=2)

	ax.set_title('10 Day Bollinger Band For ' + symbol)
	ax.set_xlabel('Date (Year/Month)')
	ax.set_ylabel('Price(USD)')

	ax.legend()
	plt.show()

# plotting bounds using 20 day bollinger bands method, for testing
def plotBBBounds20(symbol):
	df = web.DataReader(symbol, data_source = 'yahoo', 
		start = datetime.now() - timedelta(days = 200), end = datetime.now())
	df['20 Day MA'] = df['Adj Close'].rolling(window = 20).mean()
	df['20 Day STD'] = df['Adj Close'].rolling(window = 20).std().apply(
		lambda x: x * (math.sqrt(19) / math.sqrt(20)))
	df['Upper Band'] = df['20 Day MA'] + 2 * df['20 Day STD']
	df['Lower Band'] = df['20 Day MA'] - 2 * df['20 Day STD']
	df[['Adj Close', '20 Day MA', 'Upper Band', 'Lower Band']].plot(figsize=(12,6))

	plt.style.use('fivethirtyeight')
	fig = plt.figure(figsize=(12,6))
	ax = fig.add_subplot(111)
	x_axis = df.index.get_level_values(0)

	ax.fill_between(x_axis, df['Upper Band'], df['Lower Band'], color='grey')

	ax.plot(x_axis, df['Adj Close'], color='blue', lw=2)
	ax.plot(x_axis, df['20 Day MA'], color='black', lw=2)

	ax.set_title('20 Day Bollinger Band For ' + symbol)
	ax.set_xlabel('Date (Year/Month)')
	ax.set_ylabel('Price(USD)')

	# need to add legend
	ax.legend()
	plt.show()

# finds the RSI for a stock
def findRSI(symbol):
	df = web.DataReader(symbol, data_source = 'yahoo', 
		start = datetime.now() - timedelta(days = 30), end = datetime.now())
	df['Gain'] = df['Adj Close'] - df['Open']
	current = df.iloc[-1]
	df = df.iloc[-15:-1]
	dfGain = df[df['Gain'] >= 0]
	dfLose = df[df['Gain'] < 0]
	avgUp = dfGain['Gain'].sum()/14
	avgDown = dfLose['Gain'].sum()/14 * -1
	currGain = 0
	currLoss = 0
	if current['Gain'] > 0:
		currGain = current['Gain']
	else:
		currLoss = abs(current['Gain'])
	avgUp = (avgUp * 13 + currGain)/14
	avgDown = (avgDown * 13 + currLoss)/14
	RS = avgUp/avgDown
	RSI = 100 - 100/(RS + 1)
	return RSI

# gets current price of stock, a little bit behind real time
def getPrice(symbol):
	price = web.DataReader(symbol, data_source = 'yahoo', 
		start = datetime.now() - timedelta(days = 5), end = datetime.now())
	price = price.iloc[-1]['Close']
	return price

# decides what to do with the stock: buy, sell or hold
def decide(symbol):
	fObj = open('DayLog.csv', 'a')
	upperBand, lowerBand, bandWidth = find10BBBounds(symbol)
	x, y, bandWidth = find20BBBounds(symbol)
	rsi = findRSI(symbol)
	price = web.DataReader(symbol, data_source = 'yahoo', 
		start = datetime.now() - timedelta(days = 5), end = datetime.now())
	price = price.iloc[-1]['Close']
	upperSlope, realSlope, lowerSlope, upperI, realI, lowerI = findEquations(symbol)
	nextDayUp = upperSlope + upperI
	nextDayReal = realSlope + realI
	nextDayLow = lowerSlope + lowerI

	if len(portfolio) >= MAX_SIZE:
		action = 'portfolio size large'
	elif (abs((upperSlope - realSlope)/upperSlope) < 0.2 and upperSlope > 0 and 
			abs((upperI - realI)/upperI) < 0.02 and rsi > 20 and rsi < 60):
		print('Upward Slope Buy ' + symbol)
		action = 'buy'
	elif ((realSlope - lowerSlope)/lowerSlope) < 0.2 and abs((lowerI - realI)/lowerI) < 0.02:
		print('Downward Slope Sell ' + symbol)
		action = 'sell'
	elif price < lowerBand and rsi < 35 and (nextDayReal - nextDayLow)/abs(nextDayLow) > 0.01:
		print('Low relative price buy ' + symbol)
		action = 'buy'
	elif price > upperBand and rsi > 70 and abs((nextDayUp - nextDayReal)/nextDayUp) > 0.01:
		print('High relative price sell ' + symbol)
		action = 'sell'
	elif bandWidth < 0.05 and rsi < 35 and rsi > 20:
		print('Expecting surge buy ' + symbol)
		action = 'buy'
	elif bandWidth < 0.05 and rsi > 70:
		print('Expecting drop sell ' + symbol)
		action = 'sell'
	elif bandWidth > 0.3 and rsi > 70:
		print('Surge dying down sell ' + symbol)
		action = 'sell'
	else:
		action = 'hold'
	if symbol in portfolio and action == 'buy':
		action = 'already in portfolio'
	if symbol not in portfolio and action == 'sell':
		action = 'not in portfolio'
	line = '\n' + symbol + ',' + str(datetime.now()) + ',' + str(price) + ',' + str(upperBand) + ',' + \
		str(lowerBand) + ',' + str(bandWidth) + ',' + str(rsi) + ',' + str(upperSlope) + ',' + \
		str(realSlope) + ',' + str(lowerSlope) + ',' + str(upperI) + ',' + str(realI) +',' + str(lowerI) + \
		',' + str(action)
	fObj.write(line)
	fObj.close()
	return action