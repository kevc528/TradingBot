import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import math
from pandas_datareader import data as web
from datetime import datetime, timedelta
from FindTrendingStocks import findTrendingStocks
import datetime as dt
from sklearn.linear_model import LinearRegression

portfolio = {}

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

MAX_SIZE = 30

# up, low, width
def findBBBounds(symbol):
	df = web.DataReader(symbol, data_source = 'yahoo', 
		start = datetime.now() - timedelta(days = 40), end = datetime.now())
	df['10 Day MA'] = df['Adj Close'].rolling(window = 10).mean()
	df['10 Day STD'] = df['Adj Close'].rolling(window = 10).std().apply(
		lambda x: x * (math.sqrt(9) / math.sqrt(10)))
	df['Upper Band'] = df['10 Day MA'] + 1.5 * df['10 Day STD']
	df['Lower Band'] = df['10 Day MA'] - 1.5 * df['10 Day STD']
	return (df.iloc[-1]['Upper Band'], df.iloc[-1]['Lower Band'], 
	(df.iloc[-1]['Upper Band'] - df.iloc[-1]['Lower Band']) / df.iloc[-1]['10 Day MA'])	

def findEquations(symbol):
	df = web.DataReader(symbol, data_source = 'yahoo', 
		start = datetime.now() - timedelta(days = 60), end = datetime.now())
	df['20 Day MA'] = df['Adj Close'].rolling(window = 20).mean()
	df['20 Day STD'] = df['Adj Close'].rolling(window = 20).std().apply(
		lambda x: x * (math.sqrt(19) / math.sqrt(20)))
	df['Upper Band'] = df['20 Day MA'] + 2 * df['20 Day STD']
	df['Lower Band'] = df['20 Day MA'] - 2 * df['20 Day STD']
	df = df.reset_index()
	df['Date'] = pd.to_datetime(df['Date'])
	df['Date']= df['Date'].map(dt.datetime.toordinal)
	df['Date'] = df['Date'] - df.iloc[-10]['Date']
	prevChart = df.iloc[-10:]

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

# plotting bounds using bollinger bands method, for testing
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

	# need to add legend
	ax.legend()
	plt.show()

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

def getPrice(symbol):
	price = web.DataReader(symbol, data_source = 'yahoo', 
		start = datetime.now() - timedelta(days = 5), end = datetime.now())
	price = price.iloc[-1]['Close']
	return price

def decide(symbol):
	fObj = open('DayLog.csv', 'a')
	upperBand, lowerBand, bandWidth = findBBBounds(symbol)
	rsi = findRSI(symbol)
	price = web.DataReader(symbol, data_source = 'yahoo', 
		start = datetime.now() - timedelta(days = 5), end = datetime.now())
	price = price.iloc[-1]['Close']
	upperSlope, realSlope, lowerSlope, upperI, realI, lowerI = findEquations(symbol)

	# could do distance between fit lines, but currently just testing slope
	if len(portfolio) >= MAX_SIZE:
		action = 'portfolio size large'
	# elif abs((upperSlope - realSlope)/upperSlope) < 0.3 and abs((upperI - realI)/upperI) < 0.2 and rsi < 70:
	# 	print('Upward Slope Buy')
	# 	action = 'buy'
	elif ((upperSlope - realSlope)/upperSlope) < 0.3 and upperSlope > 0 and abs((upperI - realI)/upperI) < 0.2 and rsi < 40:
		print('Upward Slope Buy ' + symbol)
		action = 'buy'
	# elif abs((lowerSlope - realSlope)/lowerSlope) < 0.25 and abs((lowerI - realI)/lowerI) < 0.2:
	# 	print('Downward Slope Sell')
	# 	action = 'sell'
	elif ((realSlope - lowerSlope)/lowerSlope) < 0.25 and abs((lowerI - realI)/lowerI) < 0.2:
		print('Downward Slope Sell ' + symbol)
		action = 'sell'
	elif bandWidth < 0.2 and rsi < 35:
		print('Expecting surge buy ' + symbol)
		action = 'buy'
	elif price < lowerBand and rsi < 35:
		print('Low relative price buy ' + symbol)
		action = 'buy'
	elif price > upperBand and rsi > 70:
		print('High relative price sell ' + symbol)
		action = 'sell'
	elif bandWidth < 0.3 and rsi > 70:
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