from bs4 import BeautifulSoup
import requests

# scrapes for stocks off of yahoo finance trending
# def findTrendingStocks():

# 	url = 'https://finance.yahoo.com/trending-tickers'
# 	resp = requests.get(url)
# 	html = resp.content
# 	soup = BeautifulSoup(html, 'html.parser')
# 	tr_tags = soup.find_all('tr')
# 	td_tags = [tag.find('td') for tag in tr_tags]

# 	symbols = [tag.find('a').text for tag in td_tags if tag != None and '=' not in tag.find('a').text and '^' not in tag.find('a').text]
# 	print('run scrape')
# 	fObj = open('watchlist.csv', 'w')
# 	for s in symbols:
# 		fObj.write(s + '\n')
# 	fObj.close()

# scrapes for stocks off of high momentum charts
# def findTrendingStocks():

# 	url = 'https://tradingstockalerts.com/PremiumAlerts/Momentum'
# 	resp = requests.get(url)
# 	html = resp.content
# 	soup = BeautifulSoup(html, 'html.parser')
# 	table = soup.find('table', {'id' : 'TABLE_1'})
# 	tr_tags = table.find_all('tr')[1:]
# 	td_tags = [tag.find_all('td')[1] for tag in tr_tags]

# 	symbols = [tag.text.strip() for tag in td_tags if tag != None and '=' not in tag.text.strip() and '^' not in tag.text.strip()]
# 	print('run scrape')
# 	fObj = open('watchlist.csv', 'w')
# 	for s in symbols:
# 		fObj.write(s + '\n')
# 	fObj.close()

# scrapes most popular stocks from financial content
def findTrendingStocks():

	symbols = []

	def processPage(page):
		url = page
		resp = requests.get(url)
		html = resp.content
		soup = BeautifulSoup(html, 'html.parser')
		symbolCol = soup.find_all('td', {'class' : 'last col_symbol'})
		return [tag.text.strip() for tag in symbolCol]

	symbols += processPage('http://markets.financialcontent.com/stocks/stocks/dashboard/mostactive')
	symbols += processPage('http://markets.financialcontent.com/stocks/stocks/dashboard/mostactive?CurrentPage=1')
	symbols += processPage('http://markets.financialcontent.com/stocks/stocks/dashboard/mostactive?CurrentPage=2')
	print('run scrape')
	fObj = open('watchlist.csv', 'w')
	for s in symbols:
		fObj.write(s + '\n')
	fObj.close()
